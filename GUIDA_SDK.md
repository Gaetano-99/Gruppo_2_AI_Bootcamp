# 📖 Guida all'SDK — LearnAI Platform

Questa guida spiega come usare le funzioni dell'SDK per interagire con l'AI e il database.

---

## 🏗️ Struttura del progetto

```
learnai-modulo-XX/
├── app.py                    ← Pagina principale (la modificate voi)
├── pages/                    ← Pagine aggiuntive Streamlit
│   ├── 01_💬_Chat_AI.py      ← Esempio di chatbot
│   ├── 02_🗄️_Database.py    ← Esempio CRUD database
│   └── 03_🤖_Agente_AI.py   ← Esempio agente con tool
├── config.py                 ← Configurazione (NON modificare)
├── platform_sdk/             ← SDK (NON modificare)
│   ├── llm.py                ← Funzioni per l'AI
│   ├── database.py           ← Funzioni per il database
│   ├── agent.py              ← Funzioni per creare agenti
│   └── utils.py              ← Utilità varie
├── database/
│   ├── schema.sql            ← Struttura tabelle
│   └── seed.sql              ← Dati iniziali
└── data/
    └── knowledge_base/       ← I vostri dati e documenti
```

---

## 🤖 Funzioni AI (`platform_sdk.llm`)

### `chiedi(prompt)` — Domanda semplice
```python
from platform_sdk.llm import chiedi

risposta = chiedi("Quali competenze servono per un data analyst?")
print(risposta)
```

### `chiedi_veloce(prompt)` — Risposta veloce (modello economico)
```python
from platform_sdk.llm import chiedi_veloce

categoria = chiedi_veloce("Classifica 'Python': Technical, Soft o Domain? Rispondi con una sola parola.")
```

### `chiedi_con_contesto(domanda, contesto, istruzioni)` — Con contesto
```python
from platform_sdk.llm import chiedi_con_contesto

risposta = chiedi_con_contesto(
    domanda="Quali corsi mi consigli?",
    contesto="L'utente è un junior analyst con competenze in Excel e SQL base.",
    istruzioni="Suggerisci massimo 3 corsi. Rispondi in italiano."
)
```

### `genera_json(prompt, schema)` — Output JSON strutturato
```python
from platform_sdk.llm import genera_json

piano = genera_json(
    prompt="Crea un piano formativo per un junior data analyst",
    schema={
        "corsi": [{"titolo": "str", "durata_ore": "int", "priorita": "str"}],
        "durata_totale_settimane": "int"
    },
    istruzioni="Rispondi in italiano"
)
# piano è un dizionario Python!
print(piano["corsi"][0]["titolo"])
```

### `chat(messaggi, system_prompt)` — Conversazione multi-turn
```python
from platform_sdk.llm import chat

storia = [
    {"role": "user", "content": "Ciao! Sono Marco, nuovo in azienda."},
    {"role": "assistant", "content": "Benvenuto Marco! Come posso aiutarti?"},
    {"role": "user", "content": "Vorrei capire quali corsi seguire."},
]

risposta = chat(storia, system_prompt="Sei il chatbot di onboarding di LearnAI.")
```

### `chat_stream(messaggi, system_prompt)` — Chat con streaming
```python
# Dentro Streamlit
from platform_sdk.llm import chat_stream

with st.chat_message("assistant"):
    risposta = st.write_stream(
        chat_stream(messaggi, system_prompt="Sei un tutor AI.")
    )
```

### `analizza_documento(testo, istruzioni)` — Analisi testo lungo
```python
from platform_sdk.llm import analizza_documento

risultato = analizza_documento(
    testo_documento="Mario Rossi, laureato in economia...",
    istruzioni="Estrai: nome, cognome, competenze. Rispondi in JSON."
)
```

### `estrai_testo_da_upload(file)` — Legge un file caricato
Supporta file `.txt`, `.md`, `.csv`, `.pdf`, `.xls` e `.xlsx`.
```python
from platform_sdk.llm import estrai_testo_da_upload

file = st.file_uploader("Carica un file", type=["txt", "pdf", "csv", "xls", "xlsx"])
if file:
    testo = estrai_testo_da_upload(file)
```

---

## 🗄️ Funzioni Database (`platform_sdk.database`)

```python
from platform_sdk.database import db
```

### Inserire dati
```python
# Inserisci una riga
user_id = db.inserisci("users", {
    "nome": "Mario",
    "cognome": "Rossi",
    "email": "m.rossi@test.it",
    "ruolo": "Junior Analyst"
})

# Inserisci più righe
db.inserisci_molti("user_skills", [
    {"user_id": 1, "skill_id": 1, "livello_attuale": 3},
    {"user_id": 1, "skill_id": 2, "livello_attuale": 2},
])
```

### Leggere dati
```python
# Trova un utente specifico
utente = db.trova_uno("users", {"id": 1})
print(utente["nome"])  # → "Marco"

# Trova tutti gli utenti di un dipartimento
utenti_it = db.trova_tutti("users", {"dipartimento": "IT"})

# Conta le righe
n = db.conta("courses")
```

