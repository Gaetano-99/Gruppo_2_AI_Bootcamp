"""
Modulo: content_gen.py
Responsabilità: Content Generation Engine (Agent 5).

Implementa un grafo LangGraph che:
    1. Recupera chunk semantici dal database (RAG).
    2. Genera una lezione in Markdown **esclusivamente** dai chunk recuperati.
    3. Genera strumenti didattici (quiz o flashcard) in formato strutturato
       con ``with_structured_output()`` e modelli Pydantic.
    4. Salva tutto nel database tracciando i ``chunk_ids_utilizzati``.

Note architetturali:
    - Il grafo è di tipo StateGraph (non ReAct), con nodi deterministici e
      un tool interno (`recupera_materiale_corso`) richiamato esplicitamente.
    - Il system prompt del LLM vieta esplicitamente l'uso di conoscenza esterna,
      garantendo la tracciabilità RAG.
    - Per `lezioni_corso` è obbligatorio `docente_id`; viene recuperato da
      `st.session_state.user`.
    - Per `piano_contenuti` è obbligatorio `paragrafo_id`; viene creato un
      paragrafo/capitolo/piano dedicato per ogni sessione.
"""

import json
import sys
import os
from typing import TypedDict, Literal, Annotated
import operator
import streamlit as st

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

from platform_sdk.database import db
from platform_sdk.llm import get_llm
from src.tools.rag_engine import cerca_chunk_rilevanti, formatta_contesto_rag, conta_chunk_corso

# ---------------------------------------------------------------------------
# Costanti
# ---------------------------------------------------------------------------
_MAX_CHUNK_IN_CONTESTO: int = 8   # limita il contesto per non eccedere i token

_SYSTEM_PROMPT_AGENTE = """Sei il Content Generation Engine della piattaforma LearnAI.
Il tuo compito è generare materiale didattico di alta qualità.

VINCOLO FONDAMENTALE — RISPETTALO RIGOROSAMENTE:
Puoi usare ESCLUSIVAMENTE le informazioni contenute nei chunk didattici che ti vengono
forniti come contesto. È severamente vietato attingere a conoscenze esterne.
Se i chunk non contengono informazioni sufficienti sull'argomento richiesto,
dichiara esplicitamente che il materiale disponibile è insufficiente.

Regole di stile:
- Scrivi sempre in italiano.
- Usa Markdown per le lezioni (titoli, elenchi, blocchi codice dove utile).
- Per quiz e flashcard usa strutture JSON precise e complete.
"""


# ---------------------------------------------------------------------------
# Stato del grafo
# ---------------------------------------------------------------------------

class ContentGenState(TypedDict):
    """Stato che fluisce attraverso i nodi del grafo LangGraph.

    Attributes:
        corso_id: ID del corso universitario da cui recuperare i materiali.
        argomento_richiesto: Descrizione dell'argomento da trattare.
        tipo_strumento: Tipo di strumento didattico da generare ('quiz' o 'flashcard').
        chunks_recuperati: Lista di dizionari con i chunk RAG (id, testo, ...).
        lezione_generata: Testo Markdown della lezione prodotta dall'LLM.
        strumenti_studio_generati: Dizionario con quiz o flashcard generati.
        chunk_ids_utilizzati: Lista degli ID dei chunk usati nella generazione.
        errore: Messaggio di errore, se presente (None in caso di successo).
    """
    corso_id: int
    argomento_richiesto: str
    tipo_strumento: Literal["quiz", "flashcard"]
    chunks_recuperati: list[dict]
    n_chunk_totali_corso: int           # conta totale per display UI
    lezione_generata: str
    strumenti_studio_generati: dict
    chunk_ids_utilizzati: list[int]
    errore: str | None


# ---------------------------------------------------------------------------
# Modelli Pydantic per structured output
# ---------------------------------------------------------------------------

