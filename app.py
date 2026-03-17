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


# ---------------------------------------------------------------------------
# Verifica dipendenze da requirements.txt (auto-install se mancanti)
# ---------------------------------------------------------------------------
def _verifica_e_installa_dipendenze():
    """Controlla che tutti i pacchetti in requirements.txt siano installati.

    Se ne manca qualcuno, lo installa automaticamente con pip.
    Viene eseguito una sola volta all'avvio.
    """
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if not os.path.exists(req_path):
        return

    # Mappa nome-pacchetto → nome-import per i casi in cui differiscono
    _NOME_IMPORT = {
        "python-dotenv": "dotenv",
        "pypdf2": "PyPDF2",
        "pymupdf": "fitz",
        "python-docx": "docx",
        "python-pptx": "pptx",
        "sentence-transformers": "sentence_transformers",
        "langchain-aws": "langchain_aws",
        "langchain-huggingface": "langchain_huggingface",
    }

    mancanti: list[str] = []

    with open(req_path, "r", encoding="utf-8") as f:
        for riga in f:
            riga = riga.strip()
            if not riga or riga.startswith("#"):
                continue
            # Estrai il nome del pacchetto (prima di >=, ==, <, ecc.)
            for sep in (">=", "==", "<=", "!=", "<", ">", "~="):
                if sep in riga:
                    nome_pkg = riga.split(sep)[0].strip()
                    break
            else:
                nome_pkg = riga.strip()

            nome_import = _NOME_IMPORT.get(nome_pkg.lower(), nome_pkg.replace("-", "_"))
            try:
                __import__(nome_import)
            except ImportError:
                mancanti.append(riga)

    if mancanti:
        import subprocess
        print(f"\n[DIPENDENZE] Pacchetti mancanti: {', '.join(mancanti)}")
        print("[DIPENDENZE] Installazione in corso...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", *mancanti],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        print(f"[DIPENDENZE] OK — {len(mancanti)} pacchetti installati con successo.\n")
    else:
        print("[DIPENDENZE] OK — Tutti i pacchetti di requirements.txt sono presenti.")


import streamlit as st

# DEBUG — rimuovere dopo aver risolto il problema di import
st.sidebar.caption(f"Python: {sys.executable}")
st.sidebar.caption(f"Version: {sys.version_info[:3]}")


@st.cache_resource
def _esegui_verifica_dipendenze():
    """Wrapper cached: esegue il check dipendenze una sola volta per sessione."""
    _verifica_e_installa_dipendenze()

_esegui_verifica_dipendenze()

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
    """Rileva desync SQLite/ChromaDB e ri-vettorizza se necessario.

    Al termine stampa un report diagnostico completo sullo stato del
    vector store e del database.
    """
    import traceback

    ok = True
    dettagli_errore: list[str] = []

    # --- 1. Integrità e sync embedding ---------------------------------
    try:
        from src.tools.vector_store import (
            verifica_integrita_vectorstore,
            sincronizza_embeddings_pendenti,
        )

        n_desync = verifica_integrita_vectorstore()
        if n_desync > 0:
            print(f"[INFO app] Vector store: ri-vettorizzati {n_desync} chunk dopo desync.")

        n_pending = sincronizza_embeddings_pendenti()
        if n_pending > 0:
            print(f"[INFO app] Vector store: vettorizzati {n_pending} chunk pendenti.")
    except Exception as e:
        ok = False
        dettagli_errore.append(f"Sync embedding fallita: {e}\n{traceback.format_exc()}")

    # --- 2. Verifica finale coerenza SQLite ↔ ChromaDB -----------------
    try:
        from database import db

        totale_chunks = db.conta("materiali_chunks")
        synced_chunks = db.conta("materiali_chunks", {"embedding_sync": 1})
        pending_chunks = totale_chunks - synced_chunks
        n_materiali = db.conta("materiali_didattici")
        n_corsi = db.conta("corsi_universitari")

        import chromadb, config
        client = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)
        collections = client.list_collections()
        chroma_totale = 0
        chroma_dettaglio: list[str] = []
        for c in collections:
            col = client.get_collection(c.name)
            count = col.count()
            chroma_totale += count
            chroma_dettaglio.append(f"    {c.name}: {count} doc")

        # Segnala anomalie
        if pending_chunks > 0:
            ok = False
            dettagli_errore.append(
                f"{pending_chunks} chunk ancora con embedding_sync=0 dopo la sync"
            )
        if synced_chunks > 0 and chroma_totale == 0:
            ok = False
            dettagli_errore.append(
                "ChromaDB vuoto nonostante chunk marcati come sincronizzati"
            )

        # --- 3. Report diagnostico -------------------------------------
        print("\n" + "=" * 60)
        if ok:
            print(" VECTOR STORE: OK — Tutti i sistemi operativi")
        else:
            print(" VECTOR STORE: ERRORE — Problemi rilevati")
        print("=" * 60)
        print(f"  Corsi:       {n_corsi}")
        print(f"  Materiali:   {n_materiali}")
        print(f"  Chunk tot:   {totale_chunks}  (sync: {synced_chunks}, pending: {pending_chunks})")
        print(f"  ChromaDB:    {chroma_totale} documenti in {len(collections)} collection")
        for d in chroma_dettaglio:
            print(d)

        if not ok:
            print("-" * 60)
            print(" DETTAGLIO ERRORI:")
            for err in dettagli_errore:
                print(f"  - {err}")

        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n[ERRORE app] Diagnostica vector store fallita: {e}")
        print(traceback.format_exc())

    return ok


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
