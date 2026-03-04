-- ============================================================================
-- LearnAI Platform — Schema Database Condiviso
-- Tutte le tabelle usate dai 7 moduli della piattaforma.
-- Ogni gruppo usa solo le tabelle rilevanti per il proprio modulo.
-- ============================================================================

-- === UTENTI ===
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cognome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    ruolo TEXT,                          -- es: "Studente", "Docente", "Admin"
    dipartimento TEXT,                   -- es: "Economia", "Fisica", "Medicina"
    data_assunzione DATE,
    cv_testo TEXT,                       -- Testo estratto dal CV
    profilo_json TEXT,                   -- JSON: competenze, interessi, obiettivi
    creato_il TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- === COMPETENZE ===
CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    categoria TEXT,                      -- "Technical", "Soft", "Domain"
    descrizione TEXT
);

CREATE TABLE IF NOT EXISTS user_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    skill_id INTEGER REFERENCES skills(id),
    livello_attuale INTEGER CHECK(livello_attuale BETWEEN 1 AND 5),
    livello_target INTEGER CHECK(livello_target BETWEEN 1 AND 5),
    valutato_il TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- === CATALOGO CORSI ===
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titolo TEXT NOT NULL,
    descrizione TEXT,
    categoria TEXT,                      -- "Data Science", "Business", "Cardiologia"
    durata_ore INTEGER,
    livello TEXT CHECK(livello IN ('base', 'intermedio', 'avanzato')),
    prerequisiti_json TEXT,              -- JSON: lista di course_id richiesti
    contenuto_json TEXT,                 -- JSON: moduli, argomenti, obiettivi
    creato_il TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- === ASSESSMENT ===
CREATE TABLE IF NOT EXISTS assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    tipo TEXT,                           -- "iniziale", "quiz", "intermedio", "finale"
    domande_json TEXT,                   -- JSON: domande e risposte
    risultati_json TEXT,                 -- JSON: punteggi per area
    aspirazioni_json TEXT,               -- JSON: obiettivi breve/medio/lungo termine
    creato_il TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- === PIANI FORMATIVI ===
CREATE TABLE IF NOT EXISTS training_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    nome TEXT,
    orizzonte TEXT CHECK(orizzonte IN ('breve', 'medio', 'lungo')),
    stato TEXT DEFAULT 'bozza' CHECK(stato IN ('bozza', 'attivo', 'completato', 'sospeso')),
    note_ai TEXT,
    creato_il TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aggiornato_il TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS training_plan_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER REFERENCES training_plans(id),
    course_id INTEGER REFERENCES courses(id),
    ordine INTEGER,
    stato TEXT DEFAULT 'da_iniziare'
        CHECK(stato IN ('da_iniziare', 'in_corso', 'completato', 'saltato')),
    data_inizio_prevista DATE,
    data_fine_prevista DATE,
    data_inizio_effettiva DATE,
    data_completamento DATE,
    progresso INTEGER DEFAULT 0 CHECK(progresso BETWEEN 0 AND 100),
    voto INTEGER CHECK(voto BETWEEN 1 AND 100)
);

-- === MODIFICHE AL PIANO ===
CREATE TABLE IF NOT EXISTS plan_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER REFERENCES training_plans(id),
    user_id INTEGER REFERENCES users(id),
    tipo_modifica TEXT,                  -- "aggiunta", "rimozione", "rischedulazione", "sostituzione"
    dettagli_json TEXT,
    motivazione TEXT,
    creato_il TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- === MONITORAGGIO ===
CREATE TABLE IF NOT EXISTS progress_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    plan_item_id INTEGER REFERENCES training_plan_items(id),
    evento TEXT,                         -- "iniziato", "completato", "in_ritardo", "abbandonato"
    dettagli TEXT,
    creato_il TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    tipo TEXT,                           -- "promemoria", "ritardo", "completamento", "suggerimento"
    titolo TEXT,
    messaggio TEXT,
    letto INTEGER DEFAULT 0,
    creato_il TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- === SURVEY ===
CREATE TABLE IF NOT EXISTS surveys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    course_id INTEGER REFERENCES courses(id),
    tipo TEXT,                           -- "gradimento_corso", "piattaforma", "periodico"
    domande_json TEXT,
    risposte_json TEXT,
    sentiment_score REAL,               -- -1.0 a 1.0
    aree_miglioramento_json TEXT,
    creato_il TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- === SKILL GAP ===
CREATE TABLE IF NOT EXISTS skill_gap_analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    ruolo_target TEXT,
    gap_json TEXT,
    raccomandazioni_json TEXT,
    punteggio_prontezza INTEGER CHECK(punteggio_prontezza BETWEEN 0 AND 100),
    creato_il TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Aggiunta del riferimento al docente nel corso
ALTER TABLE courses ADD COLUMN docente_id INTEGER REFERENCES users(id);

-- === MATERIALI DIDATTICI (Fonte di verità per il RAG) ===
CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER REFERENCES courses(id),
    docente_id INTEGER REFERENCES users(id),
    titolo_file TEXT NOT NULL,
    tipo_file TEXT CHECK(tipo_file IN ('PDF', 'Video', 'Audio', 'Slide')),
    s3_key TEXT NOT NULL,                -- Percorso del file su Amazon S3
    testo_estratto TEXT,                 -- Testo parsato via PyPDF2 per il RAG
    caricato_il TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);