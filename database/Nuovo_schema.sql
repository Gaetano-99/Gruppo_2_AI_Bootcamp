-- ============================================================================
-- LearnAI Platform — Schema Database
-- Università Federico II / Deloitte — Digita Academy 2025
-- ============================================================================
-- STEP 1: users + struttura universitaria reale
-- STEP 2: quiz e assessment
-- STEP 3: materiali didattici + piani personalizzati AI
-- STEP 4: lezioni dei corsi
--
-- REGOLE GENERALI:
--   ON DELETE CASCADE  → il figlio non ha senso senza il padre
--   ON DELETE RESTRICT → il figlio deve essere gestito prima di eliminare il padre
--   ON DELETE SET NULL → la FK è opzionale, NULL è un valore valido
--
--   OSPITE → nessuna tabella, stato volatile solo in st.session_state
--   ADMIN  → ruolo nella tabella users, record inseriti manualmente
-- ============================================================================

PRAGMA foreign_keys = ON;


-- ============================================================================
-- STEP 1A: TABELLE SENZA DIPENDENZE (definite per prime)
-- ============================================================================

-- corsi_di_laurea prima di users (users.corso_di_laurea_id la referenzia)
CREATE TABLE IF NOT EXISTS corsi_di_laurea (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        TEXT    NOT NULL,               -- es. "Ingegneria Informatica"
    facolta     TEXT    NOT NULL,               -- es. "Ingegneria"
    descrizione TEXT,                           -- descrizione del corso per il catalogo ospiti
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- USERS — Tabella unificata per studenti, docenti e admin.
--
-- Il campo ruolo discrimina il tipo di utente e controlla l'accesso alle pagine.
-- I campi specifici per ruolo sono nullable: ogni utente popola solo i propri.
--
-- Campi per ruolo='studente':
--   data_nascita, telefono, matricola_studente, corso_di_laurea_id, anno_corso
--
-- Campi per ruolo='docente':
--   matricola_docente, dipartimento
--
-- ruolo='admin': nessun campo aggiuntivo, gestione manuale.
--
-- Campi di sicurezza (comuni a tutti i ruoli):
--   tentativi_falliti  → contatore reset a 0 ad ogni login riuscito
--   bloccato_fino_a    → NULL = non bloccato; timestamp = blocco temporaneo
--   last_login         → aggiornato ad ogni autenticazione riuscita
--
-- Logica di blocco (da implementare in db_handler.py):
--   Se tentativi_falliti >= 5 → imposta bloccato_fino_a = now + 15 minuti
--   Ad ogni login: controlla bloccato_fino_a PRIMA di verificare la password
--
-- VINCOLO APPLICATIVO su quiz.studente_id e quiz.docente_id:
--   SQLite non supporta CHECK cross-tabella. Il codice in db_handler.py deve
--   verificare users.ruolo prima di ogni INSERT su tabelle che usano questi FK.
--
-- OSPITE → nessuna riga in questa tabella; stato volatile in st.session_state.
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Campi comuni a tutti i ruoli
    nome                TEXT    NOT NULL,
    cognome             TEXT    NOT NULL,
    email               TEXT    UNIQUE NOT NULL,
    password_hash       TEXT    NOT NULL,
    ruolo               TEXT    NOT NULL
                            CHECK(ruolo IN ('studente', 'docente', 'admin')),
    stato               TEXT    NOT NULL DEFAULT 'active'
                            CHECK(stato IN ('active', 'sospeso')),
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- Sicurezza login (comuni a tutti i ruoli)
    last_login          DATETIME,                -- aggiornato ad ogni login riuscito
    tentativi_falliti   INTEGER NOT NULL DEFAULT 0, -- reset a 0 ad ogni login riuscito
    bloccato_fino_a     DATETIME,                -- NULL = libero; timestamp = bloccato

    -- Campi specifici per ruolo='studente' (NULL se docente o admin)
    data_nascita        TEXT,                    -- formato YYYY-MM-DD
    telefono            TEXT,
    matricola_studente  TEXT    UNIQUE,          -- es. "N86001234"
    corso_di_laurea_id  INTEGER REFERENCES corsi_di_laurea(id)
                            ON DELETE SET NULL,  -- se CDL eliminato, utente rimane
    anno_corso          INTEGER,                 -- 1-5

    -- Campi specifici per ruolo='docente' (NULL se studente o admin)
    matricola_docente   TEXT    UNIQUE,          -- es. "DOC-2021-042"
    dipartimento        TEXT
);


