"""
Modulo: orchestrator.py
Responsabilità: Agente Supervisore Contesto-Aware — unico punto di contatto tra UI e backend.

Architettura (agente singolo):
    L'orchestratore combina responsabilità conversazionali e di routing in un solo agente.
    Non esiste un layer conversazionale separato: questo agente parla direttamente con
    l'utente E smista il lavoro agli agenti specializzati.

    UI  →  Orchestrator  →  ContentGen / PracticeGen / DB

    Aggiungere un agente separato per la conversazione introdurrebbe:
        - Latenza doppia (due chiamate LLM per ogni messaggio)
        - Un punto di fallimento in più (traduzione intent → JSON)
        - Complessità di debug non giustificata (solo 3 tool)

Gestione della memoria (fix Streamlit):
    In Streamlit le variabili globali vengono distrutte ad ogni rerun della pagina.
    Tutti i singleton (orchestratore, agente teorico) vivono in ``st.session_state``
    per sopravvivere ai rerun e mantenere la memoria conversazionale di LangGraph.

API pubblica:
    - ``chat_con_orchestratore()``: unica funzione chiamata dalle pagine Streamlit.
    - ``aggiorna_contesto_sessione()``: chiamare quando l'utente cambia pagina/corso.
    - ``reset_sessione_chat()``: chiamare al logout.
"""

import sys
import os
import json

import streamlit as st

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from langchain_core.tools import tool
from platform_sdk.database import db
from platform_sdk.agent import crea_agente, esegui_agente

from src.agents.content_gen import crea_agente_content_gen, esegui_generazione
from src.agents.practice_gen import esegui_generazione_pratica

# ---------------------------------------------------------------------------
# Chiavi session_state
# ---------------------------------------------------------------------------
_SK_ORCHESTRATORE = "_orch_agente_compilato"
_SK_AGENTE_TEORICO = "_orch_agente_teorico"
_SK_THREAD_ID     = "_orch_thread_id"
_SK_CONTESTO      = "_orch_contesto_sessione"

# ---------------------------------------------------------------------------
# Variabile globale thread-safe per studente_id
# ---------------------------------------------------------------------------
# PROBLEMA: LangGraph esegue i tool in thread background (ThreadPoolExecutor).
# In quei thread st.session_state NON è accessibile — restituisce None
# silenziosamente, causando il fallback a studente_id=1 (sempre Giulia).
# Questo è confermato dai warning "missing ScriptRunContext" nel terminale.
#
# SOLUZIONE: variabile globale a livello di modulo Python.
# I moduli Python sono condivisi all'interno dello stesso processo,
# quindi è visibile sia dal thread principale Streamlit che dai thread
# background di LangGraph. Viene aggiornata PRIMA di ogni chiamata
# all'agente, dal thread principale dove session_state funziona.
_STUDENTE_ID_CORRENTE: int = 1


def _aggiorna_studente_corrente() -> None:
    """Legge studente_id da session_state (thread principale) e lo salva
    nella variabile globale, rendendolo disponibile ai thread background."""
    global _STUDENTE_ID_CORRENTE
    sid = (
        st.session_state.get("current_user_id")
        or st.session_state.get("user", {}).get("user_id")
        or st.session_state.get("user", {}).get("id")
    )
    if sid:
        _STUDENTE_ID_CORRENTE = int(sid)


