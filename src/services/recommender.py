"""
Modulo: recommender.py
Responsabilità: Motore di raccomandazione corsi per la dashboard studente.

Algoritmo a tre segnali (nessuna chiamata LLM — deterministico e spiegabile):

    Segnale 1 — Curriculum  (peso 40%)
        I corsi obbligatori del corso di laurea dello studente che non ha ancora
        frequentato sono la raccomandazione più solida: sono nel suo percorso
        e non li ha ancora affrontati.

    Segnale 2 — Engagement  (peso 35%)
        Ogni piano generato autonomamente è un segnale forte di interesse.
        Si calcola un punteggio pesato per recency (i piani recenti valgono
        di più) e frequenza (più piani sullo stesso corso → interesse consolidato).

    Segnale 3 — Similarità semantica  (peso 25%)
        Si costruisce il "profilo di interesse" dello studente aggregando le
        keyword (argomenti_chiave) dei corsi che ha già studiato.
        Per ogni corso candidato si calcola la similarità di Jaccard tra le
        sue keyword e il profilo studente. Corsi con temi affini vengono promossi.

Output:
    Lista di ``RaccomandazioneCorso`` ordinata per ``score_totale`` decrescente,
    con breakdown per segnale e motivazione leggibile per la UI.

Note architetturali:
    - Zero dipendenze esterne oltre alla platform_sdk.
    - Tutti i calcoli avvengono in memoria su liste di dizionari.
    - Il modulo è stateless: si può chiamare ad ogni caricamento della dashboard.
    - La motivazione è costruita in italiano, pronta per essere mostrata in UI.
"""

import json
import math
import sys
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))  # src/services/ → root
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from platform_sdk.database import db


# ---------------------------------------------------------------------------
# Pesi dei segnali (devono sommare a 1.0)
# ---------------------------------------------------------------------------
_PESO_CURRICULUM  : float = 0.40
_PESO_ENGAGEMENT  : float = 0.35
_PESO_SEMANTICO   : float = 0.25

# Decadimento temporale per l'engagement: ogni 30 giorni il peso si dimezza
_DECAY_DIMEZZAMENTO_GIORNI: int = 30

# Numero massimo di raccomandazioni restituite
_TOP_N_DEFAULT: int = 6


# ---------------------------------------------------------------------------
# Strutture dati output
# ---------------------------------------------------------------------------

@dataclass
class ScoreBreakdown:
    """Dettaglio del punteggio per ogni segnale (0.0 – 1.0 ciascuno)."""
    curriculum : float = 0.0   # è un corso obbligatorio non frequentato?
    engagement : float = 0.0   # ha già generato contenuti su questo corso?
    semantico  : float = 0.0   # le sue keyword coincidono con quelle del corso?


@dataclass
class RaccomandazioneCorso:
    """Un singolo corso raccomandato, con score e motivazione."""
    corso_id        : int
    corso_nome      : str
    score_totale    : float                    # 0.0 – 1.0
    breakdown       : ScoreBreakdown
    motivazione     : str                      # testo UI-ready in italiano
    tag             : list[str] = field(default_factory=list)  # es. ["Obbligatorio", "Già esplorato"]


# ===========================================================================
# Entry point pubblico
# ===========================================================================

def raccomanda_corsi(
    studente_id: int,
    top_n: int = _TOP_N_DEFAULT,
) -> list[RaccomandazioneCorso]:
    """Calcola e restituisce i corsi consigliati per uno studente.

    Args:
        studente_id: ID dell'utente per cui calcolare le raccomandazioni.
        top_n: Numero massimo di risultati da restituire.

    Returns:
        Lista di ``RaccomandazioneCorso`` ordinata per score decrescente.
        Restituisce lista vuota se lo studente non esiste o non ci sono
        corsi candidati.

    Example (in una pagina Streamlit)::

        from src.services.recommender import raccomanda_corsi

        raccomandazioni = raccomanda_corsi(st.session_state.user["user_id"])
        for r in raccomandazioni:
            st.metric(r.corso_nome, f"{r.score_totale:.0%}")
            st.caption(r.motivazione)
    """
    # 1. Carica profilo studente
    studente = _carica_studente(studente_id)
    if not studente:
        return []

    # 2. Corsi già frequentati / iscritti (da escludere dai candidati)
    corsi_iscritti: set[int] = _corsi_iscritti(studente_id)

    # 3. Tutti i corsi attivi non ancora iscritti → candidati
    candidati: list[dict] = _corsi_candidati(corsi_iscritti)
    if not candidati:
        return []

    # 4. Calcola i tre segnali
    s1 = _segnale_curriculum(studente, candidati)
    s2 = _segnale_engagement(studente_id, candidati)
    s3 = _segnale_semantico(studente_id, corsi_iscritti, candidati)

    # 5. Combina i segnali e costruisce le raccomandazioni
    raccomandazioni: list[RaccomandazioneCorso] = []
    for corso in candidati:
        cid = corso["id"]

        breakdown = ScoreBreakdown(
            curriculum = s1.get(cid, 0.0),
            engagement = s2.get(cid, 0.0),
            semantico  = s3.get(cid, 0.0),
        )
        score_totale = (
            breakdown.curriculum * _PESO_CURRICULUM
            + breakdown.engagement * _PESO_ENGAGEMENT
            + breakdown.semantico  * _PESO_SEMANTICO
        )

        motivazione, tag = _costruisci_motivazione(breakdown, corso)

        raccomandazioni.append(RaccomandazioneCorso(
            corso_id     = cid,
            corso_nome   = corso["nome"],
            score_totale = round(score_totale, 4),
            breakdown    = breakdown,
            motivazione  = motivazione,
            tag          = tag,
        ))

    # 6. Ordina per score decrescente, poi per nome (stabilità)
    raccomandazioni.sort(key=lambda r: (-r.score_totale, r.corso_nome))

    # Filtra solo corsi con almeno un segnale attivo (score > 0)
    raccomandazioni = [r for r in raccomandazioni if r.score_totale > 0]

    return raccomandazioni[:top_n]


