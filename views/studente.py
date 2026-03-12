# ============================================================================
# LearnAI Platform — Homepage Studente
# Università Federico II di Napoli
#
# Layout a tre colonne:
#   SINISTRA  — Corsi iscritti + piani personalizzati AI (navigazione)
#   CENTRO    — Contenuto corso selezionato (capitoli → paragrafi → testo)
#   DESTRA    — Chatbot Lea (orchestratore AI)
#
# Dipendenze:
#   platform_sdk.database.db    → query DB
#   src.agents.orchestrator     → chatbot Lea
#   src.services.recommender    → raccomandazioni corsi
# ============================================================================

import json
import sys
import os

import streamlit as st

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from platform_sdk.database import db

# Import lazy degli agenti AI (solo se necessario, evita errori se AWS non configurato)
def _import_orchestratore():
    try:
        from src.agents.orchestrator import (
            chat_con_orchestratore,
            aggiorna_contesto_sessione,
            reset_sessione_chat,
        )
        return chat_con_orchestratore, aggiorna_contesto_sessione, reset_sessione_chat
    except Exception as e:
        return None, None, None


def _import_recommender():
    try:
        from src.services.recommender import raccomanda_corsi
        return raccomanda_corsi
    except Exception:
        return None


# ---------------------------------------------------------------------------
# CSS — Palette Federico II
# ---------------------------------------------------------------------------
_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Source+Sans+3:wght@300;400;600&display=swap');

:root {
    --blue:      #003087;
    --blue-dark: #001A4D;
    --blue-mid:  #1351A8;
    --red:       #C8102E;
    --gold:      #C5A028;
    --light:     #F0F4F8;
    --gray:      #5A6A7E;
    --border:    #C8D5E3;
    --white:     #FFFFFF;
    --green:     #1A7F4B;
}

.stApp {
    background: #F0F4F8 !important;
    font-family: 'Source Sans 3', sans-serif !important;
}
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 0 !important; padding-bottom: 0 !important; }

