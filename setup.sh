#!/usr/bin/env bash
# ============================================================================
# LearnAI Platform — Script di setup per Mac/Linux
# Questo script configura l'ambiente di sviluppo per la piattaforma LearnAI.
# Pensato per studenti al primo approccio con Python.
# ============================================================================

set -e  # Esci immediatamente in caso di errore

# --- Colori per i messaggi ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # Nessun colore

# --- Funzione per stampare errori e uscire ---
errore_e_esci() {
    echo ""
    echo -e "${RED}❌ ERRORE: $1${NC}"
    if [ -n "$2" ]; then
        echo -e "${YELLOW}💡 Suggerimento: $2${NC}"
    fi
    echo ""
    exit 1
}

# --- Funzione per stampare step ---
stampa_step() {
    echo ""
    echo -e "${CYAN}[$1/8]${NC} ${BOLD}$2${NC}"
}

# ============================================================================
# BANNER DI BENVENUTO
# ============================================================================
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                              ║${NC}"
echo -e "${BLUE}║${NC}   🎓  ${BOLD}LearnAI Platform — Setup Ambiente di Sviluppo${NC}   🤖   ${BLUE}║${NC}"
echo -e "${BLUE}║                                                              ║${NC}"
echo -e "${BLUE}║${NC}   Piattaforma di e-learning guidata da Intelligenza         ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}   Artificiale per studenti universitari.                    ${BLUE}║${NC}"
echo -e "${BLUE}║                                                              ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "📂 Cartella progetto: ${BOLD}$(pwd)${NC}"
echo -e "🖥️  Sistema operativo: ${BOLD}$(uname -s) $(uname -m)${NC}"
echo ""

# ============================================================================
# STEP 1 — Verifica Python 3.11+
# ============================================================================
stampa_step 1 "🐍 Verifica installazione Python 3.11+..."

# Cerca il comando python3 disponibile
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi

# Se non è stato trovato nessun comando Python
if [ -z "$PYTHON_CMD" ]; then
    errore_e_esci \
        "Python non è installato o non è nel PATH." \
        "Installa Python 3.11+ da https://www.python.org/downloads/ e riprova."
fi

# Controlla la versione di Python (serve 3.11 o superiore)
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
    errore_e_esci \
        "Python $PYTHON_VERSION trovato, ma serve Python 3.11 o superiore." \
        "Scarica l'ultima versione da https://www.python.org/downloads/ e riprova."
fi

echo -e "   ✅ Python ${GREEN}$PYTHON_VERSION${NC} trovato ($PYTHON_CMD)"

# ============================================================================
# STEP 2 — Verifica pip
# ============================================================================
stampa_step 2 "📦 Verifica disponibilità pip..."

if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    errore_e_esci \
        "pip non è disponibile." \
        "Prova a installarlo con: $PYTHON_CMD -m ensurepip --upgrade"
fi

PIP_VERSION=$($PYTHON_CMD -m pip --version | awk '{print $2}')
echo -e "   ✅ pip ${GREEN}$PIP_VERSION${NC} disponibile"

# ============================================================================
# STEP 3 — Creazione ambiente virtuale (venv)
# ============================================================================
stampa_step 3 "🏗️  Creazione ambiente virtuale (venv)..."

if [ -d "venv" ]; then
    echo -e "   ⚠️  La cartella ${YELLOW}venv/${NC} esiste già — la riutilizzo"
else
    $PYTHON_CMD -m venv venv || errore_e_esci \
        "Impossibile creare l'ambiente virtuale." \
        "Assicurati che il modulo 'venv' sia installato. Su Ubuntu/Debian: sudo apt install python3-venv"
    echo -e "   ✅ Ambiente virtuale creato in ${GREEN}venv/${NC}"
fi

# ============================================================================
# STEP 4 — Attivazione venv
# ============================================================================
stampa_step 4 "🔌 Attivazione ambiente virtuale..."

# shellcheck disable=SC1091
source venv/bin/activate || errore_e_esci \
    "Impossibile attivare l'ambiente virtuale." \
    "Prova manualmente con: source venv/bin/activate"

echo -e "   ✅ Ambiente virtuale ${GREEN}attivato${NC}"

