"""
Modulo: practice_gen.py
Responsabilità: Agente Pratico (Esercitatore) — Generazione di strumenti di studio.

Riceve in input il testo di un paragrafo specifico e genera, a comando, 
quiz, flashcard o diagrammi (Mermaid) basati ESCLUSIVAMENTE su quel testo.
Salva i risultati nel database mantenendo il collegamento con il paragrafo.
"""

import json
import sys
import os
from typing import TypedDict, Optional

from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from platform_sdk.database import db
from platform_sdk.llm import get_llm

# ---------------------------------------------------------------------------
# Costanti
# ---------------------------------------------------------------------------
_SYSTEM_PROMPT = """Sei l'Agente Esercitatore della piattaforma LearnAI.
Il tuo compito è creare strumenti di studio (quiz, flashcard, diagrammi) a partire da un testo didattico.

VINCOLO FONDAMENTALE:
Usa ESCLUSIVAMENTE le informazioni presenti nel testo fornito. Non inventare o aggiungere 
concetti esterni. Se il testo non contiene informazioni sufficienti per uno strumento, 
non generarlo.

Regole:
- Scrivi sempre in italiano.
- I quiz devono avere sempre 3 o 4 opzioni plausibili.
- Le flashcard devono essere concise (domanda diretta, risposta chiara).
- I diagrammi Mermaid devono essere validi e pronti per il rendering (es. graph TD).
"""

# ---------------------------------------------------------------------------
# Modelli Pydantic — Structured Output
# ---------------------------------------------------------------------------

class DomandaQuiz(BaseModel):
    testo: str = Field(description="Il testo della domanda")
    tipo: str = Field(description="Tipo di domanda, deve essere sempre 'scelta_multipla'", default="scelta_multipla")
    opzioni: list[str] = Field(description="Lista delle opzioni di risposta")
    indice_corretta: int = Field(description="Indice (partendo da 0) dell'opzione corretta")
    spiegazione: str = Field(description="Breve spiegazione del perché la risposta è corretta")

class Flashcard(BaseModel):
    fronte: str = Field(description="Domanda o concetto da ricordare (Fronte della carta)")
    retro: str = Field(description="Risposta o spiegazione del concetto (Retro della carta)")

class SchemaMermaid(BaseModel):
    codice_mermaid: str = Field(description="Codice Mermaid.js valido per renderizzare il diagramma")

class GenerazionePratica(BaseModel):
    """Contenitore per tutti gli strumenti generati."""
    quiz: Optional[list[DomandaQuiz]] = Field(default=None, description="Lista di domande per il quiz")
    flashcards: Optional[list[Flashcard]] = Field(default=None, description="Lista di flashcard")
    schema_mermaid: Optional[SchemaMermaid] = Field(default=None, description="Schema o diagramma concettuale")

# ---------------------------------------------------------------------------
# Stato del grafo
# ---------------------------------------------------------------------------

class PracticeGenState(TypedDict):
    paragrafo_id: int
    testo_paragrafo: str
    strumenti_richiesti: list[str]  # es. ["quiz", "flashcard", "schema"]
    studente_id: int
    corso_universitario_id: Optional[int]
    chunk_ids_utilizzati: list[int]
    strumenti_generati: dict
    errore: Optional[str]

# ---------------------------------------------------------------------------
# Nodi del grafo
# ---------------------------------------------------------------------------

def _nodo_genera_strumenti(stato: PracticeGenState) -> dict:
    """Invoca l'LLM per generare gli strumenti richiesti."""
    testo = stato["testo_paragrafo"]
    richiesti = stato["strumenti_richiesti"]
    
    if not testo or not richiesti:
        return {"errore": "Testo mancante o nessuno strumento richiesto."}

    prompt_utente = f"""Genera i seguenti strumenti di studio: {', '.join(richiesti)}.
    
Basati ESCLUSIVAMENTE su questo testo didattico:
---
{testo}
---
"""

    llm = get_llm()
    llm_strutturato = llm.with_structured_output(GenerazionePratica)
    
    messaggi = [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=prompt_utente)
    ]
    
    try:
        output: GenerazionePratica = llm_strutturato.invoke(messaggi)
        return {"strumenti_generati": output.model_dump(exclude_none=True)}
    except Exception as e:
        return {"errore": f"Errore nella generazione LLM: {str(e)}"}


