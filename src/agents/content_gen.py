"""
Modulo: content_gen.py
Responsabilità: Agente Teorico (Docente) — Content Generation Engine.

Implementa un grafo LangGraph che:
    1. Recupera chunk semantici dal database (RAG).
    2. Genera una struttura corso JSON fortemente tipizzata tramite Pydantic
       (`StrutturaCorso`) usando `with_structured_output()`.
    3. Salva il JSON strutturato nel database tracciando i `chunk_ids_utilizzati`.

La generazione di quiz e flashcard è delegata ad agenti separati (fuori scope).

Note architetturali:
    - Il grafo è di tipo StateGraph con nodi deterministici.
    - Il system prompt del LLM vieta esplicitamente l'uso di conoscenza esterna,
      garantendo la tracciabilità RAG.
    - Per `lezioni_corso` è obbligatorio `docente_id`; viene recuperato da
      `st.session_state.user`.
"""

import json
import sys
import os
import re
from functools import lru_cache
from typing import TypedDict

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
from src.tools.rag_engine import cerca_chunk_rilevanti, formatta_contesto_rag, conta_chunk_corso


# ---------------------------------------------------------------------------
# Costanti
# ---------------------------------------------------------------------------
_MAX_CHUNK_IN_CONTESTO: int = 8

_SYSTEM_PROMPT_AGENTE = """Sei il Content Generation Engine della piattaforma LearnAI.
Il tuo compito è strutturare materiale didattico in un formato JSON rigoroso.

VINCOLO FONDAMENTALE — RISPETTALO RIGOROSAMENTE:
Puoi usare ESCLUSIVAMENTE le informazioni contenute nei chunk didattici che ti vengono
forniti come contesto. È severamente vietato attingere a conoscenze esterne.
Se i chunk non contengono informazioni sufficienti sull'argomento richiesto,
dichiara esplicitamente che il materiale disponibile è insufficiente.

Regole:
- Scrivi sempre in italiano.
- Struttura i contenuti in capitoli e paragrafi coerenti.
- Ogni paragrafo deve contenere testo didattico sostanzioso estratto dai chunk.
- Assegna ID univoci a capitoli (cap_01, cap_02, ...) e paragrafi (par_01_01, par_01_02, ...).
"""


@lru_cache(maxsize=1)
def _db_supporta_tipo_corso() -> bool:
    """Rileva se il DB corrente accetta `tipo='corso'` in piani_personalizzati."""
    try:
        righe = db.esegui(
            "SELECT sql FROM sqlite_master WHERE type = ? AND name = ?",
            ["table", "piani_personalizzati"],
        )
    except Exception:
        return False

    if not righe:
        return False

    create_sql = (righe[0].get("sql") or "").lower()
    return bool(
        re.search(
            r"check\s*\(\s*tipo\s+in\s*\(\s*'esame'\s*,\s*'libero'\s*,\s*'corso'\s*\)\s*\)",
            create_sql,
        )
    )


def _tipo_piano_da_salvare(is_corso: bool) -> str:
    """Mantiene compatibilita' con DB legacy che non accettano ancora `corso`."""
    if not is_corso:
        return "esame"
    return "corso" if _db_supporta_tipo_corso() else "esame"


# ---------------------------------------------------------------------------
# Modelli Pydantic — Structured Output
# ---------------------------------------------------------------------------

class Paragrafo(BaseModel):
    """Un singolo paragrafo didattico all'interno di un capitolo."""
    id_paragrafo: str = Field(description="ID univoco del paragrafo (es: par_01_01)")
    titolo: str = Field(description="Titolo del paragrafo")
    testo: str = Field(description="Contenuto didattico completo del paragrafo")


class Capitolo(BaseModel):
    """Un capitolo del corso, contenente uno o più paragrafi."""
    id_capitolo: str = Field(description="ID univoco del capitolo (es: cap_01)")
    titolo: str = Field(description="Titolo del capitolo")
    ordine: int = Field(description="Ordine sequenziale del capitolo nel corso")
    paragrafi: list[Paragrafo] = Field(description="Lista dei paragrafi del capitolo")


class StrutturaCorso(BaseModel):
    """Output strutturato: la struttura completa di un corso generato dall'LLM."""
    titolo_corso: str = Field(description="Titolo del corso")
    descrizione_breve: str = Field(description="Descrizione sintetica del corso")
    durata_stimata_minuti: int = Field(description="Durata stimata in minuti")
    capitoli: list[Capitolo] = Field(description="Lista dei capitoli del corso")


# ---------------------------------------------------------------------------
# Stato del grafo
# ---------------------------------------------------------------------------

