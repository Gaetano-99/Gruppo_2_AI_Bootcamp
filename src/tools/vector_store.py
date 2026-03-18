"""
Modulo: vector_store.py
Responsabilità: gestione degli embedding vettoriali e del database ChromaDB
per la ricerca semantica nel sistema RAG di LearnAI.

Architettura:
    - Embedding model: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
      (multilingue, 384 dimensioni, ottimizzato per italiano).
    - Vector store: ChromaDB con persistenza locale su disco.
    - Collection per corso: ``learnai_corso_{id}`` per isolamento e performance.
    - Collection piattaforma: ``learnai_tutti`` per ricerche cross-corso.
    - Ogni chunk viene inserito in entrambe le collection.

Il collegamento con SQLite avviene tramite ``materiali_chunks.id`` come
document_id nel vector store, come previsto dallo schema DB (riga 239-253).
"""

import os
import sys
from typing import Optional

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import chromadb
from langchain_huggingface import HuggingFaceEmbeddings

import config
from platform_sdk.database import db


# ---------------------------------------------------------------------------
# Eccezione specifica per fallimento ricerca semantica
# ---------------------------------------------------------------------------

class RicercaSemanticaFallita(Exception):
    """Sollevata quando la ricerca semantica nel vector store non può completarsi.

    Motivi tipici: collection vuota, errore ChromaDB, nessun risultato pertinente.
    Il messaggio contiene una spiegazione leggibile dall'utente.
    """
    pass

# ---------------------------------------------------------------------------
# Singleton: embedding model
# ---------------------------------------------------------------------------
_embedding_model: Optional[HuggingFaceEmbeddings] = None


