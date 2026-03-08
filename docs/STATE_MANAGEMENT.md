# State Management

## Scopo del Documento
Questo file definisce le regole per la gestione dello stato dell'applicazione (sia frontend che backend). Serve a evitare che l'AI o gli sviluppatori utilizzino pattern diversi per gestire dati temporanei o globali, garantendo coerenza, performance e stabilità.

---

## 1. Tecnologie Scelte

Poiché l'applicazione segue un'architettura ibrida Streamlit-LangGraph, la gestione dello stato è divisa in due domini di responsabilità rigorosi:

**Frontend (UI State):** Utilizzo esclusivo del dizionario nativo `st.session_state` di Streamlit. È severamente vietato l'uso di variabili globali Python al di fuori di questo costrutto per conservare dati tra un re-render e l'altro.

**Backend (Agentic State):** Utilizzo del `StateGraph` di LangGraph. Lo stato conversazionale, il contesto dei documenti recuperati (RAG) e il piano formativo in fase di ottimizzazione viaggiano all'interno dei nodi del grafo tramite dizionari tipizzati (`TypedDict`).

> **Eccezione documentata — Threading LangGraph:**
> In `src/agents/orchestrator.py` esiste la variabile globale a livello di modulo `_STUDENTE_ID_CORRENTE: int`.
> Questa è l'unica eccezione ammessa alla regola "no globals". LangGraph esegue i tool in thread background
> (`ThreadPoolExecutor`) dove `st.session_state` non è accessibile (mancanza di `ScriptRunContext`).
> La variabile viene aggiornata dal thread principale Streamlit **prima** di ogni invocazione dell'agente,
> garantendo coerenza senza race condition. Non replicare questo pattern altrove.

---

## 2. Stato Utente e Autenticazione

Al momento dell'accesso, l'applicazione esegue una singola query su `users` e instanzia chiavi fisse in `st.session_state`:

```python
# Query di autenticazione — unica per tutti i ruoli
user = db.trova_uno("users", {"email": email})

# Verifica password
if not verifica_password(password, user["password_hash"]):
    # gestione errore
    ...

# Popolamento session state
st.session_state.is_logged_in    = True
st.session_state.current_user_id = user["id"]        # int — PK di users.id
st.session_state.user_role       = user["ruolo"].capitalize()  # 'Studente' | 'Docente' | 'Admin'
st.session_state.chat_history    = []
```

> **Convenzione ruolo:** nel database il valore è sempre minuscolo (`'studente'`, `'docente'`, `'admin'`). La capitalizzazione avviene **una sola volta** qui in `app.py`. Non normalizzare il valore in altri punti del codice.

**Routing per ruolo:**
- `'Ospite'`   → interfaccia di orientamento universitario (nessun record su DB, sessione volatile)
- `'Studente'` → interfaccia piani personalizzati e preparazione esami
- `'Docente'`  → interfaccia caricamento materiali, approvazione contenuti, report
- `'Admin'`    → interfaccia di gestione piattaforma (sviluppo futuro)

**Gatekeeper:** Ogni pagina verifica `st.session_state.user_role` prima di renderizzare. Un Ospite non può accedere alle pagine Studente, Docente o Admin.

**Ospite — stato volatile:**
L'Ospite non ha un record nella tabella `users`. Tutto il suo stato (risposte al colloquio, dati CV analizzati) vive esclusivamente in `st.session_state` e si azzera alla chiusura della sessione. Nessun dato viene scritto sul database.

---

## 3. Chiavi di Navigazione — Homepage Studente (`views/studente.py`)

La homepage studente utilizza un set di chiavi di navigazione dedicate. Tutte hanno prefisso `_` per distinguerle dalle chiavi di autenticazione globali.

### 3a. Chiavi di vista e selezione

| Chiave | Tipo | Valori | Significato |
|---|---|---|---|
| `_view_mode` | `str \| None` | `"corso"`, `"piano"`, `None` | Vista corrente nella colonna centrale |
| `_corso_sel` | `int \| None` | ID corso | Corso universitario selezionato |
| `_corso_nome` | `str` | nome corso | Nome leggibile del corso selezionato |
| `_piano_sel` | `int \| None` | ID piano | Piano personalizzato aperto |

**Regola di transizione vista:**

```
Nessuna selezione       → _view_mode = None   → Welcome screen
Click su un corso       → _view_mode = "corso" → Vista corso (sola lettura, no upload)
Click su un piano       → _view_mode = "piano" → Vista piano (con upload materiale)
Eliminazione del piano  → _view_mode = "corso" (ritorna al corso associato)
Logout                  → st.session_state.clear()
```

> **Vincolo semantico:** quando `_view_mode = "corso"`, nella colonna centrale non compaiono mai
> pulsanti di upload o modifica. I CORSI sono in sola lettura per lo studente. L'upload di materiale
> è disponibile esclusivamente quando `_view_mode = "piano"`.

### 3b. Chiavi di stato UI transiente (non persistenti)

Queste chiavi vengono create dinamicamente durante la navigazione del contenuto di un piano.
Non vanno inizializzate al login — nascono al primo click dell'utente e persistono per tutta la sessione.

| Pattern chiave | Quando esiste | Significato |
|---|---|---|
| `_fc_fc_{i}_{p_idx}_{fc_idx}_{j}` | Dopo click "Mostra risposta" su flashcard | Retro flashcard visibile |
| `_qa_qa_{i}_{p_idx}_{q_idx}_{d_idx}` | Dopo click "Mostra risposta" su domanda quiz | Risposta quiz visibile |

