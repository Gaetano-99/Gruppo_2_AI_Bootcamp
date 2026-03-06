# Technical Specifications

## Scopo del Documento
Questo file definisce il manifesto tecnologico e operativo del progetto. Il suo obiettivo è stabilire un "perimetro tecnico" rigoroso entro il quale gli sviluppatori e gli agenti IA devono operare, garantendo coerenza, sicurezza e standardizzazione in tutto il ciclo di vita del software.

---

## 1. Architettura e Stack Tecnologico

L'applicazione segue un'architettura Three-Tier orientata all'orchestrazione AI multiagente.

**Linguaggio di Riferimento:** Python.

**Presentation Layer (Frontend):** `streamlit` per la UI, la gestione delle chat in tempo reale e il routing per ruolo (Ospite / Studente / Docente).

**Data Visualization:** `plotly` per il rendering interattivo dei grafici nelle dashboard docente (report sui risultati dei test, andamento della classe).

**Data Manipulation:** `pandas` per la gestione in memoria dei dati strutturati; `openpyxl` per l'esportazione tabellare.

**Database Relazionale (Data Layer):** SQLite. Schema definito in `schema.sql` — fonte di verità per tutte le entità strutturate. Le tabelle principali sono: `users`, `corsi_di_laurea`, `corsi_universitari`, `corsi_laurea_universitari`, `studenti_corsi`, `materiali_didattici`, `materiali_chunks`, `quiz`, `domande_quiz`, `tentativi_quiz`, `risposte_domande`, `piani_personalizzati`, `piano_materiali_utilizzati`, `piano_capitoli`, `piano_paragrafi`, `piano_contenuti`, `lezioni_corso`.

**Vector Store (RAG Layer):** store esterno (es. ChromaDB in locale) per gli embedding dei `materiali_chunks`. Il collegamento con SQLite avviene tramite `materiali_chunks.id` come `document_id` nella collection. Il campo `embedding_sync` in `materiali_chunks` garantisce l'idempotenza della vettorizzazione. La query RAG è sempre ibrida: ChromaDB per la similarità semantica, SQLite per i metadati completi.

---

## 2. Intelligenza Artificiale & Ecosistema Multiagente

**Core AI Framework:** `langchain` per la gestione dei prompt e l'interazione con i modelli LLM.

**Orchestrazione Multiagente:** `langgraph` governa il ciclo di vita e la comunicazione tra i 6 agenti specializzati:

| File | Agente | Responsabilità principale |
|---|---|---|
| `agents/onboarding.py` | Onboarding Assistant | Colloquio guidato o analisi CV per Ospiti e nuovi Studenti |
| `agents/scheduler.py` | Learning Path Scheduler | Generazione piani personalizzati (`piani_personalizzati`) |
| `agents/optimizer.py` | Conversational Plan Optimizer | Modifica piani tramite linguaggio naturale |
| `agents/content_gen.py` | Adaptive Content Generation Engine | Generazione lezioni, quiz, flashcard, riassunti da `materiali_chunks` |
| `agents/gap_analysis.py` | Competency Gap Analysis AI | Analisi lacune su `tentativi_quiz` e `risposte_domande` |
| `agents/course_analysis.py` | Course Performance Analysis | Report aggregati per il docente da quiz approvati (`approvato=1`) |

**Elaborazione Documentale (RAG):** `PyPDF2` per l'estrazione del testo dai PDF caricati. Il testo estratto viene segmentato in chunks semantici e salvato in `materiali_chunks`. Ogni chunk viene successivamente vettorizzato e inserito nel vector store (`embedding_sync=0 → 1`).

**Vincolo Architetturale RAG — CRITICO:**
Il Content Generation Engine deve attingere **esclusivamente** ai `materiali_chunks` associati al corso di riferimento come unica fonte di verità. È vietato generare contenuti didattici da fonti esterne al materiale caricato dal docente. Ogni contenuto generato deve tracciare i `chunk_ids_utilizzati`.

---

## 3. Integrazioni Esterne e Cloud

**Storage File Multimediali:** `boto3` per l'integrazione con Amazon S3. Ogni file caricato dal docente ottiene un `s3_key` univoco salvato in `materiali_didattici.s3_key`.

**LLM Provider:** `langchain-aws` per interfacciarsi con i modelli linguistici su Amazon Bedrock. Le chiamate avvengono sempre tramite i nodi degli agenti LangGraph — mai direttamente dalla UI.

---

## 4. Requisiti di Sicurezza

**Gestione dei Segreti:** È severamente vietato hardcodare chiavi API (AWS, Bedrock, DB path) nel codice sorgente. Tutte le configurazioni sensibili risiedono nel file `.env`, caricato tramite `src/core/config.py`.

**Controllo Versione:** Il file `.env` deve essere incluso in `.gitignore`. Verificare prima di ogni commit.

**Accesso ai Dati:**
- I `materiali_chunks` sono accessibili solo agli utenti con `ruolo='studente'` iscritti al corso (`studenti_corsi.stato != 'abbandonato'`) e all'utente con `ruolo='docente'` titolare del corso.
- Gli Ospiti non hanno accesso a nessuna tabella del database.
- I quiz di Tipo A e B (`approvato=0`, `studente_id NOT NULL`) sono visibili solo allo studente proprietario — nessun altro utente, incluso il docente, può leggerli.

**Vincolo applicativo su FK di ruolo:** SQLite non supporta CHECK constraint cross-tabella. Il codice in `db_handler.py` deve verificare `users.ruolo` prima di ogni INSERT su: `studenti_corsi` (`studente_id`), `quiz` (`studente_id`, `docente_id`), `tentativi_quiz` (`studente_id`), `piani_personalizzati` (`studente_id`), `materiali_didattici` (`docente_id`), `lezioni_corso` (`docente_id`).

---

## 5. Vincoli di Performance

**Ottimizzazione Streamlit:** Il `st.session_state` deve essere progettato per prevenire il re-rendering inutile di componenti pesanti o il riavvio non voluto dei workflow LangGraph durante l'interazione con la chat. Le istanze degli agenti vanno messe in cache in `st.session_state` al primo caricamento.

**Latenza AI e UX:** Le interfacce di chat devono implementare token streaming dalle API di Bedrock per restituire feedback visivo immediato durante l'elaborazione.

**Idempotenza RAG — doppio livello:**
- Materiali grezzi: verificare sempre `materiali_didattici.is_processed` prima di segmentare. Se `is_processed=1`, i chunks esistono già.
- Embedding: verificare sempre `materiali_chunks.embedding_sync` prima di vettorizzare. Se `embedding_sync=1`, il vettore esiste già nel vector store.

**Indici DB:** Gli indici definiti in `schema.sql` sono obbligatori e non vanno rimossi. La query RAG più frequente (`materiali_chunks WHERE corso_universitario_id = X`) è coperta da `idx_chunks_corso`. La sincronizzazione degli embedding (`WHERE embedding_sync = 0`) è coperta da `idx_chunks_embedding_sync`.
