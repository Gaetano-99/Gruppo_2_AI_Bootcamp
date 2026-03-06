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

**Persona 1 — Futuro Studente:** Un utente non ancora immatricolato che, dopo aver creato un account, compila questionari su interessi, ambizioni future e background. Ruolo nel sistema: `"Studente"` (stesso ruolo dello studente immatricolato — la distinzione "futuro studente" è gestita dall'agente Onboarding tramite lo stato del profilo, non da un ruolo separato).

**Persona 2 — Studente:** Un utente immatricolato che utilizza la piattaforma quotidianamente per accedere a percorsi di studio ideali, generare materiali di ripasso (riassunti, flashcard, quiz) e monitorare la propria preparazione. Ruolo nel sistema: `"Studente"`.

**Persona 3 — Docente:** Il professore che carica materiali didattici (videolezioni, slide, libri) e utilizza strumenti per creare test, lanciare challenge e monitorare l'andamento della classe. Ruolo nel sistema: `"Docente"`.

> **Implementazione ruoli:** I valori `'studente'`, `'docente'`, `'admin'` sono i soli valori validi per `users.ruolo` nel database. In `st.session_state.user_role` vengono capitalizzati (`'Studente'`, `'Docente'`, `'Admin'`) una sola volta in `app.py`. Questi valori sono usati come gatekeeper nel routing delle pagine Streamlit. L'Ospite non ha un record in `users` — il suo stato è interamente volatile in `st.session_state`.

---

## 3. Value Proposition

**Per il Futuro Studente:** Un "Onboarding AI" che offre guida all'orientamento (cosa l'utente è portato a fare) e la possibilità di ottenere certificazioni propedeutiche all'accesso universitario senza test d'ingresso.

**Per lo Studente:** Un'interfaccia basata su chatbot che chiede "Cosa vuoi imparare oggi?", in grado di rispondere a domande sugli esami, creare percorsi di studio su misura e identificare lacune tramite quiz e questionari. **Il valore aggiunto principale è la garanzia della qualità del materiale didattico: l'IA genera contenuti (riassunti, flashcard, quiz) basandosi esclusivamente sulle fonti ufficiali fornite dal docente** — implementato tramite il vincolo RAG sui `materiali_chunks` associati al corso.

**Per il Docente:** Un assistente virtuale che chiede "Come posso supportarti oggi?", risponde a domande sull'andamento delle classi e genera dashboard interattive (tramite `plotly.express`) per evidenziare gli argomenti più ostici del corso.

---

## 4. Ecosistema Multiagente

La piattaforma è governata da un'architettura multiagente avanzata. Tutti gli agenti sono costruiti con `platform_sdk/agent.py` (`crea_agente`, `esegui_agente_stream`) e usano `platform_sdk/database.py` per accedere ai dati.

### Agent 1: ONBOARDING ASSISTANT
**File:** `src/agents/onboarding.py`

Un chatbot intelligente che accoglie i futuri studenti e i nuovi utenti, raccogliendo informazioni dal loro CV tramite upload. La funzione `estrai_testo_da_upload()` di `llm.py` legge il CV (`.pdf`, `.txt`, `.docx`), poi `analizza_documento()` estrae nome, competenze ed esperienze. Il profilo viene salvato su `users.ruolo = 'studente'` con i relativi campi anagrafici.

### Agent 2: INTELLIGENT LEARNING PATH SCHEDULER
**File:** `src/agents/scheduler.py`

Analizza il profilo utente (`users` con `ruolo='studente'`) e i risultati dell'assessment iniziale, consultando il catalogo corsi (`corsi_universitari`). Propone percorsi formativi personalizzati su breve, medio e lungo termine. Il piano generato viene salvato su `piani_personalizzati` + `piano_capitoli` + `piano_paragrafi` + `piano_contenuti`, rispettando la progressione didattica.

### Agent 3: CONVERSATIONAL LEARNING PLAN OPTIMIZER
**File:** `src/agents/optimizer.py`

Consente allo studente di visualizzare il proprio piano formativo (`piani_personalizzati`) e richiedere modifiche tramite linguaggio naturale (es. "Sposta il modulo di SQL a dopo la normalizzazione"). L'AI propone alternative e le applica in tempo reale aggiornando le tabelle del piano.

### Agent 4: ADAPTIVE CONTENT GENERATION ENGINE
**File:** `src/agents/content_gen.py`

Genera contenuti strutturati (riassunti, flashcard, quiz interattivi) e adatta dinamicamente la difficoltà. **Vincolo critico:** attinge **esclusivamente** ai `materiali_chunks` del corso come fonte di verità — mai da fonti esterne o dalla knowledge generale del LLM. Il quiz generato viene salvato su `quiz` (tipo A o B) solo al submit formale.