-- ============================================================================
-- STEP 1B: TABELLE CON DIPENDENZE DA users
-- ============================================================================

CREATE TABLE IF NOT EXISTS corsi_universitari (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nome            TEXT    NOT NULL,           -- es. "Basi di Dati"
    descrizione     TEXT,
    docente_id      INTEGER NOT NULL REFERENCES users(id)
                        ON DELETE RESTRICT,     -- non eliminare docente con corsi attivi
    cfu             INTEGER,
    ore_lezione     INTEGER,
    anno_di_corso   INTEGER,                    -- anno consigliato (1-5)
    semestre        INTEGER CHECK(semestre IN (1, 2)),
    livello         TEXT    CHECK(livello IN ('base', 'intermedio', 'avanzato')),
    attivo          INTEGER NOT NULL DEFAULT 1
                        CHECK(attivo IN (0, 1)), -- 0 = disattivato, non eliminare mai
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================================
-- STEP 1C: TABELLE PONTE (N:N)
-- ============================================================================

-- N:N corsi_di_laurea ↔ corsi_universitari
-- obbligatorio: distingue corsi obbligatori da corsi a scelta per quel CDL
CREATE TABLE IF NOT EXISTS corsi_laurea_universitari (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    corso_di_laurea_id      INTEGER NOT NULL REFERENCES corsi_di_laurea(id)
                                ON DELETE CASCADE,  -- CDL eliminato → rimuovi mappature
    corso_universitario_id  INTEGER NOT NULL REFERENCES corsi_universitari(id)
                                ON DELETE CASCADE,  -- corso eliminato → rimuovi mappature
    obbligatorio            INTEGER NOT NULL DEFAULT 1
                                CHECK(obbligatorio IN (0, 1)),
    UNIQUE(corso_di_laurea_id, corso_universitario_id)
);

-- N:N users(studente) ↔ corsi_universitari
-- Traccia iscrizione, stato e voto finale per ogni anno accademico.
-- UNIQUE su tre campi: permette reiscrizione in anni accademici diversi.
CREATE TABLE IF NOT EXISTS studenti_corsi (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    studente_id             INTEGER NOT NULL REFERENCES users(id)
                                ON DELETE CASCADE,  -- utente eliminato → rimuovi iscrizioni
    corso_universitario_id  INTEGER NOT NULL REFERENCES corsi_universitari(id)
                                ON DELETE RESTRICT, -- non eliminare corso con studenti iscritti
    anno_accademico         TEXT    NOT NULL,        -- es. "2025-2026"
    stato                   TEXT    NOT NULL DEFAULT 'iscritto'
                                CHECK(stato IN ('iscritto', 'completato', 'abbandonato', 'in_attesa')),
    voto                    INTEGER CHECK(voto BETWEEN 18 AND 31), -- 31 = 30 con lode
    data_iscrizione         DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_completamento      DATETIME,
    UNIQUE(studente_id, corso_universitario_id, anno_accademico)
);


-- ============================================================================
-- STEP 2: QUIZ
--
-- Tre tipi discriminati da corso_universitario_id, studente_id e approvato:
--
--   Tipo A — quiz AI nel piano personalizzato (libero)
--     corso_universitario_id = NULL
--     studente_id            = NOT NULL   (FK → users, ruolo='studente')
--     docente_id             = NULL
--     approvato              = 0
--     → non visibile al docente, non alimenta analytics
--
--   Tipo B — quiz AI generato dallo studente su un corso universitario
--     corso_universitario_id = NOT NULL
--     studente_id            = NOT NULL   (FK → users, ruolo='studente')
--     docente_id             = NULL
--     approvato              = 0
--     → non visibile al docente, non alimenta analytics
--
--   Tipo C — quiz del corso creato/approvato dal docente
--     corso_universitario_id = NOT NULL
--     studente_id            = NULL
--     docente_id             = NOT NULL   (FK → users, ruolo='docente')
--     approvato              = 1
--     → unico tipo che alimenta le analytics del docente
--
-- approvato è l'UNICO discriminante per le analytics.
-- ============================================================================
CREATE TABLE IF NOT EXISTS quiz (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    titolo                  TEXT    NOT NULL,
    corso_universitario_id  INTEGER REFERENCES corsi_universitari(id)
                                ON DELETE RESTRICT, -- non eliminare corso con quiz associati
    studente_id             INTEGER REFERENCES users(id)
                                ON DELETE CASCADE,  -- utente eliminato → elimina suoi quiz privati
    docente_id              INTEGER REFERENCES users(id)
                                ON DELETE RESTRICT, -- non eliminare docente con quiz approvati
    creato_da               TEXT    NOT NULL
                                CHECK(creato_da IN ('ai', 'docente')),
    approvato               INTEGER NOT NULL DEFAULT 0
                                CHECK(approvato IN (0, 1)),
    ripetibile              INTEGER NOT NULL DEFAULT 1
                                CHECK(ripetibile IN (0, 1)), -- rilevante solo Tipo C
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================================
-- STEP 3A: MATERIALI DIDATTICI
-- Fonte esclusiva per RAG, lezioni e quiz.
-- Caricati dal docente, associati a un corso universitario.
-- PRIVATI: mai accessibili agli ospiti.
--
-- Flusso upload:
--   1. Docente carica file → record in materiali_didattici (is_processed=0)
--   2. Agente segmenta → popola materiali_chunks → is_processed=1
--
-- REGOLA DI IDEMPOTENZA: se is_processed=1 i chunks esistono — non riprocessare.
-- ============================================================================
CREATE TABLE IF NOT EXISTS materiali_didattici (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    corso_universitario_id  INTEGER REFERENCES corsi_universitari(id)
                                ON DELETE RESTRICT, -- NULL = materiale personale senza corso
    docente_id              INTEGER NOT NULL REFERENCES users(id)
                                ON DELETE RESTRICT, -- non eliminare docente con materiali
    titolo                  TEXT    NOT NULL,
    tipo                    TEXT    NOT NULL
                                CHECK(tipo IN ('pdf', 'slide', 'video', 'dispensa', 'libro')),
    s3_key                  TEXT    NOT NULL,        -- percorso file su Amazon S3
    testo_estratto          TEXT,                    -- testo grezzo (PyPDF2 o trascrizione)
    is_processed            INTEGER NOT NULL DEFAULT 0
                                CHECK(is_processed IN (0, 1)),
    caricato_il             DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- MATERIALI_CHUNKS
-- Sezioni semantiche del materiale, generate dall'agente (una tantum).
-- Fonte di verità per: RAG, generazione contenuti, citazioni.
-- NON SVUOTARE MAI AL RIAVVIO — sono persistenti per design.
--
-- corso_universitario_id è denormalizzazione intenzionale:
--   ricavabile via JOIN su materiali_didattici, ma qui evita un JOIN
--   su ogni query RAG (che è la query più frequente dell'intera app).
--
-- INTEGRAZIONE VECTOR DATABASE (es. ChromaDB):
--   Questo schema funge da metadata store. I vettori degli embedding risiedono
--   nel vector store esterno. Il collegamento avviene tramite materiali_chunks.id
--   come document_id nel vector store (collection separata per corso).
--   embedding_sync traccia se il chunk è già stato vettorizzato, garantendo
--   la stessa idempotenza di is_processed per i materiali grezzi.
--
--   Flusso vettorizzazione:
--     1. Chunk inserito (embedding_sync=0)
--     2. Agente calcola embedding → inserisce in ChromaDB con id=chunk.id
--     3. embedding_sync=1  ← non rielaborare mai
--
--   Query RAG ibrida tipica:
--     a. ChromaDB: similarity_search(query, filter={"corso_id": X}) → [chunk_ids]
--     b. SQLite:   SELECT * FROM materiali_chunks WHERE id IN (chunk_ids)
--                  → metadati completi per il contesto LLM
-- ============================================================================
CREATE TABLE IF NOT EXISTS materiali_chunks (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    materiale_id            INTEGER NOT NULL REFERENCES materiali_didattici(id)
                                ON DELETE CASCADE,  -- materiale eliminato → elimina chunks
    corso_universitario_id  INTEGER REFERENCES corsi_universitari(id)
                                ON DELETE RESTRICT, -- denormalizzato per performance RAG; NULL = materiale senza corso
    indice_chunk            INTEGER NOT NULL,        -- posizione nel documento (0-based)
    titolo_sezione          TEXT,                    -- generato dall'agente
    testo                   TEXT    NOT NULL,
    sommario                TEXT,                    -- 2-3 righe, generato dall'agente
    argomenti_chiave        TEXT,                    -- JSON array: ["SQL", "normalizzazione"]
    livello_difficolta      INTEGER
                                CHECK(livello_difficolta BETWEEN 1 AND 5),
    pagine_riferimento      TEXT,                    -- JSON array: [12, 13, 14]
    n_token                 INTEGER,                 -- stima token per gestione contesto LLM
    embedding_sync          INTEGER NOT NULL DEFAULT 0
                                CHECK(embedding_sync IN (0, 1)), -- 1 = vettorizzato nel vector store
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- DOMANDE_QUIZ (definita qui perché referenzia materiali_chunks)
-- chunk_id: chunk da cui è stata generata la domanda.
--   NULL solo per domande inserite manualmente dal docente senza fonte AI.
-- ============================================================================
CREATE TABLE IF NOT EXISTS domande_quiz (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id             INTEGER NOT NULL REFERENCES quiz(id)
                            ON DELETE CASCADE,      -- quiz eliminato → elimina domande
    testo               TEXT    NOT NULL,
    tipo                TEXT    NOT NULL
                            CHECK(tipo IN ('scelta_multipla', 'vero_falso', 'aperta')),
    opzioni_json        TEXT,                        -- JSON array, solo per scelta_multipla
    risposta_corretta   TEXT,                        -- NULL per domande aperte
    spiegazione         TEXT,                        -- feedback formativo post-risposta
    ordine              INTEGER NOT NULL DEFAULT 0,
    chunk_id            INTEGER REFERENCES materiali_chunks(id)
                            ON DELETE SET NULL       -- chunk eliminato → domanda rimane, perde fonte
);

-- punteggio 0-100: puramente formativo, non concorre al voto del corso
CREATE TABLE IF NOT EXISTS tentativi_quiz (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id             INTEGER NOT NULL REFERENCES quiz(id)
                            ON DELETE RESTRICT,     -- non eliminare quiz con tentativi
    studente_id         INTEGER NOT NULL REFERENCES users(id)
                            ON DELETE CASCADE,      -- utente eliminato → elimina tentativi
    punteggio           REAL    CHECK(punteggio BETWEEN 0 AND 100),
    aree_deboli_json    TEXT,                        -- JSON array: argomenti dove ha sbagliato
    completato          INTEGER NOT NULL DEFAULT 0
                            CHECK(completato IN (0, 1)),
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS risposte_domande (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    tentativo_id    INTEGER NOT NULL REFERENCES tentativi_quiz(id)
                        ON DELETE CASCADE,          -- tentativo eliminato → elimina risposte
    domanda_id      INTEGER NOT NULL REFERENCES domande_quiz(id)
                        ON DELETE RESTRICT,         -- non eliminare domanda con risposte
    risposta_data   TEXT,                            -- NULL se domanda saltata
    corretta        INTEGER                          -- NULL per domande aperte
                        CHECK(corretta IN (0, 1)),
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================================
-- STEP 3B: PIANI PERSONALIZZATI AI
--
-- Gerarchia:
--   piani_personalizzati
--     → piano_materiali_utilizzati  (traccia chunks usati per il piano — livello piano)
--     → piano_capitoli
--         → piano_paragrafi
--             → piano_contenuti     (traccia chunks per singolo contenuto — livello granulare)
--
-- TIPI DI PIANO:
--   'esame'  → corso_universitario_id NOT NULL, fonte primaria = materiali di quel corso
--   'libero' → corso_universitario_id NULL, agente sceglie autonomamente i materiali
--
-- PERCHÉ piano_materiali_utilizzati NON è ridondante con chunk_ids_utilizzati
-- in piano_contenuti: piano_materiali_utilizzati permette query SQL efficienti
-- su "quali piani usano questo chunk?" senza parsare JSON. Necessario per
-- aggiornare i piani quando viene caricato nuovo materiale.
-- ============================================================================
CREATE TABLE IF NOT EXISTS piani_personalizzati (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    studente_id             INTEGER NOT NULL REFERENCES users(id)
                                ON DELETE CASCADE,  -- utente eliminato → elimina piani
    titolo                  TEXT    NOT NULL,
    descrizione             TEXT,                    -- obiettivo del piano (scritto dall'agente)
    tipo                    TEXT    NOT NULL
                                CHECK(tipo IN ('esame', 'libero', 'corso')),
    corso_universitario_id  INTEGER REFERENCES corsi_universitari(id)
                                ON DELETE SET NULL, -- NOT NULL se tipo='esame'/'corso', NULL se 'libero'
    stato                   TEXT    NOT NULL DEFAULT 'attivo'
                                CHECK(stato IN ('attivo', 'completato', 'archiviato')),
    is_corso_docente        INTEGER NOT NULL DEFAULT 0
                                CHECK(is_corso_docente IN (0, 1)),
                                -- 0 = piano personalizzato studente
                                -- 1 = corso strutturato generato per il docente
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP,
    aggiornato_il           DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS piano_materiali_utilizzati (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    piano_id    INTEGER NOT NULL REFERENCES piani_personalizzati(id)
                    ON DELETE CASCADE,              -- piano eliminato → elimina traccia
    chunk_id    INTEGER NOT NULL REFERENCES materiali_chunks(id)
                    ON DELETE RESTRICT,             -- non eliminare chunk usato in un piano
    UNIQUE(piano_id, chunk_id)
);

CREATE TABLE IF NOT EXISTS piano_capitoli (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    piano_id    INTEGER NOT NULL REFERENCES piani_personalizzati(id)
                    ON DELETE CASCADE,
    titolo      TEXT    NOT NULL,
    descrizione TEXT,
    ordine      INTEGER NOT NULL DEFAULT 0,
    completato  INTEGER NOT NULL DEFAULT 0
                    CHECK(completato IN (0, 1)),
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS piano_paragrafi (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    capitolo_id INTEGER NOT NULL REFERENCES piano_capitoli(id)
                    ON DELETE CASCADE,
    titolo      TEXT    NOT NULL,
    descrizione TEXT,
    ordine      INTEGER NOT NULL DEFAULT 0,
    completato  INTEGER NOT NULL DEFAULT 0
                    CHECK(completato IN (0, 1)),
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- tipo determina il contenuto:
--   'lezione'   → contenuto_json = testo markdown
--   'riassunto' → contenuto_json = testo sintetico
--   'schema'    → contenuto_json = struttura JSON per rendering UI
--   'flashcard' → contenuto_json = JSON array [{domanda, risposta}, ...]
--   'quiz'      → contenuto_json = NULL, quiz_id = NOT NULL (rimanda a tabella quiz)
--
-- chunk_ids_utilizzati: JSON array dei chunk usati per generare questo contenuto.
--   Più granulare di piano_materiali_utilizzati (che è a livello di piano).
--   Permette di citare la fonte precisa di ogni contenuto.
--
-- generato_al_momento: 0 = pre-generato, 1 = generato on-demand dallo studente
CREATE TABLE IF NOT EXISTS piano_contenuti (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    paragrafo_id            INTEGER NOT NULL REFERENCES piano_paragrafi(id)
                                ON DELETE CASCADE,
    tipo                    TEXT    NOT NULL
                                CHECK(tipo IN ('lezione', 'riassunto', 'schema', 'flashcard', 'quiz')),
    contenuto_json          TEXT,                    -- NULL solo se tipo='quiz'
    quiz_id                 INTEGER REFERENCES quiz(id)
                                ON DELETE SET NULL, -- NOT NULL solo se tipo='quiz'
    chunk_ids_utilizzati    TEXT,                    -- JSON array: [chunk_id, ...]
    generato_al_momento     INTEGER NOT NULL DEFAULT 0
                                CHECK(generato_al_momento IN (0, 1)),
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================================
-- STEP 4: LEZIONI DEI CORSI
-- Generate dall'agente o dal docente, approvate dal docente.
-- Speculari ai quiz Tipo C per il flusso di approvazione.
-- Visibili agli studenti solo se approvato=1.
--
-- Distinte da piano_contenuti.tipo='lezione':
--   lezioni_corso          → appartengono al corso universitario reale
--   piano_contenuti.lezione → appartengono al piano personalizzato dello studente
-- ============================================================================
CREATE TABLE IF NOT EXISTS lezioni_corso (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    corso_universitario_id  INTEGER NOT NULL REFERENCES corsi_universitari(id)
                                ON DELETE RESTRICT,
    docente_id              INTEGER NOT NULL REFERENCES users(id)
                                ON DELETE RESTRICT,
    titolo                  TEXT    NOT NULL,
    contenuto_md            TEXT,                    -- testo markdown della lezione
    creato_da               TEXT    NOT NULL
                                CHECK(creato_da IN ('ai', 'docente')),
    approvato               INTEGER NOT NULL DEFAULT 0
                                CHECK(approvato IN (0, 1)),
    chunk_ids_utilizzati    TEXT,                    -- JSON array: [chunk_id, ...]
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP,
    aggiornato_il           DATETIME DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================================
-- INDICI
-- ============================================================================

-- Auth (query più frequente: ogni login e ogni routing per ruolo)
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email
    ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_ruolo
    ON users(ruolo);

-- Struttura universitaria
CREATE INDEX IF NOT EXISTS idx_users_cdl
    ON users(corso_di_laurea_id);
CREATE INDEX IF NOT EXISTS idx_corsi_docente
    ON corsi_universitari(docente_id);
CREATE INDEX IF NOT EXISTS idx_studenti_corsi_studente
    ON studenti_corsi(studente_id);
CREATE INDEX IF NOT EXISTS idx_studenti_corsi_corso
    ON studenti_corsi(corso_universitario_id);

-- Quiz
CREATE INDEX IF NOT EXISTS idx_quiz_corso
    ON quiz(corso_universitario_id);
CREATE INDEX IF NOT EXISTS idx_quiz_studente
    ON quiz(studente_id);
CREATE INDEX IF NOT EXISTS idx_tentativi_studente
    ON tentativi_quiz(studente_id);
CREATE INDEX IF NOT EXISTS idx_tentativi_quiz
    ON tentativi_quiz(quiz_id);

-- Materiali didattici
CREATE INDEX IF NOT EXISTS idx_materiali_corso
    ON materiali_didattici(corso_universitario_id);
CREATE INDEX IF NOT EXISTS idx_chunks_materiale
    ON materiali_chunks(materiale_id);
-- Query più frequente del RAG: tutti i chunks di un corso
CREATE INDEX IF NOT EXISTS idx_chunks_corso
    ON materiali_chunks(corso_universitario_id);
-- Idempotenza vettorizzazione: trova rapidamente i chunks non ancora sincronizzati
CREATE INDEX IF NOT EXISTS idx_chunks_embedding_sync
    ON materiali_chunks(embedding_sync);

-- Piani personalizzati
CREATE INDEX IF NOT EXISTS idx_piani_studente
    ON piani_personalizzati(studente_id);
CREATE INDEX IF NOT EXISTS idx_piano_materiali_piano
    ON piano_materiali_utilizzati(piano_id);
-- Query inversa: quali piani usano questo chunk? (aggiornamento materiali)
CREATE INDEX IF NOT EXISTS idx_piano_materiali_chunk
    ON piano_materiali_utilizzati(chunk_id);
CREATE INDEX IF NOT EXISTS idx_piano_capitoli
    ON piano_capitoli(piano_id, ordine);
CREATE INDEX IF NOT EXISTS idx_piano_paragrafi
    ON piano_paragrafi(capitolo_id, ordine);
CREATE INDEX IF NOT EXISTS idx_piano_contenuti
    ON piano_contenuti(paragrafo_id);

-- Lezioni corso
CREATE INDEX IF NOT EXISTS idx_lezioni_corso_approvato
    ON lezioni_corso(corso_universitario_id, approvato);
