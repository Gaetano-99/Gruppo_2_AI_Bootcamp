@echo off
REM ============================================================================
REM LearnAI Platform - Script di setup per Windows
REM Questo script configura l'ambiente di sviluppo per la piattaforma LearnAI.
REM Pensato per studenti al primo approccio con Python.
REM ============================================================================

REM --- Abilita espansione ritardata delle variabili ---
setlocal enabledelayedexpansion

REM --- Codifica UTF-8 per supporto emoji ---
chcp 65001 >nul 2>&1

REM ============================================================================
REM BANNER DI BENVENUTO
REM ============================================================================
echo.
echo ================================================================
echo.
echo    LearnAI Platform - Setup Ambiente di Sviluppo
echo.
echo    Piattaforma di e-learning guidata da Intelligenza
echo    Artificiale per studenti universitari.
echo.
echo ================================================================
echo.
echo    Cartella progetto: %CD%
echo.

REM ============================================================================
REM STEP 1 - Verifica Python 3.11+
REM ============================================================================
echo.
echo [1/8] Verifica installazione Python 3.11+...

REM Cerca il comando python disponibile
where python >nul 2>&1
if errorlevel 1 (
    echo.
    echo    ERRORE: Python non e' installato o non e' nel PATH.
    echo    Suggerimento: Installa Python 3.11+ da https://www.python.org/downloads/
    echo    IMPORTANTE: Durante l'installazione, spunta "Add Python to PATH"
    echo.
    goto :errore
)

REM Controlla la versione di Python (serve 3.11 o superiore)
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
for /f "tokens=1,2 delims=." %%a in ("!PYTHON_VERSION!") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)

if !PYTHON_MAJOR! LSS 3 (
    echo.
    echo    ERRORE: Python !PYTHON_VERSION! trovato, ma serve Python 3.11 o superiore.
    echo    Suggerimento: Scarica l'ultima versione da https://www.python.org/downloads/
    echo.
    goto :errore
)
if !PYTHON_MAJOR! EQU 3 if !PYTHON_MINOR! LSS 11 (
    echo.
    echo    ERRORE: Python !PYTHON_VERSION! trovato, ma serve Python 3.11 o superiore.
    echo    Suggerimento: Scarica l'ultima versione da https://www.python.org/downloads/
    echo.
    goto :errore
)

echo    Python !PYTHON_VERSION! trovato

REM ============================================================================
REM STEP 2 - Verifica pip
REM ============================================================================
echo.
echo [2/8] Verifica disponibilita' pip...

python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo    ERRORE: pip non e' disponibile.
    echo    Suggerimento: Prova a installarlo con: python -m ensurepip --upgrade
    echo.
    goto :errore
)

for /f "tokens=2 delims= " %%v in ('python -m pip --version 2^>^&1') do set PIP_VERSION=%%v
echo    pip !PIP_VERSION! disponibile

REM ============================================================================
REM STEP 3 - Creazione ambiente virtuale (venv)
REM ============================================================================
echo.
echo [3/8] Creazione ambiente virtuale (venv)...

if exist "venv\" (
    echo    La cartella venv\ esiste gia' - la riutilizzo
) else (
    python -m venv venv
    if errorlevel 1 (
        echo.
        echo    ERRORE: Impossibile creare l'ambiente virtuale.
        echo    Suggerimento: Assicurati che il modulo 'venv' sia incluso nella tua installazione Python.
        echo.
        goto :errore
    )
    echo    Ambiente virtuale creato in venv\
)

REM ============================================================================
REM STEP 4 - Attivazione venv
REM ============================================================================
echo.
echo [4/8] Attivazione ambiente virtuale...

if not exist "venv\Scripts\activate.bat" (
    echo.
    echo    ERRORE: Impossibile trovare lo script di attivazione del venv.
    echo    Suggerimento: Elimina la cartella venv e riesegui questo script.
    echo.
    goto :errore
)

