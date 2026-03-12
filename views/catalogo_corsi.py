import streamlit as st
import json
from platform_sdk.database import db

def mostra_catalogo_ospite():
    st.title("Catalogo Corsi di Laurea 📚")
    
    if st.button("← Torna alla Home", key="btn_back_catalogo"):
        st.session_state["vista_ospite"] = "home"
        st.rerun()
        
    st.markdown("Esplora l'offerta formativa dell'università.")
    
    # Recupera i corsi dal DB
    corsi = db.trova_tutti("corsi_di_laurea", ordine="facolta ASC, nome ASC")
    
    if not corsi:
        st.warning("Nessun corso trovato nel catalogo.")
        return
        
    # Group by facolta
    facolta_corrente = None
    for corso in corsi:
        if corso["facolta"] != facolta_corrente:
            facolta_corrente = corso["facolta"]
            st.header(f"Area: {facolta_corrente}")
            
        with st.expander(f"{corso['nome']} - {corso['tipo']}"):
            if corso['descrizione']:
                st.markdown(f"**Descrizione:** {corso['descrizione']}")
            if corso['durata']:
                st.markdown(f"**Durata:** {corso['durata']}")
            
            if corso['materie_principali_json']:
                try:
                    materie = json.loads(corso['materie_principali_json'])
                    st.markdown("**Materie principali:** " + ", ".join(materie))
                except:
                    pass
            if corso['sbocchi_lavorativi_json']:
                try:
                    sbocchi = json.loads(corso['sbocchi_lavorativi_json'])
                    st.markdown("**Sbocchi lavorativi:** " + ", ".join(sbocchi))
                except:
                    pass
