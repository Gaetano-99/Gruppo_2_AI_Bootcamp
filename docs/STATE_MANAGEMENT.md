# State Management

## Scopo del Documento
Questo file definisce le regole per la gestione dello stato dell'applicazione (sia frontend che backend). Serve a evitare che l'AI o gli sviluppatori utilizzino pattern diversi per gestire dati temporanei o globali, garantendo coerenza, performance e stabilità.

---

## 1. Tecnologie Scelte

Poiché l'applicazione segue un'architettura ibrida Streamlit-LangGraph, la gestione dello stato è divisa in due domini di responsabilità rigorosi:

**Frontend (UI State):** Utilizzo esclusivo del dizionario nativo `st.session_state` di Streamlit. È severamente vietato l'uso di variabili globali Python al di fuori di questo costrutto per conservare dati tra un re-render e l'altro.

**Backend (Agentic State):** Utilizzo del `StateGraph` di LangGraph. Lo stato conversazionale, il contesto dei documenti recuperati (RAG) e il piano formativo in fase di ottimizzazione viaggiano all'interno dei nodi del grafo tramite dizionari tipizzati (`TypedDict`).

---

## 2. Stato Utente e Autenticazione

Al momento dell'accesso, l'applicazione recupera i dati dal database e instanzia chiavi fisse in `st.session_state`:

```python
st.session_state.is_logged_in    # bool — True se autenticato
st.session_state.current_user_id # int  — PK di studenti.id o docenti.id
st.session_state.user_role       # str  — 'Studente' | 'Docente' | 'Ospite'
st.session_state.chat_history    # list — cronologia messaggi della sessione attiva
```

**Routing per ruolo:**
- `'Ospite'`   → interfaccia di orientamento universitario (nessun record su DB, sessione volatile)
- `'Studente'` → interfaccia piani personalizzati e preparazione esami
- `'Docente'`  → interfaccia caricamento materiali, approvazione contenuti, report

**Gatekeeper:** Ogni pagina verifica `st.session_state.user_role` prima di renderizzare. Un Ospite non può accedere alle pagine Studente o Docente.

**Ospite — stato volatile:**
L'Ospite non ha un record nelle tabelle `studenti`, `docenti` o `admin`. Tutto il suo stato (risposte al colloquio, dati CV analizzati) vive esclusivamente in `st.session_state` e si azzera alla chiusura della sessione. Nessun dato viene scritto sul database.

---

## 3. Tracking dei Progressi

La transizione tra stato temporaneo e persistenza sul database segue un flusso Event-Driven rigoroso per evitare scritture inutili:

**Stato Temporaneo (Client-Side):**
I dati ad alta frequenza (risposte temporanee a un quiz prima del submit, navigazione tra paragrafi del piano) risiedono solo in `st.session_state`.

**Sincronizzazione con il DB — eventi che scatenano la scrittura:**

| Evento | Tabelle aggiornate |
|---|---|
| Submit formale di un quiz | `tentativi_quiz`, `risposte_domande` |
| Completamento di un paragrafo del piano | `piano_paragrafi.completato = 1` |
| Completamento di un capitolo del piano | `piano_capitoli.completato = 1` |
| Modifica al piano tramite chat | `piani_personalizzati`, `piano_capitoli`, `piano_paragrafi`, `piano_contenuti` |
| Approvazione contenuto da parte del docente | `lezioni_corso.approvato`, `quiz.approvato` |

**Regola:** Nessun dato viene scritto sul DB durante la navigazione passiva. Solo azioni esplicite dell'utente scatenano scritture.

---

## 4. Stati UI (Loading & Error)

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

## 5. Gestione dello Stato degli Agenti LangGraph

**Thread ID per la persistenza conversazionale:**
- Studente: `thread_id = str(studente_id)`
- Docente: `thread_id = str(docente_id)`
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