class ContentGenState(TypedDict):
    """Stato che fluisce attraverso i nodi del grafo LangGraph.

    Attributes:
        corso_id: ID del corso universitario da cui recuperare i materiali.
        argomento_richiesto: Descrizione dell'argomento da trattare.
        docente_id: ID del docente che richiede la generazione.
        is_corso_docente: Se True, il risultato è un corso docente; se False, piano studente.
        chunks_recuperati: Lista di dizionari con i chunk RAG (id, testo, ...).
        n_chunk_totali_corso: Conteggio totale chunk del corso (per display).
        struttura_corso_generata: Dizionario JSON con la StrutturaCorso prodotta.
        chunk_ids_utilizzati: Lista degli ID dei chunk usati nella generazione.
        errore: Messaggio di errore, se presente (None in caso di successo).
    """
    corso_id: int
    argomento_richiesto: str
    docente_id: int
    is_corso_docente: bool
    chunks_recuperati: list[dict]
    n_chunk_totali_corso: int
    struttura_corso_generata: dict
    chunk_ids_utilizzati: list[int]
    errore: str | None


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


def _nodo_genera_struttura_corso(stato: ContentGenState) -> dict:
    """Nodo di generazione: produce la StrutturaCorso JSON dai chunk RAG.

    Usa ``with_structured_output(StrutturaCorso)`` per forzare l'LLM a
    restituire un oggetto Pydantic validato, poi lo converte in dict.

    Args:
        stato: Stato corrente del grafo (deve contenere ``chunks_recuperati``).

    Returns:
        Aggiornamento parziale dello stato con ``struttura_corso_generata`` e
        ``chunk_ids_utilizzati``.
    """
    if stato.get("errore"):
        return {"struttura_corso_generata": {}, "chunk_ids_utilizzati": []}

    chunks: list[dict] = stato["chunks_recuperati"]
    argomento: str = stato["argomento_richiesto"]

    contesto_rag: str = formatta_contesto_rag(chunks)
    chunk_ids: list[int] = [c["id"] for c in chunks]

    prompt_struttura = f"""Genera la struttura completa di un corso didattico sull'argomento: "{argomento}".

CONTESTO DIDATTICO (usa SOLO queste informazioni):
{contesto_rag}

ISTRUZIONE FONDAMENTALE: ogni affermazione deve provenire dai chunk sopra.
Non aggiungere informazioni esterne. Se il materiale è insufficiente, dichiaralo.

Organizza i contenuti in:
- Capitoli tematici coerenti (con id_capitolo, titolo, ordine)
- Paragrafi all'interno di ogni capitolo (con id_paragrafo, titolo, testo didattico sostanzioso)

Il campo "testo" di ogni paragrafo deve contenere il contenuto didattico vero e proprio,
con spiegazioni chiare e dettagliate estratte dal materiale fornito.
Stima la durata totale del corso in minuti.

Lingua: Italiano."""

    llm = get_llm()
    llm_strutturato = llm.with_structured_output(StrutturaCorso)

    messaggi = [
        SystemMessage(content=_SYSTEM_PROMPT_AGENTE),
        HumanMessage(content=prompt_struttura),
    ]
    output: StrutturaCorso = llm_strutturato.invoke(messaggi)

    return {
        "struttura_corso_generata": output.model_dump(),
        "chunk_ids_utilizzati": chunk_ids,
    }


