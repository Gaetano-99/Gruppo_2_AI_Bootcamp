"""
Pagina Streamlit: Test End-to-End Flusso Studente
Percorso: src/ui/pages/temp_student_test.py

Questa pagina temporanea permette di:
    1. Caricare documenti didattici e frammentarli in chunk RAG.
    2. Richiedere la generazione di lezioni, quiz o flashcard tramite
       l'Agent 5 (Content Generation Engine).
    3. Visualizzare la lezione generata e verificare le fonti (chunk originali).
    4. Interagire con i quiz/flashcard generati.

Uso:
    Posizionare questo file nella cartella ``pages/`` dell'app Streamlit
    oppure avviare direttamente con: ``streamlit run src/ui/pages/temp_student_test.py``

Nota:
    Il mock di sessione imposta ``user_role="Studente"`` e ``corso_test_id=101``.
    Il ``docente_id=1`` è il valore mock usato per i campi NOT NULL dello schema.
"""

import sys
import os

import streamlit as st

# ---------------------------------------------------------------------------
# Path setup — permette l'import dalla root del progetto in qualunque contesto
# ---------------------------------------------------------------------------
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from platform_sdk.database import db
from src.tools.document_processor import (
    elabora_e_salva_documento,
    conta_chunks_corso,
)
from src.agents.content_gen import crea_agente_content_gen, esegui_generazione


# ===========================================================================
# Funzioni di rendering — definite PRIMA del corpo principale della pagina
# ===========================================================================

def _mostra_quiz(dati_quiz: dict) -> None:
    """Renderizza il quiz in modo interattivo su Streamlit.

    Args:
        dati_quiz: Dizionario con struttura ``QuizGenerato`` (titolo, domande).
    """
    st.markdown(f"### {dati_quiz.get('titolo', 'Quiz')}")

    domande: list[dict] = dati_quiz.get("domande", [])
    if not domande:
        st.info("Nessuna domanda disponibile.")
        return

    if "risposte_quiz" not in st.session_state:
        st.session_state.risposte_quiz = {}

    punteggio: int = 0
    lettere: list[str] = ["A", "B", "C", "D"]

    for i, domanda in enumerate(domande):
        with st.container(border=True):
            st.markdown(f"**Domanda {i + 1}:** {domanda.get('domanda', '')}")
            opzioni: list[str] = domanda.get("opzioni", [])
            opzioni_etichettate: list[str] = [
                f"{lett}. {testo}"
                for lett, testo in zip(lettere, opzioni)
            ]

            risposta_data: str | None = st.radio(
                "Scegli la risposta:",
                options=opzioni_etichettate,
                index=None,
                key=f"quiz_risposta_{i}",
                label_visibility="collapsed",
            )

            if risposta_data:
                lettera_scelta: str = risposta_data[0]
                risposta_corretta: str = domanda.get("risposta_corretta", "A")
                st.session_state.risposte_quiz[i] = lettera_scelta

                if lettera_scelta == risposta_corretta:
                    punteggio += 1
                    st.success(f"✅ Corretto! {domanda.get('spiegazione', '')}")
                else:
                    st.error(
                        f"❌ Risposta errata. "
                        f"La corretta era **{risposta_corretta}**. "
                        f"{domanda.get('spiegazione', '')}"
                    )

    totale: int = len(domande)
    quiz_completato: bool = len(st.session_state.get("risposte_quiz", {})) == totale
    if quiz_completato and totale > 0:
        percentuale: float = (punteggio / totale) * 100
        st.success(
            f"🎯 **Risultato finale:** {punteggio}/{totale} "
            f"({percentuale:.0f}%)"
        )
        if st.button("🔄 Ricomincia Quiz", key="reset_quiz"):
            del st.session_state["risposte_quiz"]
            st.rerun()


