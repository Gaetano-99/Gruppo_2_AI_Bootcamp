"""Homepage Docente - LearnAI Platform."""

import json
import os
import sys
from typing import Any, List, Dict

import plotly.express as px
import streamlit as st

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from platform_sdk.database import db


def _import_orchestratore():
    try:
        from src.agents.orchestrator import (
            chat_con_orchestratore,
            aggiorna_contesto_sessione,
            reset_sessione_chat,
        )
        return chat_con_orchestratore, aggiorna_contesto_sessione, reset_sessione_chat
    except Exception:
        return None, None, None


_CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --ink: #0D1117;
    --ink-2: #1C2333;
    --ink-3: #2D3748;
    --mist: #8892A4;
    --silver: #C4CDD9;
    --fog: #EDF1F7;
    --canvas: #F7F9FC;
    --white: #FFFFFF;

    --sapphire: #1847B1;
    --sapphire-dark: #0F2D7A;
    --sapphire-glow: #2558D4;
    --azure: #4F8EF7;
    --gold: #D4A843;
    --gold-pale: #FDF3D8;
    --emerald: #0FAB71;
    --emerald-pale: #E3FAF2;
    --amber: #D97706;
    --amber-pale: #FEF3C7;
    --crimson: #DC2626;

    --radius-sm: 8px;
    --radius-md: 14px;
    --radius-lg: 20px;
    --radius-xl: 28px;

    --shadow-sm: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md: 0 4px 16px rgba(15,30,80,0.10), 0 1px 4px rgba(15,30,80,0.06);
    --shadow-lg: 0 12px 40px rgba(15,30,80,0.14), 0 2px 8px rgba(15,30,80,0.08);
    --shadow-glow: 0 0 0 3px rgba(79,142,247,0.18);
}

/* ── RESET & BASE ── */
.stApp {
    background: var(--canvas) !important;
    font-family: 'DM Sans', sans-serif !important;
}
#MainMenu, footer { visibility: hidden; }
.block-container {
    padding-top: 0 !important;
    padding-bottom: 2rem !important;
    max-width: 1400px !important;
}

/* ── TOPBAR ── */
.topbar {
    background: var(--ink);
    border-bottom: 1px solid rgba(255,255,255,0.06);
    padding: 0 32px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: -1rem -1rem 28px -1rem;
    position: relative;
}
.topbar::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--azure) 30%, var(--gold) 70%, transparent);
    opacity: 0.5;
}
.topbar-brand {
    font-family: 'DM Serif Display', serif;
    color: var(--white);
    font-size: 1.2rem;
    letter-spacing: -0.02em;
    display: flex;
    align-items: center;
    gap: 10px;
}
.topbar-brand .dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--azure);
    box-shadow: 0 0 8px var(--azure);
    animation: pulse 2.5s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.6; transform: scale(0.85); }
}
.topbar-brand .accent { color: var(--azure); }
.topbar-user {
    display: flex;
    align-items: center;
    gap: 12px;
    color: rgba(255,255,255,0.7);
    font-size: 0.85rem;
}
.topbar-avatar {
    width: 36px; height: 36px;
    border-radius: 10px;
    background: linear-gradient(135deg, var(--sapphire-glow), var(--azure));
    color: var(--white);
    font-weight: 600;
    font-size: 0.85rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    box-shadow: var(--shadow-sm);
}
.topbar-name { color: var(--white); font-weight: 500; line-height: 1.2; }
.topbar-role { color: var(--azure); font-size: 0.72rem; font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase; }

/* ── SECTION CARD ── */
.section-card {
    background: var(--white);
    border-radius: var(--radius-lg);
    padding: 24px 28px;
    margin-bottom: 20px;
    box-shadow: var(--shadow-md);
    border: 1px solid rgba(196,205,217,0.5);
    position: relative;
    overflow: hidden;
}
.section-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--sapphire), var(--azure), var(--sapphire-glow));
}
.section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem;
    color: var(--ink);
    margin: 0 0 4px 0;
    letter-spacing: -0.02em;
}
.section-sub {
    color: var(--mist);
    font-size: 0.85rem;
    margin-bottom: 18px;
    font-weight: 400;
}

/* ── METRIC BOXES ── */
.metric-box {
    background: var(--fog);
    border: 1px solid rgba(196,205,217,0.6);
    border-radius: var(--radius-md);
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.metric-box:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}
.metric-box::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--azure), var(--sapphire));
    opacity: 0;
    transition: opacity 0.2s ease;
}
.metric-box:hover::after { opacity: 1; }
.metric-icon {
    font-size: 1.2rem;
    margin-bottom: 10px;
    display: block;
}
.metric-label {
    color: var(--mist);
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 6px;
}
.metric-value {
    color: var(--ink);
    font-size: 2rem;
    font-weight: 300;
    letter-spacing: -0.04em;
    font-family: 'DM Serif Display', serif;
    line-height: 1;
}

/* ── COURSE CARD ── */
.course-card {
    background: var(--white);
    border-radius: var(--radius-md);
    padding: 16px 20px;
    border: 1px solid rgba(196,205,217,0.5);
    box-shadow: var(--shadow-sm);
    margin-bottom: 10px;
    transition: box-shadow 0.2s ease, border-color 0.2s ease;
}
.course-card:hover {
    box-shadow: var(--shadow-md);
    border-color: var(--azure);
}
.course-card .title {
    font-weight: 600;
    color: var(--ink);
    margin: 0 0 8px 0;
    font-size: 0.95rem;
}
.course-card .meta {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    align-items: center;
}

/* ── STATUS PILL ── */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 999px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.status-pill::before {
    content: '';
    width: 5px; height: 5px;
    border-radius: 50%;
    background: currentColor;
    display: inline-block;
}
.pill-pub {
    background: var(--emerald-pale);
    color: var(--emerald);
    border: 1px solid rgba(15,171,113,0.2);
}
.pill-bozza {
    background: var(--amber-pale);
    color: var(--amber);
    border: 1px solid rgba(217,119,6,0.2);
}

/* ── CHIP ── */
.chip {
    display: inline-flex;
    align-items: center;
    background: var(--fog);
    color: var(--ink-3);
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 600;
    border: 1px solid rgba(196,205,217,0.5);
    font-family: 'JetBrains Mono', monospace;
}

