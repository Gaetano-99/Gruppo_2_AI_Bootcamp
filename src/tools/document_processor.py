"""
Modulo: document_processor.py
Responsabilità: estrazione del testo da file caricati, suddivisione in chunk
semantici (paragrafi) e persistenza nelle tabelle `materiali_didattici` e
`materiali_chunks` del database LearnAI.

Note architetturali:
    - Usa `estrai_testo_da_upload` dalla platform_sdk per supportare PDF,
      TXT, CSV, XLS/XLSX senza dipendenze aggiuntive.
    - Il chunking avviene su paragrafi separati da righe vuote consecutive;
      i chunk troppo brevi vengono uniti al successivo per evitare frammenti
      privi di contesto.
    - Il campo `docente_id` di `materiali_didattici` è obbligatorio per lo
      schema; in modalità test-studente viene usato il docente_id=1 (seed data).
    - Rispetta la regola di idempotenza: se `is_processed=1` i chunk esistono
      già e non vengono rigenerati.
"""

import re
import sys
import os
import streamlit as st
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage

# ---------------------------------------------------------------------------
# Path setup — permette l'import del progetto dalla root in qualunque contesto
# ---------------------------------------------------------------------------
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from platform_sdk.database import db
from platform_sdk.llm import estrai_testo_da_upload, get_llm

# ---------------------------------------------------------------------------
# Costanti di chunking
# ---------------------------------------------------------------------------
_DIMENSIONE_MIN_CHUNK_CARATTERI: int = 600   # chunk più corti vengono uniti
_DIMENSIONE_MAX_CHUNK_CARATTERI: int = 4000  # chunk più lunghi vengono divisi


# ---------------------------------------------------------------------------
# Modello Pydantic per l'arricchimento LLM dei chunk
# ---------------------------------------------------------------------------

class MetadatiChunk(BaseModel):
    """Metadati semantici generati dall'LLM per un singolo chunk didattico."""
    titolo_sezione: str = Field(description="Titolo breve e descrittivo della sezione (max 10 parole)")
    sommario: str = Field(description="Riassunto del contenuto in 2-3 frasi")
    argomenti_chiave: list[str] = Field(description="Lista di 3-7 parole/frasi chiave che identificano i concetti principali")


# ---------------------------------------------------------------------------
# Funzioni pubbliche
# ---------------------------------------------------------------------------


