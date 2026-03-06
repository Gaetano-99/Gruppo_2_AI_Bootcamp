import sys, os
import streamlit as st
import pandas as pd
import json

# Setup path per importare core e platform_sdk
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from platform_sdk.database import db
from src.tools.document_processor import elabora_e_salva_documento
from src.agents.content_gen import crea_agente_content_gen, esegui_generazione

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Testing Lab - Studente", page_icon="🧪", layout="wide")
st.markdown("<style>[data-testid='stSidebarNav']{display:none}</style>", unsafe_allow_html=True)

# Controllo Accesso
if not st.session_state.get("is_logged_in"):
    st.switch_page("app.py")

st.title("🧪 Backend Playground & Testing")
st.caption(f"Laboratorio di test per: **{st.session_state.get('user', {}).get('email', '—')}**")

# --- SIDEBAR: LOGOUT & STATO DB ---
with st.sidebar:
    st.header("⚙️ Controlli")
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("app.py")
    
    st.divider()
    st.subheader("Stato Database")
    if st.toggle("Mostra Tabelle di Sistema"):
        try:
            utenti = db.esegui("SELECT COUNT(*) as count FROM users")
            materiali = db.esegui("SELECT COUNT(*) as count FROM materiali_didattici")
            chunks = db.esegui("SELECT COUNT(*) as count FROM materiali_chunks")
            st.write(f"Utenti: {utenti[0]['count']}")
            st.write(f"Materiali: {materiali[0]['count']}")
            st.write(f"Chunks: {chunks[0]['count']}")
        except:
            st.error("Errore connessione DB")

# --- MAIN LAYOUT (Tabs per i vari test) ---
tabs = st.tabs(["📂 Ingestione Documenti", "🤖 Test Agenti", "🔍 Verifica RAG & Chunks"])

# --- TAB 1: CARICAMENTO E PARSING REAL ---
with tabs[0]:
    st.header("Caricamento Materiale Reale")
    st.info("Carica un documento per testare il `document_processor` (estrazione testo + chunking).")
    
    with st.form("upload_test"):
        uploaded_file = st.file_uploader("Scegli un file", type=["pdf", "txt", "csv", "xlsx"])
        titolo = st.text_input("Titolo Materiale", value="Lezione di Prova")
        corso_id = st.number_input("ID Corso Universitario", min_value=1, value=1)
        tipo_mat = st.selectbox("Tipo", ["pdf", "slide", "dispensa", "libro"])
        
        submit_upload = st.form_submit_button("Avvia Processamento")
        
        if submit_upload and uploaded_file:
            try:
                with st.status("Elaborazione in corso...") as status:
                    mat_id = elabora_e_salva_documento(
                        uploaded_file=uploaded_file,
                        corso_universitario_id=corso_id,
                        titolo=titolo,
                        tipo=tipo_mat
                    )
                    status.update(label="Documento processato e chunkizzato!", state="complete")
                    st.success(f"Creato materiale ID: {mat_id}")
            except Exception as e:
                st.error(f"Errore durante l'ingestione: {e}")

# --- TAB 2: GENERAZIONE CONTENUTI (Agent 5 - Content Gen) ---
with tabs[1]:
    st.header("Test Agente Content Generation (Agent 5)")
    st.write("Verifica il grafo LangGraph per la creazione di lezioni e strumenti didattici.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        argomento = st.text_input("Argomento della lezione", placeholder="es: Normalizzazione database")
        c_id = st.number_input("ID Corso", min_value=1, value=1, key="gen_corso_id")
    with col_b:
        tipo_strumento = st.radio("Strumento da generare", ["quiz", "flashcard"])

    if st.button("Esegui Grafo di Generazione"):
        if not argomento:
            st.warning("Inserisci un argomento.")
        else:
            with st.spinner("L'agente sta lavorando (RAG -> Generazione -> Persistenza)..."):
                agente = crea_agente_content_gen()
                stato_finale = esegui_generazione(agente, c_id, argomento, tipo_strumento)
                
                if stato_finale.get("errore"):
                    st.error(stato_finale["errore"])
                else:
                    st.success("Generazione completata e salvata nel database!")
                    st.markdown("### 📝 Lezione Generata")
                    st.markdown(stato_finale["lezione_generata"])
                    
                    st.markdown("### 🛠️ Strumenti Studio")
                    st.json(stato_finale["strumenti_studio_generati"])
                    
                    st.info(f"Chunks utilizzati: {stato_finale['chunk_ids_utilizzati']}")

# --- TAB 3: VERIFICA TRACCIABILITÀ ---
with tabs[2]:
    st.header("Analisi Coerenza RAG & Fonti")
    st.write("Verifica il lincaggio tra le lezioni generate e i chunk sorgente.")
    
    lezioni = db.esegui("""
        SELECT id, titolo, chunk_ids_utilizzati, contenuto_md 
        FROM lezioni_corso 
        ORDER BY id DESC
    """)
    
    if lezioni:
        df_lezioni = pd.DataFrame(lezioni)
        st.dataframe(df_lezioni[["id", "titolo", "chunk_ids_utilizzati"]], use_container_width=True)
        
        lezione_selezionata = st.selectbox("Seleziona ID Lezione per il Deep Dive", df_lezioni['id'])
        
        if st.button("Visualizza Dettagli e Sorgenti"):
            dati = next(item for item in lezioni if item["id"] == lezione_selezionata)
            
            # Parsing sicuro dei chunk IDs (possono essere stringa JSON o lista)
            c_ids = dati['chunk_ids_utilizzati']
            if isinstance(c_ids, str):
                try:
                    c_ids = json.loads(c_ids)
                except:
                    c_ids = []

            st.divider()
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("📌 Fonti (Chunks)")
                if c_ids:
                    placeholders = ", ".join(["?"] * len(c_ids))
                    chunks_db = db.esegui(f"SELECT id, testo FROM materiali_chunks WHERE id IN ({placeholders})", c_ids)
                    for c in chunks_db:
                        with st.expander(f"Chunk ID: {c['id']}"):
                            st.write(c['testo'])
                else:
                    st.warning("Nessun ID chunk tracciato per questa lezione.")

            with col2:
                st.subheader("📝 Contenuto Generato")
                st.markdown(dati['contenuto_md'])
    else:
        st.warning("Nessuna lezione presente. Usa il Tab 2 per generarne una.")