# ---------------------------------------------------------------------------
# System prompt — conversazione + routing in un unico prompt coerente
# ---------------------------------------------------------------------------
_SYSTEM_PROMPT = """Sei Lea, il tutor didattico intelligente della piattaforma LearnAI.

IL TUO CARATTERE:
Parli in italiano con un tono caldo, chiaro e motivante. Non sei un bot che esegue
comandi: capisci il contesto, anticipi i bisogni e rendi l'esperienza di studio
piacevole. Dopo ogni azione completata, proponi proattivamente il passo successivo logico.

COSA SAI FARE (tool a tua disposizione):
1. tool_leggi_contesto    → sapere quale corso sta visualizzando l'utente in questo momento.
2. tool_esplora_catalogo  → scoprire corsi o materiali disponibili.
3. tool_genera_corso      → creare una nuova lezione teorica su un argomento.
4. tool_genera_pratica    → creare quiz, flashcard o schemi su una sezione studiata.

REGOLE DI COMPORTAMENTO:
- Se l'utente fa small talk o saluta, rispondi in modo naturale senza invocare tool.
- Se la richiesta è ambigua, fai UNA sola domanda mirata. Non fare interrogatori.
- Prima di chiedere all'utente quale corso intende, usa tool_leggi_contesto per
  verificare se il contesto è già disponibile dalla pagina corrente.
- Dopo aver generato un corso, ricorda i titoli delle sezioni create. Se l'utente
  chiede "fammi i quiz" subito dopo, usa direttamente quegli ID senza chiedere di nuovo.
- Non mostrare mai ID numerici interni all'utente. Usali solo nei tool.
- Gestisci gli errori con empatia: spiega cosa è andato storto e suggerisci il passo successivo.
"""


# ===========================================================================
# Tool
# ===========================================================================

@tool
def tool_leggi_contesto() -> str:
    """
    Leggi il contesto corrente della sessione: corso visualizzato e ultime sezioni generate.
    Usa questo tool PRIMA di chiedere all'utente su quale corso vuole lavorare.
    """
    contesto = st.session_state.get(_SK_CONTESTO, {})
    if not contesto:
        return "Nessun contesto attivo. L'utente non ha ancora selezionato un corso."

    parti = []
    if contesto.get("corso_id"):
        nome = contesto.get("corso_nome", "nome non disponibile")
        parti.append(f"Corso attivo: ID {contesto['corso_id']} — {nome}")
    if contesto.get("ultimi_paragrafi"):
        lista = "\n".join(
            f"  - ID {p['id']}: {p['titolo']}"
            for p in contesto["ultimi_paragrafi"]
        )
        parti.append(f"Ultime sezioni generate:\n{lista}")

    return "\n".join(parti) if parti else "Contesto parziale: nessuna sezione generata ancora."


@tool
def tool_esplora_catalogo(tipo_ricerca: str, corso_universitario_id: int = None) -> str:
    """
    Scopri i corsi universitari disponibili o i materiali di un corso specifico.
    - tipo_ricerca='corsi'     → lista tutti i corsi attivi.
    - tipo_ricerca='argomenti' → materiali del corso (richiede corso_universitario_id).
    """
    if tipo_ricerca == "corsi":
        corsi = db.trova_tutti("corsi_universitari", {"attivo": 1})
        if not corsi:
            return "Nessun corso universitario attivo nel sistema."
        return "Corsi disponibili:\n" + "\n".join(
            f"- ID {c['id']}: {c['nome']}" for c in corsi
        )

    elif tipo_ricerca == "argomenti":
        if not corso_universitario_id:
            return "Errore: specifica corso_universitario_id per vedere gli argomenti."
        materiali = db.trova_tutti(
            "materiali_didattici", {"corso_universitario_id": corso_universitario_id}
        )
        if not materiali:
            return f"Nessun materiale caricato per il corso ID {corso_universitario_id}."
        return (
            f"Materiali del corso ID {corso_universitario_id}:\n"
            + "\n".join(f"- {m['titolo']} ({m['tipo']})" for m in materiali)
            + "\nScegli un argomento per generare una lezione."
        )

    return "Errore: tipo_ricerca deve essere 'corsi' o 'argomenti'."


