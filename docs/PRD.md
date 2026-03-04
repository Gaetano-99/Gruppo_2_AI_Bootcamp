# Product Requirements Document (PRD)

## Scopo del Documento
Questo documento rappresenta la visione strategica e il "documento d'identità" della nostra applicazione. Serve a mantenere l'intero team di sviluppo e gli strumenti di Intelligenza Artificiale (AI coding assistants) perfettamente allineati sugli obiettivi di business e sul valore reale del prodotto.

---

## 1. Visione e Obiettivi

**Problema Fondamentale:** La necessità di orientare i futuri studenti, personalizzare lo studio per gli iscritti e fornire ai docenti strumenti avanzati per la creazione di materiali e il monitoraggio delle classi.

**Visione del Prodotto:** Sviluppo di una piattaforma E-learning innovativa per l'università Federico II, basata su un'architettura IA multiagente. La piattaforma è sviluppata in collaborazione tra Deloitte e l'Università Federico II di Napoli nell'ambito della Digita Academy (2025).

**Obiettivi di Business (KPIs):**
- Per gli studenti: migliorare l'apprendimento e facilitare il superamento degli esami.
- Per i docenti: facilitare lo sviluppo dei corsi in aula e ottimizzare la valutazione degli studenti.

---

## 2. Target (User Personas)

**Persona 1 — Futuro Studente:** Un utente non ancora immatricolato che, dopo aver creato un account, compila questionari su interessi, ambizioni future e background. Ruolo nel sistema: `"Futuro Studente"`.

**Persona 2 — Studente:** Un utente immatricolato che utilizza la piattaforma quotidianamente per accedere a percorsi di studio ideali, generare materiali di ripasso (riassunti, flashcard, quiz) e monitorare la propria preparazione. Ruolo nel sistema: `"Studente"`.

**Persona 3 — Docente:** Il professore che carica materiali didattici (videolezioni, slide, libri) e utilizza strumenti per creare test, lanciare challenge e monitorare l'andamento della classe. Ruolo nel sistema: `"Docente"`.

> **Implementazione ruoli:** I valori `"Studente"`, `"Docente"`, `"Futuro Studente"` sono i soli valori validi per `users.ruolo` e per `st.session_state.user_role`. Sono usati come gatekeeper nel routing delle pagine Streamlit.

---

## 3. Value Proposition

**Per il Futuro Studente:** Un "Onboarding AI" che offre guida all'orientamento (cosa l'utente è portato a fare) e la possibilità di ottenere certificazioni propedeutiche all'accesso universitario senza test d'ingresso.

**Per lo Studente:** Un'interfaccia basata su chatbot che chiede "Cosa vuoi imparare oggi?", in grado di rispondere a domande sugli esami, creare percorsi di studio su misura e identificare lacune tramite quiz e questionari. **Il valore aggiunto principale è la garanzia della qualità del materiale didattico: l'IA genera contenuti (riassunti, flashcard, quiz) basandosi esclusivamente sulle fonti ufficiali fornite dal docente** — implementato tramite il vincolo RAG sul campo `testo_estratto` della tabella `materials`.

**Per il Docente:** Un assistente virtuale che chiede "Come posso supportarti oggi?", risponde a domande sull'andamento delle classi e genera dashboard interattive (tramite `plotly.express`) per evidenziare gli argomenti più ostici del corso.

---

## 4. Ecosistema Multiagente

La piattaforma è governata da un'architettura multiagente avanzata. Tutti gli agenti sono costruiti con `platform_sdk/agent.py` (`crea_agente`, `esegui_agente_stream`) e usano `platform_sdk/database.py` per accedere ai dati.

### Agent 1: ONBOARDING ASSISTANT
**File:** `src/agents/onboarding.py`

Un chatbot intelligente che accoglie i futuri studenti e i nuovi utenti, raccogliendo informazioni dal loro CV tramite upload. La funzione `estrai_testo_da_upload()` di `llm.py` legge il CV (`.pdf`, `.txt`, `.docx`), poi `analizza_documento()` estrae nome, competenze ed esperienze. Il profilo viene salvato su `users.cv_testo` e `users.profilo_json`. Propone un assessment iniziale basato sulle aspirazioni (`assessments.tipo = "iniziale"`).

### Agent 2: INTELLIGENT LEARNING PATH SCHEDULER
**File:** `src/agents/scheduler.py`

Analizza il profilo utente (`users.profilo_json`, `user_skills`) e i risultati dell'assessment iniziale, consultando il catalogo corsi (`courses`). Propone percorsi formativi personalizzati su breve, medio e lungo termine. Il piano generato viene salvato su `training_plans` + `training_plan_items`, rispettando i prerequisiti (`courses.prerequisiti_json`) e la progressione didattica.

### Agent 3: CONVERSATIONAL LEARNING PLAN OPTIMIZER
**File:** `src/agents/optimizer.py`

Consente allo studente di visualizzare il proprio piano formativo (`training_plans`) e richiedere modifiche tramite linguaggio naturale (es. "Sposta il corso di ML a giugno"). L'AI propone alternative e le applica in tempo reale aggiornando `training_plan_items`. Ogni modifica confermata genera un record su `plan_changes` con `tipo_modifica` e `motivazione`.

### Agent 4: AI-DRIVEN PROGRESS MONITORING AGENT
**File:** `src/agents/monitoring.py`

Traccia l'avanzamento formativo tramite dashboard con KPI (grafici `plotly`). Legge `training_plan_items.progresso` e `progress_log` per identificare ritardi o inattività. Genera automaticamente alert (`notifications`) e produce bozze di email personalizzate per i docenti tramite `chiedi_con_contesto()` di `llm.py`.

