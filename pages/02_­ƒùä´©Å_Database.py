# ============================================================================
# LearnAI Platform — Pagina di esempio: Database
# Questo file mostra come leggere e scrivere dati nel database.
# Potete usarlo come riferimento per tutte le operazioni CRUD.
# ============================================================================

import streamlit as st
import pandas as pd

st.set_page_config(page_title="🗄️ Database", page_icon="🗄️", layout="wide")

st.title("🗄️ Esplora il Database")
st.caption("Esempio di lettura/scrittura dati — usatelo come riferimento!")

from platform_sdk.database import db

# --- Sidebar: scelta tabella ---
with st.sidebar:
    st.markdown("### 📋 Tabelle disponibili")
    tabella = st.selectbox(
        "Scegli una tabella da esplorare:",
        ["users", "skills", "courses", "user_skills", "assessments",
         "training_plans", "training_plan_items", "notifications", "surveys"]
    )

# --- Tab: Visualizza / Inserisci ---
tab_vedi, tab_inserisci, tab_query = st.tabs(["👁️ Visualizza", "➕ Inserisci", "🔍 Query custom"])

# --- TAB 1: Visualizza dati ---
with tab_vedi:
    st.markdown(f"### Contenuto della tabella `{tabella}`")

    try:
        dati = db.trova_tutti(tabella)
        if dati:
            df = pd.DataFrame(dati)
            st.dataframe(df, use_container_width=True)
            st.caption(f"📊 {len(dati)} righe trovate")
        else:
            st.info(f"La tabella `{tabella}` è vuota.")
    except Exception as e:
        st.error(f"Errore: {e}")

# --- TAB 2: Inserisci dati (esempio con users) ---
with tab_inserisci:
    st.markdown("### Inserisci un nuovo utente")
    st.caption("Questo è un esempio — adattatelo per il vostro modulo!")

    with st.form("form_nuovo_utente"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome", placeholder="Mario")
            email = st.text_input("Email", placeholder="mario@learnai.it")
            dipartimento = st.selectbox("Dipartimento", ["IT", "Marketing", "Finance", "HR", "Operations"])
        with col2:
            cognome = st.text_input("Cognome", placeholder="Rossi")
            ruolo = st.text_input("Ruolo", placeholder="Junior Analyst")

        inviato = st.form_submit_button("💾 Salva nel database", type="primary")

        if inviato:
            if nome and cognome and email:
                try:
                    nuovo_id = db.inserisci("users", {
                        "nome": nome,
                        "cognome": cognome,
                        "email": email,
                        "ruolo": ruolo,
                        "dipartimento": dipartimento,
                    })
                    st.success(f"✅ Utente creato con ID: {nuovo_id}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Errore: {e}")
            else:
                st.warning("Compila almeno nome, cognome e email.")

# --- TAB 3: Query SQL custom ---
with tab_query:
    st.markdown("### Esegui una query SQL")
    st.caption("Per query più complesse potete scrivere SQL direttamente.")

    query_default = """SELECT u.nome, u.cognome, s.nome as skill, us.livello_attuale
FROM user_skills us
JOIN users u ON us.user_id = u.id
JOIN skills s ON us.skill_id = s.id
ORDER BY u.cognome, s.nome"""

    query = st.text_area("Query SQL:", value=query_default, height=150)

    if st.button("▶️ Esegui query"):
        try:
            risultati = db.esegui(query)
            if risultati:
                df = pd.DataFrame(risultati)
                st.dataframe(df, use_container_width=True)
                st.caption(f"📊 {len(risultati)} righe trovate")
            else:
                st.info("La query non ha restituito risultati.")
        except Exception as e:
            st.error(f"Errore SQL: {e}")
