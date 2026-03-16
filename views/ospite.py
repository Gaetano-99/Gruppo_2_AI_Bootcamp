"""
views/ospite.py
Pagina di onboarding per ospiti.

Flusso:
  - Home: FAQ + bottoni "Esplora Corsi" / "Questionario" + chatbot Lea
  - Catalogo: griglia di corsi letti dal DB
  - Questionario: 30 domande + analisi LLM del percorso
"""
import sys
import os

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st
from src.agents.orientamento import chiedi_agente_ospite
from views.catalogo_corsi import mostra_catalogo
from views.questionario_ospite import mostra_questionario

_CSS = """
<style>
.hero-banner {
    background: linear-gradient(135deg, #001A4D 0%, #003087 60%, #0057B8 100%);
    border-radius: 18px;
    padding: 36px 40px;
    margin-bottom: 28px;
    color: white;
}
.hero-banner h1 { color: white; margin: 0 0 8px 0; font-size: 2rem; }
.hero-banner p  { color: rgba(255,255,255,0.88); margin: 0; font-size: 1.05rem; }
.faq-section {
    background: #F6F9FF;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 24px;
    border: 1px solid #DAEAFF;
}
.action-card {
    border-radius: 14px;
    padding: 24px 26px;
    text-align: center;
    border: 2px solid transparent;
    cursor: pointer;
    transition: all 0.2s;
}
.action-card-primary {
    background: linear-gradient(135deg, #003087, #0057B8);
    color: white;
}
.action-card-secondary {
    background: linear-gradient(135deg, #C5A028, #E8BA30);
    color: white;
}
.action-card h3 { margin: 0 0 6px 0; font-size: 1.2rem; color: white; }
.action-card p  { margin: 0; font-size: 0.88rem; color: rgba(255,255,255,0.88); }
.section-label {
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #003087;
    margin: 28px 0 12px 0;
}
.chat-intro {
    background: #EEF4FF;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 16px;
    border-left: 4px solid #0057B8;
    font-size: 0.95rem;
    color: #001A4D;
}
</style>
"""

# FAQ items
_FAQ = [
    ("📅 Quando inizia l'anno accademico?", "L'anno accademico inizia solitamente a ottobre. Le iscrizioni aprono in estate, di norma tra giugno e settembre."),
    ("💰 Quanto costano le tasse universitarie?", "Le tasse variano in base all'ISEE familiare e variano da circa €200 a €3.000 all'anno. Sono previste esenzioni per borse di studio."),
    ("🔬 Esistono opportunità di tirocinio?", "Sì, la maggior parte dei corsi prevede tirocini obbligatori o facoltativi presso aziende partner e strutture convenzionate."),
    ("🌍 Posso studiare all'estero?", "Certo! Il programma Erasmus+ ti permette di trascorrere da 3 a 12 mesi in un'università europea, con borsa di studio."),
    ("📋 Come funzionano i test di ammissione?", "Alcuni corsi (es. Medicina, Architettura) hanno accesso programmato con test nazionale. Altri sono ad accesso libero."),
]


def mostra_homepage_ospite():
    """Entry point principale per la pagina ospite. Gestisce il routing tra home, catalogo e questionario."""
    st.markdown("<style>[data-testid='stSidebarNav']{display:none}</style>", unsafe_allow_html=True)
    st.markdown(_CSS, unsafe_allow_html=True)

    # Inizializza lo stato di routing
    if "ospite_pagina" not in st.session_state:
        st.session_state["ospite_pagina"] = "home"

    # Sidebar
    with st.sidebar:
        st.markdown("### Area Ospiti")
        st.info("Esplora i corsi, compila il questionario di orientamento o chatta con Lea!")
        if st.button("← Torna al Login", use_container_width=True, key="btn_login_sidebar"):
            st.session_state.clear()
            st.rerun()
        st.markdown("---")
        st.markdown("**Navigazione rapida**")
        if st.button("🏠 Home", use_container_width=True, key="sidebar_home"):
            st.session_state["ospite_pagina"] = "home"
            st.rerun()
        if st.button("📚 Catalogo Corsi", use_container_width=True, key="sidebar_catalogo"):
            st.session_state["ospite_pagina"] = "catalogo"
            st.rerun()
        if st.button("🎯 Questionario", use_container_width=True, key="sidebar_quest"):
            st.session_state["ospite_pagina"] = "questionario"
            st.rerun()

    # Routing
    pagina = st.session_state.get("ospite_pagina", "home")

    if pagina == "catalogo":
        mostra_catalogo()
        return

    if pagina == "questionario":
        mostra_questionario()
        return

    # -------------------------------------------------------------------------
    # PAGINA HOME
    # -------------------------------------------------------------------------
    _render_home()