def get_embedding_model() -> HuggingFaceEmbeddings:
    """Restituisce il modello di embedding (singleton, lazy init).

    Usa ``paraphrase-multilingual-MiniLM-L12-v2`` per supporto italiano.
    Il modello viene scaricato al primo utilizzo (~130 MB).

    Returns:
        Istanza condivisa di ``HuggingFaceEmbeddings``.
    """
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = HuggingFaceEmbeddings(
            model_name=config.EMBEDDING_MODEL_NAME,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embedding_model


# ---------------------------------------------------------------------------
# Singleton: ChromaDB client
# ---------------------------------------------------------------------------
_chroma_client: Optional[chromadb.ClientAPI] = None


def _get_chroma_client() -> chromadb.ClientAPI:
    """Restituisce il client ChromaDB persistente (singleton).

    I dati vengono salvati in ``config.CHROMA_PERSIST_DIR``.

    Returns:
        Client ChromaDB con persistenza su disco.
    """
    global _chroma_client
    if _chroma_client is None:
        os.makedirs(config.CHROMA_PERSIST_DIR, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)
    return _chroma_client


# ---------------------------------------------------------------------------
# Gestione collection
# ---------------------------------------------------------------------------

def _get_collection(corso_id: int | None) -> chromadb.Collection:
    """Restituisce la collection ChromaDB per un corso o quella globale.

    Args:
        corso_id: ID del corso. None per la collection piattaforma.

    Returns:
        Collection ChromaDB (creata se non esiste).
    """
    client = _get_chroma_client()
    nome = (
        f"{config.CHROMA_COLLECTION_PREFIX}{corso_id}"
        if corso_id is not None
        else config.CHROMA_COLLECTION_PIATTAFORMA
    )
    return client.get_or_create_collection(
        name=nome,
        metadata={"hnsw:space": "cosine"},
    )


# ---------------------------------------------------------------------------
# Vettorizzazione chunk
# ---------------------------------------------------------------------------

def vettorizza_chunks(chunk_ids: list[int], corso_id: int | None) -> int:
    """Genera embedding per i chunk specificati e li inserisce in ChromaDB.

    Per ogni chunk:
        1. Legge ``titolo_sezione``, ``sommario`` e ``testo`` da SQLite.
        2. Compone il testo da embeddare: ``titolo\\nsommario\\ntesto``.
        3. Genera l'embedding con il modello HuggingFace.
        4. Inserisce (upsert) nella collection del corso e in quella piattaforma.
        5. Aggiorna ``embedding_sync=1`` in SQLite.

    Args:
        chunk_ids: Lista di ID chunk da vettorizzare.
        corso_id: ID del corso (per la collection corso-specifica).

    Returns:
        Numero di chunk vettorizzati con successo.
    """
    if not chunk_ids:
        return 0

    model = get_embedding_model()
    collection_corso = _get_collection(corso_id) if corso_id is not None else None
    collection_tutti = _get_collection(None)

    # Recupera i dati dei chunk da SQLite
    placeholders = ",".join("?" for _ in chunk_ids)
    chunks = db.esegui(
        f"SELECT id, materiale_id, corso_universitario_id, indice_chunk, "
        f"titolo_sezione, sommario, testo "
        f"FROM materiali_chunks WHERE id IN ({placeholders})",
        chunk_ids,
    )

    if not chunks:
        return 0

    # Prepara testi per embedding
    testi: list[str] = []
    ids_doc: list[str] = []
    metadati: list[dict] = []
    chunks_validi: list[dict] = []

    for chunk in chunks:
        testo_completo = _componi_testo_embedding(chunk)
        if not testo_completo.strip():
            continue

        testi.append(testo_completo)
        ids_doc.append(str(chunk["id"]))
        metadati.append({
            "chunk_id": chunk["id"],
            "materiale_id": chunk["materiale_id"] or 0,
            "corso_universitario_id": chunk["corso_universitario_id"] or 0,
            "indice_chunk": chunk["indice_chunk"] or 0,
        })
        chunks_validi.append(chunk)

    if not testi:
        return 0

    # Genera embedding in batch
    embeddings = model.embed_documents(testi)

    # Upsert nella collection del corso (solo se corso_id specificato)
    if collection_corso is not None:
        try:
            collection_corso.upsert(
                ids=ids_doc,
                embeddings=embeddings,
                documents=testi,
                metadatas=metadati,
            )
        except Exception as e:
            print(f"[WARN vector_store] Upsert collection corso fallito: {e}")

    # Upsert nella collection piattaforma
    try:
        collection_tutti.upsert(
            ids=ids_doc,
            embeddings=embeddings,
            documents=testi,
            metadatas=metadati,
        )
    except Exception as e:
        print(f"[WARN vector_store] Upsert collection piattaforma fallito: {e}")

    # Aggiorna embedding_sync=1 in SQLite
    conteggio = 0
    for chunk in chunks_validi:
        try:
            db.aggiorna(
                "materiali_chunks",
                {"id": chunk["id"]},
                {"embedding_sync": 1},
            )
            conteggio += 1
        except Exception:
            continue

    return conteggio


def _componi_testo_embedding(chunk: dict) -> str:
    """Compone il testo da embeddare concatenando titolo, sommario e testo.

    Args:
        chunk: Dizionario con i campi del chunk da SQLite.

    Returns:
        Stringa concatenata per l'embedding.
    """
    parti: list[str] = []
    if chunk.get("titolo_sezione"):
        parti.append(chunk["titolo_sezione"])
    if chunk.get("sommario"):
        parti.append(chunk["sommario"])
    if chunk.get("testo"):
        parti.append(chunk["testo"])
    return "\n".join(parti)


# ---------------------------------------------------------------------------
# Ricerca semantica
# ---------------------------------------------------------------------------

def cerca_simili(
    query: str,
    corso_id: int | None,
    top_k: int = 8,
    materiale_id: int | None = None,
    materiale_ids: list[int] | None = None,
    _auto_rebuild: bool = True,
) -> list[int]:
    """Ricerca semantica per similarita coseno nella collection del corso.

    Args:
        query: Testo della query dell'utente.
        corso_id: ID del corso (determina la collection).
        top_k: Numero massimo di risultati.
        materiale_id: Filtra per singolo materiale (opzionale).
        materiale_ids: Filtra per piu materiali (opzionale, ha priorita).
        _auto_rebuild: Uso interno. Se True e l'indice HNSW è corrotto,
            tenta una ricostruzione automatica e riprova una volta.

    Returns:
        Lista di chunk_id ordinati per rilevanza semantica decrescente.

    Raises:
        RicercaSemanticaFallita: Se la ricerca non può completarsi (collection
            vuota, errore ChromaDB, nessun risultato pertinente).
    """
    if not query or not query.strip():
        raise RicercaSemanticaFallita("La query di ricerca è vuota.")

    try:
        model = get_embedding_model()
        collection = _get_collection(corso_id)

        # Verifica che la collection non sia vuota
        if collection.count() == 0:
            raise RicercaSemanticaFallita(
                "Il database vettoriale non contiene embedding per questo corso. "
                "I materiali potrebbero non essere ancora stati indicizzati."
            )

        # Costruisci filtro metadata
        where_filter = _costruisci_filtro(materiale_id, materiale_ids)

        # Genera embedding della query
        query_embedding = model.embed_query(query)

        # Esegui ricerca
        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": min(top_k, collection.count()),
        }
        if where_filter:
            kwargs["where"] = where_filter

        risultati = collection.query(**kwargs)

        # Estrai chunk_ids dai risultati
        if not risultati or not risultati.get("ids") or not risultati["ids"][0]:
            raise RicercaSemanticaFallita(
                "La ricerca semantica non ha trovato risultati pertinenti alla query."
            )

        return [int(doc_id) for doc_id in risultati["ids"][0]]

    except RicercaSemanticaFallita:
        raise  # Rilancia le nostre eccezioni senza wrapping

    except Exception as e:
        # Auto-healing: se l'indice HNSW è corrotto, ricostruisci e riprova
        err_lower = str(e).lower()
        is_hnsw_error = (
            "hnsw" in err_lower
            or "nothing found on disk" in err_lower
            or "segment reader" in err_lower
        )
        if is_hnsw_error and _auto_rebuild:
            print(f"[WARN vector_store] Indice HNSW corrotto, ricostruzione automatica...")
            try:
                _ricostruisci_vectorstore(
                    f"Errore HNSW rilevato durante ricerca: {e}"
                )
                return cerca_simili(
                    query, corso_id, top_k,
                    materiale_id, materiale_ids,
                    _auto_rebuild=False,
                )
            except Exception as rebuild_err:
                raise RicercaSemanticaFallita(
                    f"Ricostruzione vector store fallita: {rebuild_err}"
                ) from rebuild_err

        raise RicercaSemanticaFallita(
            f"Errore durante la ricerca nel database vettoriale: {e}"
        ) from e


