"""
views/questionario_ospite.py
Pagina questionario di orientamento per gli ospiti (30 domande, 4 opzioni ciascuna).
Le domande sono suddivise in 3 pagine da 10. Alla fine, un agente LLM analizza
le risposte e consiglia il percorso di studi più adatto.
Dopo i risultati è disponibile una chat inline con Lea per approfondire.
"""
import sys
import os

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st
from src.agents.orientamento import DOMANDE_QUESTIONARIO, analizza_questionario_esteso, chiedi_agente_ospite

_CSS = """
<style>
.quest-header {
    background: linear-gradient(135deg, #003087 0%, #0057B8 100%);
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 28px;
    color: white;
}
.quest-header h1 { color: white; margin: 0 0 6px 0; font-size: 1.8rem; }
.quest-header p { color: rgba(255,255,255,0.85); margin: 0; }
.progress-label {
    font-size: 0.82rem;
    color: #666;
    margin-bottom: 4px;
}
.domanda-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 18px;
    border-left: 4px solid #003087;
    box-shadow: 0 2px 10px rgba(0,48,135,0.07);
}
.domanda-num {
    font-size: 0.72rem;
    font-weight: 700;
    color: #C5A028;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 6px;
}
.domanda-cat {
    font-size: 0.72rem;
    background: #EEF4FF;
    color: #0057B8;
    border-radius: 20px;
    padding: 2px 10px;
    display: inline-block;
    margin-bottom: 8px;
}
.domanda-testo {
    font-size: 1.0rem;
    font-weight: 600;
    color: #001A4D;
    margin-bottom: 10px;
}
.risultato-box {
    background: linear-gradient(135deg, #EEF4FF, #F6F9FF);
    border: 1px solid #BFCFE8;
    border-radius: 14px;
    padding: 28px 32px;
    margin: 20px 0;
}
.chat-intro-box {
    background: #EEF4FF;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 16px;
    border-left: 4px solid #0057B8;
    font-size: 0.95rem;
    color: #001A4D;
}
[data-testid="stChatInput"] {
    background-color: #ffffff !important;
    border: 2px solid #DAEAFF !important;
    border-radius: 25px !important;
    box-shadow: 0 4px 6px rgba(0, 48, 135, 0.08) !important;
    transition: all 0.3s ease;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #0057B8 !important;
    box-shadow: 0 6px 12px rgba(0, 87, 184, 0.15) !important;
}
[data-testid="stChatInput"] button {
    background-color: #0057B8 !important;
    color: white !important;
    border-radius: 50% !important;
    padding: 8px !important;
    transition: all 0.2s ease;
}
[data-testid="stChatInput"] button:hover {
    background-color: #003087 !important;
    transform: scale(1.05);
}
[data-testid="stChatInput"] button svg {
    fill: white !important;
}
</style>
"""

# Script scroll: iniettato come st.markdown, targeting tutti i possibili
# contenitori scrollabili di Streamlit. Viene triggerato solo quando
# st.session_state["_scroll_top"] è True, poi resettato subito.
_SCROLL_SCRIPT = """
<script>
(function() {
    function doScroll() {
        var doc = window.parent.document;
        // Streamlit >= 1.x: il main content è in [data-testid="stAppViewContainer"]
        // oppure nella sezione .main > div oppure in .block-container
        var targets = [
            doc.querySelector('[data-testid="stAppViewContainer"]'),
            doc.querySelector('.main'),
            doc.querySelector('.block-container'),
            doc.documentElement,
            doc.body
        ];
        targets.forEach(function(el) {
            if (el) el.scrollTop = 0;
        });
        // Fallback: scroll della finestra parent
        window.parent.scrollTo(0, 0);
    }

    // Prima esecuzione immediata
    doScroll();
    // Secondo tentativo dopo il re-render di Streamlit
    setTimeout(doScroll, 80);
    setTimeout(doScroll, 250);
})();
</script>
"""

DOMANDE_PER_PAGINA = 10
TOTALE_PAGINE = 3  # 30 domande / 10 per pagina


def _init_stato():
    """Inizializza lo stato del questionario nella sessione."""
    if "quest_pagina" not in st.session_state:
        st.session_state["quest_pagina"] = 0
    if "quest_risposte" not in st.session_state:
        st.session_state["quest_risposte"] = {}
    if "quest_completato" not in st.session_state:
        st.session_state["quest_completato"] = False
    if "quest_risultato" not in st.session_state:
        st.session_state["quest_risultato"] = ""
    if "_scroll_top" not in st.session_state:
        st.session_state["_scroll_top"] = False