# ===========================================================================
# Segnale 1 — Curriculum
# ===========================================================================

def _segnale_curriculum(studente: dict, candidati: list[dict]) -> dict[int, float]:
    """Score 1.0 se il corso è obbligatorio nel percorso di laurea dello studente.

    Se lo studente non ha un corso di laurea associato, questo segnale è 0
    per tutti i candidati (non penalizza gli altri segnali).
    """
    scores: dict[int, float] = {}
    laurea_id = studente.get("corso_di_laurea_id")

    if not laurea_id:
        return {c["id"]: 0.0 for c in candidati}

    # Corsi obbligatori del suo percorso
    obbligatori = db.trova_tutti(
        "corsi_laurea_universitari",
        {"corso_di_laurea_id": laurea_id, "obbligatorio": 1},
    )
    ids_obbligatori: set[int] = {r["corso_universitario_id"] for r in obbligatori}

    # Corsi facoltativi del suo percorso (score parziale)
    facoltativi = db.trova_tutti(
        "corsi_laurea_universitari",
        {"corso_di_laurea_id": laurea_id, "obbligatorio": 0},
    )
    ids_facoltativi: set[int] = {r["corso_universitario_id"] for r in facoltativi}

    for corso in candidati:
        cid = corso["id"]
        if cid in ids_obbligatori:
            scores[cid] = 1.0
        elif cid in ids_facoltativi:
            scores[cid] = 0.5
        else:
            scores[cid] = 0.0

    return scores


# ===========================================================================
# Segnale 2 — Engagement
# ===========================================================================

def _segnale_engagement(studente_id: int, candidati: list[dict]) -> dict[int, float]:
    """Score basato su quanti piani ha generato su ogni corso e quanto recentemente.

    Formula per ogni corso:
        raw_score = Σ  decay(giorni_fa_i)   per ogni piano i sul corso
        dove decay(g) = 2^(-g / DECAY_DIMEZZAMENTO_GIORNI)

    Il risultato è normalizzato su [0, 1] dividendo per il massimo trovato.
    """
    scores: dict[int, float] = {c["id"]: 0.0 for c in candidati}
    candidati_ids: set[int] = {c["id"] for c in candidati}

    piani = db.trova_tutti("piani_personalizzati", {"studente_id": studente_id})

    ora = datetime.now(timezone.utc)

    for piano in piani:
        cid = piano.get("corso_universitario_id")
        if cid not in candidati_ids:
            continue

        # Calcola decay temporale
        created_at_str = piano.get("created_at") or ""
        try:
            created_at = datetime.fromisoformat(created_at_str.replace(" ", "T"))
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            giorni_fa = max(0, (ora - created_at).days)
        except (ValueError, AttributeError):
            giorni_fa = 30  # valore neutro se data mancante

        decay = math.pow(2, -giorni_fa / _DECAY_DIMEZZAMENTO_GIORNI)
        scores[cid] = scores.get(cid, 0.0) + decay

    # Normalizza su [0, 1]
    max_score = max(scores.values(), default=0.0)
    if max_score > 0:
        scores = {k: round(v / max_score, 4) for k, v in scores.items()}

    return scores


# ===========================================================================
# Segnale 3 — Similarità semantica
# ===========================================================================

def _segnale_semantico(
    studente_id: int,
    corsi_iscritti: set[int],
    candidati: list[dict],
) -> dict[int, float]:
    """Jaccard similarity tra il profilo keyword dello studente e i candidati.

    Profilo studente = unione di tutte le keyword dei materiali dei corsi
    che ha già studiato (piani generati + corsi iscritti).

    Jaccard(A, B) = |A ∩ B| / |A ∪ B|
    """
    # Costruisci profilo keyword studente
    profilo_studente: set[str] = _keyword_profilo_studente(studente_id, corsi_iscritti)

    if not profilo_studente:
        return {c["id"]: 0.0 for c in candidati}

    scores: dict[int, float] = {}
    for corso in candidati:
        keywords_corso: set[str] = _keyword_corso(corso["id"])
        scores[corso["id"]] = _jaccard(profilo_studente, keywords_corso)

    return scores


