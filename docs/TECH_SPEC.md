# Technical Specifications

## Scopo del Documento
Questo file definisce il manifesto tecnologico e operativo del progetto. Il suo obiettivo è stabilire un "perimetro tecnico" rigoroso entro il quale gli sviluppatori e gli agenti IA devono operare, garantendo coerenza, sicurezza e standardizzazione in tutto il ciclo di vita del software.

---

## 1. Architettura e Stack Tecnologico

L'applicazione segue un'architettura Three-Tier orientata all'orchestrazione AI.

**Linguaggio di Riferimento:** Python 3.11+

**Presentation Layer (Frontend):** `streamlit` — gestisce UI, pagine e chat in tempo reale.

**Data Visualization:** `plotly` / `plotly.express` — grafici interattivi (es. `px.pie` per distribuzione skill).

**Data Manipulation:** `pandas` — gestione in memoria di dati strutturati. `openpyxl` — esportazione/importazione Excel.

**Database (Data Layer):** SQLite (file locale `database/learnai.db`). Il percorso è configurabile tramite variabile d'ambiente; la libreria di accesso è il modulo nativo `sqlite3` con `row_factory = sqlite3.Row` per restituire righe come dizionari. Le foreign key sono abilitate esplicitamente tramite `PRAGMA foreign_keys = ON`.

> **Nota di scalabilità:** Il DDL attuale usa la sintassi `AUTOINCREMENT` propria di SQLite. Una migrazione a PostgreSQL richiederà di sostituire `AUTOINCREMENT` con `SERIAL` / `IDENTITY` e di aggiornare il driver.

---

## 2. Intelligenza Artificiale & Ecosistema Multiagente

Il cuore del sistema backend è un'architettura multiagente avanzata.

**LLM Provider:** Amazon Bedrock, acceduto tramite `langchain-aws` (`ChatBedrockConverse`).

**Modello principale (Sonnet):**
```
anthropic.claude-3-5-sonnet-20241022-v2:0
```
Usato per task complessi: generazione quiz, analisi documenti, piani formativi, chat multi-turn.

**Modello veloce (Haiku):**
```
anthropic.claude-3-5-haiku-20241022-v1:0
```
Usato per task semplici: classificazioni, risposte brevi, tool degli agenti a bassa latenza.

Entrambi i model ID sono sovrascrivibili tramite variabili d'ambiente `BEDROCK_MODEL_ID` e `BEDROCK_MODEL_ID_FAST`.

**Parametri LLM:**

| Parametro | Sonnet | Haiku |
|---|---|---|
| `temperature` | 0.3 | 0.3 |
| `max_tokens` | 4096 | 2048 |
| Regione AWS | `eu-central-1` (default) | stessa |

**Core AI Framework:** `langchain` + `langchain-aws` (`ChatBedrockConverse`) per la gestione dei prompt e la comunicazione con Bedrock. I messaggi sono tipizzati con `HumanMessage`, `SystemMessage`, `AIMessage` di `langchain_core.messages`.

**Orchestrazione Multiagente:** `langgraph` — pattern ReAct via `create_react_agent` (modulo `langgraph.prebuilt`). La memoria conversazionale è gestita da `InMemorySaver` (`langgraph.checkpoint.memory`).

**Elaborazione Documentale (RAG):** `PyPDF2` per l'estrazione del testo dai PDF caricati dai docenti (campo `testo_estratto` in tabella `materials`).

**Vincolo Architetturale RAG:** L'agente Adaptive Content Generation Engine deve attingere **esclusivamente** ai materiali (PDF/Video) caricati dai docenti come unica "fonte di verità" per generare quiz, flashcard e riassunti.

**Output strutturato (JSON):** La funzione `genera_json()` in `platform_sdk/llm.py` impone all'LLM di rispondere in JSON puro tramite system prompt dedicato, con fallback di parsing che gestisce blocchi ` ```json ``` ` e ricerca regex `{...}`.

---

## 3. Integrazioni Esterne e Cloud

**Storage dei File Multimediali:** `boto3` — integrazione con Amazon S3 per video, PDF e risorse pesanti. I file sono referenziati nel DB tramite il campo `s3_key` (es. `didattica/corsi/101/Slide_Capitolo_1.pdf`).

**Supporto file upload lato UI:** `estrai_testo_da_upload()` in `llm.py` supporta i formati `.txt`, `.md`, `.csv`, `.pdf`, `.xls`, `.xlsx`,`.docx` tramite rispettivamente `PyPDF2`, `pandas.read_csv`, `pandas.read_excel`.

---

## 4. Requisiti di Sicurezza

**Gestione dei Segreti (Strict Policy):** È severamente vietato hardcodare chiavi API (AWS, Bedrock, DB URIs) nel codice sorgente.

**Variabili d'ambiente obbligatorie** (file `.env`, lette tramite `python-dotenv` in `src/core/config.py`):

| Variabile | Descrizione | Default |
|---|---|---|
| `AWS_ACCESS_KEY_ID` | Chiave di accesso AWS | — (obbligatoria) |
| `AWS_SECRET_ACCESS_KEY` | Chiave segreta AWS | — (obbligatoria) |
| `AWS_DEFAULT_REGION` | Regione AWS | `eu-central-1` |
| `BEDROCK_MODEL_ID` | Model ID principale | `anthropic.claude-3-5-sonnet-20241022-v2:0` |
| `BEDROCK_MODEL_ID_FAST` | Model ID veloce | `anthropic.claude-3-5-haiku-20241022-v1:0` |

**Controllo Versione:** Il file `.env` deve essere incluso nel `.gitignore`. Mai committato.

---

## 5. Percorsi di Progetto (dalla configurazione reale)

| Costante | Percorso |
|---|---|
| `DATABASE_PATH` | `<root>/database/learnai.db` |
| `SCHEMA_PATH` | `<root>/database/schema.sql` |
| `SEED_PATH` | `<root>/database/seed.sql` |
| `KNOWLEDGE_BASE_PATH` | `<root>/data/knowledge_base/` |
| `SAMPLE_DATA_PATH` | `<root>/data/sample_data.json` |

Tutti i percorsi sono costruiti relativamente a `config.py` tramite `os.path.dirname(__file__)`.

---

## 6. Vincoli di Performance

**Istanze LLM (lazy initialization):** I modelli `_llm_principale` e `_llm_veloce` sono variabili globali private in `llm.py`, create alla prima chiamata e riusate per tutta la sessione. Non vanno re-istanziate ad ogni richiesta.

**Streaming:** Le interfacce di chat implementano token streaming tramite `llm.stream()` (LangChain) e `agente.stream(..., stream_mode="messages")` (LangGraph), restituendo generatori Python compatibili con `st.write_stream()` di Streamlit.

**Ottimizzazione Streamlit:** Il `st.session_state` deve essere progettato per prevenire il re-rendering di componenti grafici pesanti o il riavvio non voluto dei workflow LangGraph durante l'interazione con la chat.