def _maybe_scroll():
    """
    Inietta lo script di scroll via st.markdown (non components.html).
    st.markdown con unsafe_allow_html=True esegue il tag <script> nel
    contesto del documento parent di Streamlit, che ha accesso diretto
    ai container scrollabili — a differenza di components.html che gira
    in un iframe sandboxato separato con il suo scroll context.
    """
    if st.session_state.get("_scroll_top"):
        st.markdown(_SCROLL_SCRIPT, unsafe_allow_html=True)
        st.session_state["_scroll_top"] = False


def mostra_questionario():
    """Renderizza la pagina questionario di orientamento."""
    st.markdown(_CSS, unsafe_allow_html=True)
    _init_stato()

    # Scroll top se richiesto (dopo cambio pagina o submit)
    _maybe_scroll()

    # Header
    st.markdown("""
    <div class="quest-header">
        <h1>🎯 Questionario di Orientamento</h1>
        <p>30 domande per scoprire il percorso universitario più adatto a te.
        Rispondi sinceramente: non ci sono risposte giuste o sbagliate!</p>
    </div>
    """, unsafe_allow_html=True)

    # Se completato, mostra il risultato + chat
    if st.session_state["quest_completato"]:
        _mostra_risultato()
        return

    pagina_corrente = st.session_state["quest_pagina"]

    # Progress bar
    domande_risposte = len(st.session_state["quest_risposte"])
    progresso = domande_risposte / len(DOMANDE_QUESTIONARIO)
    st.markdown(
        f'<div class="progress-label">Progresso: <b>{domande_risposte}/{len(DOMANDE_QUESTIONARIO)}</b> domande</div>',
        unsafe_allow_html=True,
    )
    st.progress(progresso)

    # Bottone torna
    col_nav, _ = st.columns([1, 4])
    with col_nav:
        if st.button("← Torna alla home", key="btn_torna_quest_top"):
            st.session_state["ospite_pagina"] = "home"
            st.rerun()

    st.markdown("---")

    # Calcola le domande di questa pagina
    idx_start = pagina_corrente * DOMANDE_PER_PAGINA
    idx_end = idx_start + DOMANDE_PER_PAGINA
    domande_pagina = DOMANDE_QUESTIONARIO[idx_start:idx_end]

    # Indicatore pagina
    st.markdown(
        f"**Sezione {pagina_corrente + 1} di {TOTALE_PAGINE}** "
        f"— Domande {idx_start + 1}–{min(idx_end, len(DOMANDE_QUESTIONARIO))}",
    )
    st.markdown("")

    # Render domande con form
    with st.form(key=f"form_quest_pag_{pagina_corrente}"):
        risposte_pagina = {}

        for i, dom in enumerate(domande_pagina, idx_start + 1):
            categoria = dom.get("categoria", "")
            st.markdown(
                f'<div class="domanda-card">'
                f'<div class="domanda-num">Domanda {i} di {len(DOMANDE_QUESTIONARIO)}</div>'
                f'<div class="domanda-cat">📌 {categoria}</div>'
                f'<div class="domanda-testo">{dom["testo"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            val_precedente = st.session_state["quest_risposte"].get(dom["id"])
            idx_default = dom["opzioni"].index(val_precedente) if val_precedente in dom["opzioni"] else 0

            scelta = st.radio(
                label=dom["testo"],
                options=dom["opzioni"],
                index=idx_default,
                key=f"radio_{dom['id']}",
                label_visibility="collapsed",
            )
            risposte_pagina[dom["id"]] = scelta

        st.markdown("---")

        # Bottoni navigazione
        is_ultima_pagina = (pagina_corrente == TOTALE_PAGINE - 1)
        label_btn = "✅ Invia e scopri il tuo percorso" if is_ultima_pagina else f"Avanti → Sezione {pagina_corrente + 2}"

        col_btn_prev, col_btn_next = st.columns([1, 2])

        with col_btn_prev:
            btn_indietro = st.form_submit_button(
                "← Indietro",
                disabled=(pagina_corrente == 0),
            )
        with col_btn_next:
            btn_avanti = st.form_submit_button(label_btn, type="primary", use_container_width=True)

        if btn_avanti:
            st.session_state["quest_risposte"].update(risposte_pagina)

            if is_ultima_pagina:
                with st.spinner("🤖 Lea sta analizzando il tuo profilo... Un momento!"):
                    try:
                        risultato = analizza_questionario_esteso(st.session_state["quest_risposte"])
                        st.session_state["quest_risultato"] = risultato
                        st.session_state["quest_completato"] = True
                        st.session_state["chat_questionario"] = [
                            {"ruolo": "assistant", "contenuto": risultato}
                        ]
                    except Exception as e:
                        st.error(f"Errore durante l'analisi: {e}")
            else:
                st.session_state["quest_pagina"] = pagina_corrente + 1

            # Attiva lo scroll al prossimo re-render
            st.session_state["_scroll_top"] = True
            st.rerun()

        if btn_indietro and pagina_corrente > 0:
            st.session_state["quest_risposte"].update(risposte_pagina)
            st.session_state["quest_pagina"] = pagina_corrente - 1
            # Attiva lo scroll al prossimo re-render
            st.session_state["_scroll_top"] = True
            st.rerun()


def _mostra_risultato():
    """Mostra il risultato LLM, i bottoni di navigazione e la chat inline."""
    risultato = st.session_state.get("quest_risultato", "")

    st.markdown("### 🎓 Il tuo percorso di studi consigliato da Lea")
    if risultato:
        st.markdown(
            f'<div class="risultato-box">{risultato}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("Nessun risultato disponibile.")

    st.markdown("---")

    # Bottoni navigazione
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("← Torna alla home", key="btn_torna_home_risultato", type="primary"):
            st.session_state["ospite_pagina"] = "home"
            st.rerun()
    with col_b:
        if st.button("🔄 Rifai il questionario", key="btn_rifai"):
            for k in [
                "quest_pagina",
                "quest_risposte",
                "quest_completato",
                "quest_risultato",
                "chat_questionario",
            ]:
                st.session_state.pop(k, None)
            st.rerun()
    with col_c:
        if st.button("📚 Esplora il catalogo", key="btn_vai_catalogo_risultato"):
            st.session_state["ospite_pagina"] = "catalogo"
            st.rerun()

    # Chat inline con Lea
    st.markdown("---")
    st.markdown("#### 💬 Vuoi saperne di più? Chatta con Lea!")
    st.markdown(
        '<div class="chat-intro-box">'
        "Puoi chiedermi tutto sui corsi consigliati: materie, durata, sbocchi lavorativi, "
        "differenze tra percorsi simili, test d'ammissione e altro ancora."
        "</div>",
        unsafe_allow_html=True,
    )

    # Suggerimenti rapidi
    suggerimenti_post = [
        "Spiegami le differenze tra i corsi consigliati",
        "Quali sbocchi lavorativi hanno?",
        "Cosa si studia nel primo anno?",
        "Come si accede a questi corsi?",
    ]
    cols = st.columns(len(suggerimenti_post))
    domanda_cliccata = None
    for i, sugg in enumerate(suggerimenti_post):
        with cols[i]:
            if st.button(sugg, use_container_width=True, key=f"sugg_post_{i}"):
                domanda_cliccata = sugg

    st.markdown("")

    if "chat_questionario" not in st.session_state:
        st.session_state["chat_questionario"] = (
            [{"ruolo": "assistant", "contenuto": risultato}] if risultato else []
        )

    # Mostra la storia (dal secondo messaggio: il primo è il risultato già mostrato sopra)
    for msg in st.session_state["chat_questionario"][1:]:
        with st.chat_message(msg["ruolo"]):
            st.markdown(msg["contenuto"])

    # Input chat
    prompt = st.chat_input("Chiedi a Lea sui corsi consigliati...")
    if domanda_cliccata:
        prompt = domanda_cliccata

    if prompt:
        st.session_state["chat_questionario"].append({"ruolo": "user", "contenuto": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Lea sta controllando il catalogo corsi..."):
                try:
                    cronologia_passata = st.session_state["chat_questionario"][:-1]
                    risposta = chiedi_agente_ospite(domanda=prompt, cronologia=cronologia_passata)
                    st.markdown(risposta)
                    st.session_state["chat_questionario"].append({"ruolo": "assistant", "contenuto": risposta})
                except Exception as e:
                    err_msg = f"Si è verificato un errore temporaneo: {e}"
                    st.error(err_msg)
                    st.session_state["chat_questionario"].append({"ruolo": "assistant", "contenuto": err_msg})