def elabora_e_salva_documento(
    uploaded_file,
    corso_universitario_id: int | None,
    titolo: str,
    tipo: str = "dispensa",
    progress_callback=None,
) -> int:
    """Estrae il testo da un file caricato, salva il materiale didattico e
    crea i chunk semantici nel database.

    Il flusso completo è:
        1. Estrai il testo grezzo dal file.
        2. Inserisci il record in ``materiali_didattici`` (``is_processed=0``).
        3. Dividi il testo in chunk per paragrafi.
        4. Salva ogni chunk in ``materiali_chunks``.
        5. Aggiorna ``is_processed=1`` su ``materiali_didattici``.

    Args:
        uploaded_file: Oggetto ``UploadedFile`` da ``st.file_uploader()``.
        corso_universitario_id: ID del corso a cui associare il materiale.
        titolo: Titolo descrittivo del documento.
        tipo: Tipo di materiale (default ``'dispensa'``).

    Returns:
        L'ID del record inserito in ``materiali_didattici``.

    Raises:
        ValueError: Se il testo estratto è vuoto o il tipo non è valido.
    """
    # Mappa le estensioni comuni ai tipi accettati dallo schema DB
    _MAPPA_ESTENSIONI = {
        "pptx": "slide", "ppt": "slide",
        "docx": "dispensa", "doc": "dispensa",
        "txt": "dispensa", "xlsx": "dispensa", "xls": "dispensa",
        "csv": "dispensa",
    }
    tipo = _MAPPA_ESTENSIONI.get(tipo, tipo)

    tipi_validi = {"pdf", "slide", "video", "dispensa", "libro"}
    if tipo not in tipi_validi:
        raise ValueError(
            f"Tipo '{tipo}' non valido. Usa uno tra: {', '.join(tipi_validi)}"
        )

    # 1. Estrai testo
    testo_estratto: str = estrai_testo_da_upload(uploaded_file)
    if not testo_estratto or not testo_estratto.strip():
        nome = getattr(uploaded_file, "name", "file")
        ext = nome.rsplit(".", 1)[-1].lower() if "." in nome else ""
        if ext == "pdf":
            raise ValueError(
                "Il PDF non contiene testo selezionabile. "
                "Probabilmente è una scansione o contiene solo immagini. "
                "Converti il file con uno strumento OCR e ricaricalo."
            )
        raise ValueError(
            f"Il file '{nome}' non contiene testo leggibile. "
            "Verifica che il file non sia corrotto o protetto da password."
        )

    # Controlla se il testo è quasi tutto composto da segnaposti immagine (PDF scansionato)
    _linee = [l.strip() for l in testo_estratto.splitlines() if l.strip()]
    if _linee:
        _linee_immagine = sum(1 for l in _linee if l.startswith("[Pagina ") and "non testuale" in l)
        if _linee_immagine == len(_linee):
            raise ValueError(
                "Il PDF sembra essere una scansione: tutte le pagine contengono solo immagini, "
                "nessun testo selezionabile è stato trovato. "
                "Converti il file con uno strumento OCR e ricaricalo."
            )

    # 2. Inserisci il materiale didattico nel DB
    materiale_id: int = db.inserisci(
        "materiali_didattici",
        {
            "corso_universitario_id": corso_universitario_id,
            "docente_id": st.session_state.user["user_id"], # <-- SOSTITUITO _DOCENTE_ID_MOCK
            "titolo": titolo,
            "tipo": tipo,
            "s3_key": f"didattica/test/{corso_universitario_id}/{titolo.replace(' ', '_')}",
            "testo_estratto": testo_estratto,
            "is_processed": 0,
        },
    )

    # 3-4. Chunking e salvataggio
    chunk_ids: list[int] = _crea_e_salva_chunks(
        testo=testo_estratto,
        materiale_id=materiale_id,
        corso_universitario_id=corso_universitario_id,
    )

    # 4b. Arricchimento semantico: genera titolo_sezione, sommario, argomenti_chiave
    _arricchisci_chunks_con_llm(chunk_ids, progress_callback=progress_callback)

    # 5. Marca il materiale come processato
    db.aggiorna(
        "materiali_didattici",
        {"id": materiale_id},
        {"is_processed": 1},
    )

    return materiale_id


def _crea_e_salva_chunks(
    testo: str,
    materiale_id: int,
    corso_universitario_id: int,
) -> list[int]:
    """Divide il testo in chunk semantici (paragrafi) e li salva nel DB.

    La suddivisione avviene su doppie interruzioni di riga (\\n\\n), che
    corrispondono alla separazione visiva dei paragrafi nei documenti.
    Chunk troppo brevi vengono aggregati al successivo; quelli troppo lunghi
    vengono troncati alla dimensione massima.

    Args:
        testo: Il testo grezzo da suddividere.
        materiale_id: FK verso ``materiali_didattici``.
        corso_universitario_id: FK denormalizzata verso ``corsi_universitari``.

    Returns:
        Lista degli ID dei chunk inseriti.
    """
    paragrafi_grezzi: list[str] = re.split(r"\n{2,}", testo)

    # Pulizia e filtraggio paragrafi vuoti
    paragrafi_puliti: list[str] = [
        p.strip() for p in paragrafi_grezzi if p.strip()
    ]

    # Aggregazione chunk troppo brevi
    chunks: list[str] = _aggrega_chunk_brevi(paragrafi_puliti)

    ids_inseriti: list[int] = []
    for indice, testo_chunk in enumerate(chunks):
        chunk_id: int = db.inserisci(
            "materiali_chunks",
            {
                "materiale_id": materiale_id,
                "corso_universitario_id": corso_universitario_id,
                "indice_chunk": indice,
                "testo": testo_chunk,
                "n_token": _stima_token(testo_chunk),
            },
        )
        ids_inseriti.append(chunk_id)

    return ids_inseriti


_SYSTEM_PROMPT_ARRICCHIMENTO = """Sei un assistente specializzato nell'analisi di testi didattici universitari.
Dato un frammento di testo, estrai i metadati semantici richiesti in italiano.
Sii conciso e preciso. Usa solo le informazioni presenti nel testo fornito."""


