"""
Modulo: rag_engine.py
Responsabilità: Retrieval intelligente dei chunk semantici per il sistema RAG.

Implementa una ricerca basata su keyword matching SQL LIKE multi-campo e
un algoritmo di scoring che assegna un punteggio di rilevanza a ogni chunk
in base al numero di parole chiave trovate e al campo in cui compaiono.

Strategia di retrieval:
    1. Estrai le parole chiave significative dall'argomento richiesto.
    2. Costruisci una query SQL con clausole LIKE sui campi ``testo``,
       ``sommario`` e ``argomenti_chiave``, filtrando per ``corso_universitario_id``.
    3. Calcola uno score di rilevanza in Python per ogni chunk trovato:
       - Ogni match in ``argomenti_chiave`` → peso 3
       - Ogni match in ``sommario``          → peso 2
       - Ogni match in ``testo``             → peso 1
    4. Ordina per score decrescente e ritorna i Top-K chunk.

Architettura:
    - Tutte le query passano per ``db.esegui()`` o ``db.trova_tutti()``.
    - Nessuna variabile globale fuori dai moduli di configurazione.
    - Type hinting completo, docstring in italiano stile Google.
"""

import sys
import os
import re
import json
from typing import Optional

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from platform_sdk.database import db

# ---------------------------------------------------------------------------
# Costanti di retrieval
# ---------------------------------------------------------------------------
_TOP_K_DEFAULT: int = 8                  # chunk massimi da passare all'LLM
_LUNGHEZZA_MIN_PAROLA: int = 3           # ignora parole troppo corte (articoli, ecc.)
_PESO_ARGOMENTI_CHIAVE: int = 3          # match sul campo argomenti_chiave
_PESO_SOMMARIO: int = 2                  # match sul campo sommario
_PESO_TESTO: int = 1                     # match sul campo testo

# Stopwords italiane da escludere dalle parole chiave
_STOPWORDS: frozenset[str] = frozenset({
    # --- Articoli, preposizioni, pronomi ---
    "del", "della", "dello", "dei", "degli", "delle", "dal", "dalla",
    "nel", "nella", "nello", "nei", "negli", "nelle", "sul", "sulla",
    "con", "per", "tra", "fra", "che", "chi", "cui", "non", "una",
    "uno", "gli", "alle", "all", "agli", "come", "dove", "quando",
    "quanto", "cosa", "questo", "questa", "questi", "queste", "ogni",
    "sono", "essere", "avere", "fare", "dire", "anche", "molto",
    "più", "suo", "sua", "suoi", "sue", "loro", "quale", "quali",
    # --- Termini didattici generici (troppo comuni nei materiali, non discriminanti) ---
    "introduzione", "applicazioni", "applicazione", "pratiche", "pratico",
    "lezione", "lezioni", "corso", "capitolo", "sezione", "argomento",
    "parte", "esempio", "esempi", "concetti", "concetto",
    "base", "basi", "fondamenti", "generale", "generali",
    "teoria", "pratica", "teorico", "teorica",
    "approfondimento", "dispensa", "materiale", "slide",
    "esercizi", "esercizio", "generi", "genera", "generare",
})


# ===========================================================================
# Funzione principale — API pubblica del modulo
# ===========================================================================