### Aggiornare dati
```python
db.aggiorna("users", {"id": 1}, {"ruolo": "Senior Analyst"})
```

### Eliminare dati
```python
db.elimina("notifications", {"user_id": 1, "letto": 1})
```

### Query SQL personalizzate
```python
risultati = db.esegui(
    "SELECT u.nome, c.titolo FROM training_plan_items tpi "
    "JOIN training_plans tp ON tpi.plan_id = tp.id "
    "JOIN users u ON tp.user_id = u.id "
    "JOIN courses c ON tpi.course_id = c.id "
    "WHERE tpi.stato = ?",
    ["in_corso"]
)
```

### Salvare dati JSON
```python
# Potete passare dizionari Python — verranno convertiti automaticamente in JSON
db.inserisci("assessments", {
    "user_id": 1,
    "tipo": "iniziale",
    "domande_json": [{"domanda": "...", "risposta": "..."}],  # ← dizionario Python
    "risultati_json": {"punteggio": 85}
})
```

---

## 🤖 Creare un Agente LangGraph (`platform_sdk.agent`)

Un agente è un'AI che può usare **strumenti (tool)** per rispondere.

### Passo 1: Definire i tool
```python
from langchain_core.tools import tool
from platform_sdk.database import db

@tool
def cerca_corsi(query: str) -> str:
    """Cerca corsi nel catalogo formativo.
    Usa questo strumento quando l'utente chiede di corsi o formazione."""
    risultati = db.esegui(
        "SELECT titolo, livello, durata_ore FROM courses WHERE titolo LIKE ?",
        [f"%{query}%"]
    )
    return str(risultati)

@tool
def salva_nota(user_id: int, nota: str) -> str:
    """Salva una nota per un utente."""
    db.aggiorna("users", {"id": user_id}, {"profilo_json": nota})
    return f"Nota salvata per utente {user_id}"
```

### Passo 2: Creare l'agente
```python
from platform_sdk.agent import crea_agente, esegui_agente

agente = crea_agente(
    tools=[cerca_corsi, salva_nota],
    system_prompt="Sei un assistente formativo. Rispondi in italiano."
)
```

### Passo 3: Usare l'agente
```python
risposta = esegui_agente(agente, "Cerco corsi su Python")
print(risposta)
```

### In Streamlit
```python
# Crea l'agente una sola volta
if "agente" not in st.session_state:
    st.session_state.agente = crea_agente(tools=[...], system_prompt="...")

# Usa l'agente
if domanda := st.chat_input("Chiedi all'agente..."):
    risposta = esegui_agente(st.session_state.agente, domanda)
    st.write(risposta)
```

---

## 📋 Tabelle del Database

| Tabella | Descrizione |
|---------|-------------|
| `users` | Profili utenti (nome, ruolo, dipartimento, CV, profilo JSON) |
| `skills` | Catalogo competenze (Python, SQL, Leadership...) |
| `user_skills` | Livello di ogni competenza per ogni utente (1-5) |
| `courses` | Catalogo corsi con descrizioni e prerequisiti |
| `assessments` | Assessment e quiz con domande e risultati |
| `training_plans` | Piani formativi (breve/medio/lungo termine) |
| `training_plan_items` | Singoli corsi nei piani con date e stato |
| `plan_changes` | Storico modifiche ai piani |
| `progress_log` | Log eventi di avanzamento |
| `notifications` | Alert e notifiche generate dall'AI |
| `surveys` | Survey compilate con risposte e sentiment |
| `skill_gap_analyses` | Analisi gap competenze vs ruolo target |

---

## 🎨 Componenti Streamlit più utili

```python
# Metriche
st.metric("👥 Utenti", 42, delta="+5")

# Colonne
col1, col2 = st.columns(2)
col1.write("Sinistra")
col2.write("Destra")

# Tab
tab1, tab2 = st.tabs(["📊 Grafici", "📋 Tabella"])

# Form
with st.form("mio_form"):
    nome = st.text_input("Nome")
    livello = st.slider("Livello", 1, 5, 3)
    if st.form_submit_button("Salva"):
        st.write(f"Salvato: {nome} livello {livello}")

# Expander
with st.expander("Dettagli"):
    st.write("Contenuto nascosto")

# Chat
if msg := st.chat_input("Scrivi..."):
    with st.chat_message("user"):
        st.write(msg)

# Spinner
with st.spinner("Caricamento..."):
    import time; time.sleep(2)

# Stato
st.success("Fatto!")
st.warning("Attenzione!")
st.error("Errore!")
st.info("Info")
```

---

## ❓ FAQ

**Come faccio a ricordare dati tra un click e l'altro?**
Usa `st.session_state`:
```python
if "contatore" not in st.session_state:
    st.session_state.contatore = 0
st.session_state.contatore += 1
```

**Come mostro un grafico?**
```python
import plotly.express as px
fig = px.bar(dataframe, x="colonna_x", y="colonna_y")
st.plotly_chart(fig)
```

**Come faccio il refresh della pagina?**
```python
st.rerun()
```