def _mostra_flashcard(dati_flashcard: dict) -> None:
    """Renderizza le flashcard in modo interattivo su Streamlit.

    Args:
        dati_flashcard: Dizionario con struttura ``FlashcardGenerata``
                        (titolo, cards).
    """
    st.markdown(f"### {dati_flashcard.get('titolo', 'Flashcard')}")

    cards: list[dict] = dati_flashcard.get("cards", [])
    if not cards:
        st.info("Nessuna flashcard disponibile.")
        return

    if "flashcard_indice" not in st.session_state:
        st.session_state.flashcard_indice = 0
    if "flashcard_mostrata" not in st.session_state:
        st.session_state.flashcard_mostrata = False

    totale: int = len(cards)
    indice: int = min(st.session_state.flashcard_indice, totale - 1)
    card_corrente: dict = cards[indice]

    st.progress((indice + 1) / totale, text=f"Carta {indice + 1} di {totale}")

    with st.container(border=True):
        col_fronte, col_retro = st.columns(2)
        with col_fronte:
            st.markdown("**❓ Fronte**")
            st.info(card_corrente.get("fronte", ""))
        with col_retro:
            st.markdown("**💡 Retro**")
            if st.session_state.flashcard_mostrata:
                st.success(card_corrente.get("retro", ""))
            else:
                if st.button("👁️ Mostra risposta", key=f"mostra_fc_{indice}"):
                    st.session_state.flashcard_mostrata = True
                    st.rerun()

    col_prev, col_reset, col_next = st.columns(3)
    with col_prev:
        if st.button("⬅️ Precedente", disabled=(indice == 0), use_container_width=True):
            st.session_state.flashcard_indice = indice - 1
            st.session_state.flashcard_mostrata = False
            st.rerun()
    with col_reset:
        if st.button("🔄 Ricomincia", use_container_width=True):
            st.session_state.flashcard_indice = 0
            st.session_state.flashcard_mostrata = False
            st.rerun()
    with col_next:
        if st.button("➡️ Successiva", disabled=(indice == totale - 1), use_container_width=True):
            st.session_state.flashcard_indice = indice + 1
            st.session_state.flashcard_mostrata = False
            st.rerun()


# ===========================================================================
# Configurazione pagina
# ===========================================================================
st.set_page_config(
    page_title="🧪 Test Studente — Content Generation",
    page_icon="🧪",
    layout="wide",
)

# ===========================================================================
# Mock sessione studente
# ===========================================================================
if "user_role" not in st.session_state:
    st.session_state.user_role = "Studente"
if "corso_test_id" not in st.session_state:
    # Default: corso ID=1 ("Basi di Dati") presente nel seed del progetto
    st.session_state.corso_test_id = 1

# ===========================================================================
# Cache agente (evita re-istanziazione a ogni rerender)
# ===========================================================================
if "agente_content_gen" not in st.session_state:
    st.session_state.agente_content_gen = crea_agente_content_gen()

# ===========================================================================
# Inizializzazione database
# ===========================================================================
try:
    db.init()
except UnicodeEncodeError:
    # Su Windows con codepage CP1252 le emoji nei print di db.init() causano
    # UnicodeEncodeError, ma lo schema/seed sono già stati eseguiti correttamente.
    pass
except Exception:
    pass  # già inizializzato o tabelle già presenti

# ===========================================================================
# Header
# ===========================================================================
st.title("🧪 Test End-to-End — Flusso Studente")
st.caption(
    f"Modalità: **{st.session_state.user_role}** · "
    f"Corso ID: **{st.session_state.corso_test_id}**"
)
st.info(
    "Questa pagina è **temporanea** e serve per testare il Content Generation Engine (Agent 5). "
    "Carica un documento, scegli un argomento e genera lezione, quiz o flashcard.",
    icon="ℹ️",
)
st.divider()

# ===========================================================================
# Sidebar: configurazione
# ===========================================================================
with st.sidebar:
    st.header("⚙️ Configurazione Test")
    corso_test_id: int = st.number_input(
        "Corso ID (mock)",
        min_value=1,
        value=st.session_state.corso_test_id,
        step=1,
        help="ID del corso universitario sul quale lavorare.",
    )
    st.session_state.corso_test_id = corso_test_id

    n_chunks: int = conta_chunks_corso(corso_test_id)
    if n_chunks > 0:
        st.success(f"{n_chunks} chunk disponibili (ID globali del DB)")
        st.caption("Il RAG seleziona i Top-K più rilevanti per l'argomento.")
    else:
        st.warning("Nessun chunk disponibile. Carica prima un documento.")

    st.divider()
    st.caption("**Ruolo mock:** Studente")
    st.caption("**Agent:** Content Generation Engine v1")

# ===========================================================================
# SEZIONE 1 — Upload Documento
# ===========================================================================
st.header("📄 1. Carica Materiale Didattico")