def cerca_chunk_rilevanti(
    corso_id: int | None,
    query: str,
    top_k: int = _TOP_K_DEFAULT,
    materiale_id: int | None = None,
    materiale_ids: list[int] | None = None,
) -> list[dict]:
    """Recupera i chunk più rilevanti per una query, filtrati per corso o materiale.

    Implementa una pipeline in due fasi:
        1. **Retrieval SQL**: query LIKE multi-parola-chiave su tre campi.
        2. **Ranking Python**: scoring basato su frequenza e campo di match.

    Quando ``corso_id`` è None, la ricerca avviene direttamente per ``materiale_id``
    o ``materiale_ids`` (materiali personali senza corso associato).

    Args:
        corso_id: ID del corso universitario. None per materiali senza corso.
        query: Argomento o domanda dell'utente.
        top_k: Numero massimo di chunk da restituire (default 8).
        materiale_id: Se specificato, limita i chunk al singolo materiale.
        materiale_ids: Se specificato, recupera chunk da più materiali contemporaneamente.
            Ha priorità su ``materiale_id`` se entrambi sono forniti.

    Returns:
        Lista di dizionari rappresentanti i chunk, ciascuno arricchito
        con il campo ``score_rilevanza`` (intero) e ``parole_trovate`` (lista).
        Ordinati per ``score_rilevanza`` decrescente.

    Example:
        >>> chunk = cerca_chunk_rilevanti(1, "normalizzazione database", top_k=5)
        >>> print(chunk[0]["score_rilevanza"])
        12
    """
    # Normalizza: se materiale_ids è fornito, usalo; altrimenti materiale_id singolo
    ids_effettivi: list[int] | None = None
    if materiale_ids and len(materiale_ids) > 0:
        ids_effettivi = materiale_ids
    elif materiale_id:
        ids_effettivi = [materiale_id]

    parole_chiave: list[str] = _estrai_parole_chiave(query)

    # Quando corso_id è None, cerca direttamente per materiale_id(s)
    if corso_id is None:
        if not ids_effettivi:
            return []
        if len(ids_effettivi) == 1:
            return _query_sql_like_materiale(ids_effettivi[0], parole_chiave, top_k)
        return _query_sql_like_materiali_multipli(ids_effettivi, parole_chiave, top_k)

    if not parole_chiave:
        # Argomento generico: restituisce i primi Top-K del corso
        candidati = _recupera_chunk_generici(corso_id, top_k * 3 if ids_effettivi else top_k)
        if ids_effettivi:
            ids_set = set(ids_effettivi)
            candidati = [c for c in candidati if c.get("materiale_id") in ids_set][:top_k]
        return candidati

    # Fase 1: retrieval SQL con LIKE
    candidati: list[dict] = _query_sql_like(corso_id, parole_chiave)

    if not candidati:
        # Fallback: nessun match → chunk generici del corso
        candidati = _recupera_chunk_generici(corso_id, top_k * 3 if ids_effettivi else top_k)
        if ids_effettivi:
            ids_set = set(ids_effettivi)
            candidati = [c for c in candidati if c.get("materiale_id") in ids_set][:top_k]
        return candidati

    # Filtra per materiale/i specifico/i se richiesto
    if ids_effettivi:
        ids_set = set(ids_effettivi)
        candidati = [c for c in candidati if c.get("materiale_id") in ids_set]

    # Fase 2: scoring e ranking
    candidati_con_score: list[dict] = _calcola_score(candidati, parole_chiave)

    # Ordina per score decrescente, poi per indice_chunk ASC (parità)
    candidati_con_score.sort(
        key=lambda c: (-c["score_rilevanza"], c.get("indice_chunk", 0))
    )

    risultato: list[dict] = candidati_con_score[:top_k]

    # Se i risultati keyword sono meno di top_k, integra con chunk generici
    # (es. corso con nome generico che non matcha il contenuto del materiale)
    if len(risultato) < top_k:
        presenti_ids: set[int] = {c["id"] for c in risultato}
        generici = _recupera_chunk_generici(corso_id, top_k)
        for g in generici:
            if g["id"] not in presenti_ids:
                risultato.append(g)
                presenti_ids.add(g["id"])
                if len(risultato) >= top_k:
                    break

    return risultato


