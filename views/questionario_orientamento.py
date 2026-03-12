import streamlit as st
import json
from src.agents.dati_questionario import QUESTIONARIO_ORIENTAMENTO
from src.agents.orientamento import analizza_risposte_questionario

def mostra_questionario_ospite():
    st.title("Questionario di Orientamento 🧭")
    
    if st.button("← Torna alla Home", key="btn_back_quest"):
        st.session_state["vista_ospite"] = "home"
        st.rerun()
    
    if "risposte_quest" not in st.session_state:
        st.session_state["risposte_quest"] = {}
        
    if "esito_quest" in st.session_state:
        st.success("Questionario completato!")
        st.markdown("### Il tuo consiglio di orientamento personalizzato:")
        st.markdown(st.session_state["esito_quest"])
        if st.button("Rifai il questionario"):
            del st.session_state["esito_quest"]
            st.session_state["risposte_quest"] = {}
            st.rerun()
        return

    st.markdown("Rispondi a queste 30 domande per ricevere un consiglio personalizzato sul tuo futuro universitario!")
    
    with st.form("form_questionario"):
        for q in QUESTIONARIO_ORIENTAMENTO:
            st.markdown(f"**{q['id']}. {q['domanda']}**")
            scelta = st.radio(
                "Scegli un'opzione",
                options=q["opzioni"],
                key=f"q_{q['id']}",
                label_visibility="collapsed"
            )
            st.session_state["risposte_quest"][q['id']] = scelta
            st.markdown("---")
            
        submit = st.form_submit_button("Invia Risposte")
        if submit:
            with st.spinner("L'intelligenza artificiale sta analizzando le tue risposte..."):
                esito = analizza_risposte_questionario(st.session_state["risposte_quest"])
                st.session_state["esito_quest"] = esito
            st.rerun()