**Tool RAG del Content Generation Agent:**
```python
@tool
def recupera_materiale_corso(corso_universitario_id: int) -> str:
    """Recupera i chunk semantici dei materiali del docente per un corso specifico."""
    # Step 1: similarità semantica nel vector store
    chunk_ids = chroma_collection.query(
        query_texts=[argomento],
        where={"corso_universitario_id": corso_universitario_id}
    )["ids"][0]

    # Step 2: metadati completi da SQLite
    chunks = db.esegui(
        "SELECT testo, sommario, argomenti_chiave FROM materiali_chunks WHERE id IN (?)",
        [chunk_ids]
    )
    return "\n\n---\n\n".join(c["testo"] for c in chunks) if chunks else \
           "Nessun materiale disponibile per questo corso."
```

### Agent 5: COMPETENCY GAP ANALYSIS AI
**File:** `src/agents/gap_analysis.py`

Analizza le aree deboli dello studente (`tentativi_quiz.aree_deboli_json`) rispetto agli argomenti del corso. Produce un report visuale con `plotly` e raccomanda i `piano_contenuti` o `lezioni_corso` più utili per colmare i gap identificati.

### Agent 6: COURSE PERFORMANCE ANALYSIS
**File:** `src/agents/course_analysis.py`

Aggrega `tentativi_quiz` + `risposte_domande` filtrati su `quiz.approvato=1` per il corso del docente. Esegue JOIN con `domande_quiz.chunk_id → materiali_chunks.argomenti_chiave` per identificare gli argomenti con tasso di errore più alto. Genera report testuale con il LLM e dashboard con `plotly`.

---

## 5. Funzionalità e User Stories

### Epic 1: Orientamento e Onboarding (Futuro Studente / Nuovo Iscritto)

**User Story 1.1:** Come nuovo utente, voglio fare l'upload del mio CV e interagire con l'Onboarding Assistant, in modo da completare rapidamente il mio profilo.
- *Implementazione:* `st.file_uploader()` → `estrai_testo_da_upload()` → `analizza_documento()` → `db.inserisci("users", {"ruolo": "studente", ...})`

**User Story 1.2:** Come futuro studente, voglio che il Learning Path Scheduler mi proponga un percorso a breve/medio termine basato sulle mie aspirazioni.
- *Implementazione:* `genera_json()` con schema piano formativo → `db.inserisci("piani_personalizzati", ...)` + `db.inserisci_molti("piano_capitoli", [...])`

### Epic 2: Apprendimento e Preparazione (Studente)

**User Story 2.1:** Come studente, voglio usare il Conversational Plan Optimizer per modificare il mio piano tramite linguaggio naturale, ricevendo alternative applicabili in tempo reale.
- *Implementazione:* `esegui_agente_stream()` → `db.aggiorna("piano_capitoli", ...)` + `db.aggiorna("piano_paragrafi", ...)`

**User Story 2.2:** Come studente, voglio che il Content Generation Engine mi crei quiz e flashcard dinamici basandosi rigorosamente sui materiali del mio professore.
- *Implementazione:* Tool RAG (ChromaDB + SQLite) → `genera_json()` → al submit: `db.inserisci("quiz", {"studente_id": users.id, "approvato": 0})`

**User Story 2.3:** Come studente, voglio utilizzare la Competency Gap Analysis AI per confrontare la mia preparazione con i requisiti dell'esame e ricevere raccomandazioni mirate.
- *Implementazione:* `db.trova_tutti("tentativi_quiz", {"studente_id": users.id})` → `chiedi_con_contesto()` → report con aree di miglioramento

### Epic 3: Supporto alla Didattica e Monitoraggio (Docente)

**User Story 3.1:** Come docente, voglio caricare i miei materiali sulla piattaforma affinché il Content Generation Engine li usi come base esclusiva per generare i supporti didattici.
- *Implementazione:* `boto3` upload su S3 → `db.inserisci("materiali_didattici", {"docente_id": users.id, "s3_key": ..., "is_processed": 0})` → segmentazione chunks → vettorizzazione (`embedding_sync=1`)

**User Story 3.2:** Come docente, voglio consultare le dashboard del Course Performance Analysis per individuare immediatamente gli argomenti più ostici per la classe.
- *Implementazione:* query JOIN tra `quiz`, `tentativi_quiz`, `domande_quiz`, `materiali_chunks` → `plotly.express` per i grafici.

**User Story 3.3:** Come docente, voglio approvare i contenuti generati dall'AI prima che siano visibili agli studenti.
- *Implementazione:* `db.aggiorna("lezioni_corso", {"approvato": 1, "id": lezione_id})` + `db.aggiorna("quiz", {"approvato": 1, "id": quiz_id})`
