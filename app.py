"""
LearnAI Platform — App Shell (branch: foundation/backend-core)

Entry point minimale Streamlit.
- Inizializza il DB all'avvio.
- Mostra un form di login che chiama verifica_credenziali() dal backend.
- In caso di successo: salva UserSession in st.session_state e mostra ruolo + ID.
- Nessun routing, nessuna dashboard, nessuna UI complessa.
"""

import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

_ROOT = os.path.abspath(os.path.dirname(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st
from platform_sdk.database import db
from src.core.auth import verifica_credenziali

# ---------------------------------------------------------------------------
# Configurazione
# ---------------------------------------------------------------------------
st.set_page_config(page_title="LearnAI — Login", page_icon="🎓", layout="centered")

# ---------------------------------------------------------------------------
# Inizializzazione DB (una sola volta)
# ---------------------------------------------------------------------------
if "db_initialized" not in st.session_state:
    try:
        db.init()
    except Exception:
        pass
    st.session_state.db_initialized = True

# ---------------------------------------------------------------------------
# Se già loggato — mostra sessione attiva
# ---------------------------------------------------------------------------
if st.session_state.get("is_logged_in"):
    sessione = st.session_state.current_user
    st.success(f"Autenticazione riuscita. Ruolo: **{sessione['ruolo']}**")
    st.json({
        "user_id": sessione["user_id"],
        "email":   sessione["email"],
        "nome":    sessione["nome"],
        "cognome": sessione["cognome"],
        "ruolo":   sessione["ruolo"],
    })
    if st.button("Logout"):
        st.session_state.is_logged_in = False
        st.session_state.current_user = None
        st.session_state.user_role = None
        st.rerun()
    st.stop()

# ---------------------------------------------------------------------------
# Form di login
# ---------------------------------------------------------------------------
st.title("🎓 LearnAI Platform")
st.caption("branch: foundation/backend-core")

with st.form("login"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login", type="primary", use_container_width=True)

if submitted:
    sessione = verifica_credenziali(email, password)
    if sessione:
        st.session_state.is_logged_in = True
        st.session_state.current_user = sessione
        st.session_state.user_id = sessione["user_id"]
        st.session_state.user_role = sessione["ruolo"]
        st.rerun()
    else:
        st.error("Credenziali errate o account non attivo.")