# ============================================================================
# STEP 5 — Aggiornamento pip (silenzioso)
# ============================================================================
stampa_step 5 "⬆️  Aggiornamento pip all'ultima versione..."

pip install --upgrade pip --quiet 2>&1 || errore_e_esci \
    "Impossibile aggiornare pip." \
    "Controlla la tua connessione internet e riprova."

echo -e "   ✅ pip aggiornato con ${GREEN}successo${NC}"

# ============================================================================
# STEP 6 — Installazione dipendenze da requirements.txt
# ============================================================================
stampa_step 6 "📥 Installazione dipendenze da requirements.txt..."

if [ ! -f "requirements.txt" ]; then
    errore_e_esci \
        "Il file requirements.txt non è stato trovato nella cartella corrente." \
        "Assicurati di eseguire lo script dalla root del progetto LearnAI."
fi

pip install -r requirements.txt --quiet 2>&1 || errore_e_esci \
    "Errore durante l'installazione delle dipendenze." \
    "Controlla la connessione internet e che requirements.txt sia corretto."

echo -e "   ✅ Tutte le dipendenze installate con ${GREEN}successo${NC}"

# ============================================================================
# STEP 7 — Configurazione file .env e cartelle
# ============================================================================
stampa_step 7 "⚙️  Configurazione ambiente e cartelle..."

# --- File .env ---
if [ -f ".env" ]; then
    echo -e "   ⚠️  Il file ${YELLOW}.env${NC} esiste già — non verrà sovrascritto"
else
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "   ✅ File ${GREEN}.env${NC} creato da .env.example"
        echo ""
        echo -e "   ${YELLOW}⚠️  ATTENZIONE: Devi inserire le tue credenziali AWS nel file .env!${NC}"
        echo -e "   ${YELLOW}   Apri il file .env e sostituisci i valori segnaposto con le${NC}"
        echo -e "   ${YELLOW}   credenziali fornite dal docente.${NC}"
        echo ""
    else
        echo -e "   ⚠️  File ${YELLOW}.env.example${NC} non trovato — il file .env non è stato creato"
        echo -e "   ${YELLOW}💡 Crea manualmente un file .env con le credenziali AWS${NC}"
    fi
fi

# --- Cartelle necessarie ---
for DIR in "data/knowledge_base" "database"; do
    if [ ! -d "$DIR" ]; then
        mkdir -p "$DIR"
        echo -e "   ✅ Cartella ${GREEN}$DIR/${NC} creata"
    else
        echo -e "   ⚠️  Cartella ${YELLOW}$DIR/${NC} già esistente"
    fi
done

# ============================================================================
# STEP 8 — Inizializzazione database SQLite
# ============================================================================
stampa_step 8 "🗄️  Inizializzazione database SQLite..."

python3 -c "from platform_sdk.database import db; db.init()" 2>/dev/null && {
    echo -e "   ✅ Database SQLite inizializzato con ${GREEN}successo${NC}"
} || {
    echo -e "   ⚠️  ${YELLOW}Inizializzazione database saltata${NC} (il modulo platform_sdk potrebbe non essere ancora disponibile)"
    echo -e "   ${YELLOW}💡 Potrai inizializzarlo in seguito eseguendo:${NC}"
    echo -e "   ${YELLOW}   python3 -c \"from platform_sdk.database import db; db.init()\"${NC}"
}

# ============================================================================
# RIEPILOGO FINALE
# ============================================================================
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}║${NC}   ✅  ${BOLD}Setup completato con successo!${NC}                         ${GREEN}║${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}║${NC}   📋 ${BOLD}Per avviare l'applicazione:${NC}                             ${GREEN}║${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}║${NC}   1️⃣  Attiva l'ambiente virtuale:                           ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}       ${CYAN}source venv/bin/activate${NC}                              ${GREEN}║${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}║${NC}   2️⃣  Avvia l'app Streamlit:                                ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}       ${CYAN}streamlit run app.py${NC}                                   ${GREEN}║${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}║${NC}   ⚠️  Non dimenticare di configurare il file ${YELLOW}.env${NC}          ${GREEN}║${NC}"
echo -e "${GREEN}║${NC}      con le credenziali AWS fornite dal docente!            ${GREEN}║${NC}"
echo -e "${GREEN}║                                                              ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