def cerca_simili_piattaforma(query: str, top_k: int = 8) -> list[int]:
    """Ricerca semantica su tutta la piattaforma (collection globale).

    Args:
        query: Testo della query dell'utente.
        top_k: Numero massimo di risultati.

    Returns:
        Lista di chunk_id ordinati per rilevanza semantica decrescente.
    """
    return cerca_simili(query=query, corso_id=None, top_k=top_k)


def _costruisci_filtro(
    materiale_id: int | None,
    materiale_ids: list[int] | None,
) -> dict | None:
    """Costruisce il filtro metadata per ChromaDB.

    Args:
        materiale_id: Singolo ID materiale.
        materiale_ids: Lista di ID materiali.

    Returns:
        Dizionario filtro per ChromaDB, o None se nessun filtro.
    """
    if materiale_ids and len(materiale_ids) > 0:
        if len(materiale_ids) == 1:
            return {"materiale_id": materiale_ids[0]}
        return {"materiale_id": {"$in": materiale_ids}}
    if materiale_id:
        return {"materiale_id": materiale_id}
    return None


# ---------------------------------------------------------------------------
# Sincronizzazione batch
# ---------------------------------------------------------------------------

def _ricostruisci_vectorstore(motivo: str) -> int:
    """Cancella tutte le collection ChromaDB corrotte e ri-vettorizza da zero.

    Args:
        motivo: Messaggio di log che descrive perché serve la ricostruzione.

    Returns:
        Numero di chunk ri-vettorizzati.
    """
    import time
    global _chroma_client

    print()
    print("!" * 60)
    print("  VECTOR STORE — RICOSTRUZIONE NECESSARIA")
    print("!" * 60)
    print(f"  Motivo: {motivo}")
    print()

    # Elimina fisicamente la directory chroma_db per garantire pulizia completa.
    # L'eliminazione via API può fallire su indici HNSW corrotti, quindi
    # usiamo sempre shutil.rmtree come strategia primaria.
    import shutil

    print("  [1/3] Pulizia fisica directory chroma_db...")
    try:
        # Reset singleton PRIMA di eliminare i file (rilascia lock)
        _chroma_client = None
        shutil.rmtree(config.CHROMA_PERSIST_DIR, ignore_errors=True)
        os.makedirs(config.CHROMA_PERSIST_DIR, exist_ok=True)
        print("         Directory chroma_db ricreata da zero.")
    except Exception as e:
        print(f"         ERRORE CRITICO: impossibile rimuovere chroma_db: {e}")
        # Tentativo fallback via API
        try:
            client = _get_chroma_client()
            for col in client.list_collections():
                client.delete_collection(col.name)
            _chroma_client = None
            print("         Fallback API: collection eliminate.")
        except Exception as e2:
            print(f"         Anche il fallback API è fallito: {e2}")

    # Reset embedding_sync=0 per tutti i chunk
    n_reset = db.conta("materiali_chunks", {"embedding_sync": 1})
    print(f"  [2/3] Reset embedding_sync: {n_reset} chunk da risincronizzare...")
    db.esegui(
        "UPDATE materiali_chunks SET embedding_sync = 0 WHERE embedding_sync = 1"
    )

    # Ri-vettorizza tutto
    print(f"  [3/3] Ri-vettorizzazione in corso...")
    t0 = time.time()
    n_vettorizzati = sincronizza_embeddings_pendenti()
    elapsed = time.time() - t0

    print()
    if n_vettorizzati > 0:
        print(f"  RICOSTRUZIONE COMPLETATA: {n_vettorizzati} chunk ri-vettorizzati "
              f"in {elapsed:.1f}s")
    else:
        print("  RICOSTRUZIONE COMPLETATA: nessun chunk da vettorizzare "
              "(materiali assenti?)")
    print("!" * 60)
    print()

    return n_vettorizzati