class DomandaQuiz(BaseModel):
    """Rappresenta una singola domanda del quiz.

    Attributes:
        domanda: Testo della domanda.
        opzioni: Lista di 4 opzioni di risposta.
        risposta_corretta: Lettera dell'opzione corretta (A, B, C o D).
        spiegazione: Breve spiegazione della risposta corretta.
    """
    domanda: str = Field(description="Testo della domanda")
    opzioni: list[str] = Field(description="Lista di 4 opzioni di risposta")
    risposta_corretta: str = Field(description="Lettera della risposta corretta: A, B, C o D")
    spiegazione: str = Field(description="Spiegazione della risposta corretta")


class QuizGenerato(BaseModel):
    """Output strutturato per la generazione di un quiz.

    Attributes:
        titolo: Titolo del quiz.
        domande: Lista di domande con le relative opzioni e risposte.
    """
    titolo: str = Field(description="Titolo del quiz")
    domande: list[DomandaQuiz] = Field(description="Lista di domande del quiz")


class Flashcard(BaseModel):
    """Rappresenta una singola flashcard.

    Attributes:
        fronte: Domanda o concetto sul fronte della flashcard.
        retro: Risposta o definizione sul retro della flashcard.
    """
    fronte: str = Field(description="Domanda o concetto chiave")
    retro: str = Field(description="Risposta o definizione")


class FlashcardGenerata(BaseModel):
    """Output strutturato per la generazione di flashcard.

    Attributes:
        titolo: Titolo del mazzo di flashcard.
        cards: Lista di flashcard generate.
    """
    titolo: str = Field(description="Titolo del mazzo di flashcard")
    cards: list[Flashcard] = Field(description="Lista di flashcard")


# ---------------------------------------------------------------------------
# Nodi del grafo
# ---------------------------------------------------------------------------

def _nodo_recupera_chunks(stato: ContentGenState) -> dict:
    """Nodo RAG: recupera i chunk più rilevanti usando il RAG Engine.

    Delega interamente a ``cerca_chunk_rilevanti`` in ``rag_engine.py``
    la logica di keyword extraction, query SQL LIKE multi-campo e scoring.

    Args:
        stato: Stato corrente del grafo.

    Returns:
        Aggiornamento parziale dello stato con ``chunks_recuperati``,
        ``n_chunk_totali_corso`` ed eventuale ``errore``.
    """
    corso_id: int = stato["corso_id"]
    argomento: str = stato["argomento_richiesto"]

    # Conta totale chunk del corso (per display UI)
    n_totali: int = conta_chunk_corso(corso_id)

    if n_totali == 0:
        return {
            "chunks_recuperati": [],
            "n_chunk_totali_corso": 0,
            "errore": (
                "Nessun materiale didattico disponibile per questo corso. "
                "Carica prima un documento nella sezione Upload."
            ),
        }

    # Retrieval intelligente: SQL LIKE + scoring pesato
    chunks_rilevanti: list[dict] = cerca_chunk_rilevanti(
        corso_id=corso_id,
        query=argomento,
        top_k=_MAX_CHUNK_IN_CONTESTO,
    )

    return {
        "chunks_recuperati": chunks_rilevanti,
        "n_chunk_totali_corso": n_totali,
        "errore": None,
    }