with st.expander("📤 Upload documento", expanded=(n_chunks == 0)):
    col1, col2 = st.columns([2, 1])
    with col1:
        uploaded_file = st.file_uploader(
            "Seleziona un file didattico",
            type=["pdf", "txt", "md", "csv"],
            help="Formati supportati: PDF, TXT, Markdown, CSV",
            key="file_uploader_doc",
        )
    with col2:
        titolo_documento: str = st.text_input(
            "Titolo documento",
            value="Dispensa Test",
            placeholder="Es. Lezioni di Basi di Dati",
        )
        tipo_documento: str = st.selectbox(
            "Tipo documento",
            options=["dispensa", "slide", "pdf", "libro"],
            index=0,
        )

    if uploaded_file is not None:
        _tipo_normalizzato = tipo_documento if tipo_documento in (
            "pdf", "slide", "video", "dispensa", "libro"
        ) else "dispensa"

        if st.button("🔄 Elabora e crea chunk", type="primary", use_container_width=True):
            with st.status(
                "⏳ Analisi del documento in corso...", expanded=True
            ) as status_bar:
                try:
                    st.write("📖 Estrazione del testo...")
                    materiale_id: int = elabora_e_salva_documento(
                        uploaded_file=uploaded_file,
                        corso_universitario_id=corso_test_id,
                        titolo=titolo_documento,
                        tipo=_tipo_normalizzato,
                    )
                    n_creati: int = conta_chunks_corso(corso_test_id)
                    st.write(
                        f"✂️ Chunking completato. "
                        f"Materiale ID: **{materiale_id}** — "
                        f"**{n_creati} chunk** salvati nel database."
                    )
                    status_bar.update(
                        label="✅ Documento elaborato con successo!", state="complete"
                    )
                    st.rerun()
                except ValueError as e:
                    status_bar.update(label="❌ Errore nell'elaborazione", state="error")
                    st.error(f"Errore: {e}")
                except Exception:
                    status_bar.update(label="❌ Errore imprevisto", state="error")
                    st.error(
                        "Si è verificato un errore durante l'elaborazione del documento. "
                        "Controlla i log per i dettagli."
                    )

# ===========================================================================
# SEZIONE 2 — Generazione Contenuti
# ===========================================================================
st.header("🤖 2. Genera Contenuti con AI")

if n_chunks == 0:
    st.warning("⚠️ Carica prima un documento per poter generare contenuti.")
else:
    with st.form(key="form_generazione"):
        argomento_input: str = st.text_area(
            "Argomento da studiare",
            placeholder="Es. Le query SQL JOIN e le loro tipologie...",
            height=80,
            help="Descrivi l'argomento su cui vuoi generare la lezione e gli strumenti.",
        )
        col_tipo, col_btn = st.columns([2, 1])
        with col_tipo:
            tipo_strumento: str = st.radio(
                "Strumento didattico",
                options=["quiz", "flashcard"],
                horizontal=True,
                help="Tipo di strumento di studio da generare insieme alla lezione.",
            )
        with col_btn:
            submitted: bool = st.form_submit_button(
                "🚀 Genera con Agent 5",
                type="primary",
                use_container_width=True,
            )

    if submitted:
        if not argomento_input.strip():
            st.warning("⚠️ Inserisci un argomento prima di generare.")
        else:
            with st.spinner(
                "🔄 Agent 5 sta generando i contenuti... (può richiedere qualche secondo)"
            ):
                try:
                    risultato: dict = esegui_generazione(
                        agente=st.session_state.agente_content_gen,
                        corso_id=corso_test_id,
                        argomento_richiesto=argomento_input.strip(),
                        tipo_strumento=tipo_strumento,
                    )
                    st.session_state.ultimo_risultato = risultato
                except Exception:
                    st.error(
                        "Si è verificato un errore durante la generazione dei contenuti. "
                        "Controlla i log per i dettagli."
                    )
                    st.session_state.pop("ultimo_risultato", None)

