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
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Source+Sans+3:wght@300;400;600&display=swap');
:root { --blue:#003087; --blue-dark:#001A4D; --blue-mid:#1351A8; --red:#C8102E; --gold:#C5A028; --light:#F0F4F8; --gray:#5A6A7E; --border:#C8D5E3; --white:#FFFFFF; --green:#1A7F4B; --card:#f8fafc; --input-bg:#f8fafc; --input-text:#1f2937; --placeholder:#4b5563; }
.stApp { background:#F0F4F8 !important; font-family:'Source Sans 3',sans-serif !important; }
#MainMenu, footer { visibility:hidden; }
.block-container { padding-top:0 !important; padding-bottom:0 !important; }
.topbar { background:linear-gradient(135deg,#001A4D 0%,#003087 60%,#1351A8 100%); border-bottom:3px solid #C5A028; padding:14px 32px; display:flex; align-items:center; justify-content:space-between; margin:-1rem -1rem 24px -1rem; }
.topbar-brand { font-family:'Playfair Display',serif; color:#fff; font-size:1.25rem; font-weight:700; }
.topbar-brand span { color:#C5A028; }
.topbar-user { color:rgba(255,255,255,0.85); font-size:0.88rem; display:flex; align-items:center; gap:12px; }
.topbar-avatar { width:34px; height:34px; border-radius:50%; background:#C5A028; color:#001A4D; font-weight:700; font-size:0.85rem; display:inline-flex; align-items:center; justify-content:center; }
.section-card { background:var(--card); border-radius:12px; padding:18px 20px; margin-bottom:18px; box-shadow:0 4px 18px rgba(0,48,135,0.08); border:1px solid #E3EAF3; }
.section-title { font-family:'Playfair Display',serif; font-size:1.35rem; color:#001A4D; margin:0 0 8px 0; font-weight:700; }
.section-sub { color:#5A6A7E; font-size:0.90rem; margin-bottom:12px; }
.metric-box { background:linear-gradient(135deg,#EEF4FF 0%,#F7FAFF 100%); border:1px solid #D6E0F0; border-radius:12px; padding:14px 16px; box-shadow:inset 0 1px 0 rgba(255,255,255,0.6); }
.metric-label { color:#5A6A7E; font-size:0.82rem; margin-bottom:4px; }
.metric-value { color:#001A4D; font-size:1.4rem; font-weight:700; }
.course-card { background:var(--card); border-radius:12px; padding:14px 16px; border-left:4px solid #C8D5E3; box-shadow:0 2px 10px rgba(0,48,135,0.07); margin-bottom:10px; }
.course-card .title { font-weight:700; color:#001A4D; margin:0; }
.course-card .meta { color:#5A6A7E; font-size:0.82rem; }
.status-pill { display:inline-block; font-size:0.72rem; font-weight:700; padding:4px 10px; border-radius:999px; text-transform:uppercase; letter-spacing:0.4px; }
.pill-pub { background:#E6F9F0; color:#1A7F4B; }
.pill-bozza { background:#FFF6E0; color:#8A6800; }
.chip { display:inline-block; background:#EEF4FF; color:#003087; padding:3px 9px; border-radius:10px; font-size:0.75rem; font-weight:700; margin-right:6px; }
.tab-note { background:#F8FAFD; border:1px solid #E3EAF3; border-radius:10px; padding:10px 12px; color:#5A6A7E; font-size:0.85rem; }
.upload-box { border:1.5px dashed #C8D5E3; border-radius:12px; padding:16px; background:var(--card); }
.chat-header { background:linear-gradient(135deg,#001A4D 0%,#003087 100%); color:#fff; padding:14px 18px; border-radius:12px 12px 0 0; display:flex; align-items:center; gap:10px; margin-bottom:0; }
.chat-online { width:8px; height:8px; border-radius:50%; background:#4FE886; flex-shrink:0; }
.chat-title { font-weight:700; font-size:0.95rem; }
.chat-sub { font-size:0.75rem; opacity:0.75; }
.chat-container { background:#fff; border:1px solid #C8D5E3; border-top:none; border-radius:0 0 12px 12px; height:420px; overflow-y:auto; padding:16px; display:flex; flex-direction:column; gap:10px; }
.msg-user { background:#003087; color:#fff; border-radius:14px 14px 4px 14px; padding:10px 14px; font-size:0.87rem; max-width:82%; align-self:flex-end; line-height:1.5; }
.msg-ai { background:#F0F4F8; color:#1A2535; border-radius:4px 14px 14px 14px; padding:10px 14px; font-size:0.87rem; max-width:88%; align-self:flex-start; line-height:1.55; border:1px solid #E0E8F2; }

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
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child {
    position: -webkit-sticky;
    position: sticky;
    top: 2rem;
    align-self: start;
    z-index: 99;
}
div[data-testid="stVerticalBlock"] {
    overflow: visible !important;
}

/* ---- CHAT INPUT NATIVO ---- */
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
        WHERE cu.docente_id = ?""" + filtri
    )
    tentativi = one(
        """
        SELECT COUNT(*) AS n
        FROM tentativi_quiz t
        JOIN quiz q ON q.id = t.quiz_id
        JOIN corsi_universitari cu ON cu.id = q.corso_universitario_id
        WHERE cu.docente_id = ?""" + filtri
    )
    corsi = one("SELECT COUNT(*) AS n FROM corsi_universitari cu WHERE cu.docente_id = ?" + filtri)

    return {"studenti": studenti, "quiz": quiz_appr, "tentativi": tentativi, "corsi": corsi}


def _stato_corso(corso: dict) -> tuple[str, str]:
    return ("Pubblicato", "pill-pub") if corso.get("attivo") else ("Da pubblicare", "pill-bozza")


def _render_topbar(utente: dict) -> bool:
    st.markdown(_CSS, unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class='topbar'>
            <div class='topbar-brand'>LearnAI <span>Docente</span></div>
            <div class='topbar-user'>
                <div class='topbar-avatar'>{(utente.get('nome','')[:1] or '?').upper()}</div>
                <div>
                    <div>{utente.get('nome','')} {utente.get('cognome','')}</div>
                    <div style='font-size:0.78rem; opacity:0.8'>Docente</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col_logout, _ = st.columns([1, 5])
    with col_logout:
        if st.button("Logout", type="secondary"):
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
    import json as _json

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Analytics</div>', unsafe_allow_html=True)

    if not corsi:
        st.info("Carica almeno un corso per vedere le analytics.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    scope_options = ["Generale"] + [f"Corso: {c['nome']} (ID {c['id']})" for c in corsi]
    scelta = st.selectbox("Ambito analytics", scope_options, key="analytics_scope")
    corso_sel_id = None
    corso_sel_nome = None
    if scelta.startswith("Corso:"):
        label_to_id = {f"Corso: {c['nome']} (ID {c['id']})": c["id"] for c in corsi}
        label_to_nome = {f"Corso: {c['nome']} (ID {c['id']})": c["nome"] for c in corsi}
        corso_sel_id = label_to_id.get(scelta)
        corso_sel_nome = label_to_nome.get(scelta)
    # Salva in session state per renderlo disponibile al chatbot
    st.session_state["_analytics_corso_id"] = corso_sel_id
    st.session_state["_analytics_corso_nome"] = corso_sel_nome

    filtro = " AND cu.id = ?" if corso_sel_id else ""
    p = [docente_id] + ([corso_sel_id] if corso_sel_id else [])

    dati = _metrics(docente_id, corso_sel_id)

    # --- Calcola metriche aggiuntive ---
    riga_media = db.esegui(
        "SELECT AVG(t.punteggio) AS media, "
        "COUNT(CASE WHEN t.punteggio >= 60 THEN 1 END) * 100.0 / MAX(COUNT(*), 1) AS tasso "
        "FROM tentativi_quiz t "
        "JOIN quiz q ON q.id = t.quiz_id "
        "JOIN corsi_universitari cu ON cu.id = q.corso_universitario_id "
        "WHERE cu.docente_id = ?" + filtro, p
    )
    media_globale = round(riga_media[0]["media"] or 0, 1) if riga_media else 0
    tasso_sup = round(riga_media[0]["tasso"] or 0, 1) if riga_media else 0

    colore_media = "#1A7F4B" if media_globale >= 70 else ("#C5A028" if media_globale >= 50 else "#C8102E")
    colore_tasso = "#1A7F4B" if tasso_sup >= 70 else ("#C5A028" if tasso_sup >= 50 else "#C8102E")

    # --- KPI cards ---
    col_a, col_b, col_c, col_d = st.columns(4)
    for col, label, val, color in [
        (col_a, "Studenti unici", dati["studenti"], "#001A4D"),
        (col_b, "Punteggio medio", f"{media_globale}/100", colore_media),
        (col_c, "Tasso superamento", f"{tasso_sup}%", colore_tasso),
        (col_d, "Tentativi quiz", dati["tentativi"], "#001A4D"),
    ]:
        with col:
            st.markdown(
                f"""<div class='metric-box'>
                    <div class='metric-label'>{label}</div>
                    <div class='metric-value' style='color:{color}'>{val}</div>
                </div>""",
                unsafe_allow_html=True,
            )

    if not dati["tentativi"]:
        st.info("Nessuna risposta ai quiz registrata ancora.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    st.markdown("---")

    # --- Riga 1: Punteggio medio per corso + Distribuzione punteggi ---
    col1, col2 = st.columns([3, 2])

    with col1:
        righe_media_corso = db.esegui(
            "SELECT cu.nome AS corso, ROUND(AVG(t.punteggio),1) AS media, COUNT(t.id) AS n "
            "FROM tentativi_quiz t "
            "JOIN quiz q ON q.id = t.quiz_id "
            "JOIN corsi_universitari cu ON cu.id = q.corso_universitario_id "
            "WHERE cu.docente_id = ?" + filtro +
            " GROUP BY cu.id, cu.nome ORDER BY media DESC", p
        )
        if righe_media_corso:
            serie_mc = [{"Corso": r["corso"], "Punteggio medio": r["media"], "Tentativi": r["n"]}
                        for r in righe_media_corso]
            fig_mc = px.bar(
                serie_mc, x="Corso", y="Punteggio medio",
                title="Punteggio medio per corso",
                color="Punteggio medio",
                color_continuous_scale=["#C8102E", "#C5A028", "#1A7F4B"],
                range_color=[0, 100],
                text="Punteggio medio",
            )
            fig_mc.update_traces(texttemplate="%{text:.0f}", textposition="outside")
            fig_mc.update_layout(height=320, margin=dict(t=50, b=20, l=10, r=10),
                                 yaxis=dict(range=[0, 110]), showlegend=False)
            st.plotly_chart(fig_mc, use_container_width=True)

    with col2:
        righe_dist = db.esegui(
            "SELECT t.punteggio FROM tentativi_quiz t "
            "JOIN quiz q ON q.id = t.quiz_id "
            "JOIN corsi_universitari cu ON cu.id = q.corso_universitario_id "
            "WHERE cu.docente_id = ?" + filtro, p
        )
        if righe_dist:
            punteggi = [r["punteggio"] for r in righe_dist if r["punteggio"] is not None]
            fig_dist = px.histogram(
                punteggi, nbins=10, range_x=[0, 100],
                title="Distribuzione punteggi",
                labels={"value": "Punteggio", "count": "Tentativi"},
                color_discrete_sequence=["#003087"],
            )
            fig_dist.update_layout(height=320, margin=dict(t=50, b=20, l=10, r=10),
                                   showlegend=False, bargap=0.05)
            st.plotly_chart(fig_dist, use_container_width=True)

    # --- Riga 2: Argomenti difficili + Domande più sbagliate ---
    col3, col4 = st.columns(2)

    with col3:
        righe_gap = db.esegui(
            "SELECT mc.argomenti_chiave "
            "FROM risposte_domande rd "
            "JOIN domande_quiz dq ON rd.domanda_id = dq.id "
            "JOIN materiali_chunks mc ON dq.chunk_id = mc.id "
            "JOIN quiz q ON dq.quiz_id = q.id "
            "JOIN corsi_universitari cu ON q.corso_universitario_id = cu.id "
            "WHERE cu.docente_id = ? AND rd.corretta = 0 AND mc.argomenti_chiave IS NOT NULL"
            + filtro, p
        )
        conteggio: dict[str, int] = {}
        for r in righe_gap:
            try:
                for a in _json.loads(r["argomenti_chiave"]):
                    conteggio[a] = conteggio.get(a, 0) + 1
            except Exception:
                pass
        if conteggio:
            serie_gap = sorted(
                [{"Argomento": k, "Errori": v} for k, v in conteggio.items()],
                key=lambda x: x["Errori"], reverse=True,
            )[:12]
            fig_gap = px.bar(
                serie_gap, x="Errori", y="Argomento", orientation="h",
                title="Argomenti con più errori",
                color="Errori", color_continuous_scale="Reds",
            )
            fig_gap.update_layout(height=400, margin=dict(t=50, b=20, l=10, r=10), showlegend=False)
            st.plotly_chart(fig_gap, use_container_width=True)
        else:
            st.info("Nessun dato sugli argomenti (i quiz potrebbero non avere chunk collegati).")

    with col4:
        righe_dom = db.esegui(
            "SELECT dq.testo, "
            "COUNT(*) AS tot, "
            "SUM(CASE WHEN rd.corretta=0 THEN 1 ELSE 0 END) AS errate, "
            "ROUND(SUM(CASE WHEN rd.corretta=0 THEN 1 ELSE 0 END)*100.0/COUNT(*),0) AS pct_errore "
            "FROM risposte_domande rd "
            "JOIN domande_quiz dq ON rd.domanda_id = dq.id "
            "JOIN quiz q ON dq.quiz_id = q.id "
            "JOIN corsi_universitari cu ON q.corso_universitario_id = cu.id "
            "WHERE cu.docente_id = ?" + filtro +
            " GROUP BY dq.id HAVING errate > 0 ORDER BY pct_errore DESC LIMIT 10", p
        )
        if righe_dom:
            st.markdown("**Domande più difficili (% errori)**")
            for r in righe_dom:
                testo = (r["testo"] or "")[:80] + ("…" if len(r["testo"] or "") > 80 else "")
                pct = int(r["pct_errore"] or 0)
                color = "#C8102E" if pct >= 70 else ("#C5A028" if pct >= 40 else "#1A7F4B")
                st.markdown(
                    f'<div style="border-left:3px solid {color};padding:6px 10px;margin-bottom:6px;'
                    f'background:#fafafa;border-radius:4px;font-size:0.82rem;">'
                    f'<span style="color:{color};font-weight:700">{pct}% errori</span> — {testo}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("Nessuna domanda con errori registrata.")

    # --- Riga 3: Studenti a rischio ---
    righe_rischio = db.esegui(
        "SELECT u.nome || ' ' || u.cognome AS studente, "
        "ROUND(AVG(t.punteggio),1) AS media, COUNT(t.id) AS tentativi "
        "FROM tentativi_quiz t "
        "JOIN quiz q ON q.id = t.quiz_id "
        "JOIN corsi_universitari cu ON cu.id = q.corso_universitario_id "
        "JOIN users u ON u.id = t.studente_id "
        "WHERE cu.docente_id = ?" + filtro +
        " GROUP BY t.studente_id HAVING media < 60 ORDER BY media ASC LIMIT 10", p
    )
    if righe_rischio:
        st.markdown("---")
        st.markdown("**⚠️ Studenti a rischio** *(punteggio medio < 60)*")
        for r in righe_rischio:
            media_s = r["media"] or 0
            colore_s = "#C8102E" if media_s < 40 else "#C5A028"
            st.markdown(
                f'<div style="border-left:3px solid {colore_s};padding:6px 10px;margin-bottom:6px;'
                f'background:#fafafa;border-radius:4px;font-size:0.85rem;">'
                f'<b>{r["studente"]}</b> — media <span style="color:{colore_s};font-weight:700">'
                f'{media_s}/100</span> su {r["tentativi"]} tentativo/i</div>',
                unsafe_allow_html=True,
            )

    st.markdown('</div>', unsafe_allow_html=True)


def _dialog_crea_corso(docente_id: int):
    header_col, close_col = st.columns([10, 1])
    with header_col:
        st.markdown("#### Nuovo corso")
    with close_col:
        if st.button("X", key="close_create_course", help="Chiudi"):
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


def _elimina_corso_completo(corso_id: int) -> None:
    """Elimina un corso e TUTTI i record dipendenti nell'ordine corretto."""

    # 1. Elimina contenuto piani docente (capitoli, paragrafi, contenuti, quiz interni)
    _cancella_contenuto_piano_corso(corso_id)

    # 2. Elimina piano_materiali_utilizzati per chunk di questo corso
    chunk_ids_rows = db.esegui(
        "SELECT id FROM materiali_chunks WHERE corso_universitario_id = ?", [corso_id]
    )
    chunk_ids = [r["id"] for r in chunk_ids_rows]
    if chunk_ids:
        ph = ",".join("?" * len(chunk_ids))
        db.esegui(f"DELETE FROM piano_materiali_utilizzati WHERE chunk_id IN ({ph})", chunk_ids)

    # 3. Elimina catena quiz: risposte → tentativi → domande → quiz
    quiz_ids_rows = db.esegui(
        "SELECT id FROM quiz WHERE corso_universitario_id = ?", [corso_id]
    )
    quiz_ids = [r["id"] for r in quiz_ids_rows]
    if quiz_ids:
        qph = ",".join("?" * len(quiz_ids))
        domande_ids_rows = db.esegui(
            f"SELECT id FROM domande_quiz WHERE quiz_id IN ({qph})", quiz_ids
        )
        domande_ids = [r["id"] for r in domande_ids_rows]
        if domande_ids:
            dph = ",".join("?" * len(domande_ids))
            db.esegui(f"DELETE FROM risposte_domande WHERE domanda_id IN ({dph})", domande_ids)
        db.esegui(f"DELETE FROM tentativi_quiz WHERE quiz_id IN ({qph})", quiz_ids)
        db.esegui(f"DELETE FROM domande_quiz WHERE quiz_id IN ({qph})", quiz_ids)
        db.esegui(f"DELETE FROM quiz WHERE id IN ({qph})", quiz_ids)

    # 4. Elimina lezioni del corso
    db.esegui("DELETE FROM lezioni_corso WHERE corso_universitario_id = ?", [corso_id])

    # 5. Elimina materiali: chunks → didattici (+ file fisici)
    materiali = db.esegui(
        "SELECT id, s3_key FROM materiali_didattici WHERE corso_universitario_id = ?", [corso_id]
    )
    if chunk_ids:
        ph = ",".join("?" * len(chunk_ids))
        db.esegui(f"DELETE FROM materiali_chunks WHERE id IN ({ph})", chunk_ids)
    for m in materiali:
        db.elimina("materiali_didattici", {"id": m["id"]})
        if m.get("s3_key"):
            try:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                file_path = os.path.join(base_dir, m["s3_key"])
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception:
                pass

    # 6. Elimina iscrizioni studenti
    db.esegui("DELETE FROM studenti_corsi WHERE corso_universitario_id = ?", [corso_id])

    # 7. Elimina il corso (corsi_laurea_universitari CASCADE, piani SET NULL automatici)
    db.elimina("corsi_universitari", {"id": corso_id})


def _dialog_elimina_corso(corso_id: int):
    st.warning("Eliminerai definitivamente il corso e i relativi materiali.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Annulla"):
            st.session_state["_doc_delete_confirm"] = None
    with c2:
        if st.button("Elimina", type="primary"):
            try:
                _elimina_corso_completo(corso_id)
                st.session_state["_doc_refresh"] = True
                st.session_state["_corso_doc_sel"] = None
                st.session_state["_doc_delete_confirm"] = None
                st.success("Corso eliminato.")
                st.rerun()
            except Exception as e:
                st.error(f"Impossibile eliminare: {e}")


def _elimina_materiale(materiale_id: int, s3_key: str | None) -> None:
    """Elimina un materiale didattico, i suoi chunk e il file fisico dal disco."""
    # 1. Elimina i chunk associati
    try:
        db.elimina("materiali_chunks", {"materiale_id": materiale_id})
    except Exception:
        pass
    # 2. Elimina il record dal DB
    db.elimina("materiali_didattici", {"id": materiale_id})
    # 3. Elimina il file fisico (se presente)
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

    # Mostra errori di upload salvati in session_state (persistono dopo il rerun)
    errori_chiave = f"_upload_errori_{corso['id']}"
    errori_salvati: list[tuple[str, str]] = st.session_state.pop(errori_chiave, [])
    for nome_file, msg_errore in errori_salvati:
        with st.expander(f"❌ Errore caricamento — {nome_file}", expanded=True):
            st.error(msg_errore)
            if any(kw in msg_errore for kw in ("testo leggibile", "scansione", "immagini")):
                st.info(
                    "**Possibili cause:**\n"
                    "- Il PDF contiene solo immagini/scansioni (nessun testo selezionabile)\n"
                    "- Il file è protetto da password\n"
                    "- Il file è corrotto o non valido\n\n"
                    "**Soluzione:** converti il PDF in testo selezionabile con un tool OCR prima di caricarlo."
                )

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
        _elabora = None
        _import_err = None
        try:
            from src.tools.document_processor import elabora_e_salva_documento as _elabora
        except Exception as _ie:
            _import_err = _ie

        if _import_err:
            st.error(
                f"**Impossibile caricare il modulo di elaborazione documenti.**\n\n"
                f"Dettaglio tecnico: `{_import_err}`\n\n"
                "Controlla che tutte le dipendenze siano installate (`pip install -r requirements.txt`)."
            )
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            upload_dir = os.path.join(base_dir, "uploads", str(corso["id"]))
            os.makedirs(upload_dir, exist_ok=True)
            ok = 0
            errori: list[tuple[str, str]] = []

            for f_idx, f in enumerate(files):
                progress_bar = st.progress(0, text=f"Elaborazione di **{f.name}**…")
                def _aggiorna_progresso_doc(i, totale, _pb=progress_bar):
                    pct = int((i + 1) / totale * 100)
                    _pb.progress(pct, text=f"Analisi sezione {i + 1}/{totale}...")
                # Salva il file fisico sul disco
                disk_path = os.path.join(upload_dir, f.name)
                with open(disk_path, "wb") as out:
                    out.write(f.getbuffer())
                f.seek(0)

                try:
                    mat_id = _elabora(
                        uploaded_file=f,
                        corso_universitario_id=corso["id"],
                        titolo=f.name,
                        tipo=tipo_scelto,
                        progress_callback=_aggiorna_progresso_doc,
                    )
                    progress_bar.progress(100, text=f"✅ {f.name} completato!")
                    db.aggiorna(
                        "materiali_didattici",
                        {"id": mat_id},
                        {"s3_key": f"uploads/{corso['id']}/{f.name}"},
                    )
                    ok += 1
                except ValueError as e:
                    # Errori prevedibili (es. file senza testo leggibile)
                    errori.append((f.name, str(e)))
                except Exception as e:
                    # Errori imprevisti — mostra tipo eccezione per diagnosi
                    errori.append((f.name, f"{type(e).__name__}: {e}"))

            if ok:
                st.session_state["_doc_refresh"] = True

            if errori:
                st.session_state[f"_upload_errori_{corso['id']}"] = errori

            # Rerun sempre: su successo aggiorna la lista materiali,
            # su errore porta gli errori in cima alla sezione via session_state
            st.rerun()


def _cancella_contenuto_piano_corso(corso_id: int) -> None:
    """Elimina TUTTI i piani docente esistenti (is_corso_docente=1) e il loro contenuto."""
    piani = db.trova_tutti("piani_personalizzati", {"corso_universitario_id": corso_id, "is_corso_docente": 1})
    if not piani:
        return
    for piano in piani:
        piano_id = piano["id"]
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
    """Salva lo schema (capitoli + test) nel DB come contenuto ufficiale del corso."""
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
    """Recupera l'ID del primo paragrafo DB per un capitolo appena salvato da content_gen."""
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


def _genera_contenuto_corso(corso: dict, docente_id: int, prompt: str, key: str, forza_keyword: bool = False) -> None:
    """Invoca agente teorico e agente pratico in sequenza, poi aggiorna lo stato UI."""
    try:
        from src.agents.content_gen import crea_agente_content_gen, esegui_generazione
        from src.agents.practice_gen import esegui_generazione_pratica
    except Exception as e:
        st.error(f"Impossibile importare gli agenti AI: {e}")
        return

    # Determina se il docente ha richiesto di NON generare quiz
    _prompt_lower = (prompt or "").lower()
    _senza_quiz = any(kw in _prompt_lower for kw in ("senza quiz", "no quiz", "without quiz", "nessun quiz", "non generare quiz"))

    # — Fase 1: Teoria —
    _fasi = "Fase 1/2" if not _senza_quiz else "Fase 1/1"
    _label = f"{_fasi} — Generazione contenuti teorici"
    if forza_keyword:
        _label += " (ricerca per parole chiave)"
    _label += "…"
    with st.spinner(_label):
        agente = crea_agente_content_gen()
        stato_t = esegui_generazione(
            agente=agente,
            corso_id=corso["id"],
            argomento_richiesto=corso["nome"],
            docente_id=docente_id,
            is_corso_docente=True,
            istruzioni_utente=prompt or "",
            forza_keyword=forza_keyword,
        )

    if stato_t.get("errore"):
        errore = stato_t["errore"]

        # Gestione speciale: ricerca semantica fallita → salva stato per chiedere consenso
        if errore.startswith("RICERCA_SEMANTICA_FALLITA|"):
            motivo = errore.split("|", 1)[1]
            # Salva in session_state per mostrare il prompt di fallback nella UI
            st.session_state[f"_sem_fallita_{corso['id']}"] = {
                "motivo": motivo,
                "prompt": prompt,
                "key": key,
            }
            st.rerun()
            return

        st.error(f"Errore teoria: {errore}")
        return

    struttura = stato_t.get("struttura_corso_generata", {})
    if not struttura or not struttura.get("capitoli"):
        st.error("L'agente non ha prodotto una struttura valida. Verifica che siano presenti materiali RAG.")
        return

    # — Fase 2: Quiz per ogni capitolo (saltata se il docente ha richiesto "senza quiz") —
    nuovo_schema: list[dict] = []
    chunk_ids = stato_t.get("chunk_ids_utilizzati", [])

    if _senza_quiz:
        for capitolo in struttura["capitoli"]:
            nuovo_schema.append({
                "tipo": "capitolo",
                "titolo": capitolo["titolo"],
                "paragrafi": [
                    {"titolo": p["titolo"], "testo": p["testo"]}
                    for p in capitolo.get("paragrafi", [])
                ],
            })
    else:
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

    # — Fase 3: Aggiornamento UI —
    st.session_state[key] = nuovo_schema
    st.success("Contenuto corso generato con successo!")
    st.rerun()


def _render_anteprima_lezione(corso_id: int) -> None:
    """Mostra il contenuto del corso salvato nel DB come lo vedrebbe uno studente."""
    try:
        piani = db.trova_tutti(
            "piani_personalizzati",
            {"corso_universitario_id": corso_id, "is_corso_docente": 1},
            ordine="id DESC",
            limite=1,
        )
    except Exception:
        return

    if not piani:
        return

    piano_id = piani[0]["id"]

    try:
        capitoli = db.esegui(
            "SELECT id, titolo FROM piano_capitoli WHERE piano_id = ? ORDER BY ordine",
            [piano_id],
        )
    except Exception:
        return

    if not capitoli:
        st.info("Nessun contenuto salvato ancora. Vai in 'Contenuti AI', genera e salva la lezione.")
        return

    st.caption("Vista studente — anteprima del contenuto salvato.")
    for cap in capitoli:
        st.markdown(f"### {cap['titolo']}")
        try:
            paragrafi = db.esegui(
                "SELECT id, titolo FROM piano_paragrafi WHERE capitolo_id = ? ORDER BY ordine",
                [cap["id"]],
            )
        except Exception:
            continue

        for par in paragrafi:
            st.markdown(f"**{par['titolo']}**")
            try:
                contenuto = db.trova_uno(
                    "piano_contenuti", {"paragrafo_id": par["id"], "tipo": "lezione"}
                )
            except Exception:
                contenuto = None

            if contenuto and contenuto.get("contenuto_json"):
                st.markdown(
                    f"<div style='background:#f8fafc;border-left:3px solid #003087;"
                    f"padding:12px 16px;border-radius:0 8px 8px 0;font-size:0.88rem;"
                    f"line-height:1.7;color:#1f2937;margin-bottom:10px'>"
                    f"{contenuto['contenuto_json'].replace(chr(10), '<br>')}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.caption("_(nessun testo salvato per questo paragrafo)_")

        # Quiz del capitolo (se presente)
        try:
            import json as _jq
            quiz_contenuti = db.esegui(
                """SELECT pc.quiz_id FROM piano_contenuti pc
                   JOIN piano_paragrafi pp ON pp.id = pc.paragrafo_id
                   WHERE pp.capitolo_id = ? AND pc.tipo = 'quiz' AND pc.quiz_id IS NOT NULL
                   LIMIT 1""",
                [cap["id"]],
            )
        except Exception:
            quiz_contenuti = []

        if quiz_contenuti and quiz_contenuti[0].get("quiz_id"):
            quiz_id = quiz_contenuti[0]["quiz_id"]
            try:
                domande = db.trova_tutti("domande_quiz", {"quiz_id": quiz_id}, ordine="ordine ASC")
            except Exception:
                domande = []
            if domande:
                st.markdown(f"**Test di verifica** ({len(domande)} domande)")
                for i, d in enumerate(domande, 1):
                    try:
                        opzioni = _jq.loads(d.get("opzioni_json") or "[]")
                    except Exception:
                        opzioni = []
                    st.markdown(
                        f"<div style='background:#f0f4f8;padding:8px 12px;border-radius:6px;"
                        f"font-size:0.85rem;margin-bottom:6px'>"
                        f"<strong>D{i}.</strong> {d.get('testo','')}</div>",
                        unsafe_allow_html=True,
                    )
                    for opz in opzioni:
                        corretta = d.get("risposta_corretta") == opz
                        colore = "#1A7F4B" if corretta else "#5A6A7E"
                        st.markdown(
                            f"<div style='font-size:0.82rem;color:{colore};padding-left:16px'>"
                            f"{'✓' if corretta else '○'} {opz}</div>",
                            unsafe_allow_html=True,
                        )

        st.markdown(
            "<hr style='border:none;border-top:1px solid #E8EEF6;margin:12px 0'>",
            unsafe_allow_html=True,
        )


def _render_contenuti_ai(corso: dict):
    st.markdown("**Contenuti generati AI (capitoli e test)**")
    st.caption(
        "Premi 'Genera contenuto corso' per produrre teoria e quiz in un solo click. "
        "Poi leggi, modifica i campi, o chiedi a Lea di riscrivere un paragrafo nella chat a destra."
    )
    docente_id = st.session_state.get("current_user_id", 1)
    key = _init_schema_state(corso["id"])
    schema = st.session_state[key]

    # Version counter: incrementato ad ogni cancellazione per forzare il refresh dei widget
    ver_key = f"_schema_ver_{corso['id']}"
    if ver_key not in st.session_state:
        st.session_state[ver_key] = 0
    ver = st.session_state[ver_key]

    # — Prompt centrale —
    prompt = st.text_area(
        "Istruzioni per generare la lezione",
        placeholder="Es: Focalizzati su esempi pratici. Usa un linguaggio accessibile agli studenti del primo anno.",
        key=f"prompt_{corso['id']}",
    )
    # Gestione fallback ricerca semantica → keyword (con consenso docente)
    _sem_fallita_key = f"_sem_fallita_{corso['id']}"
    if _sem_fallita_key in st.session_state:
        _info_fallita = st.session_state[_sem_fallita_key]
        st.warning(
            f"La ricerca nel database vettoriale non è riuscita.\n\n"
            f"**Motivo:** {_info_fallita['motivo']}\n\n"
            f"È disponibile una ricerca alternativa basata su parole chiave "
            f"(keyword matching sui metadati), che potrebbe essere meno precisa."
        )
        col_si, col_no = st.columns(2)
        with col_si:
            if st.button("Procedi con ricerca per parole chiave", key=f"kw_si_{corso['id']}"):
                _prompt_salvato = _info_fallita["prompt"]
                _key_salvato = _info_fallita["key"]
                del st.session_state[_sem_fallita_key]
                _genera_contenuto_corso(corso, docente_id, _prompt_salvato, _key_salvato, forza_keyword=True)
        with col_no:
            if st.button("Annulla", key=f"kw_no_{corso['id']}"):
                del st.session_state[_sem_fallita_key]
                st.rerun()

    if st.button("Genera contenuto corso", type="primary", key=f"gen_corso_{corso['id']}"):
        _genera_contenuto_corso(corso, docente_id, prompt, key)

    st.markdown("---")

    # — Rendering schema misto —
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
                if st.button(
                    "🗑️",
                    key=f"del_cap_{corso['id']}_{idx}_{ver}",
                    help="Elimina capitolo e i suoi paragrafi",
                ):
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
                if st.button(
                    "🗑️",
                    key=f"del_test_{corso['id']}_{idx}_{ver}",
                    help="Elimina set di domande",
                ):
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

    # — Gestione cancellazione —
    if idx_to_delete is not None:
        schema.pop(idx_to_delete)
        st.session_state[key] = schema
        st.session_state[ver_key] = ver + 1
        st.rerun()

    st.markdown("---")

    # — Bottoni di aggiunta manuale —
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
            f"<div style='font-family:Playfair Display,serif; font-size:1.2rem; font-weight:700; color:#001A4D; "
            f"margin:12px 0 4px 0;'>✏️ {corso['nome']} "
            f"<span class='status-pill {stato_class}' style='font-size:0.72rem; vertical-align:middle;'>{stato_lbl}</span></div>",
            unsafe_allow_html=True,
        )
    with close_col:
        if st.button("X", key=f"close_course_detail_{corso['id']}", help="Chiudi"):
            st.session_state["_corso_doc_sel"] = None
            st.rerun()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Panoramica", "Materiali", "Contenuti AI", "Analytics corso", "Contenuto Lezione", "Modifica Panoramica"])

    with tab1:
        tutti_cdl = _get_tutti_cdl()
        cdl_correnti_ids = _get_cdl_corso(corso["id"])
        cdl_correnti_nomi = [c["nome"] for c in tutti_cdl if c["id"] in cdl_correnti_ids]
        cdl_label = ", ".join(cdl_correnti_nomi) if cdl_correnti_nomi else "—"

        st.markdown(
            f"""
            <div class='tab-note'>
            <strong>Descrizione:</strong> {corso.get('descrizione') or '—'}<br>
            <strong>CFU:</strong> {corso.get('cfu') or '—'}<br>
            <strong>Anno:</strong> {corso.get('anno_di_corso') or '—'} · Livello: {corso.get('livello') or '—'} · Semestre: {corso.get('semestre') or '—'}<br>
            <strong>Corsi di Laurea:</strong> {cdl_label}<br>
            <strong>Studenti iscritti:</strong> {_conta_studenti_corso(corso['id'])}
            </div>
            """,
            unsafe_allow_html=True,
        )
    with tab2:
        _render_materiali(corso, docente_id)

    with tab3:
        _render_contenuti_ai(corso)

    with tab4:
        dati = _metrics(docente_id, corso["id"])
        col1, col2, col3 = st.columns(3)
        col1.metric("Studenti unici", dati["studenti"])
        col2.metric("Quiz pubblicati", dati["quiz"])
        col3.metric("Tentativi quiz", dati["tentativi"])
        st.caption("Drill-down per capitolo/argomento verrà aggiunto dopo la raccolta dati.")

    with tab5:
        _render_anteprima_lezione(corso["id"])

    with tab6:
        is_pubblicato = bool(corso.get("attivo"))
        if is_pubblicato:
            st.info("Il corso è pubblicato. Le modifiche saranno visibili immediatamente agli studenti iscritti.")
        tutti_cdl_mod = _get_tutti_cdl()
        cdl_correnti_ids_mod = _get_cdl_corso(corso["id"])
        cdl_nomi_tutti_mod = [c["nome"] for c in tutti_cdl_mod]
        cdl_correnti_nomi_mod = [c["nome"] for c in tutti_cdl_mod if c["id"] in cdl_correnti_ids_mod]
        with st.form(f"modifica_panoramica_{corso['id']}"):
            nome_mod = st.text_input("Nome corso", value=corso.get("nome", ""))
            descrizione_mod = st.text_area("Descrizione", value=corso.get("descrizione", "") or "", height=120)
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                cfu_mod = st.number_input("CFU", min_value=0, max_value=30, step=1, value=int(corso.get("cfu") or 0))
            with col_b:
                anno_mod = st.number_input("Anno (1-5)", min_value=1, max_value=5, step=1, value=int(corso.get("anno_di_corso") or 1))
            with col_c:
                livello_mod = st.selectbox(
                    "Livello",
                    ["base", "intermedio", "avanzato"],
                    index=["base", "intermedio", "avanzato"].index(corso.get("livello") or "base"),
                )
            with col_d:
                semestre_mod = st.selectbox("Semestre", [1, 2], index=[1, 2].index(corso.get("semestre") or 1))
            cdl_sel_mod = st.multiselect("Corsi di Laurea", cdl_nomi_tutti_mod, default=cdl_correnti_nomi_mod)
            label_btn = "Salva modifiche" if is_pubblicato else "Aggiorna bozza"
            if st.form_submit_button(label_btn, type="primary"):
                db.aggiorna(
                    "corsi_universitari",
                    {"id": corso["id"]},
                    {
                        "nome": nome_mod,
                        "descrizione": descrizione_mod,
                        "cfu": cfu_mod,
                        "anno_di_corso": anno_mod,
                        "livello": livello_mod,
                        "semestre": semestre_mod,
                    },
                )
                cdl_sel_ids_mod = [c["id"] for c in tutti_cdl_mod if c["nome"] in cdl_sel_mod]
                _salva_cdl_corso(corso["id"], cdl_sel_ids_mod)
                st.success("Panoramica aggiornata con successo.")
                st.session_state["_doc_refresh"] = True


def _render_corsi(docente_id: int):
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">I tuoi corsi</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Gestisci bozze, pubblicazioni e materiali.</div>', unsafe_allow_html=True)

    feedback = st.session_state.pop("_doc_create_feedback", None)
    if feedback:
        st.success(feedback)

    if st.button("Crea nuovo corso", type="primary"):
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
        st.markdown("<hr style='border:none;border-top:1px solid #E8EEF6;margin:6px 0'>", unsafe_allow_html=True)

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
    
    # Header
    st.markdown(
        """
        <div class="chat-header">
            <div class="chat-online"></div>
            <div>
                <div class="chat-title">Lea — Tutor AI</div>
                <div class="chat-sub">Supporto ai docenti</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "chat_history_doc" not in st.session_state:
        st.session_state["chat_history_doc"] = [
            {"role": "assistant", "content": f"Ciao {utente.get('nome','')}! Sono Lea. Posso aiutarti a creare materiali, quiz e monitorare i corsi."}
        ]

    # Funzione helper per l'HTML della chat (allineata a studente.py)
    def get_chat_html(is_typing=False):
        html = '<div class="chat-container" id="chat-box">'
        for msg in st.session_state["chat_history_doc"]:
            if msg["role"] == "user":
                testo_safe = msg["content"].replace("<", "&lt;").replace(">", "&gt;")
                html += f'<div class="msg-user">{testo_safe}</div>'
            else:
                import re as _re
                contenuto = msg["content"].replace("<", "&lt;").replace(">", "&gt;")
                contenuto = _re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", contenuto)
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

    # Placeholder per la chat
    chat_placeholder = st.empty()
    chat_placeholder.markdown(get_chat_html(), unsafe_allow_html=True)

    # Suggerimenti rapidi
    suggerimenti = [("📄", "Genera una lezione"), ("✅", "Crea un quiz approvato"), ("🧠", "Crea flashcard")]
    messaggio_da_suggerimento = None
    cols = st.columns(len(suggerimenti))
    for idx, (icona, testo) in enumerate(suggerimenti):
        with cols[idx]:
            if st.button(f"{icona} {testo}", key=f"sug_doc_{idx}"):
                target = corso_nome or "il tuo corso"
                messaggio_da_suggerimento = f"{testo} per {target}"

    # Input chat nativo
    user_input = st.chat_input("Chiedi a Lea (docente)...", key="lea_doc_chat_input")

    messaggio_finale = user_input or messaggio_da_suggerimento
    if messaggio_finale:
        st.session_state["chat_history_doc"].append({"role": "user", "content": messaggio_finale})
        
        # Mostra subito l'animazione di caricamento
        chat_placeholder.markdown(get_chat_html(is_typing=True), unsafe_allow_html=True)

        risposta = "Lea non è configurata (AWS Bedrock non attivo)."
        if chat_con_orchestratore and aggiorna_contesto:
            try:
                # Imposta il contesto docente: include anche il corso attivo nelle analytics
                analytics_id = st.session_state.get("_analytics_corso_id")
                analytics_nome = st.session_state.get("_analytics_corso_nome")
                ctx_id = corso_id or analytics_id
                ctx_nome = corso_nome or analytics_nome
                # Recupera il piano docente del corso per consentire modifiche via chat
                _piano_doc_id = None
                _piano_doc_titolo = None
                if ctx_id:
                    try:
                        _piani_doc = db.trova_tutti(
                            "piani_personalizzati",
                            {"corso_universitario_id": ctx_id, "is_corso_docente": 1},
                            ordine="id DESC", limite=1,
                        )
                        if _piani_doc:
                            _piano_doc_id = _piani_doc[0]["id"]
                            _piano_doc_titolo = _piani_doc[0].get("titolo", "Contenuto corso")
                    except Exception:
                        pass
                aggiorna_contesto(
                    corso_id=ctx_id,
                    corso_nome=ctx_nome,
                    tipo_vista="docente",
                    piano_id=_piano_doc_id,
                    piano_titolo=_piano_doc_titolo,
                    extra={"analytics_corso_id": analytics_id, "analytics_corso_nome": analytics_nome}
                    if analytics_id else {},
                )
                risposta = chat_con_orchestratore(
                    messaggio_utente=messaggio_finale,
                    corso_contestuale_id=corso_id,
                    corso_contestuale_nome=corso_nome,
                )
            except Exception as e:
                risposta = f"Errore: {str(e)[:120]}"
        
        st.session_state["chat_history_doc"].append({"role": "assistant", "content": risposta})
        st.rerun()


@st.dialog("Federico360 — LearnAI Platform", width="large")
def _popup_accettazione():
    """Popup di accettazione termini AI mostrato al primo accesso dopo il login."""
    st.markdown("""
    <style>
    /* Hide ALL possible close button selectors */
    button[data-testid="stBaseButton-headerNoPadding"],
    div[data-testid="stModal"] button[aria-label="Close"],
    div[data-testid="stModal"] [data-testid="stModalCloseButton"],
    div[data-testid="stModal"] header button,
    div[data-testid="stModal"] [data-testid="stHeader"] button,
    div[data-testid="stModal"] > div > div > div > button {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
        position: absolute !important;
        pointer-events: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; padding: 8px 0 4px;">
        <div style="display:flex; align-items:center; justify-content:center; gap:14px; margin-bottom:20px;">
            <span style="font-family:'Playfair Display','Source Sans 3',serif; font-size:1.3rem;
                         font-weight:700; color:#001A4D;">
                Federico<span style="color:#C5A028;">360</span>
            </span>
            <span style="color:#C8D5E3; font-size:1.4rem; font-weight:300;">|</span>
            <span style="font-family:'Source Sans 3',sans-serif; font-size:1.05rem; font-weight:600; color:#5A6A7E;">
                LearnAI Platform
            </span>
        </div>
        <h3 style="color:#001A4D; font-size:1.12rem; font-weight:700; margin:0 0 18px 0;
                    font-family:'Source Sans 3',sans-serif;">
            Benvenuto nella piattaforma LearnAI
        </h3>
        <p style="color:#5A6A7E; font-size:0.88rem; line-height:1.75; max-width:440px;
                  margin:0 auto 12px; font-family:'Source Sans 3',sans-serif;">
            Stai interagendo con un sistema basato sull'<strong style="color:#001A4D;">Intelligenza
            Artificiale</strong>, pertanto ricorda che qualsiasi contenuto generato o analizzato
            sar&agrave; prodotto dall'AI.
        </p>
        <p style="color:#5A6A7E; font-size:0.88rem; line-height:1.75; max-width:440px;
                  margin:0 auto; font-family:'Source Sans 3',sans-serif;">
            Ti ricordiamo che la piattaforma Federico360 deve essere utilizzata nel rispetto dei
            <strong style="color:#001A4D;">&ldquo;Termini e Condizioni&rdquo;</strong>. Il trattamento
            dei dati personali sar&agrave; effettuato in conformit&agrave; con la nostra
            <strong style="color:#001A4D;">Privacy Policy</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    if st.button("Accetta", type="primary", use_container_width=True, key="btn_accetta_popup"):
        st.session_state["_accettazione_accettata"] = True
        st.rerun()


def mostra_homepage_docente():
    utente = st.session_state.user
    docente_id = st.session_state.current_user_id
    if not st.session_state.get("_accettazione_accettata"):
        _popup_accettazione()
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
        # Fallback: usa il corso selezionato nella sezione analytics
        if not sel_id:
            sel_id = st.session_state.get("_analytics_corso_id")
            corso_nome = st.session_state.get("_analytics_corso_nome")
        _render_chatbot_docente(utente, sel_id, corso_nome)
    if st.session_state.get("_doc_refresh"):
        st.session_state["_doc_refresh"] = False
        st.rerun()


if __name__ == "__main__":
    mostra_homepage_docente()




