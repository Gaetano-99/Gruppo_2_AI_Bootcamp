# ============================================================================
# LearnAI Platform — Pagina di esempio: Genera JSON
# Playground per sperimentare con l'output JSON strutturato dell'AI.
# Questa è la funzione che userete di più! Provatela con diversi prompt e schema.
# ============================================================================

import json
import streamlit as st

st.set_page_config(page_title="🧪 Genera JSON", page_icon="🧪", layout="wide")

st.title("🧪 Playground — Genera JSON")
st.caption(
    "Sperimenta con `genera_json()`: dai un prompt e uno schema all'AI, "
    "e ottieni un output JSON strutturato. Questa funzione è fondamentale per il vostro modulo!"
)

# --- Sidebar con template pre-costruiti ---
with st.sidebar:
    st.markdown("### 📋 Template pronti")
    st.markdown("Seleziona un template per provare subito:")

    template = st.radio(
        "Scegli un esempio:",
        [
            "✏️ Personalizzato (scrivi tu)",
            "📄 Estrai dati da CV",
            "📚 Genera piano formativo",
            "❓ Genera quiz",
            "📊 Genera survey",
            "🎯 Analisi skill gap",
        ],
        index=0,
    )

# --- Template predefiniti ---
TEMPLATES = {
    "📄 Estrai dati da CV": {
        "prompt": """Analizza questo CV ed estrai le informazioni richieste.

CV:
Marco Bianchi, 26 anni, laureato in Economia e Management presso l'Università Federico II di Napoli.
Ha lavorato per 2 anni come Junior Analyst presso Deloitte, occupandosi di analisi dati con Excel e SQL.
Conosce Python a livello base, ha certificazione Google Data Analytics.
Parla italiano (madrelingua) e inglese (B2). Appassionato di data visualization e machine learning.""",
        "schema": """{
    "nome": "str",
    "cognome": "str",
    "eta": "int",
    "formazione": [
        {"titolo": "str", "istituto": "str"}
    ],
    "esperienze": [
        {"ruolo": "str", "azienda": "str", "durata": "str"}
    ],
    "competenze_tecniche": ["str"],
    "certificazioni": ["str"],
    "lingue": [
        {"lingua": "str", "livello": "str"}
    ]
}""",
        "istruzioni": "Estrai i dati dal CV in modo preciso. Rispondi in italiano.",
    },
    "📚 Genera piano formativo": {
        "prompt": """Crea un piano formativo personalizzato per questo utente:
- Nome: Marco Bianchi
- Ruolo attuale: Junior Data Analyst
- Competenze: Excel (4/5), SQL (2/5), Python (2/5), Statistica (3/5)
- Obiettivo: diventare Senior Data Analyst in 12 mesi
- Disponibilità: 8 ore a settimana

Corsi disponibili:
- [1] Fondamenti di Python (base, 20h)
- [2] SQL per Business (base, 15h)
- [5] Data Visualization con Python (intermedio, 15h, richiede Python)
- [6] Introduzione al Machine Learning (intermedio, 25h, richiede Python e Statistica)
- [11] Python per Data Science (intermedio, 20h, richiede Python)""",
        "schema": """{
    "piano": [
        {
            "ordine": "int",
            "corso_id": "int",
            "titolo": "str",
            "motivazione": "str",
            "data_inizio": "str (YYYY-MM-DD)",
            "data_fine": "str (YYYY-MM-DD)",
            "orizzonte": "str (breve/medio/lungo)"
        }
    ],
    "note": "str",
    "durata_totale_settimane": "int"
}""",
        "istruzioni": "Rispetta i prerequisiti. I corsi base prima di quelli avanzati. Date realistiche a partire da oggi. Rispondi in italiano.",
    },
    "❓ Genera quiz": {
        "prompt": """Genera un quiz di 4 domande sul tema "Fondamenti di SQL".
Il quiz è per un utente di livello base che sta imparando SQL per la prima volta.
Includi domande di tipi diversi: scelta multipla, vero/falso, e risposta aperta.""",
        "schema": """{
    "titolo_quiz": "str",
    "domande": [
        {
            "id": "int",
            "tipo": "str (scelta_multipla | vero_falso | aperta)",
            "domanda": "str",
            "opzioni": ["str (solo per scelta_multipla, altrimenti lista vuota)"],
            "risposta_corretta": "str",
            "spiegazione": "str"
        }
    ]
}""",
        "istruzioni": "Domande chiare e adatte a principianti. Spiegazioni utili per imparare. Rispondi in italiano.",
    },
    "📊 Genera survey": {
        "prompt": """Genera una survey di gradimento per il corso "Fondamenti di Python".
Il corso è di livello base, dura 20 ore, ed è della categoria Data Science.
Genera 5 domande miste: alcune con scala 1-5, alcune a scelta, alcune aperte.""",
        "schema": """{
    "titolo": "str",
    "domande": [
        {
            "id": "int",
            "testo": "str",
            "tipo": "str (scala_1_5 | scelta | aperta)",
            "opzioni": ["str (solo per tipo scelta, altrimenti lista vuota)"]
        }
    ]
}""",
        "istruzioni": "Domande utili per capire la soddisfazione e migliorare il corso. Rispondi in italiano.",
    },
    "🎯 Analisi skill gap": {
        "prompt": """Analizza il gap tra le competenze attuali e quelle richieste per il ruolo target.

COMPETENZE ATTUALI di Marco Bianchi:
- Python: 2/5
- SQL: 2/5
- Statistica: 3/5
- Machine Learning: 1/5
- Data Visualization: 2/5
- Comunicazione: 3/5

COMPETENZE RICHIESTE per "Senior Data Analyst":
- Python: 4/5 (critica)
- SQL: 4/5 (critica)
- Statistica: 4/5 (alta)
- Machine Learning: 3/5 (alta)
- Data Visualization: 4/5 (alta)
- Comunicazione: 3/5 (media)""",
        "schema": """{
    "gap_analysis": [
        {
            "skill": "str",
            "attuale": "int",
            "richiesto": "int",
            "gap": "int",
            "severity": "str (critico | alto | moderato | nessuno)",
            "priorita": "int (1=massima)"
        }
    ],
    "punteggio_prontezza": "int (0-100)",
    "punti_di_forza": ["str"],
    "aree_critiche": ["str"],
    "commento": "str"
}""",
        "istruzioni": "Calcola i gap numerici. Ordina per priorità. Sii oggettivo. Rispondi in italiano.",
    },
}


