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


def _get_struttura_piano(piano_id: int) -> list[dict]:
    """
    Restituisce la struttura completa di un piano SOLO per il piano indicato:
    capitoli → paragrafi → tutti i contenuti (lezione, quiz, flashcard, schema).

    Ogni paragrafo ha:
      - par["contenuti"]  → lista di tutti i record piano_contenuti
      - par["testo"]      → testo della prima lezione (stringa), o None
    """
    capitoli = db.trova_tutti("piano_capitoli", {"piano_id": piano_id}, ordine="ordine ASC")

    for cap in capitoli:
        cap["paragrafi"] = db.trova_tutti(
            "piano_paragrafi",
            {"capitolo_id": cap["id"]},
            ordine="ordine ASC",
        )
        for par in cap["paragrafi"]:
            # Fetch ALL tipi — ordine ASC per coerenza
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


def _render_sidebar_corsi(corsi: list[dict], corsi_chat_id: int | None = None):
    """Renderizza la lista corsi nella colonna sinistra."""
    st.markdown('<div class="divider-label">I tuoi corsi</div>', unsafe_allow_html=True)

    if not corsi:
        st.caption("Nessun corso trovato.")
        return

    for corso in corsi:
        cid = corso["id"]
        attivo_cls = "attivo" if st.session_state.get("_corso_sel") == cid else ""
        stato = corso["stato"]

        st.markdown(f"""
        <div class="corso-item {attivo_cls}" style="margin-bottom:8px;">
            <div class="corso-nome">{corso["nome"]}</div>
            <div class="corso-meta">
                {"Anno " + str(corso["anno_di_corso"]) if corso.get("anno_di_corso") else ""}
                {" · " + str(corso["cfu"]) + " CFU" if corso.get("cfu") else ""}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Apri →", key=f"btn_corso_{cid}", use_container_width=True):
            st.session_state["_corso_sel"]  = cid
            st.session_state["_corso_nome"] = corso["nome"]
            st.session_state["_chat_history"] = []

            # Auto-selezione piano: se ce n'è uno solo, aprilo subito
            studente_id_temp = st.session_state.get("current_user_id")
            piani_temp = db.trova_tutti(
                "piani_personalizzati",
                {"studente_id": studente_id_temp, "corso_universitario_id": cid},
            )
            if len(piani_temp) == 1:
                st.session_state["_piano_sel"] = piani_temp[0]["id"]
            else:
                st.session_state["_piano_sel"] = None

            st.rerun()


def _render_piani(studente_id: int, corso_id: int, corso_nome: str):
    """Renderizza i piani AI disponibili per il corso selezionato."""
    piani = _get_piani_corso(studente_id, corso_id)

    st.markdown(f'<div class="divider-label">Piani AI — {corso_nome[:22]}...</div>', unsafe_allow_html=True)

    if not piani:
        st.caption("💡 Chiedi a Lea di generare un piano per questo corso!")
    else:
        for piano in piani:
            pid = piano["id"]
            attivo = st.session_state.get("_piano_sel") == pid
            st.markdown(f"""
            <div class="piano-card {'attivo' if attivo else ''}">
                <h5>{piano["titolo"][:50]}{'…' if len(piano["titolo"]) > 50 else ''}</h5>
                <div class="piano-meta">
                    <span class="ai-badge">AI</span>
                    &nbsp;{piano.get("created_at", "")[:10]}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Studia →", key=f"btn_piano_{pid}", use_container_width=True):
                st.session_state["_piano_sel"] = pid
                st.rerun()


def _render_contenuto_piano(piano_id: int):
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

    st.markdown("<div style='margin-bottom:16px'></div>", unsafe_allow_html=True)

    # ------------------------------------------------------------------ #
    # 2. CONTENUTO — capitoli espandibili
    # ------------------------------------------------------------------ #
    for i, cap in enumerate(capitoli):
        with st.expander(f"📖  {cap['titolo']}", expanded=(i == 0)):
            paragrafi = cap.get("paragrafi", [])
            if not paragrafi:
                st.markdown(
                    '<p style="color:#5A6A7E;font-size:0.85rem">Nessuna sezione generata.</p>',
                    unsafe_allow_html=True,
                )
                continue

            for par in paragrafi:
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

                # ---- QUIZ ----
                for c in quiz_list:
                    raw = (c.get("contenuto_json") or "").strip()
                    dati: dict = {}
                    if raw.startswith("{") or raw.startswith("["):
                        try:
                            dati = json.loads(raw)
                        except Exception:
                            pass
                    domande = dati.get("domande") or dati.get("questions") or []
                    st.markdown(
                        '<div class="content-type-badge badge-quiz">❓ Quiz</div>',
                        unsafe_allow_html=True,
                    )
                    if domande:
                        for idx, d in enumerate(domande[:5], 1):
                            testo_d = (d.get("testo") or d.get("domanda") or d.get("question") or "")
                            testo_d_safe = testo_d.replace("<", "&lt;").replace(">", "&gt;")
                            st.markdown(
                                f'<div class="quiz-domanda">'
                                f'<span class="quiz-num">{idx}</span>{testo_d_safe}'
                                f'</div>',
                                unsafe_allow_html=True,
                            )

                # ---- FLASHCARD ----
                for c in fc_list:
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
                    # Supporta sia {"cards":[{"fronte","retro"}]} che {"cards":[{"domanda","risposta"}]}
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
                            with cols_fc[j % n_col]:
                                st.markdown(f"""
                                <div class="flashcard-mini">
                                    <div class="fc-front">{fronte}</div>
                                    <div class="fc-back">{retro}</div>
                                </div>
                                """, unsafe_allow_html=True)

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

    st.markdown("<div style='margin-bottom:16px'></div>", unsafe_allow_html=True)

    # ------------------------------------------------------------------ #
    # 2. CONTENUTO — capitoli espandibili
    # ------------------------------------------------------------------ #
    for i, cap in enumerate(capitoli):
        expanded = (i == 0)  # primo capitolo aperto di default
        with st.expander(f"📖  {cap['titolo']}", expanded=expanded):
            paragrafi = cap.get("paragrafi", [])
            if not paragrafi:
                st.markdown(
                    '<p style="color:#5A6A7E;font-size:0.85rem">Nessuna sezione generata.</p>',
                    unsafe_allow_html=True,
                )
                continue

            for par in paragrafi:
                # Header paragrafo
                st.markdown(f"""
                <div class="paragrafo-box">
                    <h5>{par["titolo"]}</h5>
                </div>
                """, unsafe_allow_html=True)

                contenuti = par.get("contenuti", [])
                ha_contenuto = False

                for c in contenuti:
                    tipo = (c.get("tipo") or "").lower()
                    raw = (c.get("contenuto_json") or "").strip()

                    # ---- LEZIONE ----
                    if tipo == "lezione":
                        testo = par.get("testo") or raw
                        if testo:
                            st.markdown(
                                f'<div class="paragrafo-testo">{testo}</div>',
                                unsafe_allow_html=True,
                            )
                            ha_contenuto = True

                    # ---- QUIZ ----
                    elif tipo == "quiz":
                        ha_contenuto = True
                        dati: dict = {}
                        if raw.startswith("{") or raw.startswith("["):
                            try:
                                dati = json.loads(raw)
                            except Exception:
                                pass
                        domande = dati.get("domande") or dati.get("questions") or []
                        if domande:
                            st.markdown(
                                '<div class="content-type-badge badge-quiz">❓ Quiz</div>',
                                unsafe_allow_html=True,
                            )
                            for idx, d in enumerate(domande[:5], 1):
                                testo_d = d.get("testo") or d.get("domanda") or d.get("question") or ""
                                st.markdown(
                                    f'<div class="quiz-domanda">'
                                    f'<span class="quiz-num">{idx}</span>{testo_d}'
                                    f'</div>',
                                    unsafe_allow_html=True,
                                )
                        else:
                            st.markdown(
                                '<div class="content-type-badge badge-quiz">❓ Quiz generato</div>',
                                unsafe_allow_html=True,
                            )

                    # ---- FLASHCARD ----
                    elif tipo == "flashcard":
                        ha_contenuto = True
                        dati = {}
                        if raw.startswith("{") or raw.startswith("["):
                            try:
                                dati = json.loads(raw) if raw.startswith("{") else {"cards": json.loads(raw)}
                            except Exception:
                                pass
                        cards = dati.get("cards") or dati.get("flashcard") or []
                        if cards:
                            st.markdown(
                                '<div class="content-type-badge badge-flash">🃏 Flashcard</div>',
                                unsafe_allow_html=True,
                            )
                            cols_fc = st.columns(min(len(cards), 3))
                            for j, card in enumerate(cards[:3]):
                                fronte = card.get("fronte") or card.get("front") or card.get("domanda") or ""
                                retro  = card.get("retro")  or card.get("back")  or card.get("risposta") or ""
                                with cols_fc[j % 3]:
                                    st.markdown(f"""
                                    <div class="flashcard-mini">
                                        <div class="fc-front">{fronte}</div>
                                        <div class="fc-back">{retro}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                        else:
                            st.markdown(
                                '<div class="content-type-badge badge-flash">🃏 Flashcard generate</div>',
                                unsafe_allow_html=True,
                            )

                    # ---- SCHEMA / ALTRI ----
                    elif tipo in ("schema", "mappa"):
                        ha_contenuto = True
                        st.markdown(
                            '<div class="content-type-badge badge-schema">🗺 Schema</div>',
                            unsafe_allow_html=True,
                        )
                        if raw:
                            st.code(raw, language="")

                if not ha_contenuto:
                    st.markdown(
                        '<p style="color:#5A6A7E;font-size:0.83rem;margin:6px 0 10px 0">'
                        '⏳ Contenuto non ancora generato — chiedi a Lea di generarlo!</p>',
                        unsafe_allow_html=True,
                    )


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
# Chatbot Lea
# ---------------------------------------------------------------------------

def _render_chatbot(utente: dict, corso_id: int | None, corso_nome: str | None):
    """Renderizza il chatbot Lea nella colonna destra."""
    chat_con_orchestratore, aggiorna_contesto, _ = _import_orchestratore()

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

    # Render messaggi
    chat_html = '<div class="chat-container" id="chat-box">'
    for msg in st.session_state["chat_history_display"]:
        if msg["role"] == "user":
            testo_safe = msg["content"].replace("<", "&lt;").replace(">", "&gt;")
            chat_html += f'<div class="msg-user">{testo_safe}</div>'
        else:
            # Converti markdown minimo: **testo** → <strong>testo</strong>, \n → <br>
            import re as _re
            contenuto = msg["content"].replace("<", "&lt;").replace(">", "&gt;")
            contenuto = _re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', contenuto)
            contenuto = contenuto.replace("\n", "<br>")
            chat_html += f'<div class="msg-ai">{contenuto}</div>'
    chat_html += "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)

    # ---- Suggerimenti rapidi — compatti, sopra l'input ----
    suggerimenti = [
        ("📚", "Genera un piano"),
        ("❓", "Crea un quiz"),
        ("🃏", "Flashcard"),
    ]
    cols_sug = st.columns(3)
    messaggio_da_suggerimento: str | None = None
    for i, (icona, testo) in enumerate(suggerimenti):
        if cols_sug[i].button(f"{icona} {testo}", key=f"sug_{i}", use_container_width=True):
            messaggio_da_suggerimento = testo

    # ---- Input chat nativo (pulizia automatica dopo invio) ----
    user_input = st.chat_input("Chiedi a Lea...", key="lea_chat_input")

    # Unifica input da campo libero e da suggerimento
    messaggio_finale: str | None = user_input or messaggio_da_suggerimento

    if messaggio_finale:
        st.session_state["chat_history_display"].append(
            {"role": "user", "content": messaggio_finale}
        )

        if chat_con_orchestratore is not None and aggiorna_contesto is not None:
            if corso_id:
                aggiorna_contesto(corso_id=corso_id, corso_nome=corso_nome)
            try:
                risposta = chat_con_orchestratore(
                    messaggio_utente=messaggio_finale,
                    corso_contestuale_id=corso_id,
                    corso_contestuale_nome=corso_nome,
                )
            except Exception as e:
                risposta = f"⚠️ Errore: {str(e)[:120]}"
        else:
            risposta = (
                "⚙️ Lea non è ancora configurata (AWS Bedrock non attivo). "
                "Configura le credenziali AWS in `config.py` per abilitarla."
            )

        st.session_state["chat_history_display"].append(
            {"role": "assistant", "content": risposta}
        )
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
    for corso in corsi_attivi:
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

    # Carica corsi e selezioni correnti
    corsi = _get_corsi_studente(studente_id)
    corso_sel_id   = st.session_state.get("_corso_sel")
    corso_sel_nome = st.session_state.get("_corso_nome", "")
    piano_sel_id   = st.session_state.get("_piano_sel")

    # Layout a tre colonne — sx:navigazione, cx:contenuto, dx:chatbot
    col_sx, col_cx, col_dx = st.columns([1.5, 3.0, 2.5], gap="small")

    # -------------------------------------------------------------------------
    # COLONNA SINISTRA — navigazione
    # -------------------------------------------------------------------------
    with col_sx:
        _render_sidebar_corsi(corsi, corso_sel_id)

        if corso_sel_id and corso_sel_nome:
            _render_piani(studente_id, corso_sel_id, corso_sel_nome)

        _render_raccomandazioni(studente_id)

    # -------------------------------------------------------------------------
    # COLONNA CENTRALE — contenuto
    # -------------------------------------------------------------------------
    with col_cx:
        if not corso_sel_id:
            # Welcome screen
            nome = utente["nome"]
            st.markdown(f"""
            <div class="empty-state" style="padding-top:32px">
                <div class="icon">🎓</div>
                <h3>Benvenuto, {nome}!</h3>
                <p style="max-width:360px; margin:0 auto; line-height:1.7">
                    Seleziona un corso dalla barra laterale per visualizzare
                    i tuoi piani personalizzati AI, o chiedi a <strong>Lea</strong>
                    di creare un nuovo piano di studio.
                </p>
            </div>
            """, unsafe_allow_html=True)

        elif not piano_sel_id:
            # Mostra info corso e invita a scegliere un piano
            st.markdown(f"""
            <div class="section-header">{corso_sel_nome}</div>
            <div class="section-sub">Seleziona un piano di studio dalla sidebar o chiedi a Lea di generarne uno nuovo.</div>
            """, unsafe_allow_html=True)

            # Mostra i piani come card cliccabili anche qui
            piani = _get_piani_corso(studente_id, corso_sel_id)
            if piani:
                st.markdown("### 📋 Piani disponibili")
                for piano in piani:
                    pid = piano["id"]
                    struttura = _get_struttura_piano(pid)
                    n_cap = len(struttura)
                    n_par = sum(len(c.get("paragrafi", [])) for c in struttura)
                    col_a, col_b = st.columns([4, 1])
                    with col_a:
                        st.markdown(f"""
                        <div class="piano-card">
                            <h5>{piano["titolo"]}</h5>
                            <div class="piano-meta">
                                <span class="ai-badge">AI</span>
                                &nbsp;{n_cap} capitoli · {n_par} paragrafi
                                &nbsp;·&nbsp; {piano.get("created_at", "")[:10]}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_b:
                        if st.button("Apri", key=f"open_piano_{pid}", use_container_width=True):
                            st.session_state["_piano_sel"] = pid
                            st.rerun()
            else:
                st.info("💡 Nessun piano ancora. Chiedi a Lea: *\"Genera un piano per Basi di Dati\"*")

        else:
            # Mostra il contenuto del piano selezionato
            piano_info = db.trova_tutti("piani_personalizzati", {"id": piano_sel_id})
            titolo_piano = piano_info[0]["titolo"] if piano_info else "Piano di studio"

            st.markdown(f"""
            <div class="section-header">{corso_sel_nome}</div>
            <div class="section-sub">{titolo_piano}</div>
            """, unsafe_allow_html=True)

            col_back, col_space = st.columns([1, 5])
            with col_back:
                if st.button("← Indietro"):
                    st.session_state["_piano_sel"] = None
                    st.rerun()

            _render_contenuto_piano(piano_sel_id)

    # -------------------------------------------------------------------------
    # COLONNA DESTRA — Chatbot Lea
    # -------------------------------------------------------------------------
    with col_dx:
        _render_chatbot(utente, corso_sel_id, corso_sel_nome)
