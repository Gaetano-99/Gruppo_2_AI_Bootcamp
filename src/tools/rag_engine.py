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
    "del", "della", "dello", "dei", "degli", "delle", "dal", "dalla",
    "nel", "nella", "nello", "nei", "negli", "nelle", "sul", "sulla",
    "con", "per", "tra", "fra", "che", "chi", "cui", "non", "una",
    "uno", "gli", "alle", "all", "agli", "come", "dove", "quando",
    "quanto", "cosa", "questo", "questa", "questi", "queste", "ogni",
    "sono", "essere", "avere", "fare", "dire", "anche", "molto",
    "più", "suo", "sua", "suoi", "sue", "loro", "quale", "quali",
})


# ===========================================================================
# Funzione principale — API pubblica del modulo
# ===========================================================================

def cerca_chunk_rilevanti(
    corso_id: int | None,
    query: str,
    top_k: int = _TOP_K_DEFAULT,
    materiale_id: int | None = None,
) -> list[dict]:
    """Recupera i chunk più rilevanti per una query, filtrati per corso o materiale.

    Implementa una pipeline in due fasi:
        1. **Retrieval SQL**: query LIKE multi-parola-chiave su tre campi.
        2. **Ranking Python**: scoring basato su frequenza e campo di match.

    Quando ``corso_id`` è None, la ricerca avviene direttamente per ``materiale_id``
    (materiali personali senza corso associato).

    Args:
        corso_id: ID del corso universitario. None per materiali senza corso.
        query: Argomento o domanda dell'utente.
        top_k: Numero massimo di chunk da restituire (default 8).
        materiale_id: Se specificato, limita i chunk al singolo materiale.

    Returns:
        Lista di dizionari rappresentanti i chunk, ciascuno arricchito
        con il campo ``score_rilevanza`` (intero) e ``parole_trovate`` (lista).
        Ordinati per ``score_rilevanza`` decrescente.

    Example:
        >>> chunk = cerca_chunk_rilevanti(1, "normalizzazione database", top_k=5)
        >>> print(chunk[0]["score_rilevanza"])
        12
    """
    parole_chiave: list[str] = _estrai_parole_chiave(query)

    # Quando corso_id è None, cerca direttamente per materiale_id
    if corso_id is None:
        if not materiale_id:
            return []
        return _query_sql_like_materiale(materiale_id, parole_chiave, top_k)

    if not parole_chiave:
        # Argomento generico: restituisce i primi Top-K del corso
        candidati = _recupera_chunk_generici(corso_id, top_k * 3 if materiale_id else top_k)
        if materiale_id:
            candidati = [c for c in candidati if c.get("materiale_id") == materiale_id][:top_k]
        return candidati

    # Fase 1: retrieval SQL con LIKE
    candidati: list[dict] = _query_sql_like(corso_id, parole_chiave)

    if not candidati:
        # Fallback: nessun match → chunk generici del corso
        candidati = _recupera_chunk_generici(corso_id, top_k * 3 if materiale_id else top_k)
        if materiale_id:
            candidati = [c for c in candidati if c.get("materiale_id") == materiale_id][:top_k]
        return candidati

    # Filtra per materiale specifico se richiesto
    if materiale_id:
        candidati = [c for c in candidati if c.get("materiale_id") == materiale_id]

    # Fase 2: scoring e ranking
    candidati_con_score: list[dict] = _calcola_score(candidati, parole_chiave)

    # Ordina per score decrescente, poi per indice_chunk ASC (parità)
    candidati_con_score.sort(
        key=lambda c: (-c["score_rilevanza"], c.get("indice_chunk", 0))
    )

    return candidati_con_score[:top_k]


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


def conta_chunk_corso(corso_id: int | None, materiale_id: int | None = None) -> int:
    """Conta il numero totale di chunk disponibili per un corso o materiale.

    Args:
        corso_id: ID del corso universitario. None per materiali senza corso.
        materiale_id: Se specificato e corso_id è None, conta per materiale.

    Returns:
        Numero totale di chunk in ``materiali_chunks``.
    """
    if corso_id is None:
        if materiale_id:
            return db.conta("materiali_chunks", {"materiale_id": materiale_id})
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
