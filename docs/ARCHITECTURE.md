# System Architecture

## Scopo del Documento
Questo documento fornisce la mappa strutturale e logica dell'intera applicazione. È fondamentale sia per l'onboarding di nuovi sviluppatori, sia per orientare correttamente gli strumenti di vibecoding, indicando l'esatta collocazione dei moduli e il funzionamento del "motore" software.

---

## 1. Design di Sistema (System Design)

L'applicazione segue un'architettura a tre livelli (Three-Tier), fortemente orientata all'orchestrazione di AI (Agentic Workflow).

- **Presentation Layer (Frontend):** Sviluppato interamente in `streamlit`. Gestisce UI, rendering grafici (`plotly.express`) e interazione in tempo reale con i chatbot tramite `st.write_stream()`.
- **Logic & AI Orchestration Layer (Backend — Platform SDK):** Il "cervello" del sistema. Esposto come package Python `platform_sdk/` con moduli specializzati (`llm.py`, `agent.py`, `database.py`). Usa `langgraph` (`create_react_agent`) per orchestrare i 7 agenti IA. `langchain` e `langchain-aws` (`ChatBedrockConverse`) gestiscono i prompt e la comunicazione con Amazon Bedrock. L'estrazione dei testi avviene tramite `PyPDF2`.
- **Data & Storage Layer:** I file multimediali e i PDF dei docenti sono archiviati su cloud tramite `boto3` (Amazon S3). I dati strutturati sono memorizzati in SQLite (`database/learnai.db`), gestito tramite il modulo nativo `sqlite3` con helper CRUD in `platform_sdk/database.py`. I dati in memoria sono manipolati con `pandas`.

---

## 2. Contratto di Integrazione LangGraph ↔ Streamlit

Questo è il pattern ufficiale con cui i nodi LangGraph restituiscono output alla UI. Ogni sviluppatore deve seguirlo per garantire coerenza tra moduli.

**Pattern sincrono** (per agenti che restituiscono una risposta completa):
```python
# In una pagina Streamlit
from platform_sdk.agent import crea_agente, esegui_agente

agente = crea_agente(tools=[...], system_prompt="...")
risposta = esegui_agente(agente, messaggio=domanda, thread_id=str(st.session_state.current_user_id))
st.write(risposta)
```

**Pattern streaming** (preferito per la UX — mostra la risposta token per token):
```python
# In una pagina Streamlit
from platform_sdk.agent import crea_agente, esegui_agente_stream

agente = crea_agente(tools=[...], system_prompt="...")
with st.chat_message("assistant"):
    risposta = st.write_stream(
        esegui_agente_stream(agente, messaggio=domanda, thread_id=st.session_state.current_user_id)
    )
```

**Thread ID:** Deve essere sempre `str(st.session_state.current_user_id)` per legare la memoria dell'agente all'utente corrente. Usare `"default"` solo nei test.

**Memoria:** `InMemorySaver` di LangGraph mantiene la storia conversazionale per `thread_id`. La memoria si azzera al riavvio dell'app (non è persistita su DB). Per persistenza multi-sessione, occorre implementare un checkpointer su SQLite o S3.

---

## 3. Alberatura del Progetto (Directory Structure)

