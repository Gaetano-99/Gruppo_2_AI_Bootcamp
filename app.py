# ============================================================================
# LearnAI Platform — Entry Point
# Università Federico II di Napoli
#
# Avvio: streamlit run app.py
#
# Routing basato su st.session_state["user"]:
#   None           → pagina di login
#   ruolo=studente → views/studente.py
#   ruolo=docente  → views/docente.py
#   ruolo=admin    → views/admin.py    (futura implementazione)
# ============================================================================

import atexit
import os
import shutil
import sys
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

import streamlit as st

# DEBUG — rimuovere dopo aver risolto il problema di import
st.sidebar.caption(f"Python: {sys.executable}")
st.sidebar.caption(f"Version: {sys.version_info[:3]}")

# ---------------------------------------------------------------------------
# Pulizia file temporanei alla chiusura del server
# ---------------------------------------------------------------------------
_ROOT_DIR = os.path.dirname(__file__)
_UPLOAD_DIR = os.path.join(_ROOT_DIR, "uploads")

def _cleanup_temp():
    if os.path.exists(_UPLOAD_DIR):
        shutil.rmtree(_UPLOAD_DIR, ignore_errors=True)
    for root, _, files in os.walk(_ROOT_DIR):
        if ".claude" in root or "venv" in root:
            continue
        for fname in files:
            if ".tmp" in fname or ".temp" in fname:
                os.remove(os.path.join(root, fname))

atexit.register(_cleanup_temp)

# ---------------------------------------------------------------------------
# Configurazione pagina — deve essere il PRIMO comando Streamlit
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="LearnAI – Federico II",
    page_icon="📓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Import views (dopo set_page_config)
# ---------------------------------------------------------------------------
from views.login import mostra_login
from views.studente import mostra_homepage_studente
from views.docente import mostra_homepage_docente
from views.ospite import mostra_homepage_ospite

# ---------------------------------------------------------------------------
# Mini HTTP server per servire index.html come pagina standalone
# ---------------------------------------------------------------------------
_LANDING_PORT = 8502


class _SilentHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=_ROOT_DIR, **kwargs)

    def log_message(self, format, *args):
        pass  # niente log in console


@st.cache_resource
def _avvia_landing_server():
    try:
        server = HTTPServer(("localhost", _LANDING_PORT), _SilentHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        return True
    except OSError:
        return False  # porta già in uso (server già avviato)


_avvia_landing_server()


# ---------------------------------------------------------------------------
# Verifica integrità vector store (una sola volta per sessione Streamlit)
# ---------------------------------------------------------------------------
@st.cache_resource
def _verifica_vectorstore():
    """Rileva desync SQLite/ChromaDB e ri-vettorizza se necessario."""
    try:
        from src.tools.vector_store import verifica_integrita_vectorstore
        n = verifica_integrita_vectorstore()
        if n > 0:
            print(f"[INFO app] Vector store: ri-vettorizzati {n} chunk dopo desync.")
    except Exception as e:
        print(f"[WARN app] Verifica vector store fallita: {e}")
    return True


_verifica_vectorstore()


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------
def main():
    # Query params routing — dalla landing page HTML esterna
    azione = st.query_params.get("azione", "")
    if azione == "ospite":
        st.session_state.is_logged_in    = True
        st.session_state.current_user_id = "ospite_000"
        st.session_state.user_role       = "Ospite"
        st.session_state.chat_history    = []
        st.session_state.user = {
            "user_id": "ospite_000",
            "nome":    "Ospite",
            "cognome": "",
            "email":   "ospite@unina.it",
            "ruolo":   "Ospite",
            "matricola":          None,
            "corso_di_laurea_id": None,
            "anno_corso":         None,
            "dipartimento":       None,
        }
        st.query_params.clear()
        st.rerun()
    elif azione == "login":
        st.query_params.clear()

    # Gatekeeper — standard STATE_MANAGEMENT.md
    if not st.session_state.get("is_logged_in"):
        mostra_login()
        return

    ruolo = st.session_state.get("user_role", "")  # 'Studente' | 'Docente' | 'Admin'

    if ruolo == "Studente":
        mostra_homepage_studente()
    elif ruolo == "Docente":
        mostra_homepage_docente()
    elif ruolo == "Admin":
        st.info("🚧 Pagina admin in costruzione.")
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()
    elif ruolo == "Ospite":
        mostra_homepage_ospite()
    else:
        st.error("Ruolo non riconosciuto. Effettua il logout.")
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()


if __name__ == "__main__":
    main()