/* ── CHAT ── */
.chat-header {
    background: var(--ink);
    color: var(--white);
    padding: 16px 20px;
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    display: flex;
    align-items: center;
    gap: 12px;
    position: relative;
    overflow: hidden;
}
.chat-header::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(79,142,247,0.12) 0%, transparent 60%);
}
.chat-header-inner { position: relative; z-index: 1; display: flex; align-items: center; gap: 12px; width: 100%; }
.chat-avatar {
    width: 38px; height: 38px;
    border-radius: 10px;
    background: linear-gradient(135deg, var(--sapphire-glow), var(--azure));
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
    box-shadow: 0 0 12px rgba(79,142,247,0.4);
}
.chat-title {
    font-weight: 600;
    font-size: 0.95rem;
    line-height: 1.2;
}
.chat-sub {
    font-size: 0.72rem;
    color: rgba(255,255,255,0.5);
    font-weight: 400;
}
.chat-online {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--emerald);
    box-shadow: 0 0 6px var(--emerald);
    margin-left: auto;
    animation: pulse 2.5s ease-in-out infinite;
}
.chat-container {
    background: var(--white);
    border: 1px solid rgba(196,205,217,0.5);
    border-top: none;
    border-radius: 0 0 var(--radius-lg) var(--radius-lg);
    min-height: 400px;
    padding: 20px 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}
.msg-user {
    background: linear-gradient(135deg, var(--sapphire), var(--sapphire-glow));
    color: var(--white);
    border-radius: 16px 16px 4px 16px;
    padding: 11px 16px;
    font-size: 0.86rem;
    max-width: 84%;
    align-self: flex-end;
    line-height: 1.55;
    box-shadow: 0 2px 8px rgba(24,71,177,0.25);
}
.msg-ai {
    background: var(--fog);
    color: var(--ink-3);
    border-radius: 4px 16px 16px 16px;
    padding: 11px 16px;
    font-size: 0.86rem;
    max-width: 90%;
    align-self: flex-start;
    line-height: 1.6;
    border: 1px solid rgba(196,205,217,0.5);
}

/* ── INPUTS ── */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stChatInput textarea {
    background: var(--fog) !important;
    color: var(--ink) !important;
    border: 1px solid var(--silver) !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: var(--azure) !important;
    box-shadow: var(--shadow-glow) !important;
}
.stTextInput input::placeholder,
.stTextArea textarea::placeholder,
.stChatInput textarea::placeholder {
    color: var(--mist) !important;
}

div[data-baseweb="select"] {
    background: var(--fog) !important;
    color: var(--ink) !important;
    border-radius: var(--radius-sm) !important;
}
div[data-baseweb="select"] input { color: var(--ink) !important; }

/* ── LABELS ── */
label[data-testid="stWidgetLabel"] p,
label[data-testid="stWidgetLabel"] div,
div[data-testid="stWidgetLabel"] p,
div[data-testid="stWidgetLabel"] div,
label p {
    color: var(--ink-3) !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: var(--fog);
    padding: 4px;
    border-radius: var(--radius-sm);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    color: var(--mist) !important;
    padding: 6px 14px !important;
}
.stTabs [aria-selected="true"] {
    background: var(--white) !important;
    color: var(--ink) !important;
    box-shadow: var(--shadow-sm) !important;
}

/* ── BUTTONS (Streamlit overrides) ── */
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--sapphire), var(--sapphire-glow)) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.45rem 1.1rem !important;
    box-shadow: 0 2px 8px rgba(24,71,177,0.3) !important;
    transition: opacity 0.15s, transform 0.15s !important;
}
div.stButton > button[kind="primary"]:hover {
    opacity: 0.92 !important;
    transform: translateY(-1px) !important;
}
div.stButton > button[kind="secondary"] {
    background: var(--fog) !important;
    color: var(--ink-3) !important;
    border: 1px solid var(--silver) !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
}

/* ── TAB NOTE ── */
.tab-note {
    background: var(--fog);
    border: 1px solid rgba(196,205,217,0.5);
    border-radius: var(--radius-md);
    padding: 16px 20px;
    color: var(--ink-3);
    font-size: 0.87rem;
    line-height: 1.7;
}
.tab-note strong { color: var(--ink); font-weight: 600; }

/* ── DIVIDERS ── */
hr.styled {
    border: none;
    border-top: 1px solid rgba(196,205,217,0.4);
    margin: 12px 0;
}

/* ── SUGGESTIONS ── */
.sug-btn div.stButton > button {
    background: var(--white) !important;
    border: 1px solid var(--silver) !important;
    color: var(--ink-3) !important;
    font-size: 0.8rem !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.35rem 0.8rem !important;
}
.sug-btn div.stButton > button:hover {
    border-color: var(--azure) !important;
    color: var(--sapphire) !important;
    background: rgba(79,142,247,0.06) !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--silver); border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: var(--mist); }

/* ── COLUMN LAYOUT ── */
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-of-type {
    position: static;
    max-height: none;
    overflow: visible;
}

/* ── FORM SUBMIT ── */
div.stFormSubmitButton > button {
    background: linear-gradient(135deg, var(--sapphire), var(--sapphire-glow)) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(24,71,177,0.3) !important;
}
</style>
"""


def _get_corsi_docente(docente_id: int) -> List[dict]:
    return db.trova_tutti("corsi_universitari", {"docente_id": docente_id}, ordine="created_at DESC")


def _get_tutti_cdl() -> List[dict]:
    try:
        return db.trova_tutti("corsi_di_laurea", {}, ordine="nome ASC")
    except Exception:
        return []


def _get_cdl_corso(corso_id: int) -> List[int]:
    try:
        rows = db.trova_tutti("corsi_laurea_universitari", {"corso_universitario_id": corso_id})
        return [r["corso_di_laurea_id"] for r in rows]
    except Exception:
        return []


def _salva_cdl_corso(corso_id: int, cdl_ids: List[int]) -> None:
    try:
        db.esegui("DELETE FROM corsi_laurea_universitari WHERE corso_universitario_id = ?", [corso_id])
    except Exception:
        pass
    for cdl_id in cdl_ids:
        try:
            db.inserisci("corsi_laurea_universitari", {
                "corso_di_laurea_id": cdl_id,
                "corso_universitario_id": corso_id,
                "obbligatorio": 1,
            })
        except Exception:
            pass


def _get_materiali_corso(corso_id: int) -> List[dict]:
    try:
        return db.trova_tutti("materiali_didattici", {"corso_universitario_id": corso_id}, ordine="caricato_il DESC")
    except Exception:
        return []


def _conta_studenti_corso(corso_id: int) -> int:
    try:
        rows = db.esegui(
            "SELECT COUNT(DISTINCT studente_id) AS n FROM studenti_corsi WHERE corso_universitario_id = ?",
            [corso_id],
        )
        return int(rows[0]["n"]) if rows else 0
    except Exception:
        return 0


def _metrics(docente_id: int, corso_id: int | None = None) -> Dict[str, Any]:
    filtri = ""
    params = [docente_id]
    if corso_id:
        filtri = " AND cu.id = ?"
        params.append(corso_id)

    def one(sql: str, default: int = 0) -> int:
        try:
            res = db.esegui(sql, params)
            return int(res[0]["n"]) if res else default
        except Exception:
            return default

    studenti = one(
        """
        SELECT COUNT(DISTINCT sc.studente_id) AS n
        FROM corsi_universitari cu
        LEFT JOIN studenti_corsi sc ON sc.corso_universitario_id = cu.id
        WHERE cu.docente_id = ?""" + filtri
    )
    quiz_appr = one(
        """
        SELECT COUNT(*) AS n
        FROM quiz q
        JOIN corsi_universitari cu ON cu.id = q.corso_universitario_id
        WHERE cu.docente_id = ? AND q.approvato = 1""" + filtri
    )
    tentativi = one(
        """
        SELECT COUNT(*) AS n
        FROM tentativi_quiz t
        JOIN quiz q ON q.id = t.quiz_id
        JOIN corsi_universitari cu ON cu.id = q.corso_universitario_id
        WHERE cu.docente_id = ? AND q.approvato = 1""" + filtri
    )
    corsi = one("SELECT COUNT(*) AS n FROM corsi_universitari cu WHERE cu.docente_id = ?" + filtri)

    return {"studenti": studenti, "quiz": quiz_appr, "tentativi": tentativi, "corsi": corsi}


def _stato_corso(corso: dict) -> tuple[str, str]:
    return ("Pubblicato", "pill-pub") if corso.get("attivo") else ("Da pubblicare", "pill-bozza")


def _render_topbar(utente: dict) -> bool:
    st.markdown(_CSS, unsafe_allow_html=True)
    initials = (utente.get('nome', '')[:1] or '?').upper()
    st.markdown(
        f"""
        <div class='topbar'>
            <div class='topbar-brand'>
                <div class='dot'></div>
                LearnAI <span class='accent'>Docente</span>
            </div>
            <div class='topbar-user'>
                <div>
                    <div class='topbar-name'>{utente.get('nome','')} {utente.get('cognome','')}</div>
                    <div class='topbar-role'>Docente</div>
                </div>
                <div class='topbar-avatar'>{initials}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col_logout, _ = st.columns([1, 5])
    with col_logout:
        if st.button("↩ Logout", type="secondary"):
            _, _, reset_fn = _import_orchestratore()
            if reset_fn:
                try:
                    reset_fn()
                except Exception:
                    pass
            st.session_state.clear()
            st.rerun()
            return True
    return False


