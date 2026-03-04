# State Management

## Scopo del Documento
Questo file definisce le regole per la gestione dello stato dell'applicazione (sia frontend che backend). In una piattaforma di E-Learning, lo stato cambia continuamente (es. progresso video, risposte ai quiz, stato di login). Questo documento serve a evitare che l'IA o gli sviluppatori utilizzino pattern o librerie diverse per gestire dati temporanei o globali, garantendo coerenza, performance e stabilità.

---

## 1. Tecnologie Scelte

Poiché l'applicazione segue un'architettura ibrida Streamlit + LangGraph, la gestione dello stato è divisa in due domini di responsabilità rigorosi:

**Frontend (UI State):** Utilizzo esclusivo del dizionario nativo `st.session_state` di Streamlit. È severamente vietato l'uso di variabili globali Python al di fuori di questo costrutto per conservare dati tra un re-render e l'altro.

**Backend (Agentic State):** Il `StateGraph` di LangGraph. Lo stato conversazionale e il contesto dei documenti recuperati (RAG) viaggiano all'interno dei nodi del grafo tramite `TypedDict`. La memoria è gestita da `InMemorySaver` (`langgraph.checkpoint.memory`), legata al `thread_id` dell'utente.

**Istanze SDK (singleton di sessione):** Gli oggetti `agente` creati con `crea_agente()` e i modelli LLM (`_llm_principale`, `_llm_veloce`) sono singleton lazy in `llm.py`. Non vanno ricreati ad ogni interazione — vanno messi in `st.session_state` la prima volta e riutilizzati:

```python
if "agente_onboarding" not in st.session_state:
    st.session_state.agente_onboarding = crea_agente(
        tools=[...],
        system_prompt="..."
    )
```

---

## 2. Stato Utente e Autenticazione

Al momento dell'accesso, l'applicazione deve recuperare i dati dal database e instanziare le seguenti chiavi fisse in `st.session_state`:

| Chiave | Tipo | Descrizione |
|---|---|---|
| `st.session_state.is_logged_in` | `bool` | `True` se l'utente ha effettuato l'accesso |
| `st.session_state.current_user_id` | `int` | Chiave primaria della tabella `users` (es. `1`) |
| `st.session_state.user_role` | `str` | `"Studente"`, `"Docente"` o `"Futuro Studente"` |
| `st.session_state.chat_history` | `list[dict]` | Cronologia messaggi nel formato `{"role": "user"\|"assistant", "content": "..."}` |

**Gatekeeper di routing:** `user_role` è l'unico valore che governa l'accesso alle pagine. Ogni pagina protetta deve verificare:

```python
# Gatekeeper per pagine riservate al Docente
if st.session_state.get("user_role") != "Docente":
    st.error("Accesso riservato ai docenti.")
    st.stop()

# Gatekeeper per pagine riservate al Futuro Studente
if st.session_state.get("user_role") != "Futuro Studente":
    st.error("Accesso riservato ai futuri studenti.")
    st.stop()

# Gatekeeper per pagine riservate allo Studente
if st.session_state.get("user_role") != "Studente":
    st.error("Accesso riservato agli studenti iscritti.")
    st.stop()
```
**Ruoli ammessi (valori esatti — rispettare le maiuscole):**
- `"Studente"` — accesso a chat, quiz, piano formativo, gap analysis
- `"Docente"` — accesso a dashboard analitiche, upload materiali, monitoring, survey
- `"Futuro Studente"` — accesso a onboarding, orientamento, certificazioni propedeutiche

---

## 3. Formato della Chat History

La chiave `st.session_state.chat_history` deve contenere messaggi nel formato dizionario standard, compatibile sia con `platform_sdk/llm.py` (`chat()`, `chat_stream()`) sia con il rendering nativo di Streamlit:

```python
# Struttura corretta
st.session_state.chat_history = [
    {"role": "user",      "content": "Ciao! Vorrei un quiz su Machine Learning."},
    {"role": "assistant", "content": "Certo! Ecco 3 domande sul learning rate..."},
]

# Aggiungere un messaggio utente
st.session_state.chat_history.append({"role": "user", "content": domanda})

# Aggiungere la risposta dell'AI (dopo st.write_stream)
st.session_state.chat_history.append({"role": "assistant", "content": risposta_completa})
```

**Thread ID per LangGraph:** Usare sempre `str(st.session_state.current_user_id)` come `thread_id` nelle chiamate ad `esegui_agente()` / `esegui_agente_stream()`. Non usare stringhe hardcoded come `"default"` in produzione.

