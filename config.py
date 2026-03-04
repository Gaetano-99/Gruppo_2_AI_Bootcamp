# ============================================================================
# LearnAI Platform — Configurazione centrale
# Questo file contiene tutte le impostazioni del progetto.
# Gli studenti NON devono modificare questo file (a meno che non sia richiesto).
# ============================================================================

import os
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# --- Credenziali AWS ---
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", "eu-central-1")

# --- Modelli Bedrock ---
# Modello principale (più intelligente, per task complessi)
BEDROCK_MODEL_ID = os.getenv(
    "BEDROCK_MODEL_ID",
    "anthropic.claude-3-5-sonnet-20241022-v2:0"
)

# Modello veloce (più economico, per task semplici)
BEDROCK_MODEL_ID_FAST = os.getenv(
    "BEDROCK_MODEL_ID_FAST",
    "anthropic.claude-3-5-haiku-20241022-v1:0"
)

# --- Parametri LLM ---
LLM_TEMPERATURE = 0.3          # Creatività: 0 = deterministico, 1 = molto creativo
LLM_MAX_TOKENS = 4096          # Lunghezza massima della risposta
LLM_MAX_TOKENS_FAST = 2048     # Lunghezza massima per il modello veloce

# --- Database ---
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "database", "learnai.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "database", "schema.sql")
SEED_PATH = os.path.join(os.path.dirname(__file__), "database", "seed.sql")

# --- Percorsi ---
KNOWLEDGE_BASE_PATH = os.path.join(os.path.dirname(__file__), "data", "knowledge_base")
SAMPLE_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "sample_data.json")

# --- Streamlit ---
APP_TITLE = "🎓 LearnAI Platform"
APP_ICON = "🎓"