def formatta_contesto_rag(chunks: list[dict]) -> str:
    """Formatta i chunk recuperati in una stringa di contesto per l'LLM.

    Il formato include esplicitamente gli ID globali dei chunk in modo che
    l'LLM possa citarli nei ``chunk_ids_utilizzati``.

    Args:
        chunks: Lista di chunk (come restituiti da ``cerca_chunk_rilevanti``).

    Returns:
        Stringa formattata con separatori e intestazioni per ogni chunk.

    Example:
        >>> testo = formatta_contesto_rag(chunks)
        >>> print(testo[:80])
        [Chunk ID: 42 | Score: 9 | Parole chiave trovate: sql, join]
        Testo: ...
    """
    if not chunks:
        return "(Nessun materiale disponibile per questo argomento)"

    blocchi: list[str] = []
    for chunk in chunks:
        chunk_id: int = chunk["id"]
        score: int = chunk.get("score_rilevanza", 0)
        parole: list[str] = chunk.get("parole_trovate", [])
        testo: str = chunk.get("testo", "")
        sommario: str = chunk.get("sommario") or ""

        intestazione = (
            f"[Chunk ID: {chunk_id} | Score rilevanza: {score} | "
            f"Parole chiave: {', '.join(parole) if parole else '(generico)'}]"
        )
        corpo = f"Testo: {testo}"
        if sommario:
            corpo = f"Sommario: {sommario}\n{corpo}"

        blocchi.append(f"{intestazione}\n{corpo}")

    return "\n\n---\n\n".join(blocchi)


def conta_chunk_corso(
    corso_id: int | None,
    materiale_id: int | None = None,
    materiale_ids: list[int] | None = None,
) -> int:
    """Conta il numero totale di chunk disponibili per un corso o materiale.

    Args:
        corso_id: ID del corso universitario. None per materiali senza corso.
        materiale_id: Se specificato e corso_id è None, conta per materiale.
        materiale_ids: Se specificato, conta chunk per più materiali.

    Returns:
        Numero totale di chunk in ``materiali_chunks``.
    """
    # Normalizza: materiale_ids ha priorità
    ids_effettivi: list[int] | None = None
    if materiale_ids and len(materiale_ids) > 0:
        ids_effettivi = materiale_ids
    elif materiale_id:
        ids_effettivi = [materiale_id]

    if corso_id is None:
        if ids_effettivi:
            if len(ids_effettivi) == 1:
                return db.conta("materiali_chunks", {"materiale_id": ids_effettivi[0]})
            placeholders = ",".join("?" for _ in ids_effettivi)
            righe = db.esegui(
                f"SELECT COUNT(*) AS n FROM materiali_chunks WHERE materiale_id IN ({placeholders})",
                ids_effettivi,
            )
            return righe[0]["n"] if righe else 0
        return 0
    return db.conta("materiali_chunks", {"corso_universitario_id": corso_id})


# ===========================================================================
# Funzioni interne
# ===========================================================================

def _estrai_parole_chiave(testo: str) -> list[str]:
    """Estrae le parole chiave significative da un testo.

    Rimuove punteggiatura, converte in minuscolo, filtra stopwords italiane
    e parole troppo brevi.

    Args:
        testo: Argomento o query dell'utente.

    Returns:
        Lista di parole chiave pulite e deuplicate, ordinate per lunghezza
        decrescente (le parole più specifiche hanno priorità).

    Example:
        >>> _estrai_parole_chiave("le query SQL di tipo JOIN nel database")
        ['query', 'tipo', 'join', 'database']
    """
    # Rimuovi punteggiatura e converti in minuscolo
    testo_pulito: str = re.sub(r"[^\w\s]", " ", testo.lower())
    parole: list[str] = testo_pulito.split()

    # Filtraggio: lunghezza minima + stopwords
    parole_filtrate: list[str] = [
        p for p in parole
        if len(p) >= _LUNGHEZZA_MIN_PAROLA and p not in _STOPWORDS
    ]

    # Deduplicazione mantenendo l'ordine
    viste: set[str] = set()
    parole_uniche: list[str] = []
    for p in parole_filtrate:
        if p not in viste:
            viste.add(p)
            parole_uniche.append(p)

    # Ordina per lunghezza decrescente (parole più specifiche prima)
    parole_uniche.sort(key=len, reverse=True)
    return parole_uniche