def _render_home():
    """Renderizza la home page dell'ospite: FAQ + bottoni + chatbot."""

    # Hero banner
    st.markdown("""
    <div class="hero-banner">
        <h1>Scopri il tuo percorso universitario 🎓</h1>
        <p>Benvenuto/a! Sono <strong>Lea</strong>, la tua assistente di orientamento.
        Esplora il catalogo dei corsi, fai il questionario o chiedimi qualsiasi cosa sui percorsi di studio.</p>
    </div>
    """, unsafe_allow_html=True)

    # FAQ collassabili
    st.markdown('<div class="section-label">❓ Domande frequenti</div>', unsafe_allow_html=True)
    with st.container():
        for domanda, risposta in _FAQ:
            with st.expander(domanda):
                st.markdown(risposta)

    st.markdown("---")

    # Bottoni principali
    st.markdown('<div class="section-label">🚀 Da dove vuoi iniziare?</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2, gap="medium")

    with col_a:
        st.markdown("""
        <div class="action-card action-card-primary">
            <h3>📚 Esplora Corsi</h3>
            <p>Sfoglia tutti i corsi di laurea disponibili con descrizioni e facoltà.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📚 Esplora Corsi", use_container_width=True, type="primary", key="btn_catalogo_home"):
            st.session_state["ospite_pagina"] = "catalogo"
            st.rerun()

    with col_b:
        st.markdown("""
        <div class="action-card action-card-secondary">
            <h3>🎯 Questionario</h3>
            <p>30 domande per scoprire il percorso di studi più adatto al tuo profilo.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🎯 Fai il Questionario", use_container_width=True, key="btn_questionario_home"):
            st.session_state["ospite_pagina"] = "questionario"
            st.rerun()

    st.markdown("---")

    # Chatbot Lea
    st.markdown('<div class="section-label">💬 Chatta con Lea</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="chat-intro">
        👋 Puoi chiedermi qualsiasi cosa sui corsi di laurea: durata, materie, sbocchi lavorativi,
        differenze tra percorsi simili e molto altro.
        <br><br>
        <em>Suggerimenti: "Cosa si studia a Ingegneria Informatica?",
        "Qual è la differenza tra Economia e Giurisprudenza?",
        "Quali corsi offrono accesso al mondo della finanza?"</em>
    </div>
    """, unsafe_allow_html=True)

    # Suggerimenti rapidi
    suggerimenti = [
        "🖥️ Cosa si studia a Informatica?",
        "💼 Sbocchi lavorativi di Economia?",
        "⚕️ Come si accede a Medicina?",
    ]
    cols = st.columns(len(suggerimenti))
    domanda_cliccata = None
    for i, sugg in enumerate(suggerimenti):
        with cols[i]:
            if st.button(sugg, use_container_width=True, key=f"sugg_home_{i}"):
                domanda_cliccata = sugg

    st.markdown("")

    # Inizializza la chat
    if "chat_ospite" not in st.session_state:
        st.session_state["chat_ospite"] = []

    # Mostra la storia della chat
    for msg in st.session_state["chat_ospite"]:
        with st.chat_message(msg["ruolo"]):
            st.markdown(msg["contenuto"])

    # Input chat
    prompt = st.chat_input("Chiedi a Lea info sui corsi (es. 'Quanto dura Ingegneria?')...")
    if domanda_cliccata:
        prompt = domanda_cliccata

    if prompt:
        st.session_state["chat_ospite"].append({"ruolo": "user", "contenuto": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Lea sta consultando il catalogo corsi..."):
                try:
                    cronologia_passata = st.session_state["chat_ospite"][:-1]
                    risposta = chiedi_agente_ospite(domanda=prompt, cronologia=cronologia_passata)
                    st.markdown(risposta)
                    st.session_state["chat_ospite"].append({"ruolo": "assistant", "contenuto": risposta})
                except Exception as e:
                    err_msg = f"Si è verificato un errore temporaneo: {e}"
                    st.error(err_msg)
                    st.session_state["chat_ospite"].append({"ruolo": "assistant", "contenuto": err_msg})