# --- Area principale ---
col_input, col_output = st.columns([1, 1])

with col_input:
    st.markdown("### 📝 Input")

    # Carica template se selezionato
    if template in TEMPLATES:
        t = TEMPLATES[template]
        default_prompt = t["prompt"]
        default_schema = t["schema"]
        default_istruzioni = t["istruzioni"]
    else:
        default_prompt = "Crea una lista di 3 corsi consigliati per un junior data analyst"
        default_schema = '{\n    "corsi": [\n        {"titolo": "str", "durata_ore": "int", "priorita": "str"}\n    ]\n}'
        default_istruzioni = "Rispondi in italiano"

    prompt = st.text_area(
        "**Prompt** (cosa chiedi all'AI):",
        value=default_prompt,
        height=200,
    )

    schema_str = st.text_area(
        "**Schema JSON** (struttura dell'output atteso):",
        value=default_schema,
        height=200,
    )

    istruzioni = st.text_input(
        "**Istruzioni aggiuntive** (opzionale):",
        value=default_istruzioni,
    )

    genera = st.button("🚀 Genera JSON", type="primary", use_container_width=True)

with col_output:
    st.markdown("### 📤 Output")

    if genera:
        # Valida lo schema
        try:
            schema = json.loads(schema_str)
        except json.JSONDecodeError as e:
            st.error(f"❌ Lo schema JSON non è valido: {e}")
            st.warning("Controlla la sintassi del JSON nello schema.")
            st.stop()

        # Chiama l'AI
        with st.spinner("🤖 L'AI sta generando il JSON..."):
            try:
                from platform_sdk.llm import genera_json

                risultato = genera_json(
                    prompt=prompt,
                    schema=schema,
                    istruzioni=istruzioni,
                )

                # Controlla se c'è un errore di parsing
                if "errore" in risultato:
                    st.warning("⚠️ L'AI ha risposto ma il JSON non è perfetto:")
                    st.code(risultato.get("risposta_grezza", ""), language="text")
                else:
                    st.success("✅ JSON generato con successo!")

                    # Mostra il JSON formattato
                    json_formattato = json.dumps(risultato, indent=2, ensure_ascii=False)
                    st.code(json_formattato, language="json")

                    # Mostra anche come dizionario Python esplorabile
                    with st.expander("🔍 Esplora il risultato come dizionario Python"):
                        st.json(risultato)

                    # Suggerimenti su come usarlo nel codice
                    with st.expander("💻 Come usarlo nel tuo codice"):
                        st.markdown(
                            f"""
```python
from platform_sdk.llm import genera_json

risultato = genera_json(
    prompt=\"\"\"{prompt[:80]}...\"\"\",
    schema={schema_str},
    istruzioni="{istruzioni}"
)

# Accedi ai dati:
# risultato è un dizionario Python normale!
# Esempio: risultato["corsi"][0]["titolo"]
```
"""
                        )

            except Exception as e:
                st.error(f"❌ Errore: {e}")
                st.warning("Controlla le credenziali AWS nel file .env")
    else:
        st.info(
            "👈 Compila il prompt e lo schema, poi clicca **Genera JSON** per vedere il risultato."
        )

        # Mostra un esempio statico per far capire cosa aspettarsi
        st.markdown("**Esempio di output atteso:**")
        esempio = {
            "corsi": [
                {"titolo": "Fondamenti di Python", "durata_ore": 20, "priorita": "alta"},
                {"titolo": "SQL per Business", "durata_ore": 15, "priorita": "alta"},
                {"titolo": "Data Visualization", "durata_ore": 15, "priorita": "media"},
            ]
        }
        st.code(json.dumps(esempio, indent=2, ensure_ascii=False), language="json")
