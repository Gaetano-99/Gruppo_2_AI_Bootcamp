"""
LearnAI Platform — Login + routing per ruolo.
"""
import sys, os

_ROOT = os.path.abspath(os.path.dirname(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st
from platform_sdk.database import db
from src.core.auth import verifica_credenziali

st.set_page_config(page_title="LearnAI — Login", page_icon="🎓", layout="centered")

# Nasconde la navigazione automatica della sidebar
st.markdown("<style>[data-testid='stSidebarNav']{display:none}</style>", unsafe_allow_html=True)

# DB init (una sola volta)
if "db_initialized" not in st.session_state:
    try:
        db.init()
    except Exception:
        pass
    st.session_state.db_initialized = True

# Se già loggato → redirect immediato
if st.session_state.get("is_logged_in"):
    if st.session_state.get("user_role") in ("docente", "admin"):
        st.switch_page("pages/docente.py")
    else:
        st.switch_page("pages/studente.py")

# Form di login
st.title("🎓 LearnAI Platform")

with st.form("login"):
    email_input = st.text_input("Email")
    password_input = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Accedi", type="primary", use_container_width=True)

if submitted:
    # normalizziamo l'input dell'utente in modo minimale (il backend fa il resto)
    email_to_check = email_input.strip()

    # Passiamo i dati alla funzione di auth
    sessione = verifica_credenziali(email_to_check, password_input)
    
    if sessione:
        # Salviamo la sessione reale nello stato
        st.session_state.is_logged_in = True
        st.session_state.user = sessione
        st.session_state.user_role = sessione["ruolo"]
        
        # ROUTING: Diciamo a Streamlit in quale pagina mandare l'utente
        if sessione["ruolo"] == "docente":
            st.switch_page("pages/docente.py")
        elif sessione["ruolo"] == "studente":
            st.switch_page("pages/studente.py")
    else:
        st.error("Credenziali errate.")

# Accesso ospite
st.divider()
st.caption("Non hai un account?")
if st.button("Accedi come ospite", use_container_width=True):
    st.switch_page("pages/ospite.py")