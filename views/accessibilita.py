# ============================================================================
# Accessibilita — Utility condivisa per override CSS
# ============================================================================

import streamlit as st

# ---------------------------------------------------------------------------
# Palette per modalita
# ---------------------------------------------------------------------------
ACCESSIBILITY_OPTIONS = [
    "Default",
    "Contrasto elevato (ipovedenti)",
    "Modalita daltonici",
]

# Override CSS per ipovedenti (contrasto elevato, WCAG AAA)
# Palette: nero puro #000 + giallo #FFD700 + bianco #FFF + ciano #00E5FF
# Ispirata a Windows High Contrast Black + raccomandazioni Perkins School
# Rapporto contrasto: bianco su nero = 21:1 (massimo), giallo su nero = 15.4:1
_CSS_IPOVEDENTI = """
<style>
/* === CONTRASTO ELEVATO (ipovedenti) === */
/* Fonte: Perkins School for the Blind — nero/giallo e nero/bianco */
/* WCAG AAA: rapporto minimo 7:1, qui garantito 15:1+ su tutti gli elementi */

/* Font-size globale aumentato per leggibilita */
.stApp { font-size: 1.05rem !important; }

/* ── Sfondo app: nero puro ── */
.stApp { background: #000000 !important; }

/* ── Testo generico: bianco puro su nero ── */
.stApp, .stApp p, .stApp span, .stApp div, .stApp li, .stApp label,
.stApp td, .stApp th, .stMarkdown, .stApp [class*="css"] {
    color: #FFFFFF !important;
}

/* ── Heading: giallo vivo ── */
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
    color: #FFD700 !important;
}

/* ── Card e contenitori: nero con bordo giallo spesso ── */
.f360-card, .section-card, .course-card, .paragrafo-box, .capitolo-header,
.raccomandazione-card, .piano-card, .nav-toc, .metric-box, .tab-note,
.demo-box, .corso-item, .upload-box {
    background: #0A0A0A !important;
    border: 2px solid #FFD700 !important;
    color: #FFFFFF !important;
}
.corso-item .corso-nome, .course-card .title, .piano-card h5,
.section-header, .section-title, .nav-toc-title {
    color: #FFD700 !important;
}
.corso-item .corso-meta, .course-card .meta, .piano-card .piano-meta,
.section-sub, .no-content-hint {
    color: #E0E0E0 !important;
}
.paragrafo-testo {
    color: #FFFFFF !important;
}

/* ── Sidebar: nero con bordo giallo ── */
.st-key-sidebar,
.st-key-doc_sidebar > div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #0A0A0A !important;
    border: 2px solid #FFD700 !important;
}
/* Expander sidebar — override specifico per nth-of-type del tema originale */
.st-key-sidebar [data-testid="stExpander"],
.st-key-sidebar [data-testid="stExpander"]:nth-of-type(1),
.st-key-sidebar [data-testid="stExpander"]:nth-of-type(2),
.st-key-sidebar [data-testid="stExpander"]:nth-of-type(n) {
    background: #111111 !important;
    border: 2px solid #FFD700 !important;
}
.st-key-sidebar [data-testid="stExpander"] summary,
.st-key-sidebar [data-testid="stExpander"]:nth-of-type(1) summary,
.st-key-sidebar [data-testid="stExpander"]:nth-of-type(2) summary,
.st-key-sidebar [data-testid="stExpander"]:nth-of-type(n) summary {
    background: #111111 !important;
    color: #FFD700 !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
}
.st-key-sidebar [data-testid="stExpander"] summary p,
.st-key-sidebar [data-testid="stExpander"] summary span {
    color: #FFD700 !important;
}
.st-key-sidebar [data-testid="stExpander"] summary svg {
    color: #FFD700 !important;
    opacity: 1 !important;
}
/* Contenuto dentro expander aperto */
.st-key-sidebar [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    background: #0A0A0A !important;
}

/* ── Input: nero con bordo giallo, testo bianco ── */
.stTextInput input, .stTextArea textarea,
.stSelectbox > div > div, .stSelectbox [data-baseweb="select"] {
    background: #111111 !important;
    border: 2px solid #FFD700 !important;
    color: #FFFFFF !important;
    font-size: 1rem !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {
    color: #AAAAAA !important;
}
.stTextInput label, .stTextArea label, .stSelectbox label {
    color: #FFD700 !important;
    font-size: 0.95rem !important;
}

/* ── Bottoni: giallo su nero (alta visibilita) ── */
.stButton > button {
    background: #FFD700 !important;
    color: #000000 !important;
    border: 3px solid #FFD700 !important;
    font-weight: 800 !important;
    font-size: 1rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}
.stButton > button:hover {
    background: #FFFFFF !important;
    color: #000000 !important;
    border-color: #FFFFFF !important;
}

/* ── Bottoni sidebar: bordo giallo, testo giallo ── */
.st-key-sidebar .stButton > button {
    background: #000000 !important;
    color: #FFD700 !important;
    border: 2px solid #FFD700 !important;
}
.st-key-sidebar .stButton > button:hover {
    background: #FFD700 !important;
    color: #000000 !important;
}

/* ── Bottone accessibilita: visibile ── */
.btn-accessibilita button {
    color: #00E5FF !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
}
.btn-accessibilita button:hover {
    color: #FFD700 !important;
}

/* ── Header e Footer: nero puro, bordo giallo ── */
.app-header, .f360-footer, .app-footer {
    background: #000000 !important;
    border-color: #FFD700 !important;
    border-bottom: 3px solid #FFD700 !important;
}
.app-header .header-brand-text, .app-footer .footer-copy, .f360-footer div {
    color: #FFFFFF !important;
}
.app-footer .footer-links a, .f360-footer a {
    color: #00E5FF !important;
    font-size: 0.9rem !important;
    text-decoration: underline !important;
}
.app-footer .footer-links a:hover, .f360-footer a:hover {
    color: #FFD700 !important;
}

/* ── Chat ── */
.chat-header {
    background: #000000 !important;
    border: 3px solid #FFD700 !important;
    border-bottom: none !important;
}
.chat-container {
    background: #0A0A0A !important;
    border: 3px solid #FFD700 !important;
    border-top: none !important;
}
.msg-user {
    background: #FFD700 !important;
    color: #000000 !important;
    font-weight: 600 !important;
}
.msg-ai {
    background: #111111 !important;
    color: #FFFFFF !important;
    border: 2px solid #444444 !important;
}
.msg-ai strong { color: #FFD700 !important; }
.chat-title, .chat-sub { color: #FFFFFF !important; }
.chat-online { background: #00FF00 !important; width: 10px !important; height: 10px !important; }

/* ── Status pills e badge ── */
.stato-iscritto, .pill-pub {
    background: #003300 !important;
    color: #00FF00 !important;
    border: 1px solid #00FF00 !important;
    font-weight: 700 !important;
}
.stato-completato {
    background: #003300 !important;
    color: #00FF00 !important;
    border: 1px solid #00FF00 !important;
}
.stato-abbandonato, .pill-bozza {
    background: #330000 !important;
    color: #FF4444 !important;
    border: 1px solid #FF4444 !important;
}
.content-type-badge {
    border: 2px solid #FFD700 !important;
    font-weight: 700 !important;
}
.ai-badge {
    background: #FFD700 !important;
    color: #000000 !important;
}
.chip {
    background: #111111 !important;
    color: #FFD700 !important;
    border: 1px solid #FFD700 !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    border: 2px solid #FFD700 !important;
    background: #0A0A0A !important;
}
[data-testid="stExpander"] summary {
    color: #FFD700 !important;
    font-weight: 700 !important;
}
[data-testid="stExpander"] summary svg {
    color: #FFD700 !important;
}

/* ── Checkbox, Radio, Tabs ── */
.stCheckbox label span, .stRadio label span {
    color: #FFFFFF !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: #000000 !important;
    border-bottom: 2px solid #FFD700 !important;
}
.stTabs [data-baseweb="tab"] {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
    color: #FFD700 !important;
    border-bottom-color: #FFD700 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 10px !important; }
::-webkit-scrollbar-thumb { background: #FFD700 !important; border-radius: 5px !important; }
::-webkit-scrollbar-track { background: #111111 !important; }

/* ── Link: ciano (distinguibile dal giallo) ── */
a { color: #00E5FF !important; text-decoration: underline !important; }
a:hover { color: #FFD700 !important; }

/* ── Score bar ── */
.score-bar-outer { background: #222222 !important; }
.score-bar-inner { background: linear-gradient(90deg, #FFD700, #00FF00) !important; }

/* ── Flashcard ── */
.fc-front, .fc-front-side {
    background: #FFD700 !important;
    color: #000000 !important;
    font-weight: 700 !important;
}
.fc-back, .fc-back-side {
    background: #111111 !important;
    color: #FFFFFF !important;
    border: 2px solid #FFD700 !important;
}

/* ── Pannello contenuto scrollabile ── */
.st-key-corso_scroll, .st-key-piano_scroll {
    background: #0A0A0A !important;
    border: 2px solid #FFD700 !important;
}

/* ── Card click rows ── */
.element-container:has(.card-click) + .element-container [data-testid="stHorizontalBlock"] {
    background: #0A0A0A !important;
    border: 2px solid #FFD700 !important;
}
.element-container:has(.card-corso-active) + .element-container [data-testid="stHorizontalBlock"],
.element-container:has(.card-piano-active) + .element-container [data-testid="stHorizontalBlock"] {
    background: #1A1A00 !important;
    border: 3px solid #FFD700 !important;
}
.element-container:has(.card-click) + .element-container button {
    color: #FFD700 !important;
    font-weight: 700 !important;
}

/* ── Quiz ── */
.quiz-domanda {
    background: #111111 !important;
    border: 2px solid #FFD700 !important;
    color: #FFFFFF !important;
}
.quiz-num { background: #FFD700 !important; color: #000000 !important; font-weight: 800 !important; }
.toc-num { background: #FFD700 !important; color: #000000 !important; }
.toc-link { color: #00E5FF !important; font-weight: 700 !important; }
.toc-link:hover { color: #FFD700 !important; }

/* ── Divider ── */
hr, .divider-label::after { border-color: #FFD700 !important; background: #FFD700 !important; }
.divider-label { color: #FFD700 !important; }

/* ── Metriche ── */
.metric-box { background: #0A0A0A !important; border: 2px solid #FFD700 !important; }
.metric-label { color: #E0E0E0 !important; font-size: 0.9rem !important; }
.metric-value { color: #FFD700 !important; }

/* ── Raccomandazioni ── */
.raccomandazione-card { border-left: 4px solid #FFD700 !important; }
.slideshow-track .slide-card { border-left: 4px solid #FFD700 !important; background: #0A0A0A !important; }
.slideshow-nav button { background: #FFD700 !important; color: #000000 !important; }

/* ── Chat input ── */
.stChatInput textarea {
    background: #111111 !important;
    border: 2px solid #FFD700 !important;
    color: #FFFFFF !important;
    font-size: 1rem !important;
}
.stChatInput textarea:focus {
    border-color: #00E5FF !important;
    box-shadow: 0 0 0 3px rgba(0,229,255,0.3) !important;
}

/* ── Demo box (login) ── */
.demo-box {
    background: #111111 !important;
    border: 2px dashed #FFD700 !important;
    color: #FFFFFF !important;
}
.demo-box strong { color: #FFD700 !important; }
.demo-box code { background: #003300 !important; color: #00FF00 !important; }

/* ── Streamlit nativi ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: transparent !important;
}
.stAlert { border: 2px solid #FFD700 !important; background: #111111 !important; }

/* ══════════════════════════════════════════════════════════════════
   FIX: Raccomandazioni slideshow — card HTML inline con style
   ══════════════════════════════════════════════════════════════════ */
/* Le card raccomandazioni usano HTML inline, servono selettori generici */
.raccomandazione-card,
.slideshow-track .slide-card,
div[style*="border-left: 4px solid"],
div[style*="border-left:4px solid"] {
    background: #0A0A0A !important;
    border-color: #FFD700 !important;
    color: #FFFFFF !important;
}
.raccomandazione-card h5, .slideshow-track .slide-card h5 {
    color: #FFD700 !important;
}
.raccomandazione-card p, .slideshow-track .slide-card p {
    color: #E0E0E0 !important;
}
/* Tag/chip dentro le raccomandazioni */
.raccomandazione-card span[style], .slideshow-track span[style] {
    background: #111111 !important;
    color: #FFD700 !important;
    border: 1px solid #FFD700 !important;
}
/* Dots slideshow */
.slideshow-dots .dot-indicator { background: #444444 !important; }
.slideshow-dots .dot-indicator.active { background: #FFD700 !important; }

/* ══════════════════════════════════════════════════════════════════
   FIX: Chat Lea — bolla AI e contenitore
   ══════════════════════════════════════════════════════════════════ */
/* Il contenitore chat puo essere un div generico con background bianco */
div[style*="background:#fff"],
div[style*="background: #fff"],
div[style*="background:#FFFFFF"],
div[style*="background: #FFFFFF"],
div[style*="background: white"],
div[style*="background:#ffffff"] {
    background: #0A0A0A !important;
    color: #FFFFFF !important;
}
/* Doc banner nella chat */
.chat-doc-banner {
    background: #111111 !important;
    border-color: #FFD700 !important;
    color: #FFFFFF !important;
}
.chat-doc-banner .doc-name { color: #FFD700 !important; }
.chat-doc-banner .doc-label { color: #E0E0E0 !important; }
/* Inner chat scrollable */
.chat-inner { background: transparent !important; }
/* Typing indicator */
.typing-bubble {
    background: #111111 !important;
    border-color: #FFD700 !important;
}
.typing-bubble .dot { background: #FFD700 !important; }

/* ══════════════════════════════════════════════════════════════════
   FIX: Input focus — resta scuro, non diventa bianco
   ══════════════════════════════════════════════════════════════════ */
.stTextInput input:focus,
.stTextInput input:active,
.stTextInput input:hover,
.stTextArea textarea:focus,
.stTextArea textarea:active,
.stTextArea textarea:hover {
    background: #111111 !important;
    border-color: #00E5FF !important;
    color: #FFFFFF !important;
    box-shadow: 0 0 0 3px rgba(0,229,255,0.3) !important;
}
/* Selectbox dropdown aperto */
[data-baseweb="popover"],
[data-baseweb="menu"],
[data-baseweb="select"] ul,
[data-baseweb="select"] li,
[role="listbox"],
[role="option"] {
    background: #111111 !important;
    color: #FFFFFF !important;
    border-color: #FFD700 !important;
}
[role="option"]:hover,
[data-baseweb="menu"] li:hover {
    background: #FFD700 !important;
    color: #000000 !important;
}

/* ══════════════════════════════════════════════════════════════════
   FIX: Tutti i container Streamlit con sfondo bianco inline
   ══════════════════════════════════════════════════════════════════ */
[data-testid="stForm"],
[data-testid="stHorizontalBlock"],
[data-testid="stVerticalBlock"],
[data-testid="stColumn"] {
    background: transparent !important;
}
/* Immagine container */
[data-testid="stImage"] { background: transparent !important; }
/* Markdown containers */
.stMarkdown { color: #FFFFFF !important; }

/* ══════════════════════════════════════════════════════════════════
   FIX: Suggerimenti chat (bottoni secondary)
   ══════════════════════════════════════════════════════════════════ */
.stButton > button[kind="secondary"] {
    background: #111111 !important;
    color: #00E5FF !important;
    border: 2px solid #00E5FF !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #00E5FF !important;
    color: #000000 !important;
}

/* ══════════════════════════════════════════════════════════════════
   FIX: iframes (TOC, componenti HTML) — sfondo trasparente
   ══════════════════════════════════════════════════════════════════ */
iframe { background: transparent !important; }
</style>
"""

