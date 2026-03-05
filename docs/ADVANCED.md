# 🚀 Guida Avanzata — Usare LangChain e LangGraph direttamente

Questa guida spiega come usare **LangChain** e **LangGraph** senza passare dal `platform_sdk`.

Il `platform_sdk` è un wrapper semplificato: dietro le quinte usa proprio queste librerie. Imparare a usarle direttamente vi dà **più controllo** e vi prepara a lavorare su progetti reali.

> **Prerequisito**: aver completato almeno un esercizio con il `platform_sdk` e avere il progetto configurato (`.env` con le credenziali AWS funzionante).

---

## 📖 Indice

1. [Cos'è LangChain e cos'è LangGraph](#-cosè-langchain-e-cosè-langgraph)
2. [Setup: ottenere il modello LLM](#-setup-ottenere-il-modello-llm)
3. [Usare il modello direttamente (LangChain)](#-usare-il-modello-direttamente-langchain)
4. [Creare tool personalizzati](#-creare-tool-personalizzati)
5. [Creare un agente con LangGraph (prebuilt)](#-creare-un-agente-con-langgraph-prebuilt)
6. [Creare un agente custom con il Graph API](#-creare-un-agente-custom-con-il-graph-api)
7. [Output strutturato (JSON)](#-output-strutturato-json)
8. [Tabella di confronto SDK vs diretto](#-tabella-di-confronto-sdk-vs-diretto)
9. [Risorse utili](#-risorse-utili)

---

## 🔍 Cos'è LangChain e cos'è LangGraph

| Libreria | Cosa fa | Quando usarla |
|----------|---------|---------------|
| **LangChain** | Fornisce componenti standard per interagire con i modelli AI (messaggi, tool, output strutturato) | Quando volete parlare con un LLM, usare tool, o ottenere risposte strutturate |
| **LangGraph** | Framework per costruire **grafi** (workflow) con nodi e archi, ideale per agenti complessi | Quando volete un agente che ragiona in più passi, usa tool, e mantiene memoria |

**In parole semplici:**
- **LangChain** = il "vocabolario" per parlare con l'AI (messaggi, modelli, tool)
- **LangGraph** = il "motore" che fa girare un agente in loop (ragiona → agisce → osserva → ripete)

Il `platform_sdk` che avete usato finora è un **wrapper** che semplifica queste due librerie.

---

## 🔧 Setup: ottenere il modello LLM

### Opzione A: usare `get_llm()` dal SDK (scorciatoia consigliata)

Il modo più semplice per ottenere un oggetto LLM già configurato con le vostre credenziali AWS:

```python
from platform_sdk.llm import get_llm

# Modello principale (Claude Sonnet — più intelligente)
llm = get_llm()

# Modello veloce (Claude Haiku — più economico)
llm_veloce = get_llm(veloce=True)
```

> `get_llm()` restituisce un oggetto `ChatBedrockConverse` di LangChain, già pronto all'uso. Potete usarlo con tutte le API di LangChain e LangGraph.

### Opzione B: creare il modello da zero (senza SDK)

Se volete capire cosa succede dietro le quinte, potete creare il modello manualmente:

```python
import os
from dotenv import load_dotenv
from langchain_aws import ChatBedrockConverse

# Carica le variabili dal file .env
load_dotenv()

# Crea il modello manualmente
llm = ChatBedrockConverse(
    model="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region_name=os.getenv("AWS_DEFAULT_REGION", "eu-central-1"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    temperature=0.3,       # 0 = preciso, 1 = creativo
    max_tokens=4096,       # lunghezza massima della risposta
)
```

> Questo è esattamente quello che fa `get_llm()` internamente!

---

## 🤖 Usare il modello direttamente (LangChain)

Ora che avete l'oggetto `llm`, potete usarlo direttamente con le API di LangChain.

### Domanda semplice con `invoke()`

```python
from platform_sdk.llm import get_llm
from langchain_core.messages import HumanMessage

llm = get_llm()

# Invoca il modello con un messaggio
risposta = llm.invoke([HumanMessage(content="Cos'è il machine learning?")])

# Il risultato è un oggetto AIMessage
print(risposta.content)  # → il testo della risposta
```

**Cosa succede qui:**
1. Creiamo un messaggio di tipo `HumanMessage` (= messaggio dell'utente)
2. Lo passiamo al modello con `invoke()`
3. Il modello restituisce un `AIMessage` con la risposta nel campo `.content`

### Conversazione con più messaggi

```python
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

messaggi = [
    # Istruzione di sistema: dice al modello come comportarsi
    SystemMessage(content="Sei un tutor di Python. Rispondi in italiano, in modo semplice."),

    # Primo scambio
    HumanMessage(content="Cos'è una lista in Python?"),
    AIMessage(content="Una lista è una collezione ordinata di elementi..."),

    # Nuova domanda dell'utente
    HumanMessage(content="Come aggiungo un elemento?"),
]

risposta = llm.invoke(messaggi)
print(risposta.content)
```

**I tre tipi di messaggio:**
| Tipo | Ruolo | Esempio |
|------|-------|---------|
| `SystemMessage` | Istruzioni per il modello | "Sei un assistente formativo" |
| `HumanMessage` | Messaggio dell'utente | "Quali corsi mi consigli?" |
| `AIMessage` | Risposta del modello | "Ti consiglio questi 3 corsi..." |

### Streaming (risposta in tempo reale)

```python
from langchain_core.messages import HumanMessage

# stream() restituisce i pezzi della risposta man mano che vengono generati
for chunk in llm.stream([HumanMessage(content="Raccontami una breve storia")]):
    print(chunk.content, end="", flush=True)
```

**In Streamlit:**

```python
import streamlit as st
from platform_sdk.llm import get_llm
from langchain_core.messages import HumanMessage, SystemMessage

llm = get_llm()

if domanda := st.chat_input("Scrivi una domanda..."):
    messaggi = [
        SystemMessage(content="Sei un tutor AI. Rispondi in italiano."),
        HumanMessage(content=domanda),
    ]

    with st.chat_message("assistant"):
        # st.write_stream accetta un generatore
        def genera_stream():
            for chunk in llm.stream(messaggi):
                if chunk.content:
                    yield chunk.content

        st.write_stream(genera_stream())
```

---

## 🔨 Creare tool personalizzati

Un **tool** è una funzione Python che l'AI può decidere di chiamare. Serve a dare all'agente la capacità di **fare cose** (leggere dal database, fare calcoli, chiamare API, ecc.).

### Regole d'oro per i tool

1. **Il nome della funzione** deve descrivere cosa fa (es: `cerca_corsi`, `conta_utenti`)
2. **Il docstring** (la stringa tra triple virgolette) è fondamentale: è la descrizione che l'AI legge per decidere quando usare il tool
3. **I parametri** devono avere tipi espliciti (es: `query: str`, `user_id: int`)
4. **Il valore di ritorno** deve essere una stringa leggibile

```python
from langchain_core.tools import tool
from platform_sdk.database import db

@tool
def cerca_corsi(query: str) -> str:
    """Cerca corsi nel catalogo formativo della piattaforma.
    Usa questo strumento quando l'utente chiede informazioni su corsi o formazione.

    Args:
        query: il termine di ricerca (es: "Python", "leadership", "data")
    """
    risultati = db.esegui(
        "SELECT titolo, livello, durata_ore FROM courses WHERE titolo LIKE ?",
        [f"%{query}%"]
    )
    if not risultati:
        return f"Nessun corso trovato per '{query}'"
    return "\n".join(
        f"- {r['titolo']} (livello: {r['livello']}, durata: {r['durata_ore']}h)"
        for r in risultati
    )


@tool
def conta_utenti() -> str:
    """Conta il numero totale di utenti registrati nella piattaforma.
    Usa questo strumento quando l'utente chiede quanti utenti ci sono."""
    n = db.conta("users")
    return f"Ci sono {n} utenti registrati nella piattaforma."


@tool
def ottieni_profilo(user_id: int) -> str:
    """Recupera il profilo di un utente dato il suo ID.

    Args:
        user_id: l'identificativo numerico dell'utente
    """
    utente = db.trova_uno("users", {"id": user_id})
    if not utente:
        return f"Nessun utente trovato con ID {user_id}"
    return f"Nome: {utente['nome']} {utente['cognome']}, Ruolo: {utente['ruolo']}"
```

### Testare un tool manualmente

I tool sono normali funzioni Python. Potete testarli direttamente:

```python
# Test diretto (senza AI)
risultato = cerca_corsi.invoke({"query": "Python"})
print(risultato)
```

### Collegare tool al modello con `bind_tools()`

Prima di poter usare i tool con un agente, potete anche testarli in modo "manuale" collegandoli al modello:

```python
from platform_sdk.llm import get_llm

llm = get_llm()

# Collega i tool al modello
llm_con_tools = llm.bind_tools([cerca_corsi, conta_utenti, ottieni_profilo])

# Ora il modello sa che può usare questi tool
risposta = llm_con_tools.invoke("Quanti utenti ci sono?")

# La risposta potrebbe contenere una richiesta di chiamata a un tool
print(risposta.tool_calls)
# → [{'name': 'conta_utenti', 'args': {}, 'id': '...'}]
```

> **Nota**: con `bind_tools()` il modello *chiede* di usare un tool, ma non lo esegue da solo. Serve un agente (vedi sezione successiva) per completare il ciclo.

---

## 🤖 Creare un agente con LangGraph (prebuilt)

Il modo più veloce per creare un agente funzionante è usare `create_react_agent` di LangGraph. È lo stesso che il `platform_sdk` usa internamente.

### Cos'è un agente ReAct?

Un agente **ReAct** (Reasoning + Acting) segue questo ciclo:

```
     ┌──────────────────────────────────┐
     │                                  │
     ▼                                  │
  RAGIONA → AGISCE (chiama tool) → OSSERVA il risultato
     │
     ▼
  RISPONDE (quando ha abbastanza informazioni)
```

### Esempio completo

```python
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from platform_sdk.llm import get_llm
from platform_sdk.database import db

# --- 1. Definisci i tool ---

@tool
def cerca_corsi(query: str) -> str:
    """Cerca corsi nel catalogo formativo."""
    risultati = db.esegui(
        "SELECT titolo, livello, durata_ore FROM courses WHERE titolo LIKE ?",
        [f"%{query}%"]
    )
    if not risultati:
        return f"Nessun corso trovato per '{query}'"
    return str(risultati)


@tool
def conta_utenti() -> str:
    """Conta gli utenti registrati."""
    n = db.conta("users")
    return f"Ci sono {n} utenti."


# --- 2. Crea l'agente ---

llm = get_llm()

agente = create_react_agent(
    model=llm,
    tools=[cerca_corsi, conta_utenti],
    prompt="Sei un assistente della piattaforma LearnAI. Rispondi sempre in italiano.",
)

# --- 3. Usa l'agente ---

risultato = agente.invoke(
    {"messages": [{"role": "user", "content": "Ci sono corsi su Python?"}]},
    config={"configurable": {"thread_id": "conversazione_1"}},
)

# Estrai l'ultimo messaggio (la risposta dell'agente)
ultimo_messaggio = risultato["messages"][-1]
print(ultimo_messaggio.content)
```

### Aggiungere la memoria (ricordare la conversazione)

```python
from langgraph.checkpoint.memory import InMemorySaver

# La memoria salva lo stato della conversazione
memoria = InMemorySaver()

agente = create_react_agent(
    model=llm,
    tools=[cerca_corsi, conta_utenti],
    prompt="Sei un assistente della piattaforma LearnAI. Rispondi in italiano.",
    checkpointer=memoria,  # ← aggiunge la memoria
)

# Prima domanda
config = {"configurable": {"thread_id": "sessione_1"}}

risultato1 = agente.invoke(
    {"messages": [{"role": "user", "content": "Cerco corsi su Python"}]},
    config=config,
)

# Seconda domanda — l'agente ricorda la prima!
risultato2 = agente.invoke(
    {"messages": [{"role": "user", "content": "Ce ne sono anche su SQL?"}]},
    config=config,  # ← stesso thread_id = stessa conversazione
)
```

> Il `thread_id` identifica una conversazione. Usate lo stesso per continuare la stessa conversazione, uno diverso per iniziarne una nuova.

### Streaming dell'agente in Streamlit

```python
import streamlit as st
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from platform_sdk.llm import get_llm
from platform_sdk.database import db

# --- Tool ---
@tool
def cerca_corsi(query: str) -> str:
    """Cerca corsi nel catalogo formativo."""
    risultati = db.trova_tutti("courses")
    return str(risultati[:5])  # massimo 5 risultati


# --- Inizializzazione (una sola volta) ---
if "agente" not in st.session_state:
    llm = get_llm()
    memoria = InMemorySaver()
    st.session_state.agente = create_react_agent(
        model=llm,
        tools=[cerca_corsi],
        prompt="Sei un assistente AI. Rispondi in italiano.",
        checkpointer=memoria,
    )

if "messaggi_chat" not in st.session_state:
    st.session_state.messaggi_chat = []

# --- Mostra la cronologia ---
for msg in st.session_state.messaggi_chat:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- Input utente ---
if domanda := st.chat_input("Chiedi qualcosa..."):
    # Mostra il messaggio dell'utente
    st.session_state.messaggi_chat.append({"role": "user", "content": domanda})
    with st.chat_message("user"):
        st.write(domanda)

    # Esegui l'agente con streaming
    config = {"configurable": {"thread_id": "streamlit_session"}}

    with st.chat_message("assistant"):
        risposta_completa = ""
        placeholder = st.empty()

        for evento in st.session_state.agente.stream(
            {"messages": [{"role": "user", "content": domanda}]},
            config=config,
            stream_mode="messages",
        ):
            messaggio, metadata = evento
            # Mostra solo i messaggi dell'AI (non i tool)
            if hasattr(messaggio, "content") and messaggio.type == "ai":
                if isinstance(messaggio.content, str) and messaggio.content:
                    risposta_completa += messaggio.content
                    placeholder.write(risposta_completa)

    st.session_state.messaggi_chat.append({"role": "assistant", "content": risposta_completa})
```

---

## 🏗️ Creare un agente custom con il Graph API

Per il massimo controllo, potete costruire il vostro agente da zero usando il **Graph API** di LangGraph. Questo vi permette di definire esattamente i passi che l'agente segue.

### Concetti chiave

| Concetto | Cosa fa | Analogia |
|----------|---------|----------|
| **State** | I dati che l'agente ricorda tra un passo e l'altro | La "memoria di lavoro" |
| **Node** | Una funzione che fa qualcosa (es: chiama il modello, esegue un tool) | Un "passo" del processo |
| **Edge** | Un collegamento tra due nodi | Una "freccia" nel diagramma di flusso |
| **Conditional Edge** | Un collegamento che dipende da una condizione | Un "bivio" nel flusso |

### Esempio: agente calcolatrice

```python
import operator
from typing import Annotated, Literal

from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

from platform_sdk.llm import get_llm


# ============================================================
# PASSO 1: Definisci i tool
# ============================================================

@tool
def somma(a: int, b: int) -> int:
    """Somma due numeri.

    Args:
        a: primo numero
        b: secondo numero
    """
    return a + b


@tool
def moltiplica(a: int, b: int) -> int:
    """Moltiplica due numeri.

    Args:
        a: primo numero
        b: secondo numero
    """
    return a * b


# ============================================================
# PASSO 2: Definisci lo stato del grafo
# ============================================================

class StatoAgente(TypedDict):
    # Annotated[..., operator.add] significa: i nuovi messaggi vengono
    # AGGIUNTI alla lista, non la sostituiscono
    messages: Annotated[list[AnyMessage], operator.add]


# ============================================================
# PASSO 3: Prepara il modello con i tool
# ============================================================

llm = get_llm()
tools = [somma, moltiplica]
tools_per_nome = {t.name: t for t in tools}
llm_con_tools = llm.bind_tools(tools)


# ============================================================
# PASSO 4: Definisci i nodi (le funzioni)
# ============================================================

def nodo_modello(state: dict):
    """Chiama il modello. Il modello decide se usare un tool o rispondere."""
    messaggi = [
        SystemMessage(content="Sei un assistente che fa calcoli. Rispondi in italiano.")
    ] + state["messages"]

    risposta = llm_con_tools.invoke(messaggi)

    return {"messages": [risposta]}


def nodo_tool(state: dict):
    """Esegue i tool richiesti dal modello e restituisce i risultati."""
    risultati = []

    # L'ultimo messaggio contiene le richieste di tool
    for chiamata in state["messages"][-1].tool_calls:
        nome_tool = chiamata["name"]
        argomenti = chiamata["args"]

        # Esegui il tool
        tool_da_eseguire = tools_per_nome[nome_tool]
        risultato = tool_da_eseguire.invoke(argomenti)

        # Crea un ToolMessage con il risultato
        risultati.append(
            ToolMessage(content=str(risultato), tool_call_id=chiamata["id"])
        )

    return {"messages": risultati}


# ============================================================
# PASSO 5: Definisci la logica di routing
# ============================================================

def decidi_prossimo_passo(state: StatoAgente) -> Literal["nodo_tool", "__end__"]:
    """Decide se continuare (eseguire tool) o fermarsi (rispondere)."""
    ultimo_messaggio = state["messages"][-1]

    # Se il modello ha chiesto di usare un tool → vai al nodo_tool
    if ultimo_messaggio.tool_calls:
        return "nodo_tool"

    # Altrimenti → fine (il modello ha dato la risposta finale)
    return END


# ============================================================
# PASSO 6: Costruisci e compila il grafo
# ============================================================

# Crea il grafo
grafo = StateGraph(StatoAgente)

# Aggiungi i nodi
grafo.add_node("nodo_modello", nodo_modello)
grafo.add_node("nodo_tool", nodo_tool)

# Aggiungi gli archi
grafo.add_edge(START, "nodo_modello")              # Inizio → Modello
grafo.add_conditional_edges(                         # Modello → Tool o Fine
    "nodo_modello",
    decidi_prossimo_passo,
    ["nodo_tool", END],
)
grafo.add_edge("nodo_tool", "nodo_modello")          # Tool → Modello (torna a ragionare)

# Compila
agente = grafo.compile()


# ============================================================
# PASSO 7: Usa l'agente
# ============================================================

risultato = agente.invoke({
    "messages": [HumanMessage(content="Quanto fa 15 per 7, e poi aggiungi 33?")]
})

# Stampa tutti i messaggi per vedere il ragionamento
for msg in risultato["messages"]:
    if hasattr(msg, "pretty_print"):
        msg.pretty_print()
```

**Come funziona il flusso:**

```
START
  │
  ▼
nodo_modello ──────────────────────────────────┐
  │                                            │
  │ (il modello vuole usare un tool?)          │
  │                                            │
  ├── SÌ ──► nodo_tool ──► torna a nodo_modello
  │
  └── NO ──► END (risponde all'utente)
```

---

## 📦 Output strutturato (JSON)

Se avete bisogno che il modello risponda in un formato JSON preciso, potete usare `with_structured_output()` di LangChain.

### Con Pydantic (consigliato)

```python
from pydantic import BaseModel, Field
from platform_sdk.llm import get_llm

# Definisci la struttura della risposta
class Corso(BaseModel):
    """Un corso formativo."""
    titolo: str = Field(description="Il titolo del corso")
    durata_ore: int = Field(description="La durata in ore")
    livello: str = Field(description="Il livello: base, intermedio, avanzato")


class PianoFormativo(BaseModel):
    """Un piano formativo con una lista di corsi."""
    corsi: list[Corso] = Field(description="La lista dei corsi consigliati")
    durata_totale_settimane: int = Field(description="La durata totale in settimane")


llm = get_llm()

# Crea un modello che restituisce SEMPRE un oggetto PianoFormativo
llm_strutturato = llm.with_structured_output(PianoFormativo)

risultato = llm_strutturato.invoke(
    "Crea un piano formativo per un junior data analyst. Includi 3 corsi."
)

# risultato è un oggetto PianoFormativo, non una stringa!
print(risultato.corsi[0].titolo)          # → "Introduzione a Python"
print(risultato.durata_totale_settimane)   # → 8
```

### Con un dizionario TypedDict (alternativa più semplice)

```python
from typing_extensions import TypedDict

class InfoCorso(TypedDict):
    titolo: str
    livello: str
    durata_ore: int

llm_strutturato = llm.with_structured_output(InfoCorso)
risultato = llm_strutturato.invoke("Descrivi un corso di Python base")

# risultato è un dizionario Python
print(risultato["titolo"])
```

> **Differenza con `genera_json()` del SDK**: il metodo SDK usa un approccio basato su prompt (chiede al modello di restituire JSON e poi lo parsa). `with_structured_output()` di LangChain usa le API native del modello per garantire che l'output sia sempre nel formato corretto — è più affidabile.

---

## 📊 Tabella di confronto SDK vs diretto

| Cosa volete fare | Con il `platform_sdk` | Con LangChain/LangGraph direttamente |
|------------------|----------------------|--------------------------------------|
| Domanda semplice | `chiedi("domanda")` | `llm.invoke([HumanMessage("domanda")])` |
| Con contesto | `chiedi_con_contesto(d, c, i)` | `llm.invoke([SystemMessage(i), HumanMessage(c + d)])` |
| Risposta veloce | `chiedi_veloce("domanda")` | `get_llm(veloce=True).invoke([HumanMessage("domanda")])` |
| Chat multi-turn | `chat(messaggi, system)` | `llm.invoke([SystemMessage(system)] + messaggi)` |
| Streaming | `chat_stream(messaggi)` | `llm.stream(messaggi)` |
| JSON strutturato | `genera_json(prompt, schema)` | `llm.with_structured_output(MySchema).invoke(prompt)` |
| Creare un agente | `crea_agente(tools, prompt)` | `create_react_agent(model=llm, tools=tools, prompt=prompt)` |
| Eseguire un agente | `esegui_agente(agente, msg)` | `agente.invoke({"messages": [{"role": "user", "content": msg}]})` |

---

## 📚 Risorse utili

| Risorsa | Link | Descrizione |
|---------|------|-------------|
| **LangChain Docs** | [docs.langchain.com](https://docs.langchain.com/oss/python/langchain/overview) | Documentazione ufficiale di LangChain |
| **LangGraph Docs** | [docs.langchain.com/langgraph](https://docs.langchain.com/oss/python/langgraph/overview) | Documentazione ufficiale di LangGraph |
| **LangGraph Quickstart** | [Quickstart](https://docs.langchain.com/oss/python/langgraph/quickstart) | Tutorial passo-passo per creare un agente |
| **LangChain Agents** | [Agents](https://docs.langchain.com/oss/python/langchain/agents) | Guida completa agli agenti LangChain |
| **LangChain Models** | [Models](https://docs.langchain.com/oss/python/langchain/models) | Come usare i modelli (invoke, stream, tool calling) |
| **LangChain Tools** | [Tools](https://docs.langchain.com/oss/python/langchain/tools) | Come creare e usare tool personalizzati |
| **LangChain AWS** | [langchain-aws](https://docs.langchain.com/oss/python/integrations/chat/bedrock) | Integrazione con AWS Bedrock |

---

## 💡 Consigli finali

1. **Partite dal semplice**: usate `get_llm()` del SDK per ottenere il modello, poi usatelo con le API LangChain
2. **Per agenti semplici**: `create_react_agent` è sufficiente nella maggior parte dei casi
3. **Per agenti custom**: usate il Graph API solo quando avete bisogno di un flusso personalizzato
4. **Testate i tool da soli**: prima di metterli in un agente, verificate che funzionino con `.invoke()`
5. **Un buon docstring è tutto**: l'AI decide quale tool usare basandosi SOLO sulla descrizione. Scrivetela bene!