def recupera_sommari_materiali(materiale_ids: list[int]) -> list[dict]:
    """Recupera un sommario sintetico per ciascun materiale, utile per analisi di coerenza.

    Per ogni materiale restituisce titolo, tipo, e gli argomenti chiave aggregati
    dai suoi chunk.

    Args:
        materiale_ids: Lista di ID materiali da analizzare.

    Returns:
        Lista di dizionari con 'materiale_id', 'titolo', 'tipo', 'argomenti_chiave',
        'sommari_chunks'.
    """
    risultati: list[dict] = []
    for mid in materiale_ids:
        # Info base del materiale
        mat = db.esegui(
            "SELECT id, titolo, tipo FROM materiali_didattici WHERE id = ?", [mid]
        )
        if not mat:
            continue
        info = mat[0]

        # Aggregazione argomenti chiave e sommari dai chunk
        chunks = db.esegui(
            "SELECT argomenti_chiave, sommario, titolo_sezione "
            "FROM materiali_chunks WHERE materiale_id = ? ORDER BY indice_chunk ASC",
            [mid],
        )
        argomenti_tutti: list[str] = []
        sommari: list[str] = []
        for c in chunks:
            if c.get("argomenti_chiave"):
                try:
                    argomenti_tutti.extend(json.loads(c["argomenti_chiave"]))
                except (json.JSONDecodeError, TypeError):
                    pass
            if c.get("sommario"):
                sommari.append(c["sommario"])

        # Deduplicazione argomenti
        argomenti_unici = list(dict.fromkeys(argomenti_tutti))

        risultati.append({
            "materiale_id": info["id"],
            "titolo": info["titolo"],
            "tipo": info.get("tipo", ""),
            "argomenti_chiave": argomenti_unici,
            "sommari_chunks": sommari[:5],  # max 5 sommari per non esplodere il contesto
        })

    return risultati


def _query_sql_like_materiali_multipli(
    materiale_ids: list[int],
    parole_chiave: list[str],
    top_k: int = _TOP_K_DEFAULT,
) -> list[dict]:
    """Cerca chunk filtrati per più materiale_ids (usato quando corso_id è None).

    Args:
        materiale_ids: Lista di ID materiali.
        parole_chiave: Parole chiave da cercare.
        top_k: Numero massimo di chunk da restituire.

    Returns:
        Lista di chunk con score di rilevanza.
    """
    placeholders = ",".join("?" for _ in materiale_ids)

    if not parole_chiave:
        chunks = db.esegui(
            f"SELECT id, materiale_id, corso_universitario_id, indice_chunk, "
            f"titolo_sezione, testo, sommario, argomenti_chiave, n_token "
            f"FROM materiali_chunks WHERE materiale_id IN ({placeholders}) "
            f"ORDER BY materiale_id, indice_chunk ASC",
            list(materiale_ids),
        )
        # Distribuzione equa dei chunk tra i materiali
        chunks = _distribuisci_chunk_equi(chunks, materiale_ids, top_k)
        for c in chunks:
            c["score_rilevanza"] = 0
            c["parole_trovate"] = []
        return chunks

    condizioni: list[str] = []
    parametri: list = list(materiale_ids)
    for parola in parole_chiave:
        condizioni.append(
            "(LOWER(testo) LIKE ? OR LOWER(sommario) LIKE ? OR LOWER(argomenti_chiave) LIKE ?)"
        )
        parametri.extend([f"%{parola}%", f"%{parola}%", f"%{parola}%"])

    clausola_where = " OR ".join(condizioni)
    query = (
        "SELECT id, materiale_id, corso_universitario_id, indice_chunk, "
        "titolo_sezione, testo, sommario, argomenti_chiave, n_token "
        f"FROM materiali_chunks "
        f"WHERE materiale_id IN ({placeholders}) AND ({clausola_where}) "
        f"ORDER BY indice_chunk ASC"
    )
    candidati = db.esegui(query, parametri)

    if not candidati:
        # Fallback: tutti i chunk dei materiali
        candidati = db.esegui(
            f"SELECT id, materiale_id, corso_universitario_id, indice_chunk, "
            f"titolo_sezione, testo, sommario, argomenti_chiave, n_token "
            f"FROM materiali_chunks WHERE materiale_id IN ({placeholders}) "
            f"ORDER BY materiale_id, indice_chunk ASC",
            list(materiale_ids),
        )
        candidati = _distribuisci_chunk_equi(candidati, materiale_ids, top_k)
        for c in candidati:
            c["score_rilevanza"] = 0
            c["parole_trovate"] = []
        return candidati

    return _calcola_score(candidati, parole_chiave)[:top_k]