def _arricchisci_chunks_con_llm(chunk_ids: list[int], progress_callback=None) -> None:
    """Arricchisce ogni chunk con metadati semantici generati dall'LLM.

    Per ogni chunk recupera il testo dal DB, chiama l'LLM con structured output
    per generare ``titolo_sezione``, ``sommario`` e ``argomenti_chiave``,
    poi aggiorna il record nel DB.

    Args:
        chunk_ids: Lista degli ID dei chunk da arricchire.
        progress_callback: Funzione opzionale (i, totale) per aggiornare la progress bar.
    """
    if not chunk_ids:
        return

    import json as _json
    llm = get_llm(veloce=True)
    llm_strutturato = llm.with_structured_output(MetadatiChunk)

    totale = len(chunk_ids)
    for idx, chunk_id in enumerate(chunk_ids):
        if progress_callback:
            progress_callback(idx, totale)
        righe = db.esegui(
            "SELECT testo FROM materiali_chunks WHERE id = ?", [chunk_id]
        )
        if not righe or not righe[0].get("testo"):
            continue

        testo_chunk: str = righe[0]["testo"]

        try:
            messaggi = [
                SystemMessage(content=_SYSTEM_PROMPT_ARRICCHIMENTO),
                HumanMessage(content=(
                    f"Analizza questo frammento di materiale didattico e genera i metadati:\n\n"
                    f"{testo_chunk}"
                )),
            ]
            metadati: MetadatiChunk = llm_strutturato.invoke(messaggi)

            db.aggiorna(
                "materiali_chunks",
                {"id": chunk_id},
                {
                    "titolo_sezione": metadati.titolo_sezione,
                    "sommario": metadati.sommario,
                    "argomenti_chiave": _json.dumps(metadati.argomenti_chiave, ensure_ascii=False),
                },
            )
        except Exception:
            # Se l'arricchimento fallisce per un chunk, si continua con il successivo.
            # Il chunk rimane nel DB con i campi NULL — il RAG userà solo il campo testo.
            continue


def _aggrega_chunk_brevi(paragrafi: list[str]) -> list[str]:
    """Unisce i paragrafi troppo brevi al successivo per creare chunk più
    ricchi di contesto.

    Args:
        paragrafi: Lista di paragrafi già puliti.

    Returns:
        Lista di chunk dopo l'aggregazione.
    """
    if not paragrafi:
        return []

    risultato: list[str] = []
    buffer: str = ""

    for paragrafo in paragrafi:
        # Tronca i paragrafi eccessivamente lunghi
        if len(paragrafo) > _DIMENSIONE_MAX_CHUNK_CARATTERI:
            if buffer:
                risultato.append(buffer)
                buffer = ""
            # Dividi in spezzoni da _DIMENSIONE_MAX_CHUNK_CARATTERI
            for i in range(0, len(paragrafo), _DIMENSIONE_MAX_CHUNK_CARATTERI):
                risultato.append(paragrafo[i : i + _DIMENSIONE_MAX_CHUNK_CARATTERI])
            continue

        if buffer:
            candidato = buffer + "\n\n" + paragrafo
        else:
            candidato = paragrafo

        if len(candidato) >= _DIMENSIONE_MIN_CHUNK_CARATTERI:
            risultato.append(candidato)
            buffer = ""
        else:
            buffer = candidato

    # Flush del buffer residuo
    if buffer:
        risultato.append(buffer)

    return risultato


def _stima_token(testo: str) -> int:
    """Stima approssimativa del numero di token (4 caratteri ≈ 1 token).

    Args:
        testo: Testo di cui stimare i token.

    Returns:
        Numero stimato di token.
    """
    return max(1, len(testo) // 4)


def conta_chunks_corso(corso_universitario_id: int) -> int:
    """Conta i chunk disponibili per un corso universitario.

    Args:
        corso_universitario_id: ID del corso da interrogare.

    Returns:
        Numero di chunk presenti nella tabella ``materiali_chunks``.
    """
    return db.conta("materiali_chunks", {"corso_universitario_id": corso_universitario_id})


def recupera_chunks_corso(corso_universitario_id: int) -> list[dict]:
    """Recupera tutti i chunk di un corso, ordinati per posizione.

    Args:
        corso_universitario_id: ID del corso da interrogare.

    Returns:
        Lista di dizionari rappresentanti i record di ``materiali_chunks``.
    """
    return db.trova_tutti(
        "materiali_chunks",
        {"corso_universitario_id": corso_universitario_id},
        ordine="indice_chunk ASC",
    )
