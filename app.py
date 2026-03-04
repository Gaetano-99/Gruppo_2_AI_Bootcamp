# ============================================================================
# LearnAI Platform — App Principale
# Questo è il punto di ingresso dell'applicazione Streamlit.
# Avviatela con: streamlit run app.py
# ============================================================================

import streamlit as st
import config

# --- Configurazione pagina ---
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Sidebar ---
with st.sidebar:
    st.title(f"{config.APP_ICON} LearnAI")
    st.caption("Piattaforma di e-learning guidata da AI")
    st.divider()

    st.markdown("### 📚 Navigazione")
    st.markdown(
        "Usa il menu qui a sinistra per navigare "
        "tra le pagine dell'applicazione."
    )

    st.divider()
    st.markdown("### ℹ️ Info tecnica")
    st.markdown(f"**Modello AI:** `Sonnet`")
    st.markdown(f"**Modello veloce:** `Haiku`")
    st.markdown(f"**Database:** SQLite")
    st.markdown(f"**Framework:** LangChain + LangGraph")

# ============================================================================
# HEADER
# ============================================================================

st.title("🎓 Benvenuto su LearnAI!")
st.markdown(
    "La tua piattaforma di apprendimento guidata dall'Intelligenza Artificiale. "
    "Ogni modulo è potenziato da agenti AI che ti aiutano a crescere professionalmente."
)

st.markdown("---")

# ============================================================================
# DASHBOARD OVERVIEW — dati reali dal database
# ============================================================================

st.markdown("### 📊 Overview della piattaforma")