def verifica_integrita_vectorstore() -> int:
    """Rileva e ripara desync o corruzione tra SQLite e ChromaDB.

    Scenari rilevati:
    1. ChromaDB vuoto/mancante ma SQLite ha ``embedding_sync=1`` (tipico
       dopo clone, git clean o cancellazione di ``data/chroma_db/``).
    2. Indice HNSW corrotto: le collection esistono e ``count()`` funziona,
       ma ``query()`` fallisce perché i file dell'indice (es. ``link_lists.bin``)
       sono vuoti o danneggiati.

    In entrambi i casi resetta ``embedding_sync=0`` e ri-vettorizza.

    Returns:
        Numero di chunk ri-vettorizzati.
    """
    print()
    print("-" * 60)
    print("  VECTOR STORE — Verifica integrita")
    print("-" * 60)

    # Conta chunk che SQLite ritiene sincronizzati
    n_sync = db.conta("materiali_chunks", {"embedding_sync": 1})
    n_totali = db.conta("materiali_chunks")
    print(f"  Chunk in SQLite:   {n_totali} totali, {n_sync} con embedding_sync=1")

    if n_sync == 0:
        print("  Nessun chunk sincronizzato — nulla da verificare.")
        print("-" * 60)
        print()
        return 0

    # Controlla se ChromaDB ha effettivamente dati
    try:
        collection_tutti = _get_collection(None)
        n_chroma = collection_tutti.count()
    except Exception:
        n_chroma = 0
    print(f"  Chunk in ChromaDB: {n_chroma} (collection piattaforma)")

    if n_chroma < n_sync:
        print(f"  PROBLEMA: ChromaDB ha meno embedding di quelli attesi "
              f"({n_chroma} < {n_sync})")
        print("-" * 60)
        return _ricostruisci_vectorstore(
            f"Desync rilevato: SQLite ha {n_sync} chunk con "
            f"embedding_sync=1, ma ChromaDB ne contiene solo {n_chroma}."
        )

    # Conteggi coerenti — verifica che l'indice HNSW funzioni davvero
    # con una query di test. Se fallisce, l'indice è corrotto.
    print("  Conteggi coerenti. Test query HNSW in corso...")
    try:
        model = get_embedding_model()
        test_embedding = model.embed_query("test di integrità")
        collection_tutti.query(
            query_embeddings=[test_embedding],
            n_results=1,
        )
    except Exception as e:
        print(f"  PROBLEMA: query HNSW fallita — {e}")
        print("-" * 60)
        return _ricostruisci_vectorstore(
            f"Indice HNSW corrotto (count OK ma query fallita): {e}"
        )

    print("  Esito: OK — Vector store integro e funzionante")
    print("-" * 60)
    print()
    return 0


def sincronizza_embeddings_pendenti() -> int:
    """Vettorizza tutti i chunk con ``embedding_sync=0``.

    Raggruppa i chunk per ``corso_universitario_id`` e chiama
    ``vettorizza_chunks()`` per ogni gruppo.

    Returns:
        Numero totale di chunk vettorizzati.
    """
    chunks_pendenti = db.esegui(
        "SELECT id, corso_universitario_id FROM materiali_chunks WHERE embedding_sync = 0"
    )

    if not chunks_pendenti:
        return 0

    # Raggruppa per corso
    per_corso: dict[int | None, list[int]] = {}
    for chunk in chunks_pendenti:
        cid = chunk.get("corso_universitario_id")
        if cid not in per_corso:
            per_corso[cid] = []
        per_corso[cid].append(chunk["id"])

    totale = 0
    for corso_id, chunk_ids in per_corso.items():
        try:
            totale += vettorizza_chunks(chunk_ids, corso_id)
        except Exception as e:
            print(f"[WARN vector_store] Sync corso {corso_id} fallita: {e}")
            continue

    return totale


# ---------------------------------------------------------------------------
# Rimozione chunk
# ---------------------------------------------------------------------------

def rimuovi_chunks_da_vectorstore(
    chunk_ids: list[int],
    corso_id: int | None,
) -> None:
    """Rimuove chunk da ChromaDB (collection corso + piattaforma).

    Args:
        chunk_ids: Lista di ID chunk da rimuovere.
        corso_id: ID del corso per la collection corso-specifica.
    """
    if not chunk_ids:
        return

    ids_doc = [str(cid) for cid in chunk_ids]

    if corso_id is not None:
        try:
            collection_corso = _get_collection(corso_id)
            collection_corso.delete(ids=ids_doc)
        except Exception as e:
            print(f"[WARN vector_store] Rimozione collection corso fallita: {e}")

    try:
        collection_tutti = _get_collection(None)
        collection_tutti.delete(ids=ids_doc)
    except Exception as e:
        print(f"[WARN vector_store] Rimozione collection piattaforma fallita: {e}")