call venv\Scripts\activate.bat
if errorlevel 1 (
    echo.
    echo    ERRORE: Impossibile attivare l'ambiente virtuale.
    echo    Suggerimento: Prova manualmente con: venv\Scripts\activate
    echo.
    goto :errore
)

echo    Ambiente virtuale attivato

REM ============================================================================
REM STEP 5 - Aggiornamento pip (silenzioso)
REM ============================================================================
echo.
echo [5/8] Aggiornamento pip all'ultima versione...

pip install --upgrade pip --quiet 2>&1
if errorlevel 1 (
    echo.
    echo    ERRORE: Impossibile aggiornare pip.
    echo    Suggerimento: Controlla la tua connessione internet e riprova.
    echo.
    goto :errore
)

echo    pip aggiornato con successo

REM ============================================================================
REM STEP 6 - Installazione dipendenze da requirements.txt
REM ============================================================================
echo.
echo [6/8] Installazione dipendenze da requirements.txt...

if not exist "requirements.txt" (
    echo.
    echo    ERRORE: Il file requirements.txt non e' stato trovato nella cartella corrente.
    echo    Suggerimento: Assicurati di eseguire lo script dalla root del progetto LearnAI.
    echo.
    goto :errore
)

pip install -r requirements.txt --quiet 2>&1
if errorlevel 1 (
    echo.
    echo    ERRORE: Errore durante l'installazione delle dipendenze.
    echo    Suggerimento: Controlla la connessione internet e che requirements.txt sia corretto.
    echo.
    goto :errore
)

echo    Tutte le dipendenze installate con successo

REM ============================================================================
REM STEP 7 - Configurazione file .env e cartelle
REM ============================================================================
echo.
echo [7/8] Configurazione ambiente e cartelle...

REM --- File .env ---
if exist ".env" (
    echo    Il file .env esiste gia' - non verra' sovrascritto
) else (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo    File .env creato da .env.example
        echo.
        echo    ATTENZIONE: Devi inserire le tue credenziali AWS nel file .env!
        echo    Apri il file .env e sostituisci i valori segnaposto con le
        echo    credenziali fornite dal docente.
        echo.
    ) else (
        echo    File .env.example non trovato - il file .env non e' stato creato
        echo    Suggerimento: Crea manualmente un file .env con le credenziali AWS
    )
)

REM --- Cartelle necessarie ---
if not exist "data\knowledge_base" (
    mkdir "data\knowledge_base"
    echo    Cartella data\knowledge_base\ creata
) else (
    echo    Cartella data\knowledge_base\ gia' esistente
)

if not exist "database" (
    mkdir "database"
    echo    Cartella database\ creata
) else (
    echo    Cartella database\ gia' esistente
)

REM ============================================================================
REM STEP 8 - Inizializzazione database SQLite
REM ============================================================================
echo.
echo [8/8] Inizializzazione database SQLite...

python -c "from platform_sdk.database import db; db.init()" 2>nul
if errorlevel 1 (
    echo    Inizializzazione database saltata (il modulo platform_sdk potrebbe non essere ancora disponibile)
    echo    Suggerimento: Potrai inizializzarlo in seguito eseguendo:
    echo    python -c "from platform_sdk.database import db; db.init()"
) else (
    echo    Database SQLite inizializzato con successo
)

REM ============================================================================
REM RIEPILOGO FINALE
REM ============================================================================
echo.
echo ================================================================
echo.
echo    Setup completato con successo!
echo.
echo ================================================================
echo.
echo    Per avviare l'applicazione:
echo.
echo    1. Attiva l'ambiente virtuale:
echo       venv\Scripts\activate
echo.
echo    2. Avvia l'app Streamlit:
echo       streamlit run app.py
echo.
echo    Non dimenticare di configurare il file .env
echo    con le credenziali AWS fornite dal docente!
echo.
echo ================================================================
echo.

goto :fine

:errore
echo.
echo ================================================================
echo    Il setup NON e' stato completato.
echo    Risolvi l'errore indicato sopra e riesegui lo script.
echo ================================================================
echo.
exit /b 1

:fine
endlocal
exit /b 0