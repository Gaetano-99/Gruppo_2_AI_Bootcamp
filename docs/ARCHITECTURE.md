# System Architecture

## Scopo del Documento
Questo documento fornisce la mappa strutturale e logica dell'intera applicazione. È fondamentale sia per l'onboarding di nuovi sviluppatori, sia per orientare correttamente gli strumenti di *vibecoding*, indicando l'esatta collocazione dei moduli e il funzionamento del "motore" software.

---

## 1. Design di Sistema

L'applicazione segue un'architettura a tre livelli (Three-Tier), orientata all'orchestrazione AI multiagente.

* **Presentation Layer (Frontend):** Sviluppato interamente in `streamlit`. Gestisce l'interfaccia utente, il rendering dei grafici (`plotly`) e l'interazione in tempo reale con i chatbot degli agenti.

* **Logic & AI Orchestration Layer (Backend):** Il "cervello" del sistema. Utilizza `langgraph` per orchestrare i 6 agenti IA. `langchain` e `langchain-aws` gestiscono i prompt e la comunicazione con i modelli LLM su Amazon Bedrock. L'estrazione del testo dai materiali caricati avviene tramite `PyPDF2`.

* **Data & Storage Layer:**
  * I file multimediali e i PDF dei docenti sono archiviati su Amazon S3 tramite `boto3`.
  * I dati strutturati sono gestiti in un database relazionale SQLite (schema in `schema.sql`).
  * `pandas` è usato per la manipolazione in memoria dei dati; `openpyxl` per l'esportazione tabellare.

---

## 2. Alberatura del Progetto

```text
/
├── .env                        # Variabili d'ambiente (AWS keys, DB URI) — MAI COMMITTATO
├── .gitignore
├── requirements.txt
├── docs/                       # Documentazione di progetto (PRD, ARCHITECTURE, etc.)
└── src/
    ├── app.py                  # Entry point Streamlit — routing per ruolo
    ├── ui/
    │   ├── pages/              # Pagine per ruolo (ospite, studente, docente)
    │   └── components/         # Widget riutilizzabili (cards, forms, grafici)
    ├── core/
    │   ├── config.py           # Caricamento variabili da .env
    │   └── aws_client.py       # Setup Boto3 per S3 e Bedrock
    ├── agents/                 # I 6 agenti LangGraph
    │   ├── onboarding.py       # Agent 1 — Onboarding Assistant
    │   ├── scheduler.py        # Agent 2 — Learning Path Scheduler
    │   ├── optimizer.py        # Agent 3 — Conversational Plan Optimizer
    │   ├── content_gen.py      # Agent 4 — Adaptive Content Generation Engine
    │   ├── gap_analysis.py     # Agent 5 — Competency Gap Analysis AI
    │   └── course_analysis.py  # Agent 6 — Course Performance Analysis
    ├── tools/
    │   ├── rag_engine.py       # Retrieval sui materiali_chunks
    │   └── pdf_parser.py       # Estrazione testo con PyPDF2
    └── data/
        ├── schema.sql          # Schema database (fonte di verità)
        ├── schemas.py          # Entità tipizzate (Pydantic/TypedDict)
        └── db_handler.py       # Funzioni CRUD
```

---

## 3. Data Model (Entità Principali)

Le entità rispecchiano fedelmente le tabelle definite in `schema.sql`. I nomi qui sotto corrispondono esattamente ai nomi delle tabelle nel database.

**`studenti`**
Utente immatricolato. Contiene dati anagrafici, riferimento al corso di laurea (`corso_di_laurea_id`) e `profilo_json` (interessi, obiettivo professionale, stile di apprendimento) compilato dall'Onboarding Assistant tramite intervista o analisi CV.

**`docenti`**
Professore titolare di uno o più corsi universitari. Carica i materiali didattici e approva i contenuti generati dall'AI.

**`corsi_di_laurea`**
Il percorso accademico (es. "Ingegneria Informatica"). Uno studente appartiene a un solo corso di laurea.

**`corsi_universitari`**
La singola materia accademica (es. "Basi di Dati"). Appartiene a uno o più corsi di laurea tramite `corsi_laurea_universitari`. Ha un solo docente titolare.

**`materiali_didattici` + `materiali_chunks`**
Fonte di verità assoluta per il RAG. I materiali caricati dal docente (PDF, slide, video) vengono segmentati in chunks semantici dal Document Processor. I chunks sono la base esclusiva per la generazione di qualsiasi contenuto AI. Non vanno mai svuotati al riavvio.

**`piani_personalizzati`**
Piano di studio generato dall'AI per lo studente. Non collegato direttamente ai corsi universitari (eccetto tipo `'esame'`). Struttura gerarchica: `piano_capitoli` → `piano_paragrafi` → `piano_contenuti`.

**`piano_contenuti`**
Il contenuto effettivo del piano: lezione, riassunto, schema, flashcard o quiz. I contenuti di tipo `'quiz'` rimandano alla tabella `quiz`.

**`quiz` + `domande_quiz` + `tentativi_quiz` + `risposte_domande`**
Sistema di valutazione formativa. Tre tipi distinti (A: piano privato studente, B: corso privato studente, C: corso approvato docente). Solo i quiz con `approvato=1` alimentano i report del docente.

**`lezioni_corso`**
Lezioni generate dall'AI o scritte dal docente, associate a un corso universitario. Visibili agli studenti solo dopo approvazione (`approvato=1`).

**Ospite**
Non ha tabella nel database. Stato volatile gestito esclusivamente in `st.session_state`. Accede alla piattaforma come strumento di orientamento universitario senza registrazione.

---

## 4. Data Flow — Ciclo di Vita delle Richieste

### Caso d'uso: Generazione di un Quiz nel Piano Personalizzato

```
1. Studente richiede un quiz tramite chat (Streamlit)
        ↓
2. LangGraph attiva il nodo content_gen.py
        ↓
3. rag_engine.py interroga materiali_chunks
   WHERE corso_universitario_id = X
   ORDER BY rilevanza rispetto all'argomento richiesto
        ↓
4. I chunk selezionati vengono inviati al LLM (Amazon Bedrock via langchain-aws)
        ↓
5. Il JSON del quiz viene scritto su:
   - quiz (tipo A o B, approvato=0)
   - domande_quiz (chunk_id per ogni domanda)
   - piano_contenuti (quiz_id collegato, chunk_ids_utilizzati)
        ↓
6. Streamlit renderizza il quiz interattivo
        ↓
7. Al submit: tentativi_quiz + risposte_domande salvati sul DB
```

### Caso d'uso: Report Docente sull'Andamento della Classe

```
1. Docente apre la dashboard del corso
        ↓
2. course_analysis.py aggrega tentativi_quiz + risposte_domande
   filtrati su quiz.approvato=1 per quel corso_universitario_id
        ↓
3. JOIN con domande_quiz.chunk_id → materiali_chunks.argomenti_chiave
   per identificare gli argomenti con tasso di errore più alto
        ↓
4. LLM genera report testuale con insight e raccomandazioni
        ↓
5. Streamlit renderizza report + grafici Plotly per il docente
```