### Agent 5: ADAPTIVE CONTENT GENERATION ENGINE
**File:** `src/agents/content_gen.py`

Genera contenuti strutturati (riassunti, flashcard, quiz interattivi) e adatta dinamicamente la difficoltà. **Vincolo critico:** attinge **esclusivamente** ai materiali caricati dal docente (`materials.testo_estratto`) come fonte di verità — mai da fonti esterne o da knowledge generale del LLM. Il quiz generato viene salvato su `assessments` solo al submit formale.

**Tool RAG del Content Generation Agent:**
```python
@tool
def recupera_materiale_corso(course_id: int) -> str:
    """Recupera il testo estratto dai materiali del docente per un corso specifico."""
    materiali = db.trova_tutti("materials", {"course_id": course_id})
    testi = [m["testo_estratto"] for m in materiali if m.get("testo_estratto")]
    return "\n\n---\n\n".join(testi) if testi else "Nessun materiale disponibile per questo corso."
```

### Agent 6: SMART SURVEY LIFECYCLE MANAGER
**File:** `src/agents/survey.py`

Gestisce l'intero ciclo delle survey (post-corso o periodiche), generando domande contestualizzate tramite `genera_json()`. Analizza le risposte con sentiment analysis (LLM) e popola `surveys.sentiment_score` (range -1.0 / 1.0) e `surveys.aree_miglioramento_json`. Fornisce ai docenti dashboard aggregate con insight azionabili.

### Agent 7: COMPETENCY GAP ANALYSIS AI
**File:** `src/agents/gap_analysis.py`

Visualizza il profilo competenze dell'utente (`user_skills`) rispetto a un ruolo target (es. "Data Scientist Junior"). Analizza il gap skill per skill, produce un report visuale con `plotly` e salva il risultato su `skill_gap_analyses` con `punteggio_prontezza` (0–100). Raccomanda corsi dal catalogo (`courses`) per colmare i gap identificati.

---

## 5. Funzionalità e User Stories

### Epic 1: Orientamento e Onboarding (Futuro Studente / Nuovo Iscritto)

**User Story 1.1:** Come nuovo utente, voglio fare l'upload del mio CV e interagire con l'Onboarding Assistant, in modo da completare rapidamente il mio profilo ed effettuare un assessment iniziale.
- *Implementazione:* `st.file_uploader()` → `estrai_testo_da_upload()` → `analizza_documento()` → `db.inserisci("users", ...)` + `db.inserisci("assessments", ...)`

**User Story 1.2:** Come futuro studente, voglio che l'Intelligent Learning Path Scheduler mi proponga un percorso a breve/medio termine basato sulle mie aspirazioni, per ottenere certificazioni propedeutiche all'immatricolazione.
- *Implementazione:* `genera_json()` con schema piano formativo → `db.inserisci("training_plans", ...)` + `db.inserisci_molti("training_plan_items", [...])`

### Epic 2: Apprendimento e Preparazione (Studente)

**User Story 2.1:** Come studente, voglio usare il Conversational Learning Plan Optimizer per spostare o aggiungere un corso al mio piano tramite linguaggio naturale, ricevendo alternative applicabili in tempo reale.
- *Implementazione:* `esegui_agente_stream()` → `db.aggiorna("training_plan_items", ...)` + `db.inserisci("plan_changes", ...)`

**User Story 2.2:** Come studente, voglio che l'Adaptive Content Generation Engine mi crei quiz e flashcard dinamici basandosi rigorosamente sulle videolezioni del mio professore.
- *Implementazione:* Tool RAG → `db.trova_tutti("materials", {"course_id": ...})` → `genera_json()` → al submit: `db.inserisci("assessments", ...)`

**User Story 2.3:** Come studente, voglio utilizzare la Competency Gap Analysis AI per confrontare la mia preparazione con i requisiti di un esame e ricevere raccomandazioni mirate.
- *Implementazione:* `db.trova_tutti("user_skills", {"user_id": ...})` → `chiedi_con_contesto()` → `db.inserisci("skill_gap_analyses", ...)`

### Epic 3: Supporto alla Didattica e Monitoraggio (Docenti)

**User Story 3.1:** Come docente, voglio caricare i miei materiali sulla piattaforma affinché l'Adaptive Content Generation Engine li usi come base esclusiva per generare i supporti didattici per i miei studenti.
- *Implementazione:* `boto3` upload su S3 → `db.inserisci("materials", {"s3_key": ..., "testo_estratto": ..., "tipo_file": "PDF"})` con PyPDF2 per l'estrazione.

**User Story 3.2:** Come docente, voglio consultare le dashboard generate dall'AI-Driven Progress Monitoring Agent per individuare immediatamente gli studenti a rischio ritardo.
- *Implementazione:* `db.esegui(query JOIN tra users, training_plan_items, progress_log)` → `plotly.express` per i grafici.

**User Story 3.3:** Come docente, voglio che il sistema generi bozze di email personalizzate per gli studenti in difficoltà.
- *Implementazione:* `chiedi_con_contesto(domanda="Genera email per studente in ritardo", contesto=dati_studente)` → `st.text_area()` per la revisione prima dell'invio.

**User Story 3.4:** Come docente, voglio accedere agli insight dello Smart Survey Lifecycle Manager per capire quali parti del mio corso necessitano di miglioramenti.
- *Implementazione:* `db.trova_tutti("surveys", {"course_id": ...})` → aggregazione `sentiment_score` → dashboard `plotly`.