def _nodo_salva_strumenti(stato: PracticeGenState) -> dict:
    """Salva i risultati nel database secondo il Nuovo_schema.sql."""
    if stato.get("errore") or not stato.get("strumenti_generati"):
        return {}

    dati = stato["strumenti_generati"]
    paragrafo_id = stato["paragrafo_id"]
    studente_id = stato["studente_id"]
    corso_id = stato.get("corso_universitario_id")
    chunk_ids_json = json.dumps(stato.get("chunk_ids_utilizzati", []))

    # 1. Salvataggio QUIZ
    if "quiz" in dati and dati["quiz"]:
        # Crea il record principale del quiz
        quiz_id = db.inserisci("quiz", {
            "titolo": f"Quiz di ripasso (Paragrafo {paragrafo_id})",
            "corso_universitario_id": corso_id,
            "studente_id": studente_id,
            "docente_id": None,
            "creato_da": "ai",
            "approvato": 0,
            "ripetibile": 1
        })
        
        # Inserisci le singole domande
        for i, dom in enumerate(dati["quiz"]):
            db.inserisci("domande_quiz", {
                "quiz_id": quiz_id,
                "testo": dom["testo"],
                "tipo": "scelta_multipla",
                "opzioni_json": json.dumps(dom["opzioni"]),
                "risposta_corretta": str(dom["indice_corretta"]), # Salviamo l'indice come stringa
                "spiegazione": dom["spiegazione"],
                "ordine": i
            })
            
        # Collega il quiz al piano contenuti
        db.inserisci("piano_contenuti", {
            "paragrafo_id": paragrafo_id,
            "tipo": "quiz",
            "contenuto_json": None, # Il contenuto sta nelle tabelle quiz
            "quiz_id": quiz_id,
            "chunk_ids_utilizzati": chunk_ids_json,
            "generato_al_momento": 1
        })

    # 2. Salvataggio FLASHCARDS
    if "flashcards" in dati and dati["flashcards"]:
        db.inserisci("piano_contenuti", {
            "paragrafo_id": paragrafo_id,
            "tipo": "flashcard",
            "contenuto_json": json.dumps(dati["flashcards"]),
            "quiz_id": None,
            "chunk_ids_utilizzati": chunk_ids_json,
            "generato_al_momento": 1
        })

    # 3. Salvataggio SCHEMA (Mermaid)
    if "schema_mermaid" in dati and dati["schema_mermaid"]:
        db.inserisci("piano_contenuti", {
            "paragrafo_id": paragrafo_id,
            "tipo": "schema",
            "contenuto_json": json.dumps({"codice": dati["schema_mermaid"]["codice_mermaid"]}),
            "quiz_id": None,
            "chunk_ids_utilizzati": chunk_ids_json,
            "generato_al_momento": 1
        })

    return {}

# ---------------------------------------------------------------------------
# Costruzione del grafo
# ---------------------------------------------------------------------------

def crea_agente_practice_gen():
    """Costruisce e compila il grafo per l'agente pratico."""
    grafo = StateGraph(PracticeGenState)

    grafo.add_node("genera_strumenti", _nodo_genera_strumenti)
    grafo.add_node("salva_strumenti", _nodo_salva_strumenti)

    grafo.set_entry_point("genera_strumenti")
    grafo.add_edge("genera_strumenti", "salva_strumenti")
    grafo.add_edge("salva_strumenti", END)

    return grafo.compile()


def esegui_generazione_pratica(
    paragrafo_id: int,
    testo_paragrafo: str,
    strumenti_richiesti: list[str],
    studente_id: int,
    corso_universitario_id: int = None,
    chunk_ids_utilizzati: list[int] = None
) -> PracticeGenState:
    """Avvia la generazione di strumenti pratici."""
    agente = crea_agente_practice_gen()
    
    stato_iniziale: PracticeGenState = {
        "paragrafo_id": paragrafo_id,
        "testo_paragrafo": testo_paragrafo,
        "strumenti_richiesti": strumenti_richiesti,
        "studente_id": studente_id,
        "corso_universitario_id": corso_universitario_id,
        "chunk_ids_utilizzati": chunk_ids_utilizzati or [],
        "strumenti_generati": {},
        "errore": None
    }
    
    return agente.invoke(stato_iniziale)