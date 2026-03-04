# 🎓 LearnAI Platform — Starter Kit

> **Piattaforma di e-learning guidata da Intelligenza Artificiale**
> Laboratorio DIGITA 2026

---

## 📌 Cos'è questo starter kit?

Questo repository è il **punto di partenza** per sviluppare la piattaforma **LearnAI**: un sistema di e-learning che sfrutta l'AI (Claude su AWS Bedrock) per personalizzare la formazione dei dipendenti.

Ogni gruppo riceve una copia di questo starter kit e sviluppa **i moduli a scelta, possono sviluppare tutti o solo alcuni dei moduli** descritti più in basso. L'SDK incluso (`platform_sdk/`) fornisce funzioni pronte all'uso per interagire con l'AI e il database, così potete concentrarvi sulla logica del vostro modulo senza dovervi preoccupare dell'infrastruttura.

**Non serve esperienza di programmazione**: le funzioni dell'SDK sono pensate per essere semplici e intuitive.

---

## 🚀 Setup — Come iniziare

### Prerequisiti

- **Python 3.11** o superiore installato ([download](https://www.python.org/downloads/))
- **Credenziali AWS** fornite dal docente

### Installazione

#### Mac / Linux

Aprite il Terminale, navigate nella cartella del progetto ed eseguite:

```bash
chmod +x setup.sh
./setup.sh
```

#### Windows

Aprite il Prompt dei comandi (cmd), navigate nella cartella del progetto ed eseguite:

```cmd
setup.bat
```

Lo script automaticamente:
1. ✅ Verifica che Python 3.11+ sia installato
2. ✅ Crea un ambiente virtuale (`venv/`)
3. ✅ Installa tutte le dipendenze
4. ✅ Prepara il file `.env` per le credenziali
5. ✅ Crea le cartelle necessarie
6. ✅ Inizializza il database SQLite

### Configurazione credenziali

Dopo il setup, aprite il file `.env` e inserite le credenziali AWS fornite dal docente:

```
AWS_ACCESS_KEY_ID=la_vostra_access_key
AWS_SECRET_ACCESS_KEY=la_vostra_secret_key
```

### Avvio dell'applicazione

```bash
# 1. Attivate l'ambiente virtuale
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 2. Avviate l'app
streamlit run app.py
```

L'applicazione si aprirà nel browser all'indirizzo `http://localhost:8501`.

---

## 🏗️ Struttura del progetto

```
learnai-modulo-XX/
├── app.py                    ← Pagina principale Streamlit
├── pages/                    ← Pagine del menu laterale
│   ├── 01_💬_Chat_AI.py      ← Esempio: chatbot
│   ├── 02_🗄️_Database.py    ← Esempio: operazioni database
│   ├── 03_🤖_Agente_AI.py   ← Esempio: agente con tool
│   └── 04_🧪_Genera_JSON.py ← Esempio: output JSON strutturato
├── config.py                 ← Configurazione (NON modificare)
├── platform_sdk/             ← SDK della piattaforma (NON modificare)
│   ├── llm.py                ← Funzioni per l'AI
│   ├── database.py           ← Funzioni per il database
│   ├── agent.py              ← Funzioni per creare agenti
│   └── utils.py              ← Utilità varie
├── database/
│   ├── schema.sql            ← Struttura tabelle del DB
│   └── seed.sql              ← Dati iniziali di esempio
├── data/
│   └── knowledge_base/       ← I vostri documenti e dati
├── .env                      ← Credenziali AWS (NON condividere!)
├── requirements.txt          ← Dipendenze Python
├── GUIDA_SDK.md              ← Guida dettagliata all'SDK
└── LEGGIMI.md                ← Questo file
```

### ⚠️ Regole importanti

- **NON modificare** `config.py` e la cartella `platform_sdk/`
- **NON condividere** il file `.env` (contiene le credenziali AWS)
- Sviluppate il vostro modulo in `app.py` e nella cartella `pages/`
- Le pagine di esempio (01, 02, 03, 04) sono riferimenti: potete studiarle, copiarle e adattarle

---

## 📚 I 7 Moduli della piattaforma

Tutti i moduli condividono lo stesso database e lo stesso SDK.

### Modulo 1 — 📝 Profilazione e Assessment Iniziale

**Obiettivo:** Raccogliere il profilo del dipendente e valutarne le competenze iniziali.

- Upload e analisi del CV tramite AI
- Questionario interattivo per mappare competenze (hard e soft)
- Assessment iniziale con domande generate dall'AI
- Generazione automatica del profilo utente (JSON)

**Tabelle principali:** `users`, `skills`, `user_skills`, `assessments`

---

### Modulo 2 — 🎯 Skill Gap Analysis

**Obiettivo:** Confrontare le competenze attuali con quelle richieste dal ruolo target.

- Selezione del ruolo target (attuale o aspirazionale)
- Analisi automatica del gap tramite AI
- Visualizzazione radar chart delle competenze vs. obiettivo
- Raccomandazioni AI su priorità di sviluppo

**Tabelle principali:** `users`, `user_skills`, `skills`, `skill_gap_analyses`

---

### Modulo 3 — 📋 Generazione Piano Formativo

**Obiettivo:** Creare piani formativi personalizzati basati sul gap analysis.

- Generazione AI del piano (breve / medio / lungo termine)
- Selezione automatica dei corsi dal catalogo
- Ordinamento intelligente in base a prerequisiti e priorità
- Modifica interattiva del piano generato

**Tabelle principali:** `training_plans`, `training_plan_items`, `courses`, `skill_gap_analyses`

---

### Modulo 4 — 🔄 Gestione Modifiche al Piano

**Obiettivo:** Permettere modifiche al piano formativo con supporto AI.

- Chat con agente AI per richiedere modifiche (aggiunta/rimozione/sostituzione corsi)
- Rischedulazione intelligente
- Storico di tutte le modifiche con motivazioni
- Valutazione AI dell'impatto delle modifiche

**Tabelle principali:** `training_plans`, `training_plan_items`, `plan_changes`, `courses`

---

### Modulo 5 — 📊 Monitoraggio e Dashboard

**Obiettivo:** Monitorare l'avanzamento e generare insight in tempo reale.

- Dashboard con KPI: completamento, ritardi, progressi
- Grafici interattivi (Plotly) su avanzamento individuale e di gruppo
- Alert automatici AI su dipendenti in ritardo
- Report generati dall'AI con suggerimenti

**Tabelle principali:** `progress_log`, `training_plan_items`, `notifications`, `users`

---

### Modulo 6 — 📝 Survey e Feedback Analysis

**Obiettivo:** Raccogliere e analizzare il feedback sui corsi con l'AI.

- Generazione AI di survey personalizzate
- Compilazione interattiva del questionario
- Analisi automatica del sentiment
- Estrazione di aree di miglioramento e trend

**Tabelle principali:** `surveys`, `courses`, `users`

---

### Modulo 7 — 🤖 Tutor AI e Assistente

**Obiettivo:** Fornire un assistente conversazionale che aiuti il dipendente nel suo percorso.

- Chatbot con memoria della conversazione
- Agente AI con accesso a tutti i dati (corsi, piano, progressi)
- Risposte contestualizzate al profilo dell'utente
- Suggerimenti proattivi basati sull'avanzamento

**Tabelle principali:** tutte (l'agente ha accesso all'intero database)

---

## 🧰 Riferimento rapido SDK

```python
# --- AI ---
from platform_sdk.llm import chiedi, chiedi_con_contesto, genera_json, chat, chat_stream

risposta = chiedi("Dimmi le competenze chiave per un data analyst")
json_data = genera_json("Crea un quiz...", schema={...})

# --- Database ---
from platform_sdk.database import db

db.inserisci("users", {"nome": "Mario", "cognome": "Rossi"})
utente = db.trova_uno("users", {"id": 1})
tutti = db.trova_tutti("courses", {"livello": "base"})
db.aggiorna("users", {"id": 1}, {"ruolo": "Senior"})

# --- Agente ---
from platform_sdk.agent import crea_agente, esegui_agente

agente = crea_agente(tools=[...], system_prompt="...")
risposta = esegui_agente(agente, "Quanti utenti ci sono?")
```

Per la documentazione completa di tutte le funzioni, consultate 📖 [GUIDA_SDK.md](GUIDA_SDK.md).

---

## ❓ Problemi comuni

| Problema | Soluzione |
|----------|-----------|
| `ModuleNotFoundError: No module named 'platform_sdk'` | Assicuratevi di essere nella cartella del progetto e di aver attivato il venv |
| `Permission denied` su `setup.sh` | Eseguite `chmod +x setup.sh` e riprovate |
| Errore di connessione all'AI | Controllate le credenziali nel file `.env` |
| Il database è vuoto | Eseguite `python3 -c "from platform_sdk.database import db; db.init()"` |
| `streamlit: command not found` | Attivate il venv: `source venv/bin/activate` |

---

**Buon lavoro! 🚀**