def _nodo_genera_lezione(stato: ContentGenState) -> dict:
    """Nodo di generazione: produce la lezione in Markdown dai chunk RAG.

    Usa ``formatta_contesto_rag`` per costruire il contesto con ID espliciti,
    permettendo all'LLM di citare i chunk usati.

    Args:
        stato: Stato corrente del grafo (deve contenere ``chunks_recuperati``).

    Returns:
        Aggiornamento parziale dello stato con ``lezione_generata`` e
        ``chunk_ids_utilizzati``.
    """
    if stato.get("errore"):
        return {"lezione_generata": "", "chunk_ids_utilizzati": []}

    chunks: list[dict] = stato["chunks_recuperati"]
    argomento: str = stato["argomento_richiesto"]

    # Formatta il contesto RAG con ID espliciti per la citazione
    contesto_rag: str = formatta_contesto_rag(chunks)
    chunk_ids: list[int] = [c["id"] for c in chunks]

    prompt_lezione = f"""Genera una lezione didattica completa sull'argomento: "{argomento}".

CONTESTO DIDATTICO (usa SOLO queste informazioni):
{contesto_rag}

ISTRUZIONE FONDAMENTALE: ogni affermazione deve provenire dai chunk sopra.
Non aggiungere informazioni esterne. Se il materiale è insufficiente, dichiaralo.

Struttura richiesta:
1. Titolo principale (# Titolo)
2. Introduzione (2-3 paragrafi)
3. Concetti chiave (con sottotitoli ##)
4. Esempi pratici dove presenti nel materiale
5. Riepilogo finale

Formato: Markdown. Lingua: Italiano."""

    llm = get_llm()
    messaggi = [
        SystemMessage(content=_SYSTEM_PROMPT_AGENTE),
        HumanMessage(content=prompt_lezione),
    ]
    risposta = llm.invoke(messaggi)
    lezione: str = risposta.content if isinstance(risposta.content, str) else str(risposta.content)

    return {
        "lezione_generata": lezione,
        "chunk_ids_utilizzati": chunk_ids,
    }


def _nodo_genera_strumenti_studio(stato: ContentGenState) -> dict:
    """Nodo di generazione: produce quiz o flashcard con structured output.

    Args:
        stato: Stato corrente del grafo.

    Returns:
        Aggiornamento parziale dello stato con ``strumenti_studio_generati``.
    """
    if stato.get("errore") or not stato.get("lezione_generata"):
        return {"strumenti_studio_generati": {}}

    chunks: list[dict] = stato["chunks_recuperati"]
    argomento: str = stato["argomento_richiesto"]
    tipo_strumento: str = stato.get("tipo_strumento", "quiz")

    contesto_rag: str = formatta_contesto_rag(chunks)

    llm = get_llm()

    if tipo_strumento == "quiz":
        llm_strutturato = llm.with_structured_output(QuizGenerato)
        prompt = (
            f"Genera un quiz di 5 domande a risposta multipla sull'argomento: "
            f'"{argomento}".\n\n'
            f"Basa le domande ESCLUSIVAMENTE su questi chunk:\n{contesto_rag}"
        )
    else:  # flashcard
        llm_strutturato = llm.with_structured_output(FlashcardGenerata)
        prompt = (
            f"Genera 10 flashcard per studiare l'argomento: "
            f'"{argomento}".\n\n'
            f"Basa le flashcard ESCLUSIVAMENTE su questi chunk:\n{contesto_rag}"
        )

    messaggi = [
        SystemMessage(content=_SYSTEM_PROMPT_AGENTE),
        HumanMessage(content=prompt),
    ]
    output_strutturato = llm_strutturato.invoke(messaggi)
    output_dict: dict = output_strutturato.model_dump()

    return {"strumenti_studio_generati": output_dict}