```text
/
├── .env                          # Variabili d'ambiente (AWS keys, DB URIs) — MAI COMMITTATO
├── .gitignore
├── requirements.txt
├── docs/                         # Documentazione (PRD, ARCHITECTURE, GUIDA_SDK, ISTRUZIONI)
└── src/                          # Codice sorgente principale
    ├── app.py                    # Entry point Streamlit — avviare con: streamlit run app.py
    ├── config.py                 # Configurazione centrale — legge .env tramite python-dotenv
    │                             # Espone: AWS_*, BEDROCK_MODEL_ID*, LLM_*, DATABASE_PATH,
    │                             # SCHEMA_PATH, SEED_PATH, KNOWLEDGE_BASE_PATH, APP_TITLE, APP_ICON
    ├── platform_sdk/             # SDK interno — importato da tutte le pagine e agenti
    │   ├── __init__.py
    │   ├── llm.py                # Interfaccia LLM (chiedi, chat, chat_stream, genera_json, ...)
    │   ├── agent.py              # Wrapper LangGraph (crea_agente, esegui_agente, esegui_agente_stream)
    │   └── database.py           # Helper SQLite CRUD (db.inserisci, trova_tutti, aggiorna, ...)
    ├── pages/                    # Pagine Streamlit (caricate automaticamente dal framework)
    │   ├── 01_chat.py            # 💬 Chat AI — usa chat_stream()
    │   ├── 02_database.py        # 🗄️ Database — esplora tabelle, query custom
    │   ├── 03_agente.py          # 🤖 Agente AI — usa crea_agente + esegui_agente_stream
    │   ├── 04_genera_json.py     # 🧪 Playground JSON — usa genera_json()
    │   └── [moduli_gruppi]/      # Pagine sviluppate dai singoli gruppi
    ├── agents/                   # I 7 Agenti specializzati
    │   ├── onboarding.py         # Agent 1: Onboarding Assistant
    │   ├── scheduler.py          # Agent 2: Intelligent Learning Path Scheduler
    │   ├── optimizer.py          # Agent 3: Conversational Learning Plan Optimizer
    │   ├── monitoring.py         # Agent 4: AI-Driven Progress Monitoring
    │   ├── content_gen.py        # Agent 5: Adaptive Content Generation Engine
    │   ├── survey.py             # Agent 6: Smart Survey Lifecycle Manager
    │   └── gap_analysis.py       # Agent 7: Competency Gap Analysis AI
    ├── tools/                    # Tool (@tool) usati dagli agenti
    │   ├── rag_engine.py         # Retrieval sui materiali docente (fonte di verità)
    │   └── pdf_parser.py         # Estrazione testo con PyPDF2
    ├── data/                     # Gestione del Data Model
    │   ├── schemas.py            # Definizione entità (Pydantic/Dataclasses)
    │   └── db_handler.py         # Funzioni CRUD avanzate
    └── database/                 # File del database SQLite
        ├── learnai.db            # Database SQLite (generato da db.init(), non committato)
        ├── schema.sql            # DDL — crea le tabelle
        └── seed.sql              # Dati iniziali di esempio
```

**Regola di import:** Le pagine Streamlit e gli agenti importano **esclusivamente** dal package `platform_sdk`. Non accedono mai direttamente a `sqlite3`, `boto3` o `langchain` senza passare per l'SDK.

---

## 4. Platform SDK — API di Riferimento

### `platform_sdk/llm.py`

| Funzione | Scopo | Modello usato |
|---|---|---|
| `chiedi(prompt)` | Domanda semplice → risposta testuale | Sonnet |
| `chiedi_veloce(prompt)` | Domanda semplice → risposta rapida | Haiku |
| `chiedi_con_contesto(domanda, contesto, istruzioni)` | RAG semplificato | Sonnet |
| `genera_json(prompt, schema, istruzioni)` | Output JSON strutturato e parsato | Sonnet |
| `chat(messaggi, system_prompt)` | Conversazione multi-turn sincrona | Sonnet |
| `chat_stream(messaggi, system_prompt)` | Conversazione multi-turn in streaming | Sonnet |
| `analizza_documento(testo, istruzioni)` | Analisi testo lungo (CV, PDF) | Sonnet |
| `estrai_testo_da_upload(uploaded_file)` | Legge file da `st.file_uploader` (.txt/.pdf/.csv/.xls/.xlsx) | — |
| `get_llm(veloce=False)` | Restituisce l'oggetto `ChatBedrockConverse` (per LangGraph) | entrambi |

### `platform_sdk/agent.py`

| Funzione | Scopo |
|---|---|
| `crea_agente(tools, system_prompt, memoria)` | Crea un agente ReAct LangGraph con tool personalizzati |
| `esegui_agente(agente, messaggio, thread_id)` | Invoca l'agente in modo sincrono → stringa |
| `esegui_agente_stream(agente, messaggio, thread_id)` | Invoca l'agente in streaming → generatore (per `st.write_stream`) |

### `platform_sdk/database.py`

