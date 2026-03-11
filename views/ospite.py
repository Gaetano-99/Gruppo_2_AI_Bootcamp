"""
views/ospite.py
Pagina di onboarding per ospiti: questionario strutturato + chat libera con l'AI.

Flusso:
  1. Questionario strutturato (5 domande a scelta multipla)
  2. L'agente analizza le risposte e propone 2-3 corsi di laurea
  3. Chat libera per approfondire
"""
import sys
import os

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st
from src.agents.orientamento import (
    chiedi_agente_ospite,
    analizza_questionario,
    DOMANDE_QUESTIONARIO,
)

_CSS = """
<style>
.quest-card {
    background: #fff;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: 0 2px 10px rgba(0,48,135,0.08);
    border-left: 4px solid #003087;
}
.quest-num {
    font-size: 0.72rem;
    font-weight: 700;
    color: #C5A028;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 6px;
}
.quest-testo {
    font-size: 1rem;
    font-weight: 600;
    color: #001A4D;
    margin-bottom: 12px;
}
.rec-box {
    background: linear-gradient(135deg, #EEF4FF, #F6F9FF);
    border: 1px solid #BFCFE8;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
}
</style>
"""


def mostra_homepage_ospite():
    st.markdown("<style>[data-testid='stSidebarNav']{display:none}</style>", unsafe_allow_html=True)
    st.markdown(_CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### Orientamento")
        st.info("Benvenuto nell'area Ospiti. Compila il questionario per ricevere consigli personalizzati sui corsi di laurea.")
        if st.button("← Torna al Login", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        # Pulsante per ricominciare il questionario
        if st.session_state.get("_ospite_completato"):
            if st.button("🔄 Rifai il questionario", use_container_width=True):
                for k in list(st.session_state.keys()):
                    if k.startswith("_ospite") or k == "chat_ospite":
                        del st.session_state[k]
                st.rerun()

    st.title("Scopri il tuo Corso di Laurea 🎓")

    # ----------------------------------------------------------------
    # FASE 1 — Questionario strutturato
    # ----------------------------------------------------------------
    if not st.session_state.get("_ospite_completato"):
        st.markdown("Rispondi a **5 brevi domande** per ricevere una raccomandazione personalizzata.")
        st.divider()

        with st.form("questionario_orientamento"):
            risposte: dict[str, str] = {}
            for i, dom in enumerate(DOMANDE_QUESTIONARIO, 1):
                st.markdown(
                    f'<div class="quest-card">'
                    f'<div class="quest-num">Domanda {i} di {len(DOMANDE_QUESTIONARIO)}</div>'
                    f'<div class="quest-testo">{dom["testo"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                scelta = st.radio(
                    label=dom["testo"],
                    options=dom["opzioni"],
                    key=f"_quest_{dom['id']}",
                    label_visibility="collapsed",
                )
                risposte[dom["id"]] = scelta

            submitted = st.form_submit_button("Scopri i corsi adatti a me →", type="primary", use_container_width=True)

        if submitted:
            st.session_state["_ospite_risposte"] = risposte
            with st.spinner("Lea sta analizzando il tuo profilo..."):
                try:
                    raccomandazione = analizza_questionario(risposte)
                    st.session_state["_ospite_raccomandazione"] = raccomandazione
                    st.session_state["_ospite_completato"] = True
                    # Pre-popola la chat con il risultato
                    st.session_state["chat_ospite"] = [
                        {"ruolo": "assistant", "contenuto": raccomandazione}
                    ]
                except Exception as e:
                    st.error(f"Errore durante l'analisi: {e}")
            st.rerun()
        return

    # ----------------------------------------------------------------
    # FASE 2 — Raccomandazione + chat libera
    # ----------------------------------------------------------------
    st.markdown("### Le tue raccomandazioni personalizzate")
    raccomandazione = st.session_state.get("_ospite_raccomandazione", "")
    if raccomandazione:
        st.markdown(f'<div class="rec-box">{raccomandazione}</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("#### Vuoi saperne di più? Chiedimi qualsiasi cosa sui corsi!")

    # Suggerimenti rapidi post-raccomandazione
    suggerimenti = [
        "Spiegami le differenze tra i corsi consigliati",
        "Quali sono gli sbocchi lavorativi?",
        "Cosa si studia nel primo anno?",
    ]
    cols = st.columns(len(suggerimenti))
    domanda_cliccata = None
    for i, sugg in enumerate(suggerimenti):
        with cols[i]:
            if st.button(sugg, use_container_width=True, key=f"sugg_{i}"):
                domanda_cliccata = sugg

    st.divider()

    if "chat_ospite" not in st.session_state:
        st.session_state["chat_ospite"] = []

    # Mostra storia chat (salta il primo messaggio già mostrato come raccomandazione)
    for msg in st.session_state["chat_ospite"][1:]:
        with st.chat_message(msg["ruolo"]):
            st.markdown(msg["contenuto"])

    prompt = st.chat_input("Chiedi info sui corsi (es. 'Quanto dura Informatica?')...")
    if domanda_cliccata:
        prompt = domanda_cliccata

    if prompt:
        st.session_state["chat_ospite"].append({"ruolo": "user", "contenuto": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("L'assistente sta controllando il catalogo corsi..."):
                try:
                    cronologia_passata = st.session_state["chat_ospite"][:-1]
                    risposta = chiedi_agente_ospite(domanda=prompt, cronologia=cronologia_passata)
                    st.markdown(risposta)
                    st.session_state["chat_ospite"].append({"ruolo": "assistant", "contenuto": risposta})
                except Exception as e:
                    err_msg = f"Si è verificato un errore temporaneo: {e}"
                    st.error(err_msg)
                    st.session_state["chat_ospite"].append({"ruolo": "assistant", "contenuto": err_msg})