---

## 4. Tracking dei Progressi

La transizione dei dati tra lo stato effimero del client e la persistenza su SQLite segue un flusso **event-driven**. Nessuna scrittura su DB avviene in modo continuo o a ogni interazione UI.

**Stato temporaneo (solo `st.session_state`):**
- Risposte parziali a un quiz prima del submit
- Minuto corrente di riproduzione di un video
- Bozza di modifica al piano formativo prima della conferma

**Scrittura su DB — eventi che la scatenano:**

| Evento | Tabella aggiornata | Metodo SDK |
|---|---|---|
| Completamento effettivo di una lezione | `training_plan_items` (campo `stato`, `data_completamento`) | `db.aggiorna()` |
| Submit formale di un quiz | `assessments` (inserimento) + `progress_log` (evento "completato") | `db.inserisci()` |
| Modifica del piano formativa confermata | `training_plan_items` + `plan_changes` (log della modifica) | `db.aggiorna()` + `db.inserisci()` |
| Chiusura volontaria di un modulo | `progress_log` (evento "abbandonato" o "in_ritardo") | `db.inserisci()` |
| Risposta a una survey | `surveys` (inserimento) | `db.inserisci()` |

**Pattern per la scrittura su `plan_changes`** (Optimizer Agent):
```python
# 1. Applica la modifica al piano
db.aggiorna("training_plan_items", {"id": item_id}, {"stato": nuovo_stato, ...})

# 2. Registra la modifica nel log
db.inserisci("plan_changes", {
    "plan_id": plan_id,
    "user_id": st.session_state.current_user_id,
    "tipo_modifica": "rischedulazione",   # aggiunta | rimozione | rischedulazione | sostituzione
    "dettagli_json": {"vecchia_data": ..., "nuova_data": ...},
    "motivazione": "Richiesta dell'utente tramite chat"
})
```

---

## 5. Stati UI — Loading & Error

L'esperienza utente deve essere fluida, specialmente durante i task computazionalmente pesanti (chiamate LLM ad Amazon Bedrock).

### Loading

**Task AI complessi** (es. Content Generation Agent che crea un quiz):
```python
with st.status("Generazione quiz in corso...", expanded=True) as status:
    st.write("📄 Analisi del materiale del docente...")
    contesto = db.trova_tutti("materials", {"course_id": course_id})
    st.write("🧠 Generazione domande con AI...")
    quiz = genera_json(prompt, schema)
    status.update(label="Quiz pronto!", state="complete")
```

**Caricamenti generici** (fetch DB, operazioni brevi):
```python
with st.spinner("Caricamento dati..."):
    utenti = db.trova_tutti("users")
```

**Chat streaming** (pattern principale per tutte le pagine di chat):
```python
with st.chat_message("assistant"):
    risposta = st.write_stream(
        esegui_agente_stream(agente, domanda, thread_id=str(st.session_state.current_user_id))
    )
st.session_state.chat_history.append({"role": "assistant", "content": risposta})
```

### Gestione Errori

| Scenario | Componente da usare | Note |
|---|---|---|
| Errore bloccante (DB non disponibile, AWS timeout) | `st.error("❌ ...")` | Mostrare messaggio human-friendly, mai il traceback Python |
| Warning non bloccante (campo mancante nel form) | `st.warning("⚠️ ...")` | |
| Feedback non invasivo (upload completato, modifica salvata) | `st.toast("✅ ...")` | Scompare automaticamente |
| LLM non trova contesto RAG sufficiente | Risposta cortese nel flusso chat | Non sollevare eccezione — gestire nell'agent |
| Credenziali AWS mancanti nel `.env` | `st.error()` + suggerimento correzione | Vedi pattern in `app.py` |

**Regola assoluta:** Nessun traceback Python (`Exception`, `Traceback`) deve essere mostrato all'utente finale. Tutti i blocchi che chiamano `platform_sdk` devono essere avvolti in `try/except`.

Esempio dal codice reale (`app.py`):
```python
try:
    from platform_sdk.database import db
    n_utenti = db.conta("users")
    # ... rendering UI
except Exception as e:
    st.warning(
        f"⚠️ Database non disponibile: {e}\n\n"
        "Inizializza il database con: "
        '`python3 -c "from platform_sdk.database import db; db.init()"`'
    )
```