@tool
def tool_genera_corso(corso_universitario_id: int, argomento: str) -> str:
    """
    Genera e salva un corso teorico completo su un argomento specifico.
    Usa quando l'utente chiede di creare una lezione, un corso o approfondire un tema.
    """
    # Usa la variabile globale aggiornata dal thread principale prima dell'invocazione
    studente_id = _STUDENTE_ID_CORRENTE

    stato_finale = esegui_generazione(
        agente=_get_agente_teorico(),
        corso_id=corso_universitario_id,
        argomento_richiesto=argomento,
        docente_id=studente_id,
        is_corso_docente=False,
    )

    if stato_finale.get("errore"):
        return f"Errore durante la generazione: {stato_finale['errore']}"

    struttura = stato_finale.get("struttura_corso_generata", {})
    titolo = struttura.get("titolo_corso", "Senza Titolo")

    # Recupera gli ID reali dei paragrafi per la memoria dell'agente
    query_piano = (
        "SELECT id FROM piani_personalizzati "
        "WHERE studente_id = ? ORDER BY id DESC LIMIT 1"
    )
    piani = db.esegui(query_piano, [studente_id])
    if not piani:
        return f"Corso '{titolo}' generato, ma impossibile recuperare le sezioni dal DB."

    piano_id = piani[0]["id"]
    paragrafi = db.esegui(
        """SELECT pp.id, pp.titolo
           FROM piano_paragrafi pp
           JOIN piano_capitoli pc ON pp.capitolo_id = pc.id
           WHERE pc.piano_id = ?""",
        [piano_id],
    )

    # Salva i paragrafi nel contesto di sessione per le richieste successive
    contesto = st.session_state.get(_SK_CONTESTO, {})
    contesto["ultimi_paragrafi"] = paragrafi
    st.session_state[_SK_CONTESTO] = contesto

    elenco = "\n".join(f"- ID {p['id']}: {p['titolo']}" for p in paragrafi)
    return (
        f"SUCCESSO: Corso '{titolo}' generato e salvato.\n"
        f"MEMORIA (usa questi ID per quiz/flashcard se richiesti):\n{elenco}\n"
        f"Suggerisci all'utente di esercitarsi con quiz o flashcard."
    )


@tool
def tool_genera_pratica(paragrafo_id: int, strumenti: list[str]) -> str:
    """
    Genera strumenti pratici (quiz, flashcard, schema) per una sezione studiata.
    strumenti: lista con uno o più tra "quiz", "flashcard", "schema".
    """
    studente_id = _STUDENTE_ID_CORRENTE

    contenuti = db.trova_tutti(
        "piano_contenuti", {"paragrafo_id": paragrafo_id, "tipo": "lezione"}
    )
    if not contenuti or not contenuti[0].get("contenuto_json"):
        return f"Nessun testo trovato per la sezione ID {paragrafo_id}. Genera prima il corso teorico."

    testo_paragrafo = contenuti[0]["contenuto_json"]
    try:
        chunk_ids = json.loads(contenuti[0].get("chunk_ids_utilizzati", "[]"))
    except (json.JSONDecodeError, TypeError):
        chunk_ids = []

    stato_finale = esegui_generazione_pratica(
        paragrafo_id=paragrafo_id,
        testo_paragrafo=testo_paragrafo,
        strumenti_richiesti=strumenti,
        studente_id=studente_id,
        chunk_ids_utilizzati=chunk_ids,
    )

    if stato_finale.get("errore"):
        return f"Errore nella generazione pratica: {stato_finale['errore']}"

    generati = list(stato_finale.get("strumenti_generati", {}).keys())
    nomi = {"quiz": "Quiz", "flashcards": "Flashcard", "schema_mermaid": "Schema concettuale"}
    leggibili = [nomi.get(g, g) for g in generati]

    return f"SUCCESSO: {' e '.join(leggibili)} generati e salvati per la sezione {paragrafo_id}."


# ===========================================================================
# Singleton helpers (tutti in session_state)
# ===========================================================================

def _get_agente_teorico():
    """Agente ContentGen: singleton in session_state per sopravvivere ai rerun."""
    if _SK_AGENTE_TEORICO not in st.session_state:
        st.session_state[_SK_AGENTE_TEORICO] = crea_agente_content_gen()
    return st.session_state[_SK_AGENTE_TEORICO]


