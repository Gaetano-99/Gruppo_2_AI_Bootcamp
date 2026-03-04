# ============================================================================
# LearnAI Platform — Pagina di esempio: Agente AI
# Questo file mostra come creare un agente LangGraph con tool
# che può interrogare il database e generare risposte intelligenti.
# ============================================================================

import streamlit as st
from langchain_core.tools import tool

st.set_page_config(page_title="🤖 Agente AI", page_icon="🤖", layout="wide")

st.title("🤖 Agente AI con Tool")
st.caption("Esempio di agente LangGraph che può usare strumenti per rispondere!")

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 💡 Cosa può fare l'agente?")
    st.markdown("""
    Questo agente ha accesso a **3 strumenti**:
    1. 🔍 **Cerca utenti** nel database
    2. 📚 **Cerca corsi** nel catalogo
    3. 📊 **Statistiche** della piattaforma

    Prova a chiedere:
    - "Quanti utenti ci sono?"
    - "Mostrami i corsi di Data Science"
    - "Che competenze ha Marco Bianchi?"
    """)

    st.divider()
    st.markdown("### 📎 Carica un file")
    file_caricato = st.file_uploader(
        "Carica un file da far analizzare all'agente",
        type=["txt", "pdf", "csv", "xls", "xlsx"],
        help="Formati supportati: TXT, PDF, CSV, XLS, XLSX",
    )
    if file_caricato:
        from platform_sdk.llm import estrai_testo_da_upload
        testo_file = estrai_testo_da_upload(file_caricato)
        if testo_file:
            st.session_state["contesto_file"] = testo_file
            st.success(f"✅ File **{file_caricato.name}** caricato ({len(testo_file)} caratteri)")
        else:
            st.warning("⚠️ Non è stato possibile estrarre testo dal file.")
    elif "contesto_file" in st.session_state:
        del st.session_state["contesto_file"]

# -----------------------------------------------------------------------
# DEFINIZIONE DEI TOOL
# Ogni tool è una funzione Python decorata con @tool.
# L'agente decide automaticamente quale tool usare in base alla domanda.
# -----------------------------------------------------------------------

from platform_sdk.database import db


@tool
def cerca_utenti(query: str) -> str:
    """Cerca informazioni sugli utenti della piattaforma LearnAI.
    Usa questo strumento quando l'utente chiede di utenti, profili, dipendenti.
    Il parametro query può essere un nome, cognome, ruolo o dipartimento."""

    # Prima prova a cercare per nome
    risultati = db.esegui(
        "SELECT id, nome, cognome, ruolo, dipartimento FROM users "
        "WHERE nome LIKE ? OR cognome LIKE ? OR ruolo LIKE ? OR dipartimento LIKE ?",
        [f"%{query}%"] * 4
    )

    if not risultati:
        # Se non trova nulla, restituisci tutti
        risultati = db.esegui("SELECT id, nome, cognome, ruolo, dipartimento FROM users")
        return f"Nessun risultato per '{query}'. Ecco tutti gli utenti:\n{risultati}"

    return str(risultati)


@tool
def cerca_corsi(query: str) -> str:
    """Cerca corsi nel catalogo formativo della piattaforma LearnAI.
    Usa questo strumento quando l'utente chiede di corsi, formazione, training.
    Il parametro query può essere un titolo, categoria o livello."""

    risultati = db.esegui(
        "SELECT id, titolo, categoria, livello, durata_ore FROM courses "
        "WHERE titolo LIKE ? OR categoria LIKE ? OR livello LIKE ?",
        [f"%{query}%"] * 3
    )

    if not risultati:
        risultati = db.esegui("SELECT id, titolo, categoria, livello, durata_ore FROM courses")
        return f"Nessun risultato per '{query}'. Ecco tutti i corsi:\n{risultati}"

    return str(risultati)


@tool
def statistiche_piattaforma() -> str:
    """Restituisce le statistiche generali della piattaforma LearnAI.
    Usa questo strumento quando l'utente chiede numeri, statistiche, overview."""

    n_utenti = db.conta("users")
    n_corsi = db.conta("courses")
    n_skills = db.conta("skills")
    n_piani = db.conta("training_plans")

    return (
        f"Statistiche LearnAI:\n"
        f"- Utenti registrati: {n_utenti}\n"
        f"- Corsi nel catalogo: {n_corsi}\n"
        f"- Competenze tracciate: {n_skills}\n"
        f"- Piani formativi creati: {n_piani}"
    )


# -----------------------------------------------------------------------
# CREAZIONE DELL'AGENTE
# L'agente viene creato una sola volta e memorizzato in session_state
# -----------------------------------------------------------------------

if "agente" not in st.session_state:
    from platform_sdk.agent import crea_agente

    st.session_state.agente = crea_agente(
        tools=[cerca_utenti, cerca_corsi, statistiche_piattaforma],
        system_prompt=(
            "Sei un assistente della piattaforma LearnAI. "
            "Hai accesso a strumenti per cercare utenti, corsi e statistiche. "
            "Usa gli strumenti quando necessario per dare risposte accurate. "
            "Rispondi sempre in italiano in modo chiaro e amichevole."
        ),
    )

if "messaggi_agente" not in st.session_state:
    st.session_state.messaggi_agente = []

# --- Pulsante reset ---
if st.sidebar.button("🗑️ Pulisci conversazione"):
    st.session_state.messaggi_agente = []
    # Ricrea l'agente per pulire la memoria
    from platform_sdk.agent import crea_agente
    st.session_state.agente = crea_agente(
        tools=[cerca_utenti, cerca_corsi, statistiche_piattaforma],
        system_prompt=(
            "Sei un assistente della piattaforma LearnAI. "
            "Hai accesso a strumenti per cercare utenti, corsi e statistiche. "
            "Usa gli strumenti quando necessario per dare risposte accurate. "
            "Rispondi sempre in italiano in modo chiaro e amichevole."
        ),
    )
    st.rerun()

# --- Mostra messaggi precedenti ---
for msg in st.session_state.messaggi_agente:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Input utente ---
if domanda := st.chat_input("Chiedi qualcosa all'agente..."):
    # Mostra la domanda
    st.session_state.messaggi_agente.append({"role": "user", "content": domanda})
    with st.chat_message("user"):
        st.markdown(domanda)

    # Genera risposta dall'agente
    with st.chat_message("assistant"):
        with st.spinner("🤖 L'agente sta ragionando e usando i suoi strumenti..."):
            try:
                from platform_sdk.agent import esegui_agente

                # Se c'è un file caricato, aggiungi il contesto alla domanda
                _domanda = domanda
                if "contesto_file" in st.session_state:
                    _domanda = f"""L'utente ha caricato un file con questo contenuto:

--- CONTENUTO FILE ---
{st.session_state['contesto_file']}
--- FINE FILE ---

Domanda dell'utente: {domanda}"""

                risposta = esegui_agente(
                    st.session_state.agente,
                    _domanda,
                    thread_id="streamlit_session",
                )
                st.markdown(risposta)

                st.session_state.messaggi_agente.append(
                    {"role": "assistant", "content": risposta}
                )

            except Exception as e:
                st.error(f"❌ Errore dell'agente: {e}")
                st.warning("Controlla le credenziali AWS nel file .env")
