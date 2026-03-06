"""Chat per ospiti — Onboarding studenti non registrati."""
import sys, os
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st

st.set_page_config(
    page_title="LearnAI — Chat Ospite",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Nasconde sidebar e navigazione automatica
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] { display: none !important; }
        [data-testid="stSidebar"]    { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Intestazione ─────────────────────────────────────────────────────────────
st.title("💬 Chat Ospite")
st.caption("Stai usando LearnAI come ospite. [← Torna al login](/) per accedere con il tuo account.")
st.divider()

# ─── Cronologia messaggi ──────────────────────────────────────────────────────
SYSTEM_PROMPT = (
    "Sei un assistente AI della piattaforma LearnAI, specializzato nell'onboarding "
    "di nuovi studenti. Aiuta l'ospite a capire la piattaforma, i percorsi formativi "
    "disponibili e come registrarsi. Rispondi sempre in italiano in modo chiaro e conciso."
)

if "ospite_messaggi" not in st.session_state:
    st.session_state.ospite_messaggi = []

# Mostra la cronologia
for msg in st.session_state.ospite_messaggi:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ─── Input e Generazione ──────────────────────────────────────────────────────
prompt = st.chat_input("Scrivi un messaggio…")

if prompt:
    # 1. Salva e mostra il messaggio dell'utente
    st.session_state.ospite_messaggi.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Genera e mostra la risposta (usando chat normale per aggirare problema streaming boto3)
    with st.chat_message("assistant"):
        try:
            from platform_sdk.llm import chat

            with st.spinner("Sto scrivendo..."):
                risposta_completa = chat(st.session_state.ospite_messaggi, system_prompt=SYSTEM_PROMPT)
                
            st.markdown(risposta_completa)

            # Salva la risposta nella cronologia
            st.session_state.ospite_messaggi.append({"role": "assistant", "content": risposta_completa})

        except Exception as e:
            st.error(f"⚠️ Errore LLM: {e}")