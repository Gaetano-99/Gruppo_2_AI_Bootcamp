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
# ---------------------------------------------------------------------------
# Path setup — permette l'import del progetto dalla root in qualunque contesto
# ---------------------------------------------------------------------------
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from platform_sdk.database import db
from platform_sdk.llm import estrai_testo_da_upload

# ---------------------------------------------------------------------------
# Costanti di chunking
# ---------------------------------------------------------------------------
_DIMENSIONE_MIN_CHUNK_CARATTERI: int = 150   # chunk più corti vengono uniti
_DIMENSIONE_MAX_CHUNK_CARATTERI: int = 2000  # chunk più lunghi vengono divisi
_DOCENTE_ID_MOCK: int = 10   # Mario Rossi (docente, seed data)


# ---------------------------------------------------------------------------
# Funzioni pubbliche
# ---------------------------------------------------------------------------


def elabora_e_salva_documento(
    uploaded_file,
    corso_universitario_id: int | None,
    titolo: str,
    tipo: str = "dispensa",
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
    tipi_validi = {"pdf", "slide", "video", "dispensa", "libro"}
    if tipo not in tipi_validi:
        raise ValueError(
            f"Tipo '{tipo}' non valido. Usa uno tra: {', '.join(tipi_validi)}"
        )

    # 1. Estrai testo
    testo_estratto: str = estrai_testo_da_upload(uploaded_file)
    if not testo_estratto or not testo_estratto.strip():
        raise ValueError("Il file caricato non contiene testo leggibile.")

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
    _crea_e_salva_chunks(
        testo=testo_estratto,
        materiale_id=materiale_id,
        corso_universitario_id=corso_universitario_id,
    )

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