/* ---- TOPBAR ---- */
.topbar {
    background: linear-gradient(135deg, #001A4D 0%, #003087 60%, #1351A8 100%);
    border-bottom: 3px solid #C5A028;
    padding: 14px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: -1rem -1rem 24px -1rem;
}
.topbar-brand {
    font-family: 'Playfair Display', serif;
    color: #fff;
    font-size: 1.25rem;
    font-weight: 700;
}
.topbar-brand span { color: #C5A028; }
.topbar-user {
    color: rgba(255,255,255,0.85);
    font-size: 0.88rem;
    display: flex;
    align-items: center;
    gap: 12px;
}
.topbar-avatar {
    width: 34px; height: 34px;
    border-radius: 50%;
    background: #C5A028;
    color: #001A4D;
    font-weight: 700;
    font-size: 0.85rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

/* ---- SIDEBAR CORSI ---- */
.corso-item {
    background: #fff;
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 10px;
    border-left: 4px solid #C8D5E3;
    cursor: pointer;
    transition: border-color 0.15s, box-shadow 0.15s;
    box-shadow: 0 2px 8px rgba(0,48,135,0.06);
}
.corso-item:hover { border-left-color: #003087; box-shadow: 0 4px 16px rgba(0,48,135,0.12); }
.corso-item.attivo { border-left-color: #003087; background: #EEF4FF; }
.corso-item .corso-nome {
    font-weight: 600;
    color: #001A4D;
    font-size: 0.9rem;
    line-height: 1.3;
}
.corso-item .corso-meta {
    color: #5A6A7E;
    font-size: 0.78rem;
    margin-top: 4px;
}
.corso-stato {
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.stato-iscritto  { background: #E8F0FE; color: #003087; }
.stato-completato { background: #E6F9F0; color: #1A7F4B; }
.stato-abbandonato { background: #FDE8EA; color: #C8102E; }

/* ---- PIANO PERSONALIZZATO ---- */
.piano-card {
    background: linear-gradient(135deg, #EEF4FF 0%, #F6F9FF 100%);
    border: 1px solid #BFCFE8;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: box-shadow 0.15s;
}
.piano-card:hover { box-shadow: 0 4px 16px rgba(0,48,135,0.12); }
.piano-card.attivo { border: 2px solid #003087; box-shadow: 0 4px 16px rgba(0,48,135,0.15); }
.piano-card h5 {
    font-weight: 600;
    color: #001A4D;
    font-size: 0.88rem;
    margin: 0 0 4px 0;
}
.piano-card .piano-meta {
    color: #5A6A7E;
    font-size: 0.76rem;
}
.ai-badge {
    background: #003087;
    color: #fff;
    font-size: 0.62rem;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 12px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* ---- SEZIONE CENTRALE — CONTENUTO ---- */
.section-header {
    font-family: 'Playfair Display', serif;
    font-size: 1.55rem;
    color: #001A4D;
    font-weight: 700;
    margin-bottom: 4px;
}
.section-sub {
    color: #5A6A7E;
    font-size: 0.9rem;
    margin-bottom: 24px;
    font-weight: 300;
}
.capitolo-header {
    background: #fff;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 8px;
    border-left: 4px solid #003087;
    box-shadow: 0 2px 8px rgba(0,48,135,0.07);
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.capitolo-header h4 {
    font-weight: 600;
    color: #001A4D;
    font-size: 0.95rem;
    margin: 0;
}
.paragrafo-box {
    background: #fff;
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 10px;
    margin-left: 16px;
    box-shadow: 0 2px 10px rgba(0,48,135,0.07);
    border-top: 2px solid #EEF4FF;
}
.paragrafo-box h5 {
    font-weight: 600;
    color: #003087;
    font-size: 0.9rem;
    margin: 0 0 10px 0;
}
.no-content-hint {
    color: #5A6A7E;
    font-size: 0.83rem;
    font-style: italic;
    margin: 4px 0 0 0;
}
.paragrafo-testo {
    color: #2D3A4A;
    font-size: 0.92rem;
    line-height: 1.7;
}
.empty-state {
    text-align: center;
    padding: 48px 24px;
    color: #5A6A7E;
}
.empty-state .icon { font-size: 3rem; margin-bottom: 12px; }
.empty-state h3 { color: #001A4D; font-family: 'Playfair Display', serif; }

/* ---- CHATBOT LEA ---- */
.chat-header {
    background: linear-gradient(135deg, #001A4D 0%, #003087 100%);
    color: #fff;
    padding: 14px 18px;
    border-radius: 12px 12px 0 0;
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 0;
}
.chat-header .chat-title { font-weight: 700; font-size: 0.95rem; }
.chat-header .chat-sub { font-size: 0.75rem; opacity: 0.75; }
.chat-online {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #4FE886;
    flex-shrink: 0;
}
.chat-container {
    background: #fff;
    border: 1px solid #C8D5E3;
    border-top: none;
    border-radius: 0 0 12px 12px;
    height: 380px;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 10px;
}
.msg-user {
    background: #003087;
    color: #fff;
    border-radius: 14px 14px 4px 14px;
    padding: 10px 14px;
    font-size: 0.87rem;
    max-width: 82%;
    align-self: flex-end;
    line-height: 1.5;
}
.msg-ai {
    background: #F0F4F8;
    color: #1A2535;
    border-radius: 4px 14px 14px 14px;
    padding: 10px 14px;
    font-size: 0.87rem;
    max-width: 88%;
    align-self: flex-start;
    line-height: 1.55;
    border: 1px solid #E0E8F2;
}
.msg-ai strong { color: #003087; }

/* ---- TYPING INDICATOR ---- */
.typing-bubble {
    background: #F0F4F8;
    border: 1px solid #E0E8F2;
    border-radius: 4px 14px 14px 14px;
    padding: 12px 16px;
    display: flex;
    gap: 4px;
    align-items: center;
    align-self: flex-start;
    margin-bottom: 10px;
    max-width: 80px;
}
.dot {
    width: 6px; height: 6px;
    background: #5A6A7E;
    border-radius: 50%;
    animation: typing 1.4s infinite ease-in-out;
}
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing {
    0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
    30% { transform: translateY(-4px); opacity: 1; }
}

/* ---- STICKY CHAT COLUMN ---- */
/* Target specifico per l'ultima colonna del layout principale */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child {
    position: -webkit-sticky; /* Supporto Safari */
    position: sticky;
    top: 2rem;
    align-self: start;
    z-index: 99;
}

/* Fix per assicurarsi che i contenitori genitori non blocchino lo sticky */
div[data-testid="stVerticalBlock"] {
    overflow: visible !important;
}

/* ---- RACCOMANDAZIONI ---- */
.raccomandazione-card {
    background: #fff;
    border-radius: 10px;
    padding: 14px 16px;
    border-left: 4px solid #C5A028;
    box-shadow: 0 2px 8px rgba(0,48,135,0.07);
    margin-bottom: 10px;
}
.raccomandazione-card h5 {
    color: #001A4D;
    font-weight: 600;
    font-size: 0.88rem;
    margin: 0 0 4px 0;
}
.raccomandazione-card p {
    color: #5A6A7E;
    font-size: 0.8rem;
    margin: 0;
    line-height: 1.5;
}
.score-bar-outer {
    height: 4px;
    background: #E8EEF6;
    border-radius: 4px;
    margin-top: 8px;
}
.score-bar-inner {
    height: 4px;
    border-radius: 4px;
    background: linear-gradient(90deg, #003087, #C5A028);
}

/* ---- CHAT INPUT NATIVO (st.chat_input) ---- */
.stChatInput {
    border-top: 1px solid #C8D5E3 !important;
    padding-top: 6px !important;
    margin-top: 0 !important;
}
.stChatInput textarea {
    border-radius: 8px !important;
    border: 1.5px solid #C8D5E3 !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 0.88rem !important;
}
.stChatInput textarea:focus {
    border-color: #003087 !important;
    box-shadow: 0 0 0 3px rgba(0,48,135,0.08) !important;
}

/* ---- SUGGERIMENTI COMPATTI ---- */
div[data-testid="column"] .stButton > button[kind="secondary"] {
    background: #F0F4F8 !important;
    color: #003087 !important;
    border: 1px solid #C8D5E3 !important;
    border-radius: 20px !important;
    font-size: 0.78rem !important;
    padding: 5px 8px !important;
    font-weight: 600 !important;
    white-space: nowrap;
}
div[data-testid="column"] .stButton > button[kind="secondary"]:hover {
    background: #E0EBFF !important;
    border-color: #003087 !important;
}

/* Riduci gap verticale tra area chat e suggerimenti */
.stChatFloatingInputContainer { margin-top: 0 !important; }
.divider-label {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #5A6A7E;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    margin: 16px 0 10px;
}
.divider-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #C8D5E3;
}

/* ---- TOPBAR LOGOUT BG (col_esci a sinistra) ---- */
.topbar-logout-bg {
    background: linear-gradient(135deg, #001A4D 0%, #003087 100%);
    border-bottom: 3px solid #C5A028;
    height: 66px;
    margin: -1rem 0 0 -1rem;
}
/* Bottone Esci: primo stHorizontalBlock → prima column */
[data-testid="stHorizontalBlock"]:first-of-type
    [data-testid="column"]:first-child
    .stButton > button {
    background: transparent !important;
    border: 1.5px solid rgba(255,255,255,0.55) !important;
    color: #C5A028 !important;
    font-weight: 700 !important;
    font-size: 0.80rem !important;
    border-radius: 6px !important;
    margin-top: -52px !important;
    position: relative !important;
    z-index: 200 !important;
}
[data-testid="stHorizontalBlock"]:first-of-type
    [data-testid="column"]:first-child
    .stButton > button:hover {
    background: rgba(197,160,40,0.18) !important;
    border-color: #C5A028 !important;
}

/* ---- NAV TOC ---- */
.nav-toc {
    background: #fff;
    border: 1px solid #C8D5E3;
    border-left: 4px solid #C5A028;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 0;
    box-shadow: 0 2px 8px rgba(0,48,135,0.06);
}
.nav-toc-title {
    font-weight: 700;
    color: #001A4D;
    font-size: 0.85rem;
    margin-bottom: 10px;
}
.toc-list {
    list-style: none;
    padding: 0; margin: 0;
    display: flex;
    flex-direction: column;
    gap: 4px;
}
.toc-link {
    display: flex;
    align-items: center;
    gap: 8px;
    text-decoration: none;
    color: #1351A8;
    font-size: 0.83rem;
    font-weight: 600;
    padding: 5px 8px;
    border-radius: 6px;
    transition: background 0.12s;
}
.toc-link:hover { background: #EEF4FF; }
.toc-num {
    min-width: 22px; height: 22px;
    background: #003087;
    color: #fff;
    border-radius: 50%;
    font-size: 0.72rem;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.toc-count {
    margin-left: auto;
    color: #5A6A7E;
    font-size: 0.75rem;
    font-weight: 400;
}

/* ---- CONTENT TYPE BADGES ---- */
.content-type-badge {
    display: inline-block;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 12px;
    margin: 8px 0 6px;
}
.badge-quiz   { background: #FDE8EA; color: #C8102E; }
.badge-flash  { background: #FFF6E0; color: #8A6800; }
.badge-schema { background: #E6F9F0; color: #1A7F4B; }

/* ---- QUIZ DOMANDA ---- */
.quiz-domanda {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 8px 10px;
    border-radius: 8px;
    background: #FAFBFD;
    border: 1px solid #E8EEF6;
    margin-bottom: 6px;
    font-size: 0.86rem;
    color: #2D3A4A;
    line-height: 1.5;
}
.quiz-num {
    min-width: 20px; height: 20px;
    background: #C8102E;
    color: #fff;
    border-radius: 50%;
    font-size: 0.68rem;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 2px;
}

/* ---- FLASHCARD MINI ---- */
.flashcard-mini {
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,48,135,0.09);
    margin-bottom: 8px;
}
.fc-front {
    background: #003087; color: #fff;
    padding: 10px 12px;
    font-size: 0.80rem; font-weight: 600; line-height: 1.4;
}
.fc-back {
    background: #F6F9FF; color: #2D3A4A;
    padding: 10px 12px;
    font-size: 0.79rem;
    border-top: 1px solid #C8D5E3;
    line-height: 1.4;
}

/* ---- FLASHCARD INTERATTIVA (reveal) ---- */
.fc-toggle { display: none; }
.fc-front-side {
    background: #003087; color: #fff;
    padding: 10px 12px;
    border-radius: 8px 8px 0 0;
    font-size: 0.80rem; font-weight: 600; line-height: 1.4;
}
.fc-reveal-btn {
    display: block; cursor: pointer;
    font-size: 0.72rem; color: #1351A8;
    background: #EEF4FF;
    border: 1px solid #C8D5E3; border-top: none;
    border-radius: 0 0 8px 8px;
    padding: 5px 10px; text-align: center;
    user-select: none; margin-bottom: 6px;
}
.fc-back-side {
    display: none;
    background: #F6F9FF; color: #2D3A4A;
    padding: 10px 12px;
    border: 1px solid #C8D5E3; border-top: none;
    border-radius: 0 0 8px 8px;
    font-size: 0.79rem; line-height: 1.4;
    margin-bottom: 6px;
}
.fc-toggle:checked ~ .fc-back-side { display: block; }
.fc-toggle:checked ~ .fc-reveal-btn { display: none; }

/* ---- QUIZ INTERATTIVO (reveal) ---- */
.qa-toggle { display: none; }
.quiz-item { margin-bottom: 8px; }
.quiz-opzioni { margin: 6px 0 4px 28px; }
.quiz-opzione { font-size: 0.82rem; color: #2D3A4A; padding: 2px 0; }
.qa-reveal-btn {
    display: inline-block; cursor: pointer;
    font-size: 0.72rem; color: #C8102E;
    background: #FDE8EA;
    border: 1px solid #F5C0C8;
    border-radius: 12px;
    padding: 3px 10px; margin: 4px 0 2px 28px;
    user-select: none;
}
.qa-answer {
    display: none;
    background: #E6F9F0; color: #1A7F4B;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 0.82rem;
    margin: 4px 0 2px 28px;
    line-height: 1.5;
}
.qa-toggle:checked ~ .qa-answer { display: block; }
.qa-toggle:checked ~ .qa-reveal-btn { display: none; }
</style>
"""


# ---------------------------------------------------------------------------
# Helper DB
# ---------------------------------------------------------------------------

def _get_corsi_studente(studente_id: int) -> list[dict]:
    """Restituisce i corsi universitari a cui lo studente è iscritto."""
    return db.esegui("""
        SELECT
            cu.id, cu.nome, cu.cfu, cu.anno_di_corso, cu.livello,
            sc.stato, sc.voto, sc.anno_accademico
        FROM studenti_corsi sc
        JOIN corsi_universitari cu ON cu.id = sc.corso_universitario_id
        WHERE sc.studente_id = ?
        ORDER BY sc.stato ASC, cu.anno_di_corso ASC
    """, [studente_id])


def _get_piani_corso(studente_id: int, corso_id: int) -> list[dict]:
    """Restituisce i piani personalizzati AI per uno studente su un corso specifico."""
    return db.trova_tutti(
        "piani_personalizzati",
        {"studente_id": studente_id, "corso_universitario_id": corso_id},
        ordine="created_at DESC",
    )


def _get_tutti_piani_studente(studente_id: int) -> list[dict]:
    """Restituisce tutti i piani personalizzati dello studente, con nome del corso."""
    return db.esegui("""
        SELECT pp.id, pp.titolo, pp.created_at, pp.corso_universitario_id,
               cu.nome AS corso_nome
        FROM piani_personalizzati pp
        LEFT JOIN corsi_universitari cu ON cu.id = pp.corso_universitario_id
        WHERE pp.studente_id = ?
        ORDER BY pp.created_at DESC
    """, [studente_id])


def _get_tutti_cdl() -> list[dict]:
    try:
        return db.trova_tutti("corsi_di_laurea", {}, ordine="nome ASC")
    except Exception:
        return []


def _get_docenti() -> list[dict]:
    try:
        return db.esegui(
            "SELECT id, nome, cognome FROM users WHERE ruolo = 'docente' ORDER BY cognome, nome",
            [],
        )
    except Exception:
        return []


def _cerca_corsi(nome: str, docente_id: int | None, cfu: int | None, cdl_id: int | None) -> list[dict]:
    conditions = ["cu.attivo = 1"]
    params: list = []

    if nome:
        conditions.append("cu.nome LIKE ?")
        params.append(f"%{nome}%")
    if docente_id is not None:
        conditions.append("cu.docente_id = ?")
        params.append(docente_id)
    if cfu is not None and cfu > 0:
        conditions.append("cu.cfu = ?")
        params.append(cfu)
    if cdl_id is not None:
        conditions.append("clu.corso_di_laurea_id = ?")
        params.append(cdl_id)

    where = " AND ".join(conditions)
    sql = f"""
        SELECT cu.id, cu.nome, cu.cfu, cu.anno_di_corso, cu.livello, cu.semestre,
               u.id AS docente_id, u.nome AS docente_nome, u.cognome AS docente_cognome,
               GROUP_CONCAT(DISTINCT cdl.nome) AS corsi_di_laurea
        FROM corsi_universitari cu
        JOIN users u ON u.id = cu.docente_id
        LEFT JOIN corsi_laurea_universitari clu ON clu.corso_universitario_id = cu.id
        LEFT JOIN corsi_di_laurea cdl ON cdl.id = clu.corso_di_laurea_id
        WHERE {where}
        GROUP BY cu.id
        ORDER BY cu.nome ASC
    """
    try:
        return db.esegui(sql, params)
    except Exception:
        return []


def _get_piano_docente_corso(corso_id: int) -> dict | None:
    """Restituisce il piano docente ufficiale di un corso (is_corso_docente=1), se esiste."""
    try:
        piani = db.trova_tutti("piani_personalizzati", {
            "corso_universitario_id": corso_id,
            "is_corso_docente": 1,
        }, ordine="id DESC", limite=1)
        return piani[0] if piani else None
    except Exception:
        return None


def _get_struttura_piano(piano_id: int) -> list[dict]:
    """
    Restituisce la struttura completa di un piano SOLO per il piano indicato:
    capitoli → paragrafi → tutti i contenuti (lezione, quiz, flashcard, schema).

    Ogni paragrafo ha:
      - par["contenuti"]  → lista di tutti i record piano_contenuti
      - par["testo"]      → testo della prima lezione (stringa), o None

    NOTA: piano_capitoli e piano_paragrafi hanno colonna 'ordine'.
          piano_contenuti NON ha colonna 'ordine' — usa created_at.
    """
    capitoli = db.trova_tutti("piano_capitoli", {"piano_id": piano_id}, ordine="ordine ASC")

    for cap in capitoli:
        cap["paragrafi"] = db.trova_tutti(
            "piano_paragrafi",
            {"capitolo_id": cap["id"]},
            ordine="ordine ASC",
        )
        for par in cap["paragrafi"]:
            # piano_contenuti NON ha colonna 'ordine' → nessun parametro ordine
            par["contenuti"] = db.trova_tutti(
                "piano_contenuti",
                {"paragrafo_id": par["id"]},
            )

            # Shortcut: estrai testo della lezione (primo contenuto di tipo lezione)
            testo: str | None = None
            for c in par["contenuti"]:
                if (c.get("tipo") or "").lower() == "lezione":
                    raw = (c.get("contenuto_json") or "").strip()
                    if not raw:
                        continue
                    # contenuto_json può essere JSON {"testo":"..."} o testo grezzo
                    if raw.startswith("{"):
                        try:
                            parsed = json.loads(raw)
                            testo = (
                                parsed.get("testo")
                                or parsed.get("content")
                                or parsed.get("text")
                                or raw
                            )
                        except Exception:
                            testo = raw
                    else:
                        testo = raw
                    break
            par["testo"] = testo

    return capitoli


# ---------------------------------------------------------------------------
# Componenti UI riutilizzabili
# ---------------------------------------------------------------------------

def _render_topbar(utente: dict) -> bool:
    """Renderizza la topbar istituzionale con logout integrato.
    Ritorna True se il logout è stato richiesto.
    Struttura: [col_esci | col_brand] — bottone a sinistra, brand a destra."""
    iniziali = f"{utente['nome'][0]}{utente['cognome'][0]}".upper()

    # col_esci PRIMA (sinistra) così non viene coperto dal topbar HTML
    col_esci, col_brand = st.columns([1, 10])

    with col_esci:
        # Sfondo identico alla topbar per continuità visiva
        st.markdown("""
        <div class="topbar-logout-bg"></div>
        """, unsafe_allow_html=True)
        return st.button("Esci", key="logout_btn", use_container_width=True)

    with col_brand:
        st.markdown(f"""
        <div class="topbar">
            <div class="topbar-brand">Learn<span>AI</span> &nbsp;·&nbsp;
                <span style="font-size:0.82rem; font-weight:300; color:rgba(255,255,255,0.7)">
                    Università Federico II di Napoli
                </span>
            </div>
            <div class="topbar-user">
                <span>{utente['nome']} {utente['cognome']}</span>
                <div class="topbar-avatar">{iniziali}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    return False


def _render_sidebar_corsi(corsi: list[dict]):
    """Renderizza la lista corsi nella colonna sinistra (sola lettura per lo studente)."""
    st.markdown('<div class="divider-label">I tuoi corsi</div>', unsafe_allow_html=True)

    if not corsi:
        st.caption("Nessun corso trovato.")
        return

    for corso in corsi:
        cid = corso["id"]
        # Attivo solo se si sta visualizzando questo corso in modalità corso (non piano)
        attivo_cls = (
            "attivo"
            if st.session_state.get("_corso_sel") == cid
            and st.session_state.get("_view_mode") == "corso"
            else ""
        )
        stato = corso["stato"]
        stato_cls = {
            "iscritto": "stato-iscritto",
            "completato": "stato-completato",
            "abbandonato": "stato-abbandonato",
        }.get(stato, "stato-iscritto")

        st.markdown(f"""
        <div class="corso-item {attivo_cls}" style="margin-bottom:8px;">
            <div class="corso-nome">{corso["nome"]}</div>
            <div class="corso-meta">
                {"Anno " + str(corso["anno_di_corso"]) if corso.get("anno_di_corso") else ""}
                {" · " + str(corso["cfu"]) + " CFU" if corso.get("cfu") else ""}
                &nbsp;<span class="corso-stato {stato_cls}">{stato.capitalize()}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Apri →", key=f"btn_corso_{cid}", use_container_width=True):
            st.session_state["_corso_sel"]  = cid
            st.session_state["_corso_nome"] = corso["nome"]
            st.session_state["_view_mode"]  = "corso"
            st.session_state["_piano_sel"]  = None
            st.session_state["_chat_history"] = []
            st.rerun()


def _render_sidebar_piani(studente_id: int):
    """Renderizza la sezione 'I Tuoi Piani Personalizzati' nella colonna sinistra."""
    piani = _get_tutti_piani_studente(studente_id)
    st.markdown('<div class="divider-label">I tuoi piani personalizzati</div>', unsafe_allow_html=True)

    if not piani:
        st.markdown(
            '<p style="color:#5A6A7E;font-size:0.82rem;margin:4px 0 12px">'
            'Nessun piano ancora. Chiedi a Lea di generarne uno!</p>',
            unsafe_allow_html=True,
        )
        return

    for piano in piani:
        pid = piano["id"]
        attivo = (
            st.session_state.get("_piano_sel") == pid
            and st.session_state.get("_view_mode") == "piano"
        )
        corso_nome_breve = (piano.get("corso_nome") or "")[:22]
        titolo_breve = (piano["titolo"] or "")[:42]
        st.markdown(f"""
        <div class="piano-card {'attivo' if attivo else ''}">
            <h5>{titolo_breve}{'…' if len(piano["titolo"] or '') > 42 else ''}</h5>
            <div class="piano-meta">
                <span class="ai-badge">AI</span>
                &nbsp;{corso_nome_breve}
                &nbsp;·&nbsp;{piano.get("created_at", "")[:10]}
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_studia, col_del = st.columns([3, 1])
        with col_studia:
            if st.button("Studia →", key=f"btn_piano_sx_{pid}", use_container_width=True):
                st.session_state["_piano_sel"]  = pid
                st.session_state["_view_mode"]  = "piano"
                st.session_state["_corso_sel"]  = piano["corso_universitario_id"]
                st.session_state["_corso_nome"] = piano.get("corso_nome", "")
                st.session_state["_chat_history"] = []
                st.rerun()
        with col_del:
            if st.button("🗑", key=f"btn_del_piano_{pid}", use_container_width=True, help="Elimina piano"):
                _dialog_elimina_piano(pid, piano["titolo"] or "Piano")



def _render_contenuto_piano(piano_id: int, studente_id: int = 0, is_corso_docente: bool = False):
    """Renderizza il piano con:
    1. Indice di navigazione (TOC) cliccabile per capitolo
    2. Capitoli espandibili → paragrafi → lezione/quiz/flashcard/riassunto
    """
    capitoli = _get_struttura_piano(piano_id)

    if not capitoli:
        st.markdown("""
        <div class="empty-state">
            <div class="icon">📂</div>
            <h3>Piano vuoto</h3>
            <p>Il piano non contiene ancora contenuti generati.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # ------------------------------------------------------------------ #
    # 1. INDICE DI NAVIGAZIONE
    # ------------------------------------------------------------------ #
    n_par_tot = sum(len(c.get("paragrafi", [])) for c in capitoli)
    toc_items = "".join(
        f'<li><a href="#cap-{i}" class="toc-link">'
        f'<span class="toc-num">{i + 1}</span>{cap["titolo"]}'
        f'<span class="toc-count">{len(cap.get("paragrafi", []))} sez.</span>'
        f'</a></li>'
        for i, cap in enumerate(capitoli)
    )
    st.markdown(f"""
    <div class="nav-toc">
        <div class="nav-toc-title">📑 Indice — {len(capitoli)} capitoli · {n_par_tot} sezioni</div>
        <ul class="toc-list">{toc_items}</ul>
    </div>
    """, unsafe_allow_html=True)

    st.space("small")

    # ------------------------------------------------------------------ #
    # 2. CONTENUTO — capitoli espandibili
    # ------------------------------------------------------------------ #
    for i, cap in enumerate(capitoli):
        with st.expander(cap['titolo'], icon=":material/menu_book:", expanded=(i == 0)):
            paragrafi = cap.get("paragrafi", [])
            if not paragrafi:
                st.markdown(
                    '<p style="color:#5A6A7E;font-size:0.85rem">Nessuna sezione generata.</p>',
                    unsafe_allow_html=True,
                )
                continue

            for p_idx, par in enumerate(paragrafi):
                contenuti = par.get("contenuti", [])

                # Separa i tipi di contenuto
                lezioni   = [c for c in contenuti if (c.get("tipo") or "").lower() in ("lezione", "riassunto")]
                quiz_list = [c for c in contenuti if (c.get("tipo") or "").lower() == "quiz"]
                fc_list   = [c for c in contenuti if (c.get("tipo") or "").lower() == "flashcard"]
                altri     = [c for c in contenuti if (c.get("tipo") or "").lower() not in ("lezione", "riassunto", "quiz", "flashcard")]

                # ---- Costruisce HTML per header + testo lezione in UN unico blocco ----
                testo_lezione = par.get("testo") or ""
                # Sicurezza: escapa caratteri HTML problematici nel testo grezzo
                testo_safe = (testo_lezione
                              .replace("&", "&amp;")
                              .replace("<", "&lt;")
                              .replace(">", "&gt;"))
                testo_html = f'<div class="paragrafo-testo">{testo_safe}</div>' if testo_safe else (
                    "" if (quiz_list or fc_list or altri) else
                    '<p class="no-content-hint">⏳ Contenuto non ancora generato — chiedi a Lea di generarlo!</p>'
                )

                st.markdown(f"""
                <div class="paragrafo-box">
                    <h5>{par["titolo"]}</h5>
                    {testo_html}
                </div>
                """, unsafe_allow_html=True)

                # ---- QUIZ (interattivo) ----
                for q_idx, c in enumerate(quiz_list):
                    raw = (c.get("contenuto_json") or "").strip()
                    domande = []
                    ha_quiz_id = bool(c.get("quiz_id"))

                    # Caso A: contenuto_json ha le domande inline (JSON)
                    if raw.startswith("{") or raw.startswith("["):
                        try:
                            dati_raw: dict = json.loads(raw)
                            domande = dati_raw.get("domande") or dati_raw.get("questions") or []
                        except Exception:
                            pass

                    # Caso B: contenuto_json è NULL → leggi da domande_quiz via quiz_id
                    if not domande and ha_quiz_id:
                        righe = db.trova_tutti(
                            "domande_quiz",
                            {"quiz_id": c["quiz_id"]},
                            ordine="ordine ASC",
                        )
                        domande_tmp = []
                        for r in righe:
                            opzioni_parsed = []
                            try:
                                opzioni_parsed = json.loads(r.get("opzioni_json") or "[]")
                            except Exception:
                                pass
                            corretta_raw = r.get("risposta_corretta") or "0"
                            try:
                                indice_corretta = int(corretta_raw)
                            except (ValueError, TypeError):
                                try:
                                    indice_corretta = opzioni_parsed.index(corretta_raw)
                                except (ValueError, IndexError):
                                    indice_corretta = 0
                            domande_tmp.append({
                                "id": r["id"],
                                "testo": r["testo"],
                                "risposta_corretta": corretta_raw,
                                "spiegazione": r.get("spiegazione") or "",
                                "opzioni_json": r.get("opzioni_json") or "[]",
                                "indice_corretta": indice_corretta,
                            })
                        domande = domande_tmp

                    if not domande:
                        continue

                    # Stato del quiz: pending / submitted
                    stato_key = f"_quiz_stato_{c['id']}_{q_idx}"
                    ris_key   = f"_quiz_risposte_{c['id']}_{q_idx}"
                    tent_key  = f"_quiz_tentativo_{c['id']}_{q_idx}"
                    gap_key   = f"_quiz_gap_{c['id']}_{q_idx}"

                    stato_quiz = st.session_state.get(stato_key, "pending")

                    # Ripristina tentativo già completato dal DB (sopravvive al refresh)
                    if stato_quiz == "pending" and ha_quiz_id:
                        tent_db = db.esegui(
                            "SELECT id FROM tentativi_quiz WHERE quiz_id=? AND studente_id=? AND completato=1 ORDER BY id DESC LIMIT 1",
                            [c["quiz_id"], studente_id],
                        )
                        if tent_db:
                            st.session_state[tent_key] = tent_db[0]["id"]
                            st.session_state[stato_key] = "submitted"
                            stato_quiz = "submitted"

                    st.markdown(
                        '<div class="content-type-badge badge-quiz">❓ Quiz</div>',
                        unsafe_allow_html=True,
                    )

                    if stato_quiz == "submitted":
                        # Ricostruisce punteggio/corrette: da DB se la sessione è persa, altrimenti da session_state
                        tentativo_id_disp = st.session_state.get(tent_key)
                        if tentativo_id_disp and ris_key not in st.session_state:
                            tent_row = db.trova_uno("tentativi_quiz", {"id": tentativo_id_disp})
                            punteggio = float(tent_row["punteggio"]) if tent_row else 0.0
                            risp_db = db.trova_tutti("risposte_domande", {"tentativo_id": tentativo_id_disp})
                            corrette_map = {r["domanda_id"]: bool(r["corretta"]) for r in risp_db}
                            corrette = [corrette_map.get(d.get("id"), False) for d in domande]
                        else:
                            from src.agents.gap_analysis import calcola_punteggio
                            risposte_salvate = st.session_state.get(ris_key, {})
                            punteggio, corrette = calcola_punteggio(domande, risposte_salvate)
                        n_ok = sum(corrette)
                        n_tot = len(corrette)
                        colore = "#1A7F4B" if punteggio >= 70 else ("#C5A028" if punteggio >= 40 else "#C8102E")
                        st.markdown(
                            f'<div style="background:#fff;border-radius:10px;padding:16px 20px;'
                            f'border-left:4px solid {colore};margin-bottom:12px;">'
                            f'<b>Risultato:</b> {n_ok}/{n_tot} corrette — '
                            f'<span style="color:{colore};font-weight:700">{punteggio:.0f}/100</span></div>',
                            unsafe_allow_html=True,
                        )
                        for d_idx, (d, ok) in enumerate(zip(domande, corrette), 1):
                            testo_d = d.get("testo") or d.get("domanda") or ""
                            icona = "✅" if ok else "❌"
                            st.markdown(f"**{icona} Domanda {d_idx}:** {testo_d}")
                            if not ok:
                                corretta_idx = d.get("indice_corretta", 0)
                                opzioni = d.get("opzioni") or []
                                if not opzioni:
                                    try:
                                        opzioni = json.loads(d.get("opzioni_json") or "[]")
                                    except Exception:
                                        pass
                                risposta_corretta = opzioni[corretta_idx] if (opzioni and 0 <= corretta_idx < len(opzioni)) else str(corretta_idx)
                                spieg = d.get("spiegazione", "")
                                st.markdown(
                                    f'<div style="color:#5A6A7E;font-size:0.84rem;margin-left:18px;">'
                                    f'Risposta corretta: <b>{risposta_corretta}</b>'
                                    + (f'<br>{spieg}' if spieg else "")
                                    + '</div>',
                                    unsafe_allow_html=True,
                                )

                        # Bottone Analisi Lea
                        col_gap1, col_gap2 = st.columns([2, 3])
                        with col_gap1:
                            if st.button("🔍 Analizza con Lea", key=f"gap_btn_{c['id']}_{q_idx}", type="primary"):
                                tentativo_id = st.session_state.get(tent_key)
                                if tentativo_id:
                                    with st.spinner("Lea sta analizzando le tue lacune..."):
                                        try:
                                            from src.agents.gap_analysis import analizza_gap
                                            report = analizza_gap(tentativo_id, studente_id)
                                            st.session_state[gap_key] = report
                                        except Exception as ex:
                                            st.session_state[gap_key] = f"Errore analisi: {ex}"
                                else:
                                    err_detail = st.session_state.get(tent_key + "_err", "")
                                    st.session_state[gap_key] = (
                                        "Tentativo non salvato — impossibile analizzare."
                                        + (f"\n\nDettaglio errore: `{err_detail}`" if err_detail else "")
                                    )
                        with col_gap2:
                            if not is_corso_docente and st.button("🔄 Rifai quiz", key=f"redo_quiz_{c['id']}_{q_idx}"):
                                for k in [stato_key, ris_key, tent_key, gap_key]:
                                    st.session_state.pop(k, None)
                                st.rerun()

                        if gap_key in st.session_state:
                            st.markdown(
                                f'<div style="background:#EEF4FF;border-radius:10px;padding:16px 20px;'
                                f'margin-top:12px;border-left:4px solid #003087;">'
                                f'{st.session_state[gap_key]}</div>',
                                unsafe_allow_html=True,
                            )

                    else:
                        # Quiz in attesa di risposta: radio interattivi
                        risposte_correnti: dict[int, int] = st.session_state.get(ris_key, {})

                        for d_idx, d in enumerate(domande[:5]):
                            testo_d = d.get("testo") or d.get("domanda") or d.get("question") or ""
                            opzioni = d.get("opzioni") or []
                            if not opzioni:
                                try:
                                    opzioni = json.loads(d.get("opzioni_json") or "[]")
                                except Exception:
                                    pass

                            st.markdown(f"**{d_idx + 1}. {testo_d}**")
                            if opzioni:
                                scelta = st.radio(
                                    label=f"Domanda {d_idx + 1}",
                                    options=list(range(len(opzioni))),
                                    format_func=lambda x, opts=opzioni: opts[x],
                                    key=f"_quiz_radio_{c['id']}_{q_idx}_{d_idx}",
                                    label_visibility="collapsed",
                                    index=risposte_correnti.get(d_idx, 0),
                                )
                                risposte_correnti[d_idx] = scelta

                        # Bottone Commit
                        st.session_state[ris_key] = risposte_correnti
                        if st.button("✔ Conferma risposte", key=f"commit_quiz_{c['id']}_{q_idx}", type="primary"):
                            # Salva tentativo su DB se c'è un quiz_id reale
                            tentativo_id = None
                            if ha_quiz_id:
                                try:
                                    from src.agents.gap_analysis import salva_tentativo
                                    tentativo_id = salva_tentativo(
                                        quiz_id=c["quiz_id"],
                                        studente_id=studente_id,
                                        domande=domande,
                                        risposte_studente=risposte_correnti,
                                    )
                                except Exception as _save_err:
                                    st.session_state[tent_key + "_err"] = str(_save_err)
                            st.session_state[tent_key] = tentativo_id
                            st.session_state[stato_key] = "submitted"
                            st.rerun()

                # ---- FLASHCARD ----
                for fc_idx, c in enumerate(fc_list):
                    raw = (c.get("contenuto_json") or "").strip()
                    dati = {}
                    if raw.startswith("{"):
                        try:
                            dati = json.loads(raw)
                        except Exception:
                            pass
                    elif raw.startswith("["):
                        try:
                            dati = {"cards": json.loads(raw)}
                        except Exception:
                            pass
                    cards = dati.get("cards") or dati.get("flashcard") or []
                    st.markdown(
                        '<div class="content-type-badge badge-flash">🃏 Flashcard</div>',
                        unsafe_allow_html=True,
                    )
                    if cards:
                        n_col = min(len(cards), 3)
                        cols_fc = st.columns(n_col)
                        for j, card in enumerate(cards[:3]):
                            fronte = card.get("fronte") or card.get("front") or card.get("domanda") or ""
                            retro  = card.get("retro")  or card.get("back")  or card.get("risposta") or ""
                            fronte_safe = fronte.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                            retro_safe  = retro.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                            uid = f"fc_{i}_{p_idx}_{fc_idx}_{j}"
                            reveal_key = f"_fc_{uid}"
                            with cols_fc[j % n_col]:
                                # Fronte sempre visibile
                                st.markdown(
                                    f'<div class="fc-front-side">{fronte_safe}</div>',
                                    unsafe_allow_html=True,
                                )
                                # Retro: toggle con st.button (non <input> che Streamlit sanitizza)
                                if st.session_state.get(reveal_key):
                                    st.markdown(
                                        f'<div class="fc-back-side" style="display:block;">{retro_safe}</div>',
                                        unsafe_allow_html=True,
                                    )
                                else:
                                    if st.button("👁 Mostra risposta", key=f"fc_show_{uid}", use_container_width=True):
                                        st.session_state[reveal_key] = True
                                        st.rerun()

                # ---- SCHEMA / ALTRI ----
                for c in altri:
                    tipo = (c.get("tipo") or "").lower()
                    raw  = (c.get("contenuto_json") or "").strip()
                    st.markdown(
                        f'<div class="content-type-badge badge-schema">🗺 {tipo.capitalize()}</div>',
                        unsafe_allow_html=True,
                    )
                    if raw:
                        st.code(raw, language="")


def _render_raccomandazioni(studente_id: int):
    """Renderizza le raccomandazioni corsi basate sull'algoritmo AI."""
    raccomanda_corsi = _import_recommender()
    st.markdown('<div class="divider-label">Consigliati per te</div>', unsafe_allow_html=True)

    # Testo fallback sempre visibile (colore esplicito, non caption bianco)
    def _fallback(msg: str):
        st.markdown(
            f'<p style="color:#5A6A7E;font-size:0.82rem;margin:4px 0 12px">{msg}</p>',
            unsafe_allow_html=True,
        )

    if raccomanda_corsi is None:
        _fallback("Raccomandazioni non disponibili.")
        return

    try:
        raccomandazioni = raccomanda_corsi(studente_id, top_n=3)
    except Exception:
        raccomandazioni = []

    if not raccomandazioni:
        candidati = db.esegui("""
            SELECT COUNT(*) as n FROM corsi_universitari cu
            WHERE cu.attivo = 1
              AND cu.id NOT IN (
                  SELECT corso_universitario_id FROM studenti_corsi WHERE studente_id = ?
              )
        """, [studente_id])
        if candidati and candidati[0]["n"] == 0:
            _fallback("Sei già iscritto a tutti i corsi disponibili. Nuovi corsi verranno aggiunti presto! 🎓")
        else:
            _fallback("Nessuna raccomandazione disponibile al momento.")
        return

    for r in raccomandazioni:
        score_pct = int(r.score_totale * 100)
        tags_html = " ".join(
            f'<span style="background:#E8F0FE;color:#003087;font-size:0.65rem;'
            f'padding:2px 6px;border-radius:10px;margin-right:4px;">{t}</span>'
            for t in (r.tag or [])
        )
        motivazione = (r.motivazione or "")[:100]
        st.markdown(f"""
        <div class="raccomandazione-card">
            <h5>{r.corso_nome}</h5>
            <div style="margin:4px 0">{tags_html}</div>
            <p>{motivazione}{'…' if len(r.motivazione or '') > 100 else ''}</p>
            <div class="score-bar-outer">
                <div class="score-bar-inner" style="width:{score_pct}%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Ricerca corsi
# ---------------------------------------------------------------------------

def _anno_accademico_corrente() -> str:
    from datetime import date as _date
    oggi = _date.today()
    return f"{oggi.year}-{oggi.year + 1}" if oggi.month >= 9 else f"{oggi.year - 1}-{oggi.year}"


def _render_ricerca_corsi(corsi_iscritto: list[dict], studente_id: int) -> None:
    """Sezione di ricerca corsi disponibili nella piattaforma."""
    st.markdown("### 🔍 Cerca un corso")

    tutti_cdl = _get_tutti_cdl()
    docenti = _get_docenti()

    # Mappa etichetta → id per docenti e CDL
    docenti_map: dict[str, int | None] = {"Tutti": None}
    for d in docenti:
        label = f"{d['nome']} {d['cognome']} (ID {d['id']})"
        docenti_map[label] = d["id"]

    cdl_map: dict[str, int | None] = {"Tutti": None}
    for c in tutti_cdl:
        cdl_map[c["nome"]] = c["id"]

    col1, col2 = st.columns(2)
    with col1:
        nome_cerca = st.text_input("Nome del corso", placeholder="Es. Basi di Dati", key="search_nome")
        cfu_cerca = st.number_input("CFU (0 = qualsiasi)", min_value=0, max_value=30, step=1, value=0, key="search_cfu")
    with col2:
        doc_label = st.selectbox("Docente", list(docenti_map.keys()), key="search_docente")
        cdl_label = st.selectbox("Corso di Laurea", list(cdl_map.keys()), key="search_cdl")

    if st.button("Cerca", type="primary", key="search_btn"):
        risultati = _cerca_corsi(
            nome=nome_cerca,
            docente_id=docenti_map[doc_label],
            cfu=cfu_cerca if cfu_cerca > 0 else None,
            cdl_id=cdl_map[cdl_label],
        )
        st.session_state["_search_results"] = risultati

    risultati = st.session_state.get("_search_results")
    if risultati is None:
        return

    st.markdown(f"**{len(risultati)} risultati trovati**")
    if not risultati:
        st.info("Nessun corso corrisponde ai criteri di ricerca.")
        return

    ids_iscritto = {c["id"] for c in corsi_iscritto}
    corso_appena_iscritto = st.session_state.pop("_iscrizione_feedback", None)
    if corso_appena_iscritto:
        st.success(f"Iscrizione a **{corso_appena_iscritto}** completata!")

    for r in risultati:
        with st.container(border=True):
            c1, c2 = st.columns([5, 1])
            with c1:
                st.markdown(f"**{r['nome']}**")
                meta = (
                    f"Docente: {r['docente_nome']} {r['docente_cognome']} (ID {r['docente_id']})"
                    f" · CFU: {r.get('cfu') or '—'}"
                    f" · Anno: {r.get('anno_di_corso') or '—'}"
                    f" · {r.get('livello') or '—'}"
                )
                st.caption(meta)
                if r.get("corsi_di_laurea"):
                    st.caption(f"Corsi di Laurea: {r['corsi_di_laurea']}")
            with c2:
                if r["id"] in ids_iscritto:
                    if st.button("Apri →", key=f"search_open_{r['id']}"):
                        st.session_state["_corso_sel"] = r["id"]
                        st.session_state["_corso_nome"] = r["nome"]
                        st.session_state["_view_mode"] = "corso"
                        st.session_state["_piano_sel"] = None
                        st.session_state["_search_results"] = None
                        st.rerun()
                else:
                    if st.button("Iscriviti", key=f"search_iscriviti_{r['id']}", type="primary"):
                        try:
                            db.inserisci("studenti_corsi", {
                                "studente_id": studente_id,
                                "corso_universitario_id": r["id"],
                                "anno_accademico": _anno_accademico_corrente(),
                                "stato": "iscritto",
                            })
                            st.session_state["_iscrizione_feedback"] = r["nome"]
                        except Exception:
                            st.error("Iscrizione non riuscita. Potresti essere già iscritto.")
                        st.rerun()


# ---------------------------------------------------------------------------
# Chatbot Lea
# ---------------------------------------------------------------------------

def _render_chatbot(
    utente: dict,
    corso_id: int | None,
    corso_nome: str | None,
    view_mode: str | None = None,
    piano_id: int | None = None,
    piano_titolo: str | None = None,
):
    """Renderizza il chatbot Lea nella colonna destra."""
    chat_con_orchestratore, aggiorna_contesto, _ = _import_orchestratore()

    # Aggiorna il contesto ad ogni render (non solo al primo messaggio)
    # così Lea sa subito su quale piano/corso sta lavorando lo studente.
    # Nota: aggiorna anche quando corso_id è None ma piano_id è impostato.
    if aggiorna_contesto and (corso_id or piano_id or view_mode):
        aggiorna_contesto(
            corso_id=corso_id,
            corso_nome=corso_nome,
            tipo_vista=view_mode,
            piano_id=piano_id,
            piano_titolo=piano_titolo,
        )

    # ---- Bottone "Torna alla home" sopra la chat ----
    if view_mode:
        if st.button("🏠 Torna alla home", key="btn_home_chat", use_container_width=True):
            st.session_state["_view_mode"] = None
            st.session_state["_corso_sel"] = None
            st.session_state["_piano_sel"] = None
            st.session_state["_corso_nome"] = ""
            st.session_state["_search_results"] = None
            st.rerun()

    # Header
    st.markdown("""
    <div class="chat-header">
        <div class="chat-online"></div>
        <div>
            <div class="chat-title">Lea — Tutor AI</div>
            <div class="chat-sub">Il tuo assistente personale di studio</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Cronologia messaggi
    if "chat_history_display" not in st.session_state:
        st.session_state["chat_history_display"] = [
            {
                "role": "assistant",
                "content": (
                    f"Ciao {utente['nome']}! 👋 Sono **Lea**, il tuo tutor AI.\n\n"
                    "Posso aiutarti a generare contenuti per i tuoi corsi, "
                    "creare quiz e flashcard, o rispondere a domande sugli argomenti che studi. "
                    "Come posso aiutarti oggi?"
                ),
            }
        ]

    # Funzione helper per generare l'HTML della chat
    def get_chat_html(is_typing=False):
        html = '<div class="chat-container" id="chat-box">'
        for m in st.session_state["chat_history_display"]:
            if m["role"] == "user":
                testo_safe = m["content"].replace("<", "&lt;").replace(">", "&gt;")
                html += f'<div class="msg-user">{testo_safe}</div>'
            else:
                import re as _re
                contenuto = m["content"].replace("<", "&lt;").replace(">", "&gt;")
                contenuto = _re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', contenuto)
                contenuto = contenuto.replace("\n", "<br>")
                html += f'<div class="msg-ai">{contenuto}</div>'
        
        if is_typing:
            html += """
            <div class="typing-bubble">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
            """
        html += "</div>"
        return html

    # Render messaggi tramite segnaposto (per aggiornamento immediato)
    chat_placeholder = st.empty()
    chat_placeholder.markdown(get_chat_html(), unsafe_allow_html=True)

    # ---- Materiale selezionato tramite "Visualizza materiale" → auto-messaggio ----
    messaggio_da_materiale: str | None = None
    mat_scelto = st.session_state.pop("_materiale_da_studiare", None)
    if mat_scelto and aggiorna_contesto is not None:
        # Inietta il materiale nel contesto PRIMA di invocare l'agente
        aggiorna_contesto(
            corso_id=mat_scelto["corso_id"],
            materiale_selezionato=mat_scelto,
        )
        messaggio_da_materiale = f"Crea una lezione dal materiale '{mat_scelto['titolo']}'"

    # ---- Materiali liberi selezionati (senza corso) → auto-messaggio ----
    materiali_liberi = st.session_state.pop("_materiali_liberi_selezionati", None)
    if materiali_liberi and not messaggio_da_materiale:
        titoli_str = ", ".join(f"'{m['titolo']}'" for m in materiali_liberi)
        primo_id = materiali_liberi[0]["id"]
        if aggiorna_contesto is not None:
            # clear_corso=True azzera l'eventuale corso precedente nel contesto
            aggiorna_contesto(
                clear_corso=True,
                materiale_selezionato={"id": primo_id, "titolo": titoli_str, "corso_id": None},
            )
        messaggio_da_materiale = f"Genera una lezione basata sui seguenti documenti: {titoli_str}"

    # ---- Suggerimenti rapidi — compatti, sopra l'input ----
    suggerimenti = [
        ("📚", "Genera un piano"),
        ("❓", "Crea un quiz"),
        ("🃏", "Flashcard"),
    ]
    messaggio_da_suggerimento: str | None = None
    with st.container(horizontal=True):
        for sug_i, (icona, testo) in enumerate(suggerimenti):
            if st.button(f"{icona} {testo}", key=f"sug_{sug_i}"):
                if corso_id and corso_nome:
                    messaggio_da_suggerimento = f"{testo} per il corso di {corso_nome}"
                else:
                    messaggio_da_suggerimento = testo

    # ---- Input chat nativo (pulizia automatica dopo invio) ----
    user_input = st.chat_input("Chiedi a Lea...", key="lea_chat_input")

    # Unifica input da campo libero, da suggerimento e da selezione materiale
    messaggio_finale: str | None = user_input or messaggio_da_suggerimento or messaggio_da_materiale

    if messaggio_finale:
        st.session_state["chat_history_display"].append(
            {"role": "user", "content": messaggio_finale}
        )
        # Mostra subito la domanda + l'animazione "sta scrivendo..."
        chat_placeholder.markdown(get_chat_html(is_typing=True), unsafe_allow_html=True)

        # Snapshot piani esistenti PRIMA della chiamata all'agente
        _mat_libero_corso = (materiali_liberi[0].get("corso_universitario_id") if materiali_liberi else None)
        _corso_id_eff = (mat_scelto["corso_id"] if mat_scelto else None) or _mat_libero_corso or corso_id
        _studente_id_chat = st.session_state.get("current_user_id")
        _piani_prima: set[int] = set()
        if _corso_id_eff:
            _piani_prima = {
                p["id"] for p in db.trova_tutti(
                    "piani_personalizzati",
                    {"studente_id": _studente_id_chat, "corso_universitario_id": _corso_id_eff},
                )
            }
        elif materiali_liberi:
            _piani_prima = {
                p["id"] for p in db.esegui(
                    "SELECT id FROM piani_personalizzati WHERE studente_id = ? AND corso_universitario_id IS NULL",
                    [_studente_id_chat],
                )
            }

        # Esecuzione IA
        if chat_con_orchestratore is not None and aggiorna_contesto is not None:
            if corso_id or piano_id or view_mode:
                aggiorna_contesto(
                    corso_id=corso_id,
                    corso_nome=corso_nome,
                    tipo_vista=view_mode,
                    piano_id=piano_id,
                    piano_titolo=piano_titolo,
                )
            try:
                risposta = chat_con_orchestratore(
                    messaggio_utente=messaggio_finale,
                    corso_contestuale_id=corso_id,
                    corso_contestuale_nome=corso_nome,
                )
            except Exception as e:
                risposta = f"⚠️ Errore: {str(e)[:120]}"
            finally:
                # Dopo che Lea ha risposto, rimuovi il materiale selezionato dal contesto
                # per evitare che venga riutilizzato nelle conversazioni successive.
                if mat_scelto and aggiorna_contesto is not None:
                    aggiorna_contesto(clear_materiale=True)
        else:
            risposta = (
                "⚙️ Lea non è ancora configurata (AWS Bedrock non attivo). "
                "Configura le credenziali AWS in `config.py` per abilitarla."
            )

        st.session_state["chat_history_display"].append(
            {"role": "assistant", "content": risposta}
        )

        # Controlla se l'agente ha creato un nuovo piano → auto-naviga in vista piano
        _studente_id_chat = st.session_state.get("current_user_id")
        if _corso_id_eff:
            _piani_dopo = {
                p["id"] for p in db.trova_tutti(
                    "piani_personalizzati",
                    {"studente_id": _studente_id_chat, "corso_universitario_id": _corso_id_eff},
                )
            }
            nuovi = _piani_dopo - _piani_prima
            if nuovi:
                nuovo_piano_id = max(nuovi)
                st.session_state["_piano_sel"]  = nuovo_piano_id
                st.session_state["_corso_sel"]  = _corso_id_eff
                st.session_state["_view_mode"]  = "piano"
        elif materiali_liberi:
            # Piano creato senza corso: cerca i nuovi piani senza corso_universitario_id
            _tutti_piani_dopo = {
                p["id"] for p in db.esegui(
                    "SELECT id FROM piani_personalizzati WHERE studente_id = ? AND corso_universitario_id IS NULL",
                    [_studente_id_chat],
                )
            }
            nuovi = _tutti_piani_dopo - _piani_prima
            if nuovi:
                nuovo_piano_id = max(nuovi)
                st.session_state["_piano_sel"]  = nuovo_piano_id
                st.session_state["_corso_sel"]  = None
                st.session_state["_view_mode"]  = "piano"

        st.rerun()


def _seed_iscrizioni_se_mancanti(studente_id: int) -> None:
    """
    Se lo studente non ha iscrizioni in studenti_corsi, lo iscrive a tutti
    i corsi attivi con stato 'iscritto' e anno accademico corrente.
    Serve per gli utenti demo che non hanno dati nel DB di seed.
    """
    iscrizioni = db.trova_tutti("studenti_corsi", {"studente_id": studente_id})
    if iscrizioni:
        return  # già iscritto, niente da fare

    corsi_attivi = db.trova_tutti("corsi_universitari", {"attivo": 1})
    # Iscrive al massimo ai primi 2 corsi (ordinati per anno) per lasciare
    # almeno un corso come candidato per il motore di raccomandazioni.
    corsi_per_seed = sorted(corsi_attivi, key=lambda c: c.get("anno_di_corso") or 0)[:2]
    for corso in corsi_per_seed:
        try:
            db.inserisci("studenti_corsi", {
                "studente_id":            studente_id,
                "corso_universitario_id": corso["id"],
                "anno_accademico":        "2025-2026",
                "stato":                  "iscritto",
            })
        except Exception:
            pass  # ignora duplicati o errori di vincolo


# ---------------------------------------------------------------------------
# Eliminazione piani personalizzati
# ---------------------------------------------------------------------------

def _elimina_piano_db(piano_id: int) -> None:
    """Elimina un piano personalizzato e tutto il suo contenuto in cascata."""
    paragrafi = db.esegui("""
        SELECT pp.id FROM piano_paragrafi pp
        JOIN piano_capitoli pc ON pp.capitolo_id = pc.id
        WHERE pc.piano_id = ?
    """, [piano_id])
    par_ids = [p["id"] for p in paragrafi]
    if par_ids:
        placeholders = ",".join("?" * len(par_ids))
        db.esegui(f"DELETE FROM piano_contenuti WHERE paragrafo_id IN ({placeholders})", par_ids)
        db.esegui(f"DELETE FROM piano_paragrafi WHERE id IN ({placeholders})", par_ids)
    db.esegui("DELETE FROM piano_capitoli WHERE piano_id = ?", [piano_id])
    db.esegui("DELETE FROM piani_personalizzati WHERE id = ?", [piano_id])


@st.dialog("Elimina piano")
def _dialog_elimina_piano(piano_id: int, piano_titolo: str):
    st.warning(f"Stai per eliminare il piano **{piano_titolo}**.")
    st.caption("Questa azione è irreversibile. Capitoli, sezioni e contenuti verranno eliminati definitivamente.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Annulla", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("Elimina", type="primary", use_container_width=True):
            _elimina_piano_db(piano_id)
            if st.session_state.get("_piano_sel") == piano_id:
                st.session_state["_piano_sel"] = None
                st.session_state["_view_mode"] = "corso"
            st.rerun()


# ---------------------------------------------------------------------------
# Dialogs materiale didattico
# ---------------------------------------------------------------------------


@st.dialog("Cancella iscrizione")
def _dialog_cancella_iscrizione(studente_id: int, corso_id: int, corso_nome: str):
    st.warning(f"Stai per cancellare l'iscrizione a **{corso_nome}**.")
    st.caption("I tuoi piani personalizzati per questo corso verranno conservati, ma non potrai più accedere al corso.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Annulla", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("Cancella iscrizione", type="primary", use_container_width=True):
            try:
                db.esegui(
                    "DELETE FROM studenti_corsi WHERE studente_id = ? AND corso_universitario_id = ?",
                    [studente_id, corso_id],
                )
                st.session_state["_corso_sel"] = None
                st.session_state["_view_mode"] = None
                st.session_state["_piano_sel"] = None
            except Exception as e:
                st.error(f"Impossibile cancellare l'iscrizione: {e}")
            st.rerun()


def _get_materiali_usati_piano(piano_id: int) -> list[dict]:
    """Recupera i materiali didattici usati per generare un piano,
    tramite il reverse-lookup piano_contenuti → chunk_ids_utilizzati → materiali_chunks."""
    try:
        righe = db.esegui(
            """SELECT pc.chunk_ids_utilizzati
               FROM piano_contenuti pc
               JOIN piano_paragrafi pp ON pp.id = pc.paragrafo_id
               JOIN piano_capitoli pca ON pca.id = pp.capitolo_id
               WHERE pca.piano_id = ?""",
            [piano_id],
        )
    except Exception:
        return []

    chunk_ids: set[int] = set()
    for r in righe:
        try:
            ids = json.loads(r.get("chunk_ids_utilizzati") or "[]")
            chunk_ids.update(int(i) for i in ids if i)
        except Exception:
            pass

    if not chunk_ids:
        return []

    placeholders = ",".join("?" * len(chunk_ids))
    try:
        mat_rows = db.esegui(
            f"SELECT DISTINCT materiale_id FROM materiali_chunks WHERE id IN ({placeholders})",
            list(chunk_ids),
        )
    except Exception:
        return []

    materiale_ids = [r["materiale_id"] for r in mat_rows if r.get("materiale_id")]
    if not materiale_ids:
        return []

    ph2 = ",".join("?" * len(materiale_ids))
    try:
        return db.esegui(
            f"SELECT * FROM materiali_didattici WHERE id IN ({ph2}) ORDER BY caricato_il DESC",
            materiale_ids,
        )
    except Exception:
        return []


@st.dialog("Materiale del piano")
def _dialog_materiale_piano_libero(piano_id: int):
    st.markdown("**Materiale usato per generare questo piano**")
    st.caption("Questi sono i documenti da cui Lea ha creato il piano. Clicca 'Studia' per generare una nuova lezione.")
    materiali = _get_materiali_usati_piano(piano_id)

    if not materiali:
        st.info("Nessun materiale trovato per questo piano.", icon=":material/folder_open:")
        return

    for m in materiali:
        with st.container(border=True):
            elaborato = bool(m.get("is_processed"))
            c1, c2 = st.columns([4, 2])
            with c1:
                st.markdown(f"**{m['titolo']}**")
                stato_label = "✅ Elaborato" if elaborato else "⏳ Non elaborato"
                st.caption(f"{m.get('tipo', '').upper()} · {stato_label} · {(m.get('caricato_il') or '')[:10]}")
            with c2:
                if elaborato:
                    if st.button("📖 Studia", key=f"studia_mat_piano_{m['id']}", use_container_width=True):
                        st.session_state["_materiale_da_studiare"] = {
                            "id": m["id"],
                            "titolo": m["titolo"],
                            "corso_id": m.get("corso_universitario_id"),
                        }
                        st.rerun()
                else:
                    st.caption("⚠️ Non elaborato")


@st.dialog("Materiale del corso")
def _dialog_materiale_corso(corso_id: int, corso_nome: str):
    st.markdown(f"**Materiale disponibile per {corso_nome}**")
    st.caption("Clicca su un documento per chiedere a Lea di creare una lezione da quel materiale.")
    try:
        materiali = db.trova_tutti("materiali_didattici", {"corso_universitario_id": corso_id})
    except Exception:
        materiali = []

    if not materiali:
        st.info("Nessun materiale caricato per questo corso.", icon=":material/folder_open:")
        return

    for m in materiali:
        with st.container(border=True):
            elaborato = bool(m.get("is_processed"))
            c1, c2 = st.columns([4, 2])
            with c1:
                st.markdown(f"**{m['titolo']}**")
                stato_label = "✅ Elaborato" if elaborato else "⏳ Non elaborato"
                st.caption(f"{m.get('tipo', '').upper()} · {stato_label} · {(m.get('caricato_il') or '')[:10]}")
            with c2:
                if elaborato:
                    if st.button(
                        "📖 Studia",
                        key=f"studia_mat_corso_{m['id']}",
                        use_container_width=True,
                    ):
                        st.session_state["_materiale_da_studiare"] = {
                            "id": m["id"],
                            "titolo": m["titolo"],
                            "corso_id": corso_id,
                        }
                        st.rerun()
                else:
                    st.caption("⚠️ Non ancora elaborato")


@st.dialog("Carica materiale didattico")
def _dialog_upload_materiale_libero():
    st.markdown("Carica materiale per creare una lezione personalizzata")
    st.caption("Il file verrà elaborato così Lea potrà generare una lezione dal tuo materiale.")
    uploaded = st.file_uploader(
        "Seleziona un file",
        type=["pdf", "docx", "txt", "pptx", "xlsx"],
        key="upload_file_libero_dialog",
    )
    if uploaded:
        titolo = st.text_input("Titolo", value=uploaded.name.rsplit(".", 1)[0])
        if st.button("Carica ed elabora", type="primary", use_container_width=True):
            try:
                from src.tools.document_processor import elabora_e_salva_documento
                progress_bar = st.progress(0, text="Estrazione testo...")
                def _aggiorna_progresso(i, totale):
                    pct = int((i + 1) / totale * 100)
                    progress_bar.progress(pct, text=f"Analisi sezione {i + 1}/{totale}...")
                elabora_e_salva_documento(
                    uploaded_file=uploaded,
                    corso_universitario_id=None,
                    titolo=titolo,
                    tipo=uploaded.name.rsplit(".", 1)[-1].lower() or "dispensa",
                    progress_callback=_aggiorna_progresso,
                )
                progress_bar.progress(100, text="Completato!")
                st.success(f"✅ '{titolo}' caricato ed elaborato! Lea può ora usarlo per generare lezioni.")
                st.rerun()
            except Exception as e:
                st.error(f"Errore durante l'elaborazione: {e}")


@st.dialog("Materiale didattico")
def _dialog_view_materiale_libero(user_id: int):
    st.markdown("**Materiale disponibile per generare la lezione**")
    st.caption("Seleziona uno o più documenti e clicca il pulsante per generare la lezione.")
    try:
        materiali = db.esegui(
            "SELECT * FROM materiali_didattici WHERE docente_id = ? ORDER BY caricato_il DESC",
            [user_id],
        )
    except Exception:
        materiali = []

    if not materiali:
        st.caption("Nessun materiale caricato.")
        return

    for m in materiali:
        with st.container(border=True):
            col1, col2 = st.columns([5, 1])
            with col1:
                elaborato = bool(m.get("is_processed"))
                st.checkbox(
                    f"**{m['titolo']}**",
                    key=f"mat_libero_check_{m['id']}",
                    disabled=not elaborato,
                )
                stato_label = "✅ Elaborato" if elaborato else "⏳ Non elaborato"
                st.caption(f"{m.get('tipo', '').upper()} · {stato_label} · {(m.get('caricato_il') or '')[:10]}")
            with col2:
                if st.button("🗑", key=f"del_mat_libero_{m['id']}", help="Elimina"):
                    db.esegui("DELETE FROM materiali_chunks WHERE materiale_id = ?", [m["id"]])
                    db.esegui("DELETE FROM materiali_didattici WHERE id = ?", [m["id"]])
                    st.rerun()

    selezionati = [
        m for m in materiali
        if st.session_state.get(f"mat_libero_check_{m['id']}", False)
    ]

    if st.button(
        "📖 Genera lezione sui documenti selezionati",
        type="primary",
        use_container_width=True,
        disabled=not selezionati,
    ):
        # Salva i materiali selezionati e pulisce i checkbox
        st.session_state["_materiali_liberi_selezionati"] = selezionati
        for m in materiali:
            st.session_state.pop(f"mat_libero_check_{m['id']}", None)
        st.rerun()


# ---------------------------------------------------------------------------
# Entry point principale
# ---------------------------------------------------------------------------

def mostra_homepage_studente():
    """Renderizza l'intera homepage studente."""
    st.markdown(_CSS, unsafe_allow_html=True)

    utente = st.session_state.user
    studente_id = st.session_state.current_user_id

    # Topbar con logout integrato
    if _render_topbar(utente):
        _, _, reset_fn = _import_orchestratore()
        if reset_fn:
            try:
                reset_fn()
            except Exception:
                pass
        st.session_state.clear()
        st.rerun()

    # Seed iscrizioni se lo studente non ha corsi nel DB (es. utenti demo)
    _seed_iscrizioni_se_mancanti(studente_id)

    # Carica corsi e stato di navigazione corrente
    corsi          = _get_corsi_studente(studente_id)
    view_mode      = st.session_state.get("_view_mode")       # "corso" | "piano" | None
    corso_sel_id   = st.session_state.get("_corso_sel")
    corso_sel_nome = st.session_state.get("_corso_nome", "")
    piano_sel_id   = st.session_state.get("_piano_sel")

    # Layout a tre colonne — sx:navigazione, cx:contenuto, dx:chatbot
    col_sx, col_cx, col_dx = st.columns([1.5, 3.0, 2.5], gap="small")

    # -------------------------------------------------------------------------
    # COLONNA SINISTRA — navigazione
    # -------------------------------------------------------------------------
    with col_sx:
        # Pulsante ricerca corsi
        if st.button("🔍 Cerca corsi", use_container_width=True, key="btn_cerca_corsi"):
            st.session_state["_view_mode"] = "ricerca"
            st.session_state["_corso_sel"] = None
            st.session_state["_piano_sel"] = None
            st.session_state["_search_results"] = None
            st.rerun()

        # Bottoni materiale personale (sempre visibili, sempre dialog liberi)
        _sidebar_user_id = utente.get("user_id", utente.get("id", 0))
        with st.container(horizontal=True):
            if st.button(":material/upload_file: Carica il tuo materiale", key="sb_btn_upload", use_container_width=True):
                _dialog_upload_materiale_libero()
            if st.button(":material/folder_open: Visualizza il tuo materiale", key="sb_btn_view", use_container_width=True):
                if "_materiali_liberi_selezionati" not in st.session_state:
                    _dialog_view_materiale_libero(_sidebar_user_id)

        # Sezione 1: Corsi universitari (sola lettura)
        _render_sidebar_corsi(corsi)
        # Sezione 2: Piani personalizzati dello studente
        _render_sidebar_piani(studente_id)
        # Sezione 3: Raccomandazioni AI
        _render_raccomandazioni(studente_id)

    # -------------------------------------------------------------------------
    # COLONNA CENTRALE — contenuto (vista diversa per corso vs piano)
    # -------------------------------------------------------------------------
    with col_cx:
        if not view_mode:
            # Welcome screen
            nome = utente["nome"]
            st.markdown(f"""
            <div class="empty-state" style="padding-top:24px; padding-bottom:8px">
                <div class="icon">🎓</div>
                <h3>Benvenuto, {nome}!</h3>
                <p style="max-width:360px; margin:0 auto; line-height:1.7">
                    Seleziona un <strong>corso</strong> per consultarlo,
                    o apri un <strong>piano personalizzato</strong> per studiare.
                    Chiedi a <strong>Lea</strong> di creare un nuovo piano su qualsiasi argomento.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("---")
            _render_ricerca_corsi(corsi, studente_id)

        elif view_mode == "ricerca":
            # ── VISTA RICERCA ─────────────────────────────────────────────
            if st.button("← Torna alla home", key="btn_back_from_search"):
                st.session_state["_view_mode"] = None
                st.session_state["_search_results"] = None
                st.rerun()
            _render_ricerca_corsi(corsi, studente_id)

        elif view_mode == "corso" and corso_sel_id:
            # ── VISTA CORSO — sola lettura ─────────────────────────────────
            col_hdr, col_disiscriviti = st.columns([5, 1])
            with col_hdr:
                st.markdown(f"""
                <div class="section-header">{corso_sel_nome}</div>
                <div class="section-sub">Corso universitario · Sola lettura</div>
                """, unsafe_allow_html=True)
            with col_disiscriviti:
                if st.button("🚪 Cancella iscrizione", key="btn_disiscriviti", help="Cancella la tua iscrizione a questo corso"):
                    _dialog_cancella_iscrizione(studente_id, corso_sel_id, corso_sel_nome)

            if st.button("📚 Materiale del corso", key="btn_materiale_corso", use_container_width=False):
                _dialog_materiale_corso(corso_sel_id, corso_sel_nome)

            # — Contenuto ufficiale del docente (se pubblicato) —
            piano_docente = _get_piano_docente_corso(corso_sel_id)
            if piano_docente:
                st.markdown("#### Lezioni del corso")
                _render_contenuto_piano(piano_docente["id"], studente_id=studente_id, is_corso_docente=True)
                st.markdown("---")
            else:
                st.info(
                    "Il docente non ha ancora pubblicato il contenuto di questo corso.",
                    icon=":material/school:",
                )


        elif view_mode == "piano" and piano_sel_id:
            # ── VISTA PIANO — spazio studio privato dello studente ──────────
            piano_info = db.trova_tutti("piani_personalizzati", {"id": piano_sel_id})
            titolo_piano = piano_info[0]["titolo"] if piano_info else "Piano di studio"

            sub_label = f"{corso_sel_nome} · Piano personalizzato" if corso_sel_nome else "Piano personalizzato"
            st.markdown(f"""
            <div class="section-header">{titolo_piano}</div>
            <div class="section-sub">{sub_label}</div>
            """, unsafe_allow_html=True)

            col_back, col_del_piano, col_mat_piano, _ = st.columns([1, 1, 1.5, 2.5])
            with col_back:
                back_label = "← Corso" if corso_sel_id else "← Home"
                if st.button(back_label):
                    if corso_sel_id:
                        st.session_state["_view_mode"] = "corso"
                    else:
                        st.session_state["_view_mode"] = None
                    st.session_state["_piano_sel"] = None
                    st.rerun()
            with col_del_piano:
                if st.button("🗑 Elimina piano", key="btn_del_piano_cx"):
                    _dialog_elimina_piano(piano_sel_id, titolo_piano)
            with col_mat_piano:
                if corso_sel_id:
                    if st.button("📚 Materiale del corso", key="btn_mat_piano"):
                        _dialog_materiale_corso(corso_sel_id, corso_sel_nome)
                else:
                    if st.button("📚 Materiale del piano", key="btn_mat_piano_libero"):
                        _dialog_materiale_piano_libero(piano_sel_id)


            _render_contenuto_piano(piano_sel_id, studente_id=studente_id)

    # -------------------------------------------------------------------------
    # COLONNA DESTRA — Chatbot Lea (con contesto completo corso + piano)
    # -------------------------------------------------------------------------
    piano_titolo_chat = None
    if view_mode == "piano" and piano_sel_id:
        info = db.trova_tutti("piani_personalizzati", {"id": piano_sel_id})
        piano_titolo_chat = info[0]["titolo"] if info else None

    with col_dx:
        _render_chatbot(
            utente,
            corso_sel_id,
            corso_sel_nome,
            view_mode=view_mode,
            piano_id=piano_sel_id if view_mode == "piano" else None,
            piano_titolo=piano_titolo_chat,
        )
