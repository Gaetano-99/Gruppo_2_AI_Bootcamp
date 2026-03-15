# ============================================================================
# LearnAI Platform — Configurazione centrale
# Questo file contiene tutte le impostazioni del progetto.
# NON modificare questo file direttamente: usare il file .env per i valori
# specifici dell'ambiente (credenziali, percorsi, model ID).
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

# Modello veloce (più economico, per task semplici e classificazioni)
BEDROCK_MODEL_ID_FAST = os.getenv(
    "BEDROCK_MODEL_ID_FAST",
    "anthropic.claude-3-5-haiku-20241022-v1:0"
)

# Modello potente (per task complessi: generazione corsi, structured output grandi)
# Usato quando il contesto è ampio o serve output strutturato di alta qualità.
# Se non configurato, usa il modello principale.
BEDROCK_MODEL_ID_POTENTE = os.getenv(
    "BEDROCK_MODEL_ID_POTENTE",
    os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
)

# --- Parametri LLM ---
LLM_TEMPERATURE = 0.3          # Creatività: 0 = deterministico, 1 = molto creativo
LLM_MAX_TOKENS = 4096          # Lunghezza massima risposta modello principale
LLM_MAX_TOKENS_FAST = 2048     # Lunghezza massima risposta modello veloce
LLM_MAX_TOKENS_POTENTE = 8192  # Lunghezza massima per generazioni complesse

# --- Database SQLite ---
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "database", "learnai.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "database", "Nuovo_schema.sql")
SEED_PATH = os.path.join(os.path.dirname(__file__), "database", "seed.sql")

# --- Storage S3 ---
# I materiali didattici (PDF, slide, video) sono archiviati su Amazon S3.
# Il percorso del file sul DB è salvato in materiali_didattici.s3_key.
# Formato s3_key: "didattica/corsi/{corso_id}/{nome_file}"
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "learnai-materiali-didattici")

# --- Streamlit ---
APP_TITLE = "🎓 LearnAI Platform"
APP_ICON = "🎓"