def _get_orchestratore():
    """Orchestratore: singleton in session_state con memoria LangGraph intatta."""
    if _SK_ORCHESTRATORE not in st.session_state:
        st.session_state[_SK_ORCHESTRATORE] = crea_agente(
            tools=[
                tool_leggi_contesto,
                tool_esplora_catalogo,
                tool_genera_corso,
                tool_genera_pratica,
            ],
            system_prompt=_SYSTEM_PROMPT,
            memoria=True,
        )
    return st.session_state[_SK_ORCHESTRATORE]


def _get_thread_id() -> str:
    """Thread ID stabile per sessione utente, usato dal checkpointer di LangGraph."""
    if _SK_THREAD_ID not in st.session_state:
        user_id = st.session_state.get("user", {}).get("user_id", "anonimo")
        st.session_state[_SK_THREAD_ID] = f"lea_sessione_{user_id}"
    return st.session_state[_SK_THREAD_ID]


# ===========================================================================
# API pubblica
# ===========================================================================

def aggiorna_contesto_sessione(
    corso_id: int | None = None,
    corso_nome: str | None = None,
) -> None:
    """Aggiorna il contesto della sessione quando l'utente naviga tra le pagine.

    Chiamare dalle pagine Streamlit ogni volta che l'utente apre un corso.
    L'agente leggerà questo contesto tramite tool_leggi_contesto.

    Args:
        corso_id:   ID del corso attualmente visualizzato.
        corso_nome: Nome leggibile del corso.
    """
    contesto = st.session_state.get(_SK_CONTESTO, {})
    if corso_id is not None:
        contesto["corso_id"] = corso_id
        contesto["ultimi_paragrafi"] = []   # reset sezioni al cambio corso
    if corso_nome is not None:
        contesto["corso_nome"] = corso_nome
    st.session_state[_SK_CONTESTO] = contesto


def chat_con_orchestratore(
    messaggio_utente: str,
    corso_contestuale_id: int | None = None,
    corso_contestuale_nome: str | None = None,
) -> str:
    """Punto di ingresso unico per le pagine Streamlit.

    Args:
        messaggio_utente:       Testo scritto dall'utente.
        corso_contestuale_id:   ID del corso visualizzato (aggiorna il contesto se fornito).
        corso_contestuale_nome: Nome leggibile del corso (opzionale).

    Returns:
        Risposta testuale dell'agente, pronta per essere mostrata in UI.

    Esempio d'uso in una pagina Streamlit::

        from src.agents.orchestrator import chat_con_orchestratore, aggiorna_contesto_sessione

        # Una volta sola quando si carica la pagina del corso:
        aggiorna_contesto_sessione(corso_id=corso["id"], corso_nome=corso["nome"])

        # Ad ogni messaggio dell'utente:
        risposta = chat_con_orchestratore(st.session_state.input_utente)
        st.chat_message("assistant").write(risposta)
    """
    if corso_contestuale_id is not None:
        aggiorna_contesto_sessione(
            corso_id=corso_contestuale_id,
            corso_nome=corso_contestuale_nome,
        )

    # Aggiorna la variabile globale dal thread principale PRIMA di invocare
    # l'agente. I tool girano in thread background dove session_state
    # non è accessibile — leggono _STUDENTE_ID_CORRENTE dal modulo.
    _aggiorna_studente_corrente()

    return esegui_agente(
        _get_orchestratore(),
        messaggio_utente,
        thread_id=_get_thread_id(),
    )


def reset_sessione_chat() -> None:
    """Azzera agente, thread e contesto. Chiamare al logout dell'utente."""
    for chiave in [_SK_ORCHESTRATORE, _SK_AGENTE_TEORICO, _SK_THREAD_ID, _SK_CONTESTO]:
        st.session_state.pop(chiave, None)