def _nodo_salva_risultati(stato: ContentGenState) -> dict:
    """Nodo di persistenza: salva lezione e strumenti nel database.

    Salva in:
        - ``lezioni_corso`` la lezione generata con i ``chunk_ids_utilizzati``.
        - ``piano_contenuti`` il quiz/flashcard tramite un piano mock dedicato.

    Args:
        stato: Stato corrente del grafo (deve essere completo).

    Returns:
        Dizionario vuoto (non modifica lo stato).
    """
    if stato.get("errore"):
        return {}

    corso_id: int = stato["corso_id"]
    chunk_ids: list[int] = stato.get("chunk_ids_utilizzati", [])
    argomento: str = stato["argomento_richiesto"]

    # Salva la lezione
    if stato.get("lezione_generata"):
        db.inserisci(
            "lezioni_corso",
            {
                "corso_universitario_id": corso_id,
                "docente_id": st.session_state.user["user_id"],
                "titolo": f"Lezione: {argomento}",
                "contenuto_md": stato["lezione_generata"],
                "creato_da": "ai",
                "approvato": 0,
                "chunk_ids_utilizzati": chunk_ids,
            },
        )

    # Salva gli strumenti di studio tramite piano mock
    if stato.get("strumenti_studio_generati"):
        tipo_strumento: str = stato.get("tipo_strumento", "quiz")
        user_id = st.session_state.user["user_id"]

        # Crea piano mock per tracciare il contenuto (richiesto dallo schema)
        piano_id: int = db.inserisci(
            "piani_personalizzati",
            {
                "studente_id": user_id,
                "titolo": f"[TEST] Piano per: {argomento}",
                "tipo": "esame",
                "corso_universitario_id": corso_id,
                "stato": "attivo",
            },
        )
        capitolo_id: int = db.inserisci(
            "piano_capitoli",
            {
                "piano_id": piano_id,
                "titolo": argomento,
                "ordine": 0,
            },
        )
        paragrafo_id: int = db.inserisci(
            "piano_paragrafi",
            {
                "capitolo_id": capitolo_id,
                "titolo": tipo_strumento.capitalize(),
                "ordine": 0,
            },
        )
        db.inserisci(
            "piano_contenuti",
            {
                "paragrafo_id": paragrafo_id,
                "tipo": tipo_strumento,
                "contenuto_json": stato["strumenti_studio_generati"],
                "chunk_ids_utilizzati": chunk_ids,
                "generato_al_momento": 1,
            },
        )

    return {}


# ---------------------------------------------------------------------------
# Costruzione del grafo
# ---------------------------------------------------------------------------

def crea_agente_content_gen():
    """Costruisce e compila il grafo LangGraph per la generazione di contenuti.

    Il grafo segue questo flusso:
        recupera_chunks → genera_lezione → genera_strumenti → salva_risultati → END

    Returns:
        Il grafo compilato, pronto per essere invocato con ``.invoke(stato)``.
    """
    grafo = StateGraph(ContentGenState)

    grafo.add_node("recupera_chunks", _nodo_recupera_chunks)
    grafo.add_node("genera_lezione", _nodo_genera_lezione)
    grafo.add_node("genera_strumenti_studio", _nodo_genera_strumenti_studio)
    grafo.add_node("salva_risultati", _nodo_salva_risultati)

    grafo.set_entry_point("recupera_chunks")
    grafo.add_edge("recupera_chunks", "genera_lezione")
    grafo.add_edge("genera_lezione", "genera_strumenti_studio")
    grafo.add_edge("genera_strumenti_studio", "salva_risultati")
    grafo.add_edge("salva_risultati", END)

    return grafo.compile()


def esegui_generazione(
    agente,
    corso_id: int,
    argomento_richiesto: str,
    tipo_strumento: Literal["quiz", "flashcard"] = "quiz",
) -> ContentGenState:
    """Avvia il grafo di generazione contenuti e restituisce lo stato finale.

    Args:
        agente: Grafo compilato creato con ``crea_agente_content_gen()``.
        corso_id: ID del corso universitario.
        argomento_richiesto: Argomento su cui generare i contenuti.
        tipo_strumento: Tipo di strumento didattico (``'quiz'`` o ``'flashcard'``).

    Returns:
        Lo stato finale del grafo con tutti i campi popolati.
    """
    stato_iniziale: ContentGenState = {
        "corso_id": corso_id,
        "argomento_richiesto": argomento_richiesto,
        "tipo_strumento": tipo_strumento,
        "chunks_recuperati": [],
        "n_chunk_totali_corso": 0,
        "lezione_generata": "",
        "strumenti_studio_generati": {},
        "chunk_ids_utilizzati": [],
        "errore": None,
    }
    return agente.invoke(stato_iniziale)