# ===========================================================================
# SEZIONE 3 — Visualizzazione Risultati
# ===========================================================================
if "ultimo_risultato" in st.session_state:
    risultato: dict = st.session_state.ultimo_risultato

    if risultato.get("errore"):
        st.error(f"❌ Errore dall'agente: {risultato['errore']}")
    else:
        st.divider()
        st.header("📚 3. Risultati Generati")

        # ------------------------------------------------------------------
        # 3a. Lezione in Markdown
        # ------------------------------------------------------------------
        lezione_md: str = risultato.get("lezione_generata", "")
        if lezione_md:
            st.subheader("📖 Lezione Generata")
            with st.container(border=True):
                st.markdown(lezione_md)

        # ------------------------------------------------------------------
        # 3b. Verifica Fonti RAG
        # ------------------------------------------------------------------
        chunk_ids_usati: list[int] = risultato.get("chunk_ids_utilizzati", [])
        chunks_recuperati: list[dict] = risultato.get("chunks_recuperati", [])
        n_totali_corso: int = risultato.get("n_chunk_totali_corso", 0)
        argomento_usato: str = risultato.get("argomento_richiesto", "")

        if chunk_ids_usati:
            # Crea mappa id→chunk per accesso rapido ai metadati (score, parole)
            mappa_chunks: dict[int, dict] = {
                c["id"]: c for c in chunks_recuperati if "id" in c
            }

            etichetta_expander: str = (
                f"Verifica Fonti — "
                f"Top {len(chunk_ids_usati)} chunk rilevanti "
                f"su {n_totali_corso} totali disponibili nel corso"
            )
            with st.expander(f"🔍 {etichetta_expander}", expanded=False):
                st.caption(
                    f"L'AI ha selezionato i **{len(chunk_ids_usati)} chunk semanticamente più"
                    f" rilevanti** per l'argomento *\"{argomento_usato}\"* "
                    f"(su {n_totali_corso} chunk totali del corso, filtrati per rilevanza). "
                    f"Gli ID mostrati sono **ID globali del database** (chiave primaria di "
                    f"`materiali_chunks`), non contatori sequenziali per questo corso."
                )
                for chunk_id in chunk_ids_usati:
                    # Usa i dati in-memory dal grafo (con score e parole trovate)
                    meta: dict = mappa_chunks.get(chunk_id, {})
                    score: int = meta.get("score_rilevanza", 0)
                    parole: list[str] = meta.get("parole_trovate", [])

                    # Etichetta con score di rilevanza
                    if score > 0:
                        etichetta_chunk = (
                            f"Chunk #{chunk_id} "
                            f"| Score rilevanza: {score} "
                            f"| Parole chiave: {', '.join(parole)}"
                        )
                    else:
                        etichetta_chunk = (
                            f"Chunk #{chunk_id} | Selezione generica (argomento non specifico)"
                        )

                    # Testo originale dal campo in-memory o da DB come fallback
                    testo_originale: str = meta.get("testo") or ""
                    sommario_originale: str = meta.get("sommario") or ""

                    if not testo_originale:
                        # Fallback DB (non dovrebbe servire se chunks_recuperati è completo)
                        chunk_db: dict | None = db.trova_uno("materiali_chunks", {"id": chunk_id})
                        if chunk_db:
                            testo_originale = chunk_db.get("testo", "")
                            sommario_originale = chunk_db.get("sommario") or ""

                    with st.container(border=True):
                        st.markdown(f"**{etichetta_chunk}**")
                        if sommario_originale:
                            st.caption(f"Sommario: {sommario_originale}")
                        n_token: int = meta.get("n_token") or len(testo_originale) // 4
                        st.caption(f"~{n_token} token · posizione {meta.get('indice_chunk', '?')}")
                        st.text(testo_originale or "(testo non disponibile)")

        # ------------------------------------------------------------------
        # 3c. Quiz o Flashcard
        # ------------------------------------------------------------------
        strumenti: dict = risultato.get("strumenti_studio_generati", {})
        tipo_str: str = risultato.get("tipo_strumento", "quiz")

        if strumenti:
            st.divider()
            if tipo_str == "quiz":
                st.subheader("🧠 Quiz Generato")
                _mostra_quiz(strumenti)
            else:
                st.subheader("🃏 Flashcard Generate")
                _mostra_flashcard(strumenti)

# ===========================================================================
# Footer
# ===========================================================================
st.divider()
st.caption(
    "🔬 **Pagina temporanea di test** — Content Generation Engine (Agent 5) "
    "· LearnAI Platform · Digita Academy 2025"
)