try:
    from platform_sdk.database import db
    import pandas as pd

    # --- KPI principali ---
    n_utenti = db.conta("users")
    n_corsi = db.conta("courses")
    n_skills = db.conta("skills")
    n_piani = db.conta("training_plans")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 Utenti", n_utenti)
    col2.metric("📚 Corsi", n_corsi)
    col3.metric("🎯 Competenze", n_skills)
    col4.metric("📋 Piani formativi", n_piani)

    # --- Dettagli in due colonne ---
    col_sx, col_dx = st.columns(2)

    with col_sx:
        st.markdown("#### 👥 Utenti registrati")
        utenti = db.trova_tutti("users")
        if utenti:
            df_utenti = pd.DataFrame(utenti)[["nome", "cognome", "ruolo", "dipartimento"]]
            st.dataframe(df_utenti, use_container_width=True, hide_index=True)
        else:
            st.info("Nessun utente registrato. Esegui il seed del database.")

    with col_dx:
        st.markdown("#### 📚 Catalogo corsi")
        corsi = db.trova_tutti("courses")
        if corsi:
            df_corsi = pd.DataFrame(corsi)[["titolo", "categoria", "livello", "durata_ore"]]
            st.dataframe(df_corsi, use_container_width=True, hide_index=True)
        else:
            st.info("Nessun corso nel catalogo. Esegui il seed del database.")

    # --- Grafico distribuzione skill per categoria ---
    skills = db.trova_tutti("skills")
    if skills:
        df_skills = pd.DataFrame(skills)
        conteggio = df_skills["categoria"].value_counts().reset_index()
        conteggio.columns = ["Categoria", "Numero"]

        import plotly.express as px

        fig = px.pie(
            conteggio,
            values="Numero",
            names="Categoria",
            title="Distribuzione competenze per categoria",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_layout(height=300, margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.warning(
        f"⚠️ Database non disponibile: {e}\n\n"
        "Inizializza il database con: "
        '`python3 -c "from platform_sdk.database import db; db.init()"`'
    )

st.markdown("---")

# ============================================================================
# QUICK START — card per guidare i ragazzi
# ============================================================================

st.markdown("### 🚀 Quick Start — Da dove iniziare")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; height: 220px; color: #1a1a2e;">
            <h4>💬 1. Prova la Chat AI</h4>
            <p>Apri la pagina <b>Chat AI</b> dal menu e fai una domanda all'intelligenza artificiale. 
            Vedrai la risposta in tempo reale con lo streaming.</p>
            <p><em>→ Pagina: 💬 Chat AI</em></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; height: 220px; color: #1a1a2e;">
            <h4>🗄️ 2. Esplora il Database</h4>
            <p>Apri la pagina <b>Database</b> per vedere i dati, inserire nuovi utenti 
            e provare query SQL personalizzate.</p>
            <p><em>→ Pagina: 🗄️ Database</em></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; height: 220px; color: #1a1a2e;">
            <h4>🤖 3. Parla con l'Agente</h4>
            <p>Apri la pagina <b>Agente AI</b> e prova a chiedergli informazioni. 
            L'agente usa <b>tool</b> per cercare dati nel database!</p>
            <p><em>→ Pagina: 🤖 Agente AI</em></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div style="background-color: #e8f4e8; padding: 20px; border-radius: 10px; height: 220px; color: #1a1a2e;">
            <h4>🧪 4. Playground JSON</h4>
            <p>Apri la pagina <b>Genera JSON</b> per sperimentare con l'output strutturato. 
            Prova diversi prompt e schema per capire come funziona.</p>
            <p><em>→ Pagina: 🧪 Genera JSON</em></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div style="background-color: #e8f4e8; padding: 20px; border-radius: 10px; height: 220px; color: #1a1a2e;">
            <h4>📖 5. Leggi la guida SDK</h4>
            <p>Nella cartella <code>docs/GUIDA_SDK.md</code> trovi la documentazione completa 
            di tutte le funzioni con esempi pronti da copiare.</p>
            <p><em>→ File: docs/GUIDA_SDK.md</em></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div style="background-color: #e8f4e8; padding: 20px; border-radius: 10px; height: 220px; color: #1a1a2e;">
            <h4>🛠️ 6. Costruisci il tuo modulo!</h4>
            <p>Ora che conosci gli strumenti, inizia a costruire il modulo assegnato al tuo gruppo. 
            Leggi le istruzioni in <code>docs/ISTRUZIONI.md</code>.</p>
            <p><em>→ File: docs/ISTRUZIONI.md</em></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# ============================================================================
# ARCHITETTURA — schema visuale dello stack
# ============================================================================

st.markdown("### 🏗️ Architettura della piattaforma")

st.markdown(
    """
    ```
    ┌─────────────────────────────────────────────────────────────┐
    │                    🖥️  STREAMLIT (Frontend)                  │
    │                                                             │
    │   app.py ──── pages/01_chat.py ──── pages/02_db.py ─── ... │
    └──────────────────────┬──────────────────────────────────────┘
                           │
    ┌──────────────────────▼──────────────────────────────────────┐
    │                  📦  PLATFORM SDK                            │
    │                                                             │
    │   llm.py          database.py        agent.py               │
    │   ├─ chiedi()     ├─ inserisci()     ├─ crea_agente()      │
    │   ├─ genera_json()├─ trova_tutti()   └─ esegui_agente()    │
    │   ├─ chat()       ├─ aggiorna()                             │
    │   └─ chat_stream()└─ esegui()                               │
    └───────┬───────────────────┬─────────────────────────────────┘
            │                   │
    ┌───────▼───────┐   ┌──────▼──────┐
    │  🤖 Bedrock   │   │  🗄️ SQLite  │
    │  (Claude AI)  │   │  (Database) │
    │  via LangChain│   │             │
    └───────────────┘   └─────────────┘
    ```
    """
)

st.markdown("---")

# ============================================================================
# HEALTH CHECK — test connessioni (collassato)
# ============================================================================

st.markdown("### 🩺 Stato del sistema")

col1, col2 = st.columns(2)

with col1:
    with st.expander("🤖 Test connessione AI (Bedrock)", expanded=False):
        if st.button("🚀 Testa la connessione", type="primary"):
            with st.spinner("Contatto l'AI..."):
                try:
                    from platform_sdk.llm import chiedi

                    risposta = chiedi(
                        "Rispondi in italiano con una sola frase breve: "
                        "sei pronto ad aiutare gli studenti della Digita Academy?"
                    )
                    st.success("✅ Connessione riuscita!")
                    st.info(risposta)
                except Exception as e:
                    st.error(f"❌ Errore: {e}")
                    st.warning(
                        "Controlla che il file `.env` contenga le credenziali AWS corrette."
                    )

with col2:
    with st.expander("🗄️ Test database SQLite", expanded=False):
        if st.button("🗄️ Testa il database"):
            try:
                from platform_sdk.database import db

                n_utenti = db.conta("users")
                n_corsi = db.conta("courses")
                n_skills = db.conta("skills")
                st.success("✅ Database funzionante!")
                c1, c2, c3 = st.columns(3)
                c1.metric("Utenti", n_utenti)
                c2.metric("Corsi", n_corsi)
                c3.metric("Competenze", n_skills)
            except Exception as e:
                st.error(f"❌ Errore: {e}")
                st.warning(
                    "Inizializza il DB: "
                    '`python3 -c "from platform_sdk.database import db; db.init()"`'
                )

# --- Footer ---
st.markdown("---")
st.caption(
    "🎓 LearnAI Platform — Digita Academy | Deloitte × Federico II di Napoli | 2025"
)