# Override CSS per daltonici (Tol palette — blu/arancione safe)
_CSS_DALTONICI = """
<style>
/* === MODALITA DALTONICI (Tol palette) === */

/* Successo: da verde a arancione */
.stato-completato, .pill-pub {
    background: #FFF0E0 !important;
    color: #EE7733 !important;
}

/* Errore: rosso piu scuro e distinguibile */
.stato-abbandonato, .pill-bozza {
    background: #FFE5E5 !important;
    color: #CC3311 !important;
}

/* Iscritto: blu sicuro */
.stato-iscritto {
    background: #E0F0FF !important;
    color: #0077BB !important;
}

/* Accent primario: blu sicuro */
.capitolo-header { border-left-color: #0077BB !important; }
.paragrafo-box { border-top-color: #0077BB !important; }
.paragrafo-box h5 { color: #0077BB !important; }
.nav-toc { border-left-color: #EE7733 !important; }
.toc-num { background: #0077BB !important; }
.toc-link { color: #0077BB !important; }
.ai-badge { background: #0077BB !important; }

/* Bottoni */
.stButton > button {
    background: #0077BB !important;
}
.stButton > button:hover {
    background: #005599 !important;
}

/* Sidebar active */
.st-key-sidebar .stButton > button:hover {
    border-left-color: #0077BB !important;
    color: #0077BB !important;
}
.element-container:has(.card-corso-active) + .element-container [data-testid="stHorizontalBlock"] {
    border-left-color: #0077BB !important;
    background: #E0F0FF !important;
}
.element-container:has(.card-corso) + .element-container [data-testid="stHorizontalBlock"]:hover {
    border-left-color: #0077BB !important;
}

/* Quiz badge: rosso scuro distinguibile */
.badge-quiz { background: #FFE5E5 !important; color: #CC3311 !important; }
.quiz-num { background: #CC3311 !important; }

/* Flashcard badge: arancione */
.badge-flash { background: #FFF0E0 !important; color: #EE7733 !important; }

/* Schema badge: blu */
.badge-schema { background: #E0F0FF !important; color: #0077BB !important; }

/* Score bar */
.score-bar-inner {
    background: linear-gradient(90deg, #0077BB, #EE7733) !important;
}

/* Raccomandazioni: arancione */
.raccomandazione-card { border-left-color: #EE7733 !important; }
.slideshow-track .slide-card { border-left-color: #EE7733 !important; }

/* Chat */
.msg-user { background: #0077BB !important; }
.chat-header { background: linear-gradient(135deg, #003355 0%, #0077BB 100%) !important; }

/* Gold -> arancione */
.app-header { border-bottom-color: #EE7733 !important; }

/* Link */
a { color: #0077BB !important; }

/* Flashcard */
.fc-front, .fc-front-side { background: #0077BB !important; }

/* Corso selezionato */
.corso-item.attivo { border-left-color: #0077BB !important; background: #E0F0FF !important; }
.corso-item:hover { border-left-color: #0077BB !important; }

/* Chip e divider */
.chip { background: #E0F0FF !important; color: #0077BB !important; }
.divider-label { color: #0077BB !important; }

/* Sidebar hover */
.st-key-sidebar::-webkit-scrollbar-thumb:hover { background: #0077BB !important; }
.st-key-corso_scroll::-webkit-scrollbar-thumb:hover,
.st-key-piano_scroll::-webkit-scrollbar-thumb:hover { background: #0077BB !important; }

/* Login specifico */
.f360-card { border-top-color: #0077BB !important; }
</style>
"""


def get_css_accessibilita() -> str:
    """Restituisce il blocco <style> di override in base alla modalita scelta nel login."""
    modalita = st.session_state.get("accessibilita", "Default")
    if modalita == "Contrasto elevato (ipovedenti)":
        return _CSS_IPOVEDENTI
    elif modalita == "Modalita daltonici":
        return _CSS_DALTONICI
    return ""


@st.dialog(title="Impostazioni di accessibilita", width="medium")
def dialog_accessibilita():
    """Dialog per scegliere la modalita di visualizzazione."""
    corrente = st.session_state.get("accessibilita", "Default")
    scelta = st.selectbox(
        "Modalita di visualizzazione",
        ACCESSIBILITY_OPTIONS,
        index=ACCESSIBILITY_OPTIONS.index(corrente),
    )
    if st.button("Conferma", use_container_width=True):
        st.session_state["accessibilita"] = scelta
        st.rerun()
