"""
pages/ospite.py
Pagina di onboarding per ospiti: permette di esplorare i corsi di laurea con l'aiuto dell'AI.
"""
import sys
import os

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st
from src.agents.orientamento import chiedi_agente_ospite

def mostra_homepage_ospite():
    # Nascondi sidebar nativa per evitare navigazione incontrollata
    st.markdown("<style>[data-testid='stSidebarNav']{display:none}</style>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### Orientamento")
        st.info("Benvenuto nell'area Ospiti. Qui puoi esplorare i corsi di laurea disponibili.")
        if st.button("← Torna al Login", use_container_width=True):
            # 1. Pulisci la sessione (rimuove is_logged_in e user_role)
            st.session_state.clear() 
            # 2. Riavvia l'app (app.py vedrà che non sei loggato e caricherà login.py)
            st.rerun()
    st.title("Esplora i Corsi di Laurea 🎓")
    st.markdown("Fai una domanda per scoprire quale corso di laurea è più adatto a te!")

    # Inizializza cronologia specifica per ospite se non esiste
    if "chat_ospite" not in st.session_state:
        st.session_state["chat_ospite"] = []

    # Suggerimenti (chip)
    suggerimenti = [
        "Cosa si studia a Ingegneria?",
        "Quali sono gli sbocchi di Economia?",
        "Che differenza c'è tra Matematica e Fisica?"
    ]

    st.markdown("**Domande frequenti:**")
    cols = st.columns(len(suggerimenti))
    domanda_cliccata = None

    for i, sugg in enumerate(suggerimenti):
        with cols[i]:
            # Lo st.button restituisce True solo nel momento in cui viene cliccato
            if st.button(sugg, use_container_width=True):
                domanda_cliccata = sugg

    st.divider()

    # Disegna la chat history
    for msg in st.session_state["chat_ospite"]:
        with st.chat_message(msg["ruolo"]):
            st.markdown(msg["contenuto"])

    # Priorità: se ha cliccato un bottone, o se ha scritto nel chat input
    prompt = st.chat_input("Chiedi info sui corsi (es. 'Quanto dura Informatica?')...")

    # Override con pulsante se valorizzato
    if domanda_cliccata:
        prompt = domanda_cliccata

    if prompt:
        # Mostra messaggio utente nella history e a schermo
        st.session_state["chat_ospite"].append({"ruolo": "user", "contenuto": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Invocazione agente AI
        with st.chat_message("assistant"):
            with st.spinner("L'assistente sta controllando il catalogo corsi..."):
                try:
                    # Passa la cronologia meno l'ultimo elemento (che è la domanda corrente)
                    cronologia_passata = st.session_state["chat_ospite"][:-1]
                    
                    risposta = chiedi_agente_ospite(
                        domanda=prompt, 
                        cronologia=cronologia_passata
                    )
                    st.markdown(risposta)
                    st.session_state["chat_ospite"].append({"ruolo": "assistant", "contenuto": risposta})
                except Exception as e:
                    err_msg = f"Si è verificato un errore temporaneo: {e}"
                    st.error(err_msg)
                    st.session_state["chat_ospite"].append({"ruolo": "assistant", "contenuto": err_msg})