def _keyword_profilo_studente(studente_id: int, corsi_iscritti: set[int]) -> set[str]:
    """Aggrega le keyword di tutti i corsi che lo studente ha frequentato o studiato."""
    # Corsi da cui estrarre keyword: iscritti + corsi su cui ha generato piani
    piani = db.trova_tutti("piani_personalizzati", {"studente_id": studente_id})
    corsi_piani: set[int] = {p["corso_universitario_id"] for p in piani if p.get("corso_universitario_id")}

    corsi_fonte: set[int] = corsi_iscritti | corsi_piani

    keywords: set[str] = set()
    for cid in corsi_fonte:
        keywords |= _keyword_corso(cid)

    return keywords


def _keyword_corso(corso_id: int) -> set[str]:
    """Restituisce l'insieme di keyword normalizzate per un corso."""
    chunks = db.trova_tutti("materiali_chunks", {"corso_universitario_id": corso_id})
    keywords: set[str] = set()

    for chunk in chunks:
        raw = chunk.get("argomenti_chiave") or ""
        try:
            lista: list[str] = json.loads(raw)
            for kw in lista:
                # Normalizzazione: minuscolo, strip, split su spazi per keyword composte
                for token in kw.lower().strip().split():
                    if len(token) >= 3:
                        keywords.add(token)
        except (json.JSONDecodeError, TypeError):
            # Fallback: usa il sommario come keyword bag
            sommario = (chunk.get("sommario") or "").lower()
            for token in sommario.split():
                if len(token) >= 4:
                    keywords.add(token)

    return keywords


def _jaccard(a: set[str], b: set[str]) -> float:
    """Coefficiente di Jaccard tra due insiemi. Restituisce 0.0 se entrambi vuoti."""
    if not a or not b:
        return 0.0
    intersezione = len(a & b)
    unione = len(a | b)
    return round(intersezione / unione, 4) if unione > 0 else 0.0


# ===========================================================================
# Costruzione motivazione UI
# ===========================================================================

def _costruisci_motivazione(
    breakdown: ScoreBreakdown,
    corso: dict,
) -> tuple[str, list[str]]:
    """Genera una motivazione leggibile in italiano e i tag per la UI.

    Args:
        breakdown: Punteggi dettagliati per il corso.
        corso: Dizionario con i dati del corso (nome, cfu, anno_di_corso, ...).

    Returns:
        Tupla (motivazione: str, tag: list[str]).
    """
    parti: list[str] = []
    tag: list[str] = []

    if breakdown.curriculum >= 1.0:
        parti.append("fa parte del tuo percorso di laurea obbligatorio")
        tag.append("Obbligatorio")
    elif breakdown.curriculum >= 0.5:
        parti.append("è un esame facoltativo del tuo percorso di laurea")
        tag.append("Facoltativo")

    if breakdown.engagement >= 0.7:
        parti.append("hai già esplorato attivamente questi argomenti")
        tag.append("Già esplorato")
    elif breakdown.engagement >= 0.3:
        parti.append("hai già iniziato a studiare materiali correlati")

    if breakdown.semantico >= 0.15:
        parti.append("gli argomenti sono affini a quelli che stai già studiando")
        tag.append("Temi affini")
    elif breakdown.semantico >= 0.05:
        parti.append("condivide alcuni argomenti con i tuoi studi attuali")

    if not parti:
        parti.append("potrebbe arricchire il tuo percorso formativo")

    # Dati aggiuntivi del corso
    cfu = corso.get("cfu")
    anno = corso.get("anno_di_corso")
    info_extra = []
    if cfu:
        info_extra.append(f"{cfu} CFU")
    if anno:
        info_extra.append(f"anno {anno}")

    motivazione = "Ti consigliamo questo corso perché " + ", ".join(parti) + "."
    if info_extra:
        motivazione += f" ({', '.join(info_extra)})"

    return motivazione, tag


# ===========================================================================
# Helper DB
# ===========================================================================

def _carica_studente(studente_id: int) -> Optional[dict]:
    """Carica il record dell'utente dal DB."""
    risultati = db.trova_tutti("users", {"id": studente_id})
    return risultati[0] if risultati else None


def _corsi_iscritti(studente_id: int) -> set[int]:
    """Restituisce gli ID dei corsi a cui lo studente è già iscritto."""
    iscrizioni = db.trova_tutti("studenti_corsi", {"studente_id": studente_id})
    return {r["corso_universitario_id"] for r in iscrizioni}


def _corsi_candidati(corsi_iscritti: set[int]) -> list[dict]:
    """Restituisce i corsi attivi non ancora iscritti dallo studente."""
    tutti = db.trova_tutti("corsi_universitari", {"attivo": 1})
    return [c for c in tutti if c["id"] not in corsi_iscritti]