| Metodo | Firma | Note |
|---|---|---|
| `db.init()` | `() → None` | Esegue `schema.sql` e `seed.sql` |
| `db.inserisci()` | `(tabella, dati) → int` | Ritorna l'ID inserito; auto-serializza dict/list in JSON |
| `db.inserisci_molti()` | `(tabella, lista_dati) → int` | Batch insert; ritorna numero righe |
| `db.trova_uno()` | `(tabella, filtri) → dict\|None` | SELECT … LIMIT 1 |
| `db.trova_tutti()` | `(tabella, filtri, ordine, limite) → list[dict]` | SELECT * con filtri opzionali |
| `db.aggiorna()` | `(tabella, filtri, dati) → int` | UPDATE; ritorna righe aggiornate |
| `db.elimina()` | `(tabella, filtri) → int` | DELETE; richiede almeno un filtro |
| `db.conta()` | `(tabella, filtri) → int` | COUNT(*) |
| `db.esegui()` | `(sql, parametri) → list[dict]` | Query SQL custom con placeholder `?` |

**Serializzazione automatica:** I valori `dict` o `list` passati a `inserisci()` / `aggiorna()` vengono automaticamente convertiti in stringa JSON da `_serializza_json()`. Non è necessario chiamare `json.dumps()` manualmente.

**Istanza globale:** Importare sempre `from platform_sdk.database import db` — non creare nuove istanze di `Database()`.

---

## 5. Data Model (Entità Principali)

Il sistema gestisce le seguenti entità logiche fondamentali:

- **User** (`users`): Studente, Futuro Studente o Docente. Contiene ruolo, dati demografici, `cv_testo` estratto, `profilo_json` (interessi, obiettivi).
- **Course** (`courses`): Metadati corso (titolo, CFU, livello, prerequisiti in JSON) + `docente_id` FK.
- **Material** (`materials`): "Fonte di verità" assoluta caricata dal docente. Contiene `s3_key` (percorso S3) e `testo_estratto` (estratto da PyPDF2 per il RAG).
- **Skill** (`skills`) + **UserSkill** (`user_skills`): Catalogo competenze con livello attuale e target per utente.
- **TrainingPlan** (`training_plans`) + **TrainingPlanItem** (`training_plan_items`): Itinerario formativo creato dallo Scheduler Agent, con ordine, stato, date e progresso percentuale.
- **PlanChange** (`plan_changes`): Log delle modifiche al piano applicate dall'Optimizer Agent (tipo: aggiunta, rimozione, rischedulazione, sostituzione).
- **Assessment** (`assessments`): Quiz generati dinamicamente, con `domande_json` e `risultati_json`.
- **ProgressLog** (`progress_log`) + **Notification** (`notifications`): Tracciamento eventi formativi e alert generati dal Monitoring Agent.
- **Survey** (`surveys`): Rilevazioni di soddisfazione con `sentiment_score` e `aree_miglioramento_json`.
- **SkillGapAnalysis** (`skill_gap_analyses`): Report gap competenze con `punteggio_prontezza` (0–100).

---

## 6. Data Flow (Ciclo di Vita delle Richieste)

**Caso d'uso — Generazione Quiz:**

1. **User Action:** Lo studente richiede un quiz tramite la chat su Streamlit.
2. **Routing:** Streamlit recupera `st.session_state.chat_history` e chiama `esegui_agente_stream()` con `thread_id = str(current_user_id)`.
3. **Agent Activation:** LangGraph attiva il nodo `content_gen.py` (Adaptive Content Generation Engine).
4. **Tool Execution (RAG):** L'agente invoca il tool `@tool` definito in `rag_engine.py`, che recupera il `testo_estratto` dai `materials` del docente tramite `db.trova_tutti("materials", {"course_id": ...})`.
5. **LLM Inference:** Il contesto recuperato + il system prompt RAG vengono inviati a `ChatBedrockConverse` (Sonnet) tramite LangChain.
6. **Streaming Response:** Il generatore `esegui_agente_stream()` produce chunk di testo consumati da `st.write_stream()` in tempo reale.
7. **DB Write (event-driven):** Solo al submit formale del quiz, `db.inserisci("assessments", {...})` salva domande e risultati. Nessuna scrittura intermedia.
