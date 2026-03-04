# ============================================================================
# LearnAI Platform — Pagina di esempio: Chat con AI
# Questo file mostra come creare un chatbot con Streamlit + LLM.
# Potete usarlo come base per i moduli che richiedono una chat
# (Onboarding, Change Management, etc.)
# ============================================================================

import streamlit as st

st.set_page_config(page_title="💬 Chat AI", page_icon="💬", layout="wide")

st.title("💬 Chat con l'AI")
st.caption("Esempio di chatbot — potete personalizzarlo per il vostro modulo!")

# --- System prompt: qui definite il "carattere" del chatbot ---
SYSTEM_PROMPT = """Sei un assistente della piattaforma LearnAI.
Il tuo compito è aiutare gli utenti con domande sulla formazione e le competenze.
Rispondi sempre in italiano, sii amichevole e professionale.
"""

# --- Inizializza la storia dei messaggi in session_state ---
# session_state è il modo di Streamlit per ricordare dati tra un'interazione e l'altra
if "messaggi_chat" not in st.session_state:
    st.session_state.messaggi_chat = []

# --- Sidebar con info ---
with st.sidebar:
    st.markdown("### ⚙️ Impostazioni Chat")
    usa_streaming = st.toggle("Streaming (risposta in tempo reale)", value=True)

    if st.button("🗑️ Pulisci chat"):
        st.session_state.messaggi_chat = []
        st.rerun()

    st.divider()
    st.markdown("### � Carica un file")
    file_caricato = st.file_uploader(
        "Carica un file da far analizzare all'AI",
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

    st.divider()
    st.markdown("### �💡 Suggerimenti")
    st.markdown("""
    Prova a chiedere:
    - "Quali corsi mi consigli per diventare data analyst?"
    - "Spiegami cos'è il machine learning"
    - "Come posso migliorare le mie competenze in Python?"
    """)

# --- Mostra i messaggi precedenti ---
for msg in st.session_state.messaggi_chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Se l'utente ha caricato un file, aggiungilo al system prompt
_system = SYSTEM_PROMPT
if "contesto_file" in st.session_state:
    _system += f"""

--- CONTENUTO FILE CARICATO DALL'UTENTE ---
{st.session_state['contesto_file']}
--- FINE FILE ---
Usa il contenuto del file per rispondere alle domande dell'utente.
"""

# --- Input dell'utente ---
if domanda := st.chat_input("Scrivi un messaggio..."):
    # Aggiungi il messaggio dell'utente alla storia
    st.session_state.messaggi_chat.append({"role": "user", "content": domanda})

    # Mostra il messaggio dell'utente
    with st.chat_message("user"):
        st.markdown(domanda)

    # Genera la risposta dell'AI
    with st.chat_message("assistant"):
        try:
            if usa_streaming:
                # --- Modalità streaming: la risposta appare parola per parola ---
                from platform_sdk.llm import chat_stream

                risposta_completa = st.write_stream(
                    chat_stream(
                        st.session_state.messaggi_chat,
                        system_prompt=_system,
                    )
                )
            else:
                # --- Modalità normale: la risposta appare tutta insieme ---
                from platform_sdk.llm import chat

                with st.spinner("L'AI sta pensando..."):
                    risposta_completa = chat(
                        st.session_state.messaggi_chat,
                        system_prompt=_system,
                    )
                st.markdown(risposta_completa)

            # Aggiungi la risposta alla storia
            st.session_state.messaggi_chat.append(
                {"role": "assistant", "content": risposta_completa}
            )

        except Exception as e:
            st.error(f"❌ Errore: {e}")
            st.warning("Controlla le credenziali AWS nel file .env")
