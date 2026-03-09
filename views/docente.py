"""Homepage Docente - LearnAI Platform."""

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
:root { --blue:#003087; --blue-dark:#001A4D; --blue-mid:#1351A8; --red:#C8102E; --gold:#C5A028; --light:#F0F4F8; --gray:#5A6A7E; --border:#C8D5E3; --white:#FFFFFF; --green:#1A7F4B; --card:#f8fafc; --input-bg:#f8fafc; --input-text:#1f2937; --placeholder:#4b5563; } /* modifica qui i colori di fondo/riquadri */
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
.stTextInput input, .stTextArea textarea, .stSelectbox select, .stNumberInput input, .stChatInput textarea { background: var(--input-bg) !important; color: var(--input-text) !important; }
.stTextInput input::placeholder, .stTextArea textarea::placeholder, .stChatInput textarea::placeholder { color: var(--placeholder) !important; }
div[data-baseweb="select"] { background: var(--input-bg) !important; color: var(--input-text) !important; }
div[data-baseweb="select"] input { color: var(--input-text) !important; }
</style>
"""


def _get_corsi_docente(docente_id: int) -> List[dict]:
    return db.trova_tutti("corsi_universitari", {"docente_id": docente_id}, ordine="created_at DESC")


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
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Analytics</div>', unsafe_allow_html=True)
    scope_options = ["Generale"] + [f"Corso: {c['nome']} (ID {c['id']})" for c in corsi]
    scelta = st.selectbox("Ambito analytics", scope_options, key="analytics_scope")
    corso_sel_id = None
    if scelta.startswith("Corso:"):
        label_to_id = {f"Corso: {c['nome']} (ID {c['id']})": c["id"] for c in corsi}
        corso_sel_id = label_to_id.get(scelta)
    dati = _metrics(docente_id, corso_sel_id)

    col_a, col_b, col_c, col_d = st.columns(4)
    for col, label, val in [
        (col_a, "Studenti unici", dati["studenti"]),
        (col_b, "Quiz pubblicati", dati["quiz"]),
        (col_c, "Tentativi quiz", dati["tentativi"]),
        (col_d, "Corsi gestiti", dati["corsi"]),
    ]:
        with col:
            st.markdown(
                f"""
                <div class='metric-box'>
                    <div class='metric-label'>{label}</div>
                    <div class='metric-value'>{val}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if corsi:
        serie = [{"Corso": c["nome"], "Quiz approvati": _metrics(docente_id, c["id"])['quiz']} for c in corsi]
        fig = px.bar(serie, x="Corso", y="Quiz approvati", title="Quiz approvati per corso")
        fig.update_layout(height=320, margin=dict(t=50, b=20, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Carica almeno un corso per vedere le analytics.")
    st.markdown('</div>', unsafe_allow_html=True)


def _dialog_crea_corso(docente_id: int):
    with st.form("crea_corso_form"):
        nome = st.text_input("Nome corso")
        descrizione = st.text_area("Descrizione")
        cfu = st.number_input("CFU", min_value=0, max_value=30, step=1, value=0)
        anno = st.number_input("Anno di corso (1-5)", min_value=1, max_value=5, step=1, value=1)
        livello = st.selectbox("Livello", ["base", "intermedio", "avanzato"])
        semestre = st.selectbox("Semestre", [1, 2])
        submitted = st.form_submit_button("Salva bozza", type="primary")
    if submitted:
        if not nome:
            st.error("Inserisci il nome del corso.")
            return
        db.inserisci(
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
        st.success("Corso salvato in bozza.")
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


def _render_materiali(corso: dict, docente_id: int):
    st.markdown("**Materiali didattici (fonte RAG)**")
    st.caption("Carica file associati al corso. Verranno usati come unica fonte per generazione e quiz.")
    materiali = _get_materiali_corso(corso["id"])
    if materiali:
        for m in materiali:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{m['titolo']}**")
                st.caption(f"Tipo: {m['tipo']} · Caricato: {(m.get('caricato_il') or '')[:10]}")
            with col2:
                st.caption("Processed" if m.get("is_processed") else "In attesa")
            with col3:
                if st.button("Elimina", key=f"del_mat_{m['id']}"):
                    db.elimina("materiali_didattici", {"id": m["id"]})
                    st.success("Materiale eliminato.")
                    st.session_state["_doc_refresh"] = True
                    st.rerun()
    else:
        st.info("Nessun materiale caricato per questo corso.")

    with st.container(border=True):
        files = st.file_uploader(
            "Carica uno o più file",
            type=["pdf", "docx", "txt", "pptx", "xlsx"],
            accept_multiple_files=True,
            key=f"upload_{corso['id']}",
        )
        tipo_scelto = st.selectbox(
            "Tipo documento (salvato su DB)", ["pdf", "slide", "video", "dispensa", "libro"], key=f"tipo_{corso['id']}"
        )
        if files and st.button("Carica materiali", key=f"do_upload_{corso['id']}"):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            upload_dir = os.path.join(base_dir, "uploads", str(corso["id"]))
            os.makedirs(upload_dir, exist_ok=True)
            ok = 0
            for f in files:
                path = os.path.join(upload_dir, f.name)
                with open(path, "wb") as out:
                    out.write(f.getbuffer())
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
            st.success(f"{ok} file caricati. La pipeline di elaborazione partirà automaticamente.")
            st.session_state["_doc_refresh"] = True


def _init_schema_state(corso_id: int):
    key = f"_schema_{corso_id}"
    if key not in st.session_state:
        st.session_state[key] = [
            {"titolo": "Capitolo 1", "paragrafi": ["Introduzione"]},
            {"titolo": "Capitolo 2", "paragrafi": ["Argomento principale"]},
        ]
    return key


def _render_contenuti_ai(corso: dict):
    st.markdown("**Contenuti generati AI (capitoli e paragrafi)**")
    st.caption("Schema modificabile prima della pubblicazione. Usa i materiali caricati per il RAG.")
    key = _init_schema_state(corso["id"])
    schema = st.session_state[key]

    col1, col2 = st.columns([2, 1])
    with col1:
        prompt = st.text_area("Prompt per rigenerare lo schema", key=f"prompt_{corso['id']}")
    with col2:
        if st.button("Genera schema AI", key=f"gen_schema_{corso['id']}"):
            chat, aggiorna, _ = _import_orchestratore()
            if chat and aggiorna:
                try:
                    aggiorna(corso_id=corso["id"], corso_nome=corso["nome"], tipo_vista="docente", piano_id=None, piano_titolo=None)
                    risposta = chat(
                        messaggio_utente=f"Genera uno schema con capitoli e paragrafi per il corso {corso['nome']}. {prompt}",
                        corso_contestuale_id=corso["id"],
                        corso_contestuale_nome=corso["nome"],
                    )
                    schema = [
                        {"titolo": "Capitolo 1", "paragrafi": ["Paragrafo 1", "Paragrafo 2"]},
                        {"titolo": "Capitolo 2", "paragrafi": ["Paragrafo 1"]},
                    ]
                    st.session_state[key] = schema
                    st.success("Schema generato. Personalizza i testi sotto.")
                    st.caption(str(risposta))
                except Exception as e:
                    st.error(f"Errore AI: {e}")
            else:
                st.info("Configura gli agenti AI (AWS Bedrock) per usare la generazione automatica. Uso schema di esempio.")
                st.session_state[key] = schema

    # editor capitoli/paragrafi
    for idx, capitolo in enumerate(schema):
        st.markdown(f"### Capitolo {idx+1}")
        capitolo["titolo"] = st.text_input("Titolo capitolo", value=capitolo["titolo"], key=f"cap_tit_{corso['id']}_{idx}")
        for p_idx, par in enumerate(capitolo["paragrafi"]):
            capitolo["paragrafi"][p_idx] = st.text_input(
                f"Paragrafo {p_idx+1}", value=par, key=f"par_{corso['id']}_{idx}_{p_idx}"
            )
        if st.button("Aggiungi paragrafo", key=f"add_par_{corso['id']}_{idx}"):
            capitolo["paragrafi"].append("Nuovo paragrafo")
            st.session_state[key] = schema
            st.rerun()
    if st.button("Aggiungi capitolo", key=f"add_cap_{corso['id']}"):
        schema.append({"titolo": "Nuovo capitolo", "paragrafi": ["Paragrafo"]})
        st.session_state[key] = schema
        st.rerun()

    if st.button("Salva contenuti (bozza)", key=f"save_schema_{corso['id']}"):
        st.success("Contenuti salvati in bozza (sessione). Persistenza DB da implementare.")


def _render_dettaglio_corso(corso: dict, docente_id: int):
    stato_lbl, stato_class = _stato_corso(corso)
    st.markdown(
        f"""
        <div class='course-card' style='border-left-color:#003087'>
            <div class='title'>{corso['nome']}</div>
            <div class='meta'><span class='status-pill {stato_class}'>{stato_lbl}</span>
            <span class='chip'>CFU {corso.get('cfu') or '—'}</span>
            <span class='chip'>Anno {corso.get('anno_di_corso') or '—'}</span>
            <span class='chip'>{corso.get('livello') or '—'}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    actions_col1, actions_col2 = st.columns(2)
    if not corso.get("attivo"):
        with actions_col1:
            if st.button("Salva bozza", key=f"draft_{corso['id']}"):
                db.aggiorna("corsi_universitari", {"id": corso["id"]}, {"attivo": 0})
                st.success("Bozza salvata.")
        with actions_col2:
            if st.button("Pubblica", key=f"pub_det_{corso['id']}"):
                db.aggiorna("corsi_universitari", {"id": corso["id"]}, {"attivo": 1})
                st.success("Corso pubblicato.")
                st.session_state["_doc_refresh"] = True
                st.rerun()
    else:
        with actions_col1:
            if st.button("Disattiva", key=f"dis_det_{corso['id']}"):
                db.aggiorna("corsi_universitari", {"id": corso["id"]}, {"attivo": 0})
                st.session_state["_doc_refresh"] = True
                st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs(["Panoramica", "Materiali", "Contenuti AI", "Analytics corso"])

    with tab1:
        st.markdown(
            f"""
            <div class='tab-note'>
            <strong>Descrizione:</strong> {corso.get('descrizione') or '—'}<br>
            <strong>CFU:</strong> {corso.get('cfu') or '—'}<br>
            <strong>Anno:</strong> {corso.get('anno_di_corso') or '—'} · Livello: {corso.get('livello') or '—'} · Semestre: {corso.get('semestre') or '—'}<br>
            <strong>Studenti iscritti:</strong> {_conta_studenti_corso(corso['id'])}
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not corso.get("attivo"):
            st.info("Puoi modificare questo corso finché non viene pubblicato.")
            with st.form(f"modifica_corso_{corso['id']}"):
                nome = st.text_input("Nome corso", value=corso.get("nome", ""))
                descrizione = st.text_area("Descrizione", value=corso.get("descrizione", "") or "")
                cfu = st.number_input("CFU", min_value=0, max_value=30, step=1, value=int(corso.get("cfu") or 0))
                anno = st.number_input(
                    "Anno di corso (1-5)", min_value=1, max_value=5, step=1, value=int(corso.get("anno_di_corso") or 1)
                )
                livello = st.selectbox(
                    "Livello", ["base", "intermedio", "avanzato"], index=["base", "intermedio", "avanzato"].index(corso.get("livello") or "base")
                )
                semestre = st.selectbox("Semestre", [1, 2], index=[1, 2].index(corso.get("semestre") or 1))
                if st.form_submit_button("Aggiorna bozza", type="primary"):
                    db.aggiorna(
                        "corsi_universitari",
                        {"id": corso["id"]},
                        {"nome": nome, "descrizione": descrizione, "cfu": cfu, "anno_di_corso": anno, "livello": livello, "semestre": semestre},
                    )
                    st.success("Bozza aggiornata.")
                    st.session_state["_doc_refresh"] = True

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


def _render_corsi(docente_id: int):
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">I tuoi corsi</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Gestisci bozze, pubblicazioni e materiali.</div>', unsafe_allow_html=True)

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

    suggerimenti = [("📄", "Genera una lezione"), ("✅", "Crea un quiz approvato"), ("🧠", "Crea flashcard")]
    messaggio_da_suggerimento = None
    cols = st.columns(len(suggerimenti))
    for idx, (icona, testo) in enumerate(suggerimenti):
        with cols[idx]:
            if st.button(f"{icona} {testo}", key=f"sug_doc_{idx}"):
                target = corso_nome or "il tuo corso"
                messaggio_da_suggerimento = f"{testo} per {target}"

    user_input = st.chat_input("Chiedi a Lea (docente)...", key="lea_doc_input")
    messaggio_finale = user_input or messaggio_da_suggerimento
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