def _nodo_salva_risultati(stato: ContentGenState) -> dict:
    """Nodo di persistenza: normalizza e salva la StrutturaCorso nel database.

    Decompone il JSON generato e lo salva nelle tabelle relazionali:
        piani_personalizzati → piano_capitoli → piano_paragrafi → piano_contenuti

    Il campo ``is_corso_docente`` distingue tra corso docente (1) e piano studente (0).

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
    struttura: dict = stato.get("struttura_corso_generata", {})
    is_corso: bool = stato.get("is_corso_docente", True)

    if not struttura:
        return {"errore": "Struttura corso vuota: il modello non ha prodotto output valido."}

    titolo_corso: str = struttura.get("titolo_corso", argomento)
    # Per i piani studente il titolo generato dall'LLM coincide spesso col nome
    # del corso universitario. Prefissare con "Piano: " garantisce distinzione visiva.
    if not is_corso:
        titolo_corso = f"Piano: {titolo_corso}"
    descrizione: str = struttura.get("descrizione_breve", "")

    try:
        return _salva_struttura_nel_db(stato, struttura, titolo_corso, descrizione, chunk_ids, corso_id, is_corso)
    except Exception as exc:
        return {"errore": f"Errore DB durante il salvataggio: {exc}"}


def _salva_struttura_nel_db(stato, struttura, titolo_corso, descrizione, chunk_ids, corso_id, is_corso) -> dict:
    """Esegue le insert nel DB. Separata da _nodo_salva_risultati per isolare il try/except."""
    # Per i piani studente: ricava il nome del corso per evitare che capitoli/paragrafi
    # abbiano lo stesso titolo del corso universitario di appartenenza.
    nome_corso_norm: str = ""
    if not is_corso and corso_id:
        try:
            riga_corso = db.esegui("SELECT nome FROM corsi_universitari WHERE id = ?", [corso_id])
            if riga_corso:
                nome_corso_norm = (riga_corso[0]["nome"] or "").strip().lower()
        except Exception:
            pass

    def _disambigua(titolo: str) -> str:
        """Aggiunge ' — Approfondimento' se il titolo coincide col nome del corso."""
        if nome_corso_norm and titolo.strip().lower() == nome_corso_norm:
            return titolo + " — Approfondimento"
        return titolo

    # 1. Crea il piano (corso docente o piano studente)
    piano_id: int = db.inserisci(
        "piani_personalizzati",
        {
            "studente_id": stato["docente_id"],  # docente come creatore
            "titolo": titolo_corso,
            "descrizione": descrizione,
            # `is_corso_docente` resta la fonte di verita' anche sui DB legacy.
            "tipo": _tipo_piano_da_salvare(is_corso),
            "corso_universitario_id": corso_id,
            "stato": "attivo",
            "is_corso_docente": 1 if is_corso else 0,
        },
    )

    # 2. Per ogni capitolo → piano_capitoli → piano_paragrafi → piano_contenuti
    for capitolo in struttura.get("capitoli", []):
        capitolo_id: int = db.inserisci(
            "piano_capitoli",
            {
                "piano_id": piano_id,
                "titolo": _disambigua(capitolo["titolo"]),
                "ordine": capitolo.get("ordine", 0),
            },
        )

        for paragrafo in capitolo.get("paragrafi", []):
            paragrafo_id: int = db.inserisci(
                "piano_paragrafi",
                {
                    "capitolo_id": capitolo_id,
                    "titolo": _disambigua(paragrafo["titolo"]),
                    "ordine": 0,
                },
            )
            db.inserisci(
                "piano_contenuti",
                {
                    "paragrafo_id": paragrafo_id,
                    "tipo": "lezione",
                    "contenuto_json": paragrafo["testo"],
                    "chunk_ids_utilizzati": json.dumps(chunk_ids),  # FIX: lista → JSON string
                    "generato_al_momento": 0,
                },
            )

    return {}


# ---------------------------------------------------------------------------
# Costruzione del grafo
# ---------------------------------------------------------------------------

def crea_agente_content_gen():
    """Costruisce e compila il grafo LangGraph per la generazione di contenuti.

    Il grafo segue questo flusso:
        recupera_chunks → genera_struttura_corso → salva_risultati → END

    Returns:
        Il grafo compilato, pronto per essere invocato con ``.invoke(stato)``.
    """
    grafo = StateGraph(ContentGenState)

    grafo.add_node("recupera_chunks", _nodo_recupera_chunks)
    grafo.add_node("genera_struttura_corso", _nodo_genera_struttura_corso)
    grafo.add_node("salva_risultati", _nodo_salva_risultati)

    grafo.set_entry_point("recupera_chunks")
    grafo.add_edge("recupera_chunks", "genera_struttura_corso")
    grafo.add_edge("genera_struttura_corso", "salva_risultati")
    grafo.add_edge("salva_risultati", END)

    return grafo.compile()


def esegui_generazione(
    agente,
    corso_id: int,
    argomento_richiesto: str,
    docente_id: int = 1,
    is_corso_docente: bool = True,
) -> ContentGenState:
    """Avvia il grafo di generazione contenuti e restituisce lo stato finale.

    Args:
        agente: Grafo compilato creato con ``crea_agente_content_gen()``.
        corso_id: ID del corso universitario.
        argomento_richiesto: Argomento su cui generare i contenuti.
        docente_id: ID del docente che richiede la generazione.
        is_corso_docente: Se True, salva come corso docente; se False, come piano studente.

    Returns:
        Lo stato finale del grafo con tutti i campi popolati.
    """
    stato_iniziale: ContentGenState = {
        "corso_id": corso_id,
        "docente_id": docente_id,
        "is_corso_docente": is_corso_docente,
        "argomento_richiesto": argomento_richiesto,
        "chunks_recuperati": [],
        "n_chunk_totali_corso": 0,
        "struttura_corso_generata": {},
        "chunk_ids_utilizzati": [],
        "errore": None,
    }
    return agente.invoke(stato_iniziale)