def _distribuisci_chunk_equi(
    chunks: list[dict],
    materiale_ids: list[int],
    top_k: int,
) -> list[dict]:
    """Distribuisce i chunk equamente tra i materiali, garantendo rappresentazione bilanciata.

    Args:
        chunks: Tutti i chunk disponibili.
        materiale_ids: Lista degli ID materiali.
        top_k: Numero massimo totale di chunk da restituire.

    Returns:
        Lista di chunk bilanciata tra i materiali.
    """
    per_materiale: dict[int, list[dict]] = {mid: [] for mid in materiale_ids}
    for c in chunks:
        mid = c.get("materiale_id")
        if mid in per_materiale:
            per_materiale[mid].append(c)

    n_materiali = len(materiale_ids)
    quota_base = max(1, top_k // n_materiali)
    risultato: list[dict] = []

    for mid in materiale_ids:
        risultato.extend(per_materiale[mid][:quota_base])

    # Se c'è spazio residuo, riempi con chunk rimanenti
    presenti = {c["id"] for c in risultato}
    for c in chunks:
        if len(risultato) >= top_k:
            break
        if c["id"] not in presenti:
            risultato.append(c)
            presenti.add(c["id"])

    return risultato[:top_k]


def _query_sql_like_materiale(
    materiale_id: int,
    parole_chiave: list[str],
    top_k: int = _TOP_K_DEFAULT,
) -> list[dict]:
    """Cerca chunk filtrati per materiale_id (usato quando corso_id è None).

    Args:
        materiale_id: ID del materiale didattico.
        parole_chiave: Parole chiave da cercare.
        top_k: Numero massimo di chunk da restituire.

    Returns:
        Lista di chunk con score di rilevanza.
    """
    if not parole_chiave:
        chunks = db.trova_tutti(
            "materiali_chunks",
            {"materiale_id": materiale_id},
            ordine="indice_chunk ASC",
            limite=top_k,
        )
        for c in chunks:
            c["score_rilevanza"] = 0
            c["parole_trovate"] = []
        return chunks

    condizioni: list[str] = []
    parametri: list = [materiale_id]
    for parola in parole_chiave:
        condizioni.append(
            "(LOWER(testo) LIKE ? OR LOWER(sommario) LIKE ? OR LOWER(argomenti_chiave) LIKE ?)"
        )
        parametri.extend([f"%{parola}%", f"%{parola}%", f"%{parola}%"])

    clausola_where = " OR ".join(condizioni)
    query = (
        "SELECT id, materiale_id, corso_universitario_id, indice_chunk, "
        "titolo_sezione, testo, sommario, argomenti_chiave, n_token "
        f"FROM materiali_chunks "
        f"WHERE materiale_id = ? AND ({clausola_where}) "
        f"ORDER BY indice_chunk ASC"
    )
    candidati = db.esegui(query, parametri)

    if not candidati:
        # Fallback: tutti i chunk del materiale
        candidati = db.trova_tutti(
            "materiali_chunks",
            {"materiale_id": materiale_id},
            ordine="indice_chunk ASC",
            limite=top_k,
        )
        for c in candidati:
            c["score_rilevanza"] = 0
            c["parole_trovate"] = []
        return candidati

    return _calcola_score(candidati, parole_chiave)[:top_k]


def _query_sql_like(
    corso_id: int,
    parole_chiave: list[str],
) -> list[dict]:
    """Esegue una query SQL LIKE su testo, sommario e argomenti_chiave.

    Costruisce una clausola OR per ogni parola chiave e per ogni campo,
    garantendo sempre il filtro ``corso_universitario_id = ?``.

    Args:
        corso_id: ID del corso (filtro obbligatorio sullo schema).
        parole_chiave: Lista di parole chiave da cercare.

    Returns:
        Lista di chunk che matchano almeno una parola chiave in almeno un campo.
    """
    if not parole_chiave:
        return []

    # Costruisci le condizioni LIKE per ogni parola e ogni campo
    condizioni: list[str] = []
    parametri: list = [corso_id]

    for parola in parole_chiave:
        # Ogni parola viene cercata nei tre campi
        condizioni.append(
            "(LOWER(testo) LIKE ? OR LOWER(sommario) LIKE ? OR LOWER(argomenti_chiave) LIKE ?)"
        )
        parametri.extend([f"%{parola}%", f"%{parola}%", f"%{parola}%"])

    clausola_where: str = " OR ".join(condizioni)
    query: str = (
        "SELECT id, materiale_id, corso_universitario_id, indice_chunk, "
        "titolo_sezione, testo, sommario, argomenti_chiave, n_token "
        f"FROM materiali_chunks "
        f"WHERE corso_universitario_id = ? AND ({clausola_where}) "
        f"ORDER BY indice_chunk ASC"
    )

    return db.esegui(query, parametri)


def _calcola_score(
    chunks: list[dict],
    parole_chiave: list[str],
) -> list[dict]:
    """Calcola uno score di rilevanza per ogni chunk.

    Il punteggio è calcolato come somma pesata dei match:
        - ``argomenti_chiave``: peso 3 per ogni parola trovata
        - ``sommario``:         peso 2 per ogni parola trovata
        - ``testo``:            peso 1 per ogni parola trovata

    Args:
        chunks: Lista di chunk da valutare.
        parole_chiave: Parole chiave da cercare in ogni chunk.

    Returns:
        La stessa lista di chunk, ciascuno arricchito con
        ``score_rilevanza`` (int) e ``parole_trovate`` (list[str]).
    """
    chunks_arricchiti: list[dict] = []

    for chunk in chunks:
        score: int = 0
        parole_trovate: list[str] = []

        testo: str = (chunk.get("testo") or "").lower()
        sommario: str = (chunk.get("sommario") or "").lower()

        # argomenti_chiave è salvato come JSON array string (es. '["sql", "select"]').
        # Parsiamo l'array e uniamo le keyword in una stringa per il matching,
        # evitando falsi positivi sui caratteri JSON come virgolette e parentesi.
        raw_argomenti: str = chunk.get("argomenti_chiave") or ""
        try:
            argomenti_list: list[str] = json.loads(raw_argomenti)
            argomenti: str = " ".join(argomenti_list).lower()
        except (json.JSONDecodeError, TypeError):
            argomenti: str = raw_argomenti.lower()

        for parola in parole_chiave:
            trovata: bool = False
            # Match per campo con peso differente
            if parola in argomenti:
                score += _PESO_ARGOMENTI_CHIAVE
                trovata = True
            if parola in sommario:
                score += _PESO_SOMMARIO
                trovata = True
            if parola in testo:
                score += _PESO_TESTO
                trovata = True
            if trovata:
                parole_trovate.append(parola)

        chunk_arricchito: dict = dict(chunk)
        chunk_arricchito["score_rilevanza"] = score
        chunk_arricchito["parole_trovate"] = parole_trovate
        chunks_arricchiti.append(chunk_arricchito)

    return chunks_arricchiti


def _recupera_chunk_generici(corso_id: int, top_k: int) -> list[dict]:
    """Fallback: restituisce i primi Top-K chunk del corso senza filtro.

    Usato quando l'argomento è troppo generico o non ci sono match SQL.

    Args:
        corso_id: ID del corso universitario.
        top_k: Numero massimo di chunk da restituire.

    Returns:
        Lista di chunk arricchiti con ``score_rilevanza=0`` e
        ``parole_trovate=[]``.
    """
    chunks: list[dict] = db.trova_tutti(
        "materiali_chunks",
        {"corso_universitario_id": corso_id},
        ordine="indice_chunk ASC",
        limite=top_k,
    )
    for chunk in chunks:
        chunk["score_rilevanza"] = 0
        chunk["parole_trovate"] = []
    return chunks


# ===========================================================================
# Ricerca platform-wide ("Lea sceglie")
# ===========================================================================

def conta_chunk_piattaforma() -> int:
    """Conta il numero totale di chunk presenti sulla piattaforma.

    Returns:
        Numero totale di righe in ``materiali_chunks``.
    """
    righe = db.esegui("SELECT COUNT(*) AS n FROM materiali_chunks")
    return righe[0]["n"] if righe else 0


def cerca_chunk_piattaforma(
    query: str,
    top_k: int = _TOP_K_DEFAULT,
) -> list[dict]:
    """Recupera i chunk più rilevanti cercando su TUTTO il materiale della piattaforma.

    A differenza di ``cerca_chunk_rilevanti``, non filtra per corso o materiale:
    interroga l'intera tabella ``materiali_chunks`` con JOIN su ``materiali_didattici``
    per ottenere titolo e tipo del materiale sorgente.

    Args:
        query: Argomento o domanda dell'utente.
        top_k: Numero massimo di chunk da restituire (default 8).

    Returns:
        Lista di dizionari-chunk arricchiti con ``score_rilevanza``,
        ``parole_trovate``, ``materiale_titolo`` e ``materiale_tipo``.
    """
    parole_chiave: list[str] = _estrai_parole_chiave(query)

    if not parole_chiave:
        # Argomento generico: restituisce i primi chunk della piattaforma
        return _recupera_chunk_piattaforma_generici(top_k)

    # Costruisci condizioni LIKE per ogni parola chiave
    condizioni: list[str] = []
    parametri: list = []
    for parola in parole_chiave:
        condizioni.append(
            "(LOWER(mc.testo) LIKE ? OR LOWER(mc.sommario) LIKE ? OR LOWER(mc.argomenti_chiave) LIKE ?)"
        )
        parametri.extend([f"%{parola}%", f"%{parola}%", f"%{parola}%"])

    clausola_where = " OR ".join(condizioni)
    sql = (
        "SELECT mc.id, mc.materiale_id, mc.corso_universitario_id, mc.indice_chunk, "
        "mc.titolo_sezione, mc.testo, mc.sommario, mc.argomenti_chiave, mc.n_token, "
        "md.titolo AS materiale_titolo, md.tipo AS materiale_tipo "
        "FROM materiali_chunks mc "
        "JOIN materiali_didattici md ON mc.materiale_id = md.id "
        f"WHERE {clausola_where} "
        "ORDER BY mc.indice_chunk ASC "
        "LIMIT 200"
    )
    candidati: list[dict] = db.esegui(sql, parametri)

    if not candidati:
        return _recupera_chunk_piattaforma_generici(top_k)

    # Scoring e ranking
    candidati_con_score = _calcola_score(candidati, parole_chiave)
    candidati_con_score.sort(
        key=lambda c: (-c["score_rilevanza"], c.get("indice_chunk", 0))
    )

    # --- Filtro di rilevanza minima ---
    # Nella ricerca platform-wide, il rischio di includere materiali non pertinenti
    # è alto. Richiediamo che ogni chunk abbia matchato almeno una soglia minima
    # di parole chiave per essere considerato rilevante.
    if len(parole_chiave) >= 2:
        soglia_min_parole = max(2, (len(parole_chiave) + 1) // 2)  # almeno 50%
        filtrati = [
            c for c in candidati_con_score
            if len(c.get("parole_trovate", [])) >= soglia_min_parole
        ]
        # Usa il filtro solo se restano abbastanza risultati
        if filtrati:
            candidati_con_score = filtrati

    return candidati_con_score[:top_k]


def _recupera_chunk_piattaforma_generici(top_k: int) -> list[dict]:
    """Fallback: restituisce i primi chunk della piattaforma senza filtro keyword.

    Args:
        top_k: Numero massimo di chunk da restituire.

    Returns:
        Lista di chunk arricchiti con metadati del materiale sorgente.
    """
    chunks = db.esegui(
        "SELECT mc.id, mc.materiale_id, mc.corso_universitario_id, mc.indice_chunk, "
        "mc.titolo_sezione, mc.testo, mc.sommario, mc.argomenti_chiave, mc.n_token, "
        "md.titolo AS materiale_titolo, md.tipo AS materiale_tipo "
        "FROM materiali_chunks mc "
        "JOIN materiali_didattici md ON mc.materiale_id = md.id "
        "ORDER BY mc.materiale_id, mc.indice_chunk ASC "
        f"LIMIT {int(top_k)}"
    )
    for chunk in chunks:
        chunk["score_rilevanza"] = 0
        chunk["parole_trovate"] = []
    return chunks


def formatta_riferimenti_materiali(chunks: list[dict]) -> str:
    """Produce un testo formattato con i riferimenti ai materiali usati.

    Raggruppa i chunk per materiale sorgente e lista titolo, tipo e sezioni
    utilizzate. Pensato per essere inserito come capitolo finale del piano.

    Args:
        chunks: Lista di chunk (come restituiti da ``cerca_chunk_piattaforma``).

    Returns:
        Testo Markdown con l'elenco dei materiali e le sezioni consultate.
    """
    if not chunks:
        return "(Nessun materiale di riferimento disponibile)"

    # Raggruppa per materiale_id
    materiali: dict[int, dict] = {}
    for c in chunks:
        mid = c.get("materiale_id")
        if not mid:
            continue
        if mid not in materiali:
            materiali[mid] = {
                "titolo": c.get("materiale_titolo") or f"Materiale {mid}",
                "tipo": c.get("materiale_tipo") or "",
                "sezioni": [],
            }
        titolo_sez = c.get("titolo_sezione")
        if titolo_sez and titolo_sez not in materiali[mid]["sezioni"]:
            materiali[mid]["sezioni"].append(titolo_sez)

    if not materiali:
        # Fallback: chunk senza materiale_titolo (recupera dal DB)
        mat_ids = list({c.get("materiale_id") for c in chunks if c.get("materiale_id")})
        for mid in mat_ids:
            info = db.esegui("SELECT titolo, tipo FROM materiali_didattici WHERE id = ?", [mid])
            if info:
                materiali[mid] = {
                    "titolo": info[0]["titolo"],
                    "tipo": info[0].get("tipo", ""),
                    "sezioni": [],
                }

    righe: list[str] = [
        "Materiali didattici consultati per la generazione di questa lezione:\n"
    ]
    for mid, info in materiali.items():
        tipo_label = f" ({info['tipo'].upper()})" if info["tipo"] else ""
        righe.append(f"- **{info['titolo']}**{tipo_label}")
        for sez in info["sezioni"]:
            righe.append(f"  - {sez}")

    return "\n".join(righe)