> **Perché session_state e non `<input type="checkbox">`:**
> Streamlit sanitizza gli elementi `<input>` e `<label>` anche con `unsafe_allow_html=True`,
> rendendo inutilizzabile il "CSS checkbox hack" (`:checked ~ sibling`). Il toggle visuale di
> flashcard e risposte quiz usa quindi `st.button` + `st.session_state` come unico pattern affidabile.

### 3c. Chiavi chatbot

| Chiave | Tipo | Significato |
|---|---|---|
| `chat_history_display` | `list[dict]` | Messaggi mostrati in UI (`role`, `content`) |
| `_chat_history` | `list` | Alias legacy — inizializzato a `[]` al cambio corso |

---

## 4. Stato del Contesto dell'Orchestratore (`_orch_contesto_sessione`)

L'orchestratore Lea mantiene un dizionario di contesto in `st.session_state["_orch_contesto_sessione"]`.
Viene aggiornato dalla UI tramite `aggiorna_contesto_sessione()` prima di ogni chiamata AI.

```python
# Struttura del dizionario contesto
{
    "corso_id":     int | None,   # ID del corso attualmente visualizzato
    "corso_nome":   str | None,   # Nome leggibile del corso
    "tipo_vista":   str | None,   # "corso" (sola lettura) | "piano" (spazio studente)
    "piano_id":     int | None,   # ID del piano personalizzato aperto (solo se tipo_vista="piano")
    "piano_titolo": str | None,   # Titolo del piano aperto
    "ultimi_paragrafi": list[dict] # Sezioni generate nell'ultima chiamata AI (per chaining quiz/flashcard)
}
```

> `ultimi_paragrafi` viene azzerato (`[]`) ogni volta che cambia `corso_id`.
> `piano_id` e `piano_titolo` vengono aggiornati solo quando `tipo_vista = "piano"`.

**Chiavi singleton orchestratore:**

| Chiave | Contenuto |
|---|---|
| `_orch_agente_compilato` | Istanza compilata dell'orchestratore LangGraph |
| `_orch_agente_teorico` | Istanza del content generation agent |
| `_orch_thread_id` | Thread ID stabile per la memoria conversazionale |
| `_orch_contesto_sessione` | Dizionario contesto (vedi sopra) |

---

## 5. Tracking dei Progressi

La transizione tra stato temporaneo e persistenza sul database segue un flusso Event-Driven rigoroso per evitare scritture inutili:

**Stato Temporaneo (Client-Side):**
I dati ad alta frequenza (risposte temporanee a un quiz prima del submit, navigazione tra paragrafi del piano) risiedono solo in `st.session_state`.

**Sincronizzazione con il DB — eventi che scatenano la scrittura:**

| Evento | Tabelle aggiornate |
|---|---|
| Submit formale di un quiz | `tentativi_quiz`, `risposte_domande` |
| Completamento di un paragrafo del piano | `piano_paragrafi.completato = 1` |
| Completamento di un capitolo del piano | `piano_capitoli.completato = 1` |
| Generazione piano/contenuto AI tramite chat | `piani_personalizzati`, `piano_capitoli`, `piano_paragrafi`, `piano_contenuti` |
| Eliminazione piano da parte dello studente | `piano_contenuti` → `piano_paragrafi` → `piano_capitoli` → `piani_personalizzati` (cascata) |
| Upload materiale didattico studente | `materiali_didattici`, filesystem `uploads/` |
| Approvazione contenuto da parte del docente | `lezioni_corso.approvato`, `quiz.approvato` |
| Vettorizzazione di un chunk | `materiali_chunks.embedding_sync = 1` |

**Regola:** Nessun dato viene scritto sul DB durante la navigazione passiva. Solo azioni esplicite dell'utente scatenano scritture.

---

## 6. Stati UI (Loading & Error)

**Caricamenti (Loading):**
- Chiamate AI pesanti (generazione quiz, lezioni, piani): usare `st.status()` per mostrare le fasi del processo in modo trasparente (es. "Analisi del materiale...", "Generazione contenuto...").
- Caricamenti generici da DB: usare `st.spinner()`.
- Risposte in streaming dal LLM: implementare token streaming dalle API di Bedrock per feedback visivo immediato.

**Gestione Errori (Error Handling):**
- Nessun traceback Python deve essere esposto all'utente finale.
- Errori bloccanti (es. connessione DB fallita): `st.error()`.
- Feedback non critici (es. campo obbligatorio mancante): `st.toast()`.
- Mancanza di materiali per un corso (RAG senza risultati): l'agente risponde con un messaggio cortese nel flusso della chat, non come eccezione di sistema. Esempio: "Non ci sono ancora materiali caricati per questo corso. Contatta il docente."

---

## 7. Gestione dello Stato degli Agenti LangGraph

**Thread ID per la persistenza conversazionale:**
- Studente: `thread_id = "lea_sessione_" + str(user_id)`
- Docente: `thread_id = str(user_id)`
- Ospite: `thread_id = "ospite_" + str(session_uuid)` — non persistente tra sessioni

**Stato del grafo (TypedDict):**
Ogni agente deve dichiarare esplicitamente i campi del proprio stato. Esempio per il Content Generation Agent:

```python
class ContentGenState(TypedDict):
    user_id: int
    corso_id: Optional[int]
    argomento: str
    chunks_recuperati: list[dict]
    contenuto_generato: Optional[str]
    quiz_generato: Optional[dict]
```

**Regola anti-rerender:**
Il workflow LangGraph non va riavviato a ogni re-render di Streamlit. L'istanza dell'agente va salvata in `st.session_state` al primo caricamento della pagina e riutilizzata nelle chiamate successive:

```python
if "agente_content_gen" not in st.session_state:
    st.session_state.agente_content_gen = crea_agente_content_gen()
```