def _render_analytics(docente_id: int, corsi: List[dict]) -> None:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Analytics</div>', unsafe_allow_html=True)
    scope_options = ["Generale"] + [f"Corso: {c['nome']} (ID {c['id']})" for c in corsi]
    scelta = st.selectbox("Ambito analytics", scope_options, key="analytics_scope")
    corso_sel_id = None
    if scelta.startswith("Corso:"):
        label_to_id = {f"Corso: {c['nome']} (ID {c['id']})": c["id"] for c in corsi}
        corso_sel_id = label_to_id.get(scelta)
    dati = _metrics(docente_id, corso_sel_id)

    icons = ["👥", "✅", "📊", "📚"]
    col_a, col_b, col_c, col_d = st.columns(4)
    for col, label, val, icon in [
        (col_a, "Studenti unici", dati["studenti"], icons[0]),
        (col_b, "Quiz pubblicati", dati["quiz"], icons[1]),
        (col_c, "Tentativi quiz", dati["tentativi"], icons[2]),
        (col_d, "Corsi gestiti", dati["corsi"], icons[3]),
    ]:
        with col:
            st.markdown(
                f"""
                <div class='metric-box'>
                    <span class='metric-icon'>{icon}</span>
                    <div class='metric-label'>{label}</div>
                    <div class='metric-value'>{val}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if corsi:
        serie = [{"Corso": c["nome"], "Quiz approvati": _metrics(docente_id, c["id"])['quiz']} for c in corsi]
        fig = px.bar(
            serie, x="Corso", y="Quiz approvati",
            title="Quiz approvati per corso",
            color_discrete_sequence=["#2558D4"],
        )
        fig.update_layout(
            height=300,
            margin=dict(t=44, b=16, l=8, r=8),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans", size=12, color="#2D3748"),
            title_font=dict(family="DM Serif Display", size=15, color="#0D1117"),
            xaxis=dict(showgrid=False, tickfont=dict(size=11)),
            yaxis=dict(gridcolor="rgba(196,205,217,0.35)", tickfont=dict(size=11)),
        )
        fig.update_traces(marker_line_width=0, marker_cornerradius=6)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Carica almeno un corso per vedere le analytics.")
    st.markdown('</div>', unsafe_allow_html=True)


def _dialog_crea_corso(docente_id: int):
    header_col, close_col = st.columns([10, 1])
    with header_col:
        st.markdown("#### Nuovo corso")
    with close_col:
        if st.button("✕", key="close_create_course", help="Chiudi"):
            st.session_state["_doc_show_create"] = False
            st.rerun()

    tutti_cdl = _get_tutti_cdl()
    cdl_nomi = [c["nome"] for c in tutti_cdl]

    with st.form("crea_corso_form"):
        nome = st.text_input("Nome corso")
        descrizione = st.text_area("Descrizione")
        cfu = st.number_input("CFU", min_value=0, max_value=30, step=1, value=0)
        anno = st.number_input("Anno di corso (1-5)", min_value=1, max_value=5, step=1, value=1)
        livello = st.selectbox("Livello", ["base", "intermedio", "avanzato"])
        semestre = st.selectbox("Semestre", [1, 2])
        cdl_sel = st.multiselect("Corsi di Laurea", cdl_nomi)
        submitted = st.form_submit_button("Salva bozza", type="primary")
    if submitted:
        if not nome:
            st.error("Inserisci il nome del corso.")
            return
        corso_id = db.inserisci(
            "corsi_universitari",
            {
                "nome": nome,
                "descrizione": descrizione,
                "docente_id": docente_id,
                "cfu": cfu or None,
                "anno_di_corso": anno,
                "livello": livello,
                "semestre": semestre,
                "attivo": 0,
            },
        )
        cdl_sel_ids = [c["id"] for c in tutti_cdl if c["nome"] in cdl_sel]
        _salva_cdl_corso(corso_id, cdl_sel_ids)
        st.session_state["_doc_show_create"] = False
        st.session_state["_doc_create_feedback"] = "Corso salvato in bozza."
        st.session_state["_doc_refresh"] = True


def _dialog_elimina_corso(corso_id: int):
    st.warning("Eliminerai definitivamente il corso e i relativi materiali.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Annulla"):
            st.session_state["_doc_delete_confirm"] = None
    with c2:
        if st.button("Elimina", type="primary"):
            try:
                db.elimina("corsi_universitari", {"id": corso_id})
                st.session_state["_doc_refresh"] = True
                st.session_state["_corso_doc_sel"] = None
                st.success("Corso eliminato.")
            except Exception as e:
                st.error(f"Impossibile eliminare: {e}")


def _elimina_materiale(materiale_id: int, s3_key: str | None) -> None:
    try:
        db.elimina("materiali_chunks", {"materiale_id": materiale_id})
    except Exception:
        pass
    db.elimina("materiali_didattici", {"id": materiale_id})
    if s3_key:
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(base_dir, s3_key)
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception:
            pass


def _render_materiali(corso: dict, docente_id: int):
    st.markdown("### Materiali didattici (fonte RAG)")
    st.caption("Questi file alimentano la generazione di lezioni/quiz. Formati accettati: pdf, docx, txt, pptx, xlsx.")

    materiali = _get_materiali_corso(corso["id"])
    if materiali:
        for m in materiali:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{m['titolo']}**")
                st.caption(f"Tipo: {m['tipo']} · Caricato: {(m.get('caricato_il') or '')[:10]}")
            with col2:
                if m.get("is_processed"):
                    n_chunks = db.conta("materiali_chunks", {"materiale_id": m["id"]})
                    st.caption(f"✅ Processato ({n_chunks} chunk)")
                else:
                    st.caption("⏳ In attesa")
            with col3:
                if st.button("Elimina", key=f"del_mat_{m['id']}"):
                    _elimina_materiale(m["id"], m.get("s3_key"))
                    st.success("Materiale e chunk eliminati.")
                    st.session_state["_doc_refresh"] = True
                    st.rerun()
    else:
        st.info("Nessun materiale caricato per questo corso.")

    st.markdown("---")
    st.markdown("#### Carica nuovi materiali")
    files = st.file_uploader(
        "Carica uno o più file (drag & drop)",
        type=["pdf", "docx", "txt", "pptx", "xlsx"],
        accept_multiple_files=True,
        key=f"upload_{corso['id']}",
    )
    tipo_scelto = st.selectbox(
        "Tipo documento (salvato su DB)", ["pdf", "slide", "video", "dispensa", "libro"], key=f"tipo_{corso['id']}"
    )
    if files and st.button("Carica materiali", key=f"do_upload_{corso['id']}"):
        try:
            from src.tools.document_processor import elabora_e_salva_documento as _elabora
        except Exception:
            _elabora = None

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        upload_dir = os.path.join(base_dir, "uploads", str(corso["id"]))
        os.makedirs(upload_dir, exist_ok=True)
        ok = 0
        errori = []
        for f in files:
            disk_path = os.path.join(upload_dir, f.name)
            with open(disk_path, "wb") as out:
                out.write(f.getbuffer())
            f.seek(0)

            if _elabora:
                try:
                    mat_id = _elabora(
                        uploaded_file=f,
                        corso_universitario_id=corso["id"],
                        titolo=f.name,
                        tipo=tipo_scelto,
                    )
                    db.aggiorna(
                        "materiali_didattici",
                        {"id": mat_id},
                        {"s3_key": f"uploads/{corso['id']}/{f.name}"},
                    )
                    ok += 1
                except Exception as e:
                    errori.append(f"{f.name}: {e}")
            else:
                db.inserisci(
                    "materiali_didattici",
                    {
                        "corso_universitario_id": corso["id"],
                        "docente_id": docente_id,
                        "titolo": f.name,
                        "tipo": tipo_scelto,
                        "s3_key": f"uploads/{corso['id']}/{f.name}",
                        "is_processed": 0,
                    },
                )
                ok += 1

        if ok:
            st.success(f"{ok} file caricati e processati per la RAG.")
        for err in errori:
            st.error(f"Errore: {err}")
        st.session_state["_doc_refresh"] = True


def _cancella_contenuto_piano_corso(corso_id: int) -> None:
    piani = db.trova_tutti("piani_personalizzati", {"corso_universitario_id": corso_id, "is_corso_docente": 1})
    if not piani:
        return
    piano_id = piani[0]["id"]
    paragrafi = db.esegui(
        "SELECT pp.id FROM piano_paragrafi pp JOIN piano_capitoli pc ON pp.capitolo_id = pc.id WHERE pc.piano_id = ?",
        [piano_id],
    )
    par_ids = [p["id"] for p in paragrafi]
    if par_ids:
        ph = ",".join("?" * len(par_ids))
        contenuti_quiz = db.esegui(
            f"SELECT quiz_id FROM piano_contenuti WHERE paragrafo_id IN ({ph}) AND quiz_id IS NOT NULL", par_ids
        )
        quiz_ids = [c["quiz_id"] for c in contenuti_quiz if c.get("quiz_id")]
        db.esegui(f"DELETE FROM piano_contenuti WHERE paragrafo_id IN ({ph})", par_ids)
        db.esegui(f"DELETE FROM piano_paragrafi WHERE id IN ({ph})", par_ids)
        if quiz_ids:
            qph = ",".join("?" * len(quiz_ids))
            db.esegui(f"DELETE FROM domande_quiz WHERE quiz_id IN ({qph})", quiz_ids)
            db.esegui(f"DELETE FROM quiz WHERE id IN ({qph})", quiz_ids)
    db.esegui("DELETE FROM piano_capitoli WHERE piano_id = ?", [piano_id])
    db.esegui("DELETE FROM piani_personalizzati WHERE id = ?", [piano_id])


def _salva_contenuti_corso_db(corso_id: int, docente_id: int, schema: List[dict]) -> tuple[bool, str]:
    try:
        _cancella_contenuto_piano_corso(corso_id)

        piano_id = db.inserisci("piani_personalizzati", {
            "studente_id": docente_id,
            "titolo": "Contenuto corso (docente)",
            "descrizione": "",
            "tipo": "corso",
            "corso_universitario_id": corso_id,
            "stato": "attivo",
            "is_corso_docente": 1,
        })

        ordine_cap = 0
        ultimo_paragrafo_id = None

        for blocco in schema:
            tipo = blocco.get("tipo", "capitolo")

            if tipo == "capitolo":
                ordine_cap += 1
                cap_id = db.inserisci("piano_capitoli", {
                    "piano_id": piano_id,
                    "titolo": blocco.get("titolo", ""),
                    "ordine": ordine_cap,
                })
                for p_idx, par in enumerate(blocco.get("paragrafi", [])):
                    par_id = db.inserisci("piano_paragrafi", {
                        "capitolo_id": cap_id,
                        "titolo": par.get("titolo", ""),
                        "ordine": p_idx + 1,
                    })
                    ultimo_paragrafo_id = par_id
                    testo = (par.get("testo") or "").strip()
                    if testo:
                        db.inserisci("piano_contenuti", {
                            "paragrafo_id": par_id,
                            "tipo": "lezione",
                            "contenuto_json": testo,
                        })

            elif tipo == "test" and ultimo_paragrafo_id:
                domande = blocco.get("domande", [])
                if not domande:
                    continue
                quiz_id = db.inserisci("quiz", {
                    "titolo": blocco.get("titolo", "Quiz"),
                    "corso_universitario_id": corso_id,
                    "docente_id": docente_id,
                    "creato_da": "docente",
                    "approvato": 1,
                    "ripetibile": 1,
                })
                for q_idx, dom in enumerate(domande):
                    opzioni = dom.get("opzioni", [])
                    corretta_idx = int(dom.get("corretta", 0))
                    risposta_corretta = opzioni[corretta_idx] if corretta_idx < len(opzioni) else ""
                    db.inserisci("domande_quiz", {
                        "quiz_id": quiz_id,
                        "testo": dom.get("testo", ""),
                        "tipo": "scelta_multipla",
                        "opzioni_json": json.dumps(opzioni, ensure_ascii=False),
                        "risposta_corretta": risposta_corretta,
                        "ordine": q_idx + 1,
                    })
                db.inserisci("piano_contenuti", {
                    "paragrafo_id": ultimo_paragrafo_id,
                    "tipo": "quiz",
                    "quiz_id": quiz_id,
                })

        return True, f"Contenuto salvato: {ordine_cap} capitoli pubblicati."
    except Exception as e:
        return False, f"Errore durante il salvataggio: {e}"


def _init_schema_state(corso_id: int):
    key = f"_schema_{corso_id}"
    if key not in st.session_state:
        st.session_state[key] = []
    return key


def _get_primo_paragrafo_id(corso_id: int, titolo_capitolo: str) -> int:
    try:
        piani = db.trova_tutti(
            "piani_personalizzati",
            {"corso_universitario_id": corso_id, "is_corso_docente": 1},
            ordine="id DESC",
        )
        if not piani:
            return 0
        piano_id = piani[0]["id"]
        capitoli_db = db.trova_tutti("piano_capitoli", {"piano_id": piano_id})
        cap_match = next(
            (c for c in capitoli_db if c["titolo"] == titolo_capitolo),
            capitoli_db[0] if capitoli_db else None,
        )
        if not cap_match:
            return 0
        paragrafi_db = db.trova_tutti("piano_paragrafi", {"capitolo_id": cap_match["id"]})
        return paragrafi_db[0]["id"] if paragrafi_db else 0
    except Exception:
        return 0


def _genera_contenuto_corso(corso: dict, docente_id: int, prompt: str, key: str) -> None:
    try:
        from src.agents.content_gen import crea_agente_content_gen, esegui_generazione
        from src.agents.practice_gen import esegui_generazione_pratica
    except Exception as e:
        st.error(f"Impossibile importare gli agenti AI: {e}")
        return

    with st.spinner("Fase 1/2 — Generazione contenuti teorici…"):
        agente = crea_agente_content_gen()
        argomento = f"{corso['nome']}. {prompt}".strip(". ") if prompt else corso["nome"]
        stato_t = esegui_generazione(
            agente=agente,
            corso_id=corso["id"],
            argomento_richiesto=argomento,
            docente_id=docente_id,
            is_corso_docente=True,
        )

    if stato_t.get("errore"):
        st.error(f"Errore teoria: {stato_t['errore']}")
        return

    struttura = stato_t.get("struttura_corso_generata", {})
    if not struttura or not struttura.get("capitoli"):
        st.error("L'agente non ha prodotto una struttura valida. Verifica che siano presenti materiali RAG.")
        return

    nuovo_schema: list[dict] = []
    chunk_ids = stato_t.get("chunk_ids_utilizzati", [])
    with st.spinner("Fase 2/2 — Generazione quiz di verifica…"):
        for capitolo in struttura["capitoli"]:
            nuovo_schema.append({
                "tipo": "capitolo",
                "titolo": capitolo["titolo"],
                "paragrafi": [
                    {"titolo": p["titolo"], "testo": p["testo"]}
                    for p in capitolo.get("paragrafi", [])
                ],
            })
            testo_cap = "\n\n".join(
                p["testo"] for p in capitolo.get("paragrafi", []) if p.get("testo")
            )
            if not testo_cap:
                continue
            par_id = _get_primo_paragrafo_id(corso["id"], capitolo["titolo"])
            stato_p = esegui_generazione_pratica(
                paragrafo_id=par_id,
                testo_paragrafo=testo_cap,
                strumenti_richiesti=["quiz"],
                studente_id=docente_id,
                corso_universitario_id=corso["id"],
                chunk_ids_utilizzati=chunk_ids,
            )
            quiz_list = stato_p.get("strumenti_generati", {}).get("quiz", [])
            if quiz_list:
                nuovo_schema.append({
                    "tipo": "test",
                    "titolo": f"Test — {capitolo['titolo']}",
                    "domande": [
                        {
                            "testo": d["testo"],
                            "opzioni": d["opzioni"],
                            "corretta": d["indice_corretta"],
                        }
                        for d in quiz_list
                    ],
                })

    st.session_state[key] = nuovo_schema
    st.success("Contenuto corso generato con successo!")
    st.rerun()


def _render_contenuti_ai(corso: dict):
    st.markdown("**Contenuti generati AI (capitoli e test)**")
    st.caption(
        "Premi 'Genera contenuto corso' per produrre teoria e quiz in un solo click. "
        "Poi leggi, modifica i campi, o chiedi a Lea di riscrivere un paragrafo nella chat a destra."
    )
    docente_id = st.session_state.get("current_user_id", 1)
    key = _init_schema_state(corso["id"])
    schema = st.session_state[key]

    ver_key = f"_schema_ver_{corso['id']}"
    if ver_key not in st.session_state:
        st.session_state[ver_key] = 0
    ver = st.session_state[ver_key]

    prompt = st.text_area(
        "Istruzioni per generare la lezione",
        placeholder="Es: Focalizzati su esempi pratici. Usa un linguaggio accessibile agli studenti del primo anno.",
        key=f"prompt_{corso['id']}",
    )
    if st.button("✨ Genera contenuto corso", type="primary", key=f"gen_corso_{corso['id']}"):
        _genera_contenuto_corso(corso, docente_id, prompt, key)

    st.markdown("---")

    idx_to_delete = None
    cap_num = 0
    test_num = 0

    for idx, blocco in enumerate(schema):
        tipo = blocco.get("tipo", "capitolo")

        if tipo == "capitolo":
            cap_num += 1
            col_header, col_del = st.columns([11, 1])
            with col_header:
                st.markdown(f"#### Capitolo {cap_num}")
            with col_del:
                if st.button("🗑️", key=f"del_cap_{corso['id']}_{idx}_{ver}", help="Elimina capitolo"):
                    idx_to_delete = idx

            blocco["titolo"] = st.text_input(
                "Titolo capitolo",
                value=blocco.get("titolo", ""),
                key=f"cap_tit_{corso['id']}_{idx}_{ver}",
            )
            for p_idx, par in enumerate(blocco.get("paragrafi", [])):
                par["titolo"] = st.text_input(
                    f"Titolo paragrafo {p_idx + 1}",
                    value=par.get("titolo", ""),
                    key=f"par_tit_{corso['id']}_{idx}_{p_idx}_{ver}",
                )
                par["testo"] = st.text_area(
                    f"Testo paragrafo {p_idx + 1}",
                    value=par.get("testo", ""),
                    height=220,
                    key=f"par_txt_{corso['id']}_{idx}_{p_idx}_{ver}",
                )

        elif tipo == "test":
            test_num += 1
            col_header, col_del = st.columns([11, 1])
            with col_header:
                st.markdown(f"#### Test {test_num}")
            with col_del:
                if st.button("🗑️", key=f"del_test_{corso['id']}_{idx}_{ver}", help="Elimina set di domande"):
                    idx_to_delete = idx

            blocco["titolo"] = st.text_input(
                "Titolo test",
                value=blocco.get("titolo", ""),
                key=f"test_tit_{corso['id']}_{idx}_{ver}",
            )
            for d_idx, dom in enumerate(blocco.get("domande", [])):
                st.markdown(f"**Domanda {d_idx + 1}**")
                dom["testo"] = st.text_input(
                    "Testo domanda",
                    value=dom.get("testo", ""),
                    key=f"dom_txt_{corso['id']}_{idx}_{d_idx}_{ver}",
                )
                opzioni = dom.get("opzioni", ["", "", "", ""])
                for o_idx, opz in enumerate(opzioni):
                    opzioni[o_idx] = st.text_input(
                        f"Opzione {chr(65 + o_idx)}",
                        value=opz,
                        key=f"opz_{corso['id']}_{idx}_{d_idx}_{o_idx}_{ver}",
                    )
                dom["opzioni"] = opzioni
                dom["corretta"] = st.number_input(
                    "Indice risposta corretta (0 = prima opzione)",
                    min_value=0,
                    max_value=max(0, len(opzioni) - 1),
                    value=int(dom.get("corretta", 0)),
                    step=1,
                    key=f"corr_{corso['id']}_{idx}_{d_idx}_{ver}",
                )
                st.markdown("---")

    if idx_to_delete is not None:
        schema.pop(idx_to_delete)
        st.session_state[key] = schema
        st.session_state[ver_key] = ver + 1
        st.rerun()

    st.markdown("---")

    col_add1, col_add2 = st.columns(2)
    with col_add1:
        if st.button("➕ Aggiungi Capitolo", key=f"add_cap_{corso['id']}"):
            schema.append({
                "tipo": "capitolo",
                "titolo": "Nuovo capitolo",
                "paragrafi": [{"titolo": "Paragrafo 1", "testo": ""}],
            })
            st.session_state[key] = schema
            st.rerun()
    with col_add2:
        if st.button("📝 Aggiungi Test", key=f"add_test_{corso['id']}"):
            schema.append({
                "tipo": "test",
                "titolo": "Nuovo test",
                "domande": [
                    {
                        "testo": "Inserisci una domanda",
                        "opzioni": ["Opzione A", "Opzione B", "Opzione C", "Opzione D"],
                        "corretta": 0,
                    }
                ],
            })
            st.session_state[key] = schema
            st.rerun()

    pubblicato = corso.get("attivo")
    label_salva = "💾 Salva e pubblica contenuti" if pubblicato else "💾 Salva contenuti (bozza)"
    if st.button(label_salva, type="primary", key=f"save_schema_{corso['id']}"):
        ok, msg = _salva_contenuti_corso_db(corso["id"], docente_id, schema)
        if ok:
            if pubblicato:
                st.success(f"{msg} Gli studenti possono ora vedere le lezioni.")
            else:
                st.success(f"{msg} Pubblica il corso per renderlo visibile agli studenti.")
        else:
            st.error(msg)


def _render_dettaglio_corso(corso: dict, docente_id: int):
    stato_lbl, stato_class = _stato_corso(corso)
    title_col, close_col = st.columns([10, 1])
    with title_col:
        st.markdown(
            f"""
            <div style='font-family:"DM Serif Display",serif; font-size:1.2rem; font-weight:400;
                        color:#0D1117; margin:12px 0 4px 0; letter-spacing:-0.02em;'>
                {corso['nome']}
                <span class='status-pill {stato_class}' style='font-size:0.7rem; vertical-align:middle; margin-left:8px;'>{stato_lbl}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with close_col:
        if st.button("✕", key=f"close_course_detail_{corso['id']}", help="Chiudi"):
            st.session_state["_corso_doc_sel"] = None
            st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs(["Panoramica", "Materiali", "Contenuti AI", "Analytics"])

    with tab1:
        st.markdown(
            f"""
            <div class='tab-note'>
                <strong>Descrizione:</strong> {corso.get('descrizione') or '—'}<br>
                <strong>CFU:</strong> {corso.get('cfu') or '—'} &nbsp;·&nbsp;
                <strong>Anno:</strong> {corso.get('anno_di_corso') or '—'} &nbsp;·&nbsp;
                <strong>Livello:</strong> {corso.get('livello') or '—'} &nbsp;·&nbsp;
                <strong>Semestre:</strong> {corso.get('semestre') or '—'}<br>
                <strong>Studenti iscritti:</strong> {_conta_studenti_corso(corso['id'])}
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not corso.get("attivo"):
            st.info("Puoi modificare questo corso finché non viene pubblicato.")
            tutti_cdl = _get_tutti_cdl()
            cdl_correnti_ids = _get_cdl_corso(corso["id"])
            cdl_nomi_tutti = [c["nome"] for c in tutti_cdl]
            cdl_correnti_nomi = [c["nome"] for c in tutti_cdl if c["id"] in cdl_correnti_ids]
            with st.form(f"modifica_corso_{corso['id']}"):
                nome = st.text_input("Nome corso", value=corso.get("nome", ""))
                descrizione = st.text_area("Descrizione", value=corso.get("descrizione", "") or "")
                cfu = st.number_input("CFU", min_value=0, max_value=30, step=1, value=int(corso.get("cfu") or 0))
                anno = st.number_input(
                    "Anno di corso (1-5)", min_value=1, max_value=5, step=1, value=int(corso.get("anno_di_corso") or 1)
                )
                livello = st.selectbox(
                    "Livello", ["base", "intermedio", "avanzato"],
                    index=["base", "intermedio", "avanzato"].index(corso.get("livello") or "base")
                )
                semestre = st.selectbox("Semestre", [1, 2], index=[1, 2].index(corso.get("semestre") or 1))
                cdl_sel = st.multiselect("Corsi di Laurea", cdl_nomi_tutti, default=cdl_correnti_nomi)
                if st.form_submit_button("Aggiorna bozza", type="primary"):
                    db.aggiorna(
                        "corsi_universitari",
                        {"id": corso["id"]},
                        {"nome": nome, "descrizione": descrizione, "cfu": cfu,
                         "anno_di_corso": anno, "livello": livello, "semestre": semestre},
                    )
                    cdl_sel_ids = [c["id"] for c in tutti_cdl if c["nome"] in cdl_sel]
                    _salva_cdl_corso(corso["id"], cdl_sel_ids)
                    st.success("Bozza aggiornata.")
                    st.session_state["_doc_refresh"] = True

    with tab2:
        _render_materiali(corso, docente_id)

    with tab3:
        _render_contenuti_ai(corso)

    with tab4:
        dati = _metrics(docente_id, corso["id"])
        col1, col2, col3 = st.columns(3)
        for col, label, val, icon in [
            (col1, "Studenti unici", dati["studenti"], "👥"),
            (col2, "Quiz pubblicati", dati["quiz"], "✅"),
            (col3, "Tentativi quiz", dati["tentativi"], "📊"),
        ]:
            with col:
                st.markdown(
                    f"""<div class='metric-box'>
                        <span class='metric-icon'>{icon}</span>
                        <div class='metric-label'>{label}</div>
                        <div class='metric-value'>{val}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
        st.caption("Drill-down per capitolo/argomento verrà aggiunto dopo la raccolta dati.")


def _render_corsi(docente_id: int):
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">I tuoi corsi</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Gestisci bozze, pubblicazioni e materiali didattici.</div>', unsafe_allow_html=True)

    feedback = st.session_state.pop("_doc_create_feedback", None)
    if feedback:
        st.success(feedback)

    if st.button("＋ Crea nuovo corso", type="primary"):
        st.session_state["_doc_show_create"] = True
    if st.session_state.get("_doc_show_create"):
        _dialog_crea_corso(docente_id)

    corsi = _get_corsi_docente(docente_id)
    if not corsi:
        st.info("Nessun corso presente. Crea il primo corso per iniziare.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    for corso in corsi:
        stato_lbl, stato_class = _stato_corso(corso)
        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown(
                f"""
                <div class='course-card'>
                    <div class='title'>{corso['nome']}</div>
                    <div class='meta'>
                        <span class='status-pill {stato_class}'>{stato_lbl}</span>
                        <span class='chip'>CFU {corso.get('cfu') or '—'}</span>
                        <span class='chip'>Anno {corso.get('anno_di_corso') or '—'}</span>
                        <span class='chip'>{corso.get('livello') or '—'}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            c_a, c_b, c_c = st.columns(3)
            with c_a:
                if st.button("Apri", key=f"apri_{corso['id']}"):
                    st.session_state["_corso_doc_sel"] = corso["id"]
            with c_b:
                if corso.get("attivo"):
                    if st.button("Disattiva", key=f"dis_{corso['id']}"):
                        db.aggiorna("corsi_universitari", {"id": corso["id"]}, {"attivo": 0})
                        st.session_state["_doc_refresh"] = True
                        st.rerun()
                else:
                    if st.button("Pubblica", key=f"pub_{corso['id']}"):
                        db.aggiorna("corsi_universitari", {"id": corso["id"]}, {"attivo": 1})
                        st.session_state["_doc_refresh"] = True
                        st.rerun()
            with c_c:
                if st.button("Elimina", key=f"del_{corso['id']}"):
                    st.session_state["_doc_delete_confirm"] = corso["id"]
        st.markdown("<hr style='border:none;border-top:1px solid rgba(196,205,217,0.4);margin:4px 0'>", unsafe_allow_html=True)

    if st.session_state.get("_doc_delete_confirm"):
        _dialog_elimina_corso(st.session_state["_doc_delete_confirm"])

    sel_id = st.session_state.get("_corso_doc_sel")
    if sel_id:
        corso_sel = next((c for c in corsi if c["id"] == sel_id), None)
        if corso_sel:
            _render_dettaglio_corso(corso_sel, docente_id)
    else:
        st.caption("Seleziona un corso per caricare materiale didattico o generare contenuti.")

    st.markdown("</div>", unsafe_allow_html=True)


def _render_chatbot_docente(utente: dict, corso_id: int | None, corso_nome: str | None):
    chat_con_orchestratore, aggiorna_contesto, _ = _import_orchestratore()
    st.markdown(
        """
        <div class="chat-header">
            <div class="chat-header-inner">
                <div class="chat-avatar">🤖</div>
                <div>
                    <div class="chat-title">Lea — Tutor AI</div>
                    <div class="chat-sub">Supporto ai docenti</div>
                </div>
                <div class="chat-online"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if "chat_history_doc" not in st.session_state:
        st.session_state["chat_history_doc"] = [
            {"role": "assistant", "content": f"Ciao {utente.get('nome','')}! Sono Lea. Posso aiutarti a creare materiali, quiz e monitorare i corsi."}
        ]
    chat_html = '<div class="chat-container" id="chat-box">'
    for msg in st.session_state["chat_history_doc"]:
        if msg["role"] == "user":
            testo_safe = msg["content"].replace("<", "&lt;").replace(">", "&gt;")
            chat_html += f'<div class="msg-user">{testo_safe}</div>'
        else:
            import re as _re
            contenuto = msg["content"].replace("<", "&lt;").replace(">", "&gt;")
            contenuto = _re.sub(r"\*\*(.*?)\*\*", r"<strong>\\1</strong>", contenuto)
            contenuto = contenuto.replace("\n", "<br>")
            chat_html += f'<div class="msg-ai">{contenuto}</div>'
    chat_html += "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)

    suggerimenti = [("📄", "Genera una lezione"), ("✅", "Crea un quiz"), ("🧠", "Crea flashcard")]
    messaggio_da_suggerimento = None
    cols = st.columns(len(suggerimenti))
    for idx, (icona, testo) in enumerate(suggerimenti):
        with cols[idx]:
            st.markdown('<div class="sug-btn">', unsafe_allow_html=True)
            if st.button(f"{icona} {testo}", key=f"sug_doc_{idx}"):
                target = corso_nome or "il tuo corso"
                messaggio_da_suggerimento = f"{testo} per {target}"
            st.markdown("</div>", unsafe_allow_html=True)

    with st.form("lea_doc_form", clear_on_submit=True):
        input_col, send_col = st.columns([5, 1], vertical_alignment="bottom")
        with input_col:
            user_input = st.text_input(
                "Chiedi a Lea...",
                key="lea_doc_input_text",
                placeholder="Scrivi un messaggio a Lea…",
                label_visibility="collapsed",
            )
        with send_col:
            invia = st.form_submit_button("→", type="primary", use_container_width=True)

    messaggio_finale = messaggio_da_suggerimento or ((user_input or "").strip() if invia else None)
    if messaggio_finale:
        st.session_state["chat_history_doc"].append({"role": "user", "content": messaggio_finale})
        risposta = "Lea non è configurata (AWS Bedrock non attivo)."
        if chat_con_orchestratore and aggiorna_contesto:
            try:
                if corso_id:
                    aggiorna_contesto(corso_id=corso_id, corso_nome=corso_nome, tipo_vista="docente", piano_id=None, piano_titolo=None)
                risposta = chat_con_orchestratore(
                    messaggio_utente=messaggio_finale,
                    corso_contestuale_id=corso_id,
                    corso_contestuale_nome=corso_nome,
                )
            except Exception as e:
                risposta = f"Errore: {str(e)[:120]}"
        st.session_state["chat_history_doc"].append({"role": "assistant", "content": risposta})
        st.rerun()


def mostra_homepage_docente():
    utente = st.session_state.user
    docente_id = st.session_state.current_user_id
    if _render_topbar(utente):
        return
    col_main, col_chat = st.columns([4, 2.5], gap="medium")
    corsi = _get_corsi_docente(docente_id)
    with col_main:
        _render_analytics(docente_id, corsi)
        _render_corsi(docente_id)
    with col_chat:
        corso_nome = None
        sel_id = st.session_state.get("_corso_doc_sel")
        if sel_id:
            corso_sel = next((c for c in corsi if c["id"] == sel_id), None)
            if corso_sel:
                corso_nome = corso_sel["nome"]
        _render_chatbot_docente(utente, sel_id, corso_nome)
    if st.session_state.get("_doc_refresh"):
        st.session_state["_doc_refresh"] = False
        st.rerun()


if __name__ == "__main__":
    mostra_homepage_docente()