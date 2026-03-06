-- ============================================================================
-- LearnAI Platform — Seed Data per Test
-- Università Federico II / Deloitte — Digita Academy 2025
-- ============================================================================
--
-- SCOPO: Popolazione minima per testare login, caricamento documenti,
--        generazione quiz, piani personalizzati e dashboard docente.
--
-- CREDENZIALI DI TEST:
--   Admin    → a.verdi@unina.it       / admin123
--   Docente1 → m.rossi@unina.it       / docente123
--   Docente2 → l.ferrari@unina.it     / docente123
--   Studente1→ g.bianchi@studenti.unina.it  / studente123
--   Studente2→ f.esposito@studenti.unina.it / studente123
--   Studente3→ c.romano@studenti.unina.it   / studente123
--
-- NOTA SUGLI HASH:
--   Gli hash sono generati con werkzeug.security (pbkdf2:sha256).
--   Se il progetto usa bcrypt, eseguire questo snippet UNA SOLA VOLTA
--   per rigenerare gli hash e aggiornare questo file:
--
--   from bcrypt import hashpw, gensalt
--   print(hashpw(b"admin123", gensalt(12)).decode())
--
-- ============================================================================

-- Disabilita temporaneamente i vincoli FK durante l'inserimento
PRAGMA foreign_keys = OFF;


-- ============================================================================
-- STEP 1 — STRUTTURA UNIVERSITARIA
-- ============================================================================

INSERT INTO corsi_di_laurea (id, nome, facolta) VALUES
    (1, 'Ingegneria Informatica',          'Ingegneria'),
    (2, 'Informatica',                     'Scienze MMFFNN'),
    (3, 'Ingegneria Elettronica',          'Ingegneria');


-- ============================================================================
-- STEP 3 — CORSI UNIVERSITARI
-- ============================================================================

INSERT INTO corsi_universitari
    (id, nome, descrizione, docente_id, cfu, ore_lezione,
     anno_di_corso, semestre, livello, attivo) VALUES
(
    101,
    'Basi di Dati',
    'Fondamenti di progettazione e gestione di basi di dati relazionali. SQL, normalizzazione, transazioni.',
    10, 9, 72, 2, 1, 'intermedio', 1
),
(
    102,
    'Algoritmi e Strutture Dati',
    'Analisi della complessità, strutture dati fondamentali, algoritmi di ordinamento e ricerca.',
    10, 9, 72, 2, 2, 'intermedio', 1
),
(
    103,
    'Analisi Matematica I',
    'Limiti, derivate, integrali. Fondamenti di analisi per ingegneria.',
    11, 12, 96, 1, 1, 'base', 1
);


-- ============================================================================
-- STEP 4 — MAPPATURA CORSI DI LAUREA ↔ CORSI UNIVERSITARI
-- ============================================================================

INSERT INTO corsi_laurea_universitari
    (corso_di_laurea_id, corso_universitario_id, obbligatorio) VALUES
    (1, 101, 1),  -- Ing. Informatica: Basi di Dati obbligatorio
    (1, 102, 1),  -- Ing. Informatica: Algoritmi obbligatorio
    (1, 103, 1),  -- Ing. Informatica: Analisi I obbligatorio
    (2, 101, 1),  -- Informatica: Basi di Dati obbligatorio
    (2, 102, 1),  -- Informatica: Algoritmi obbligatorio
    (2, 103, 0);  -- Informatica: Analisi I a scelta


-- ============================================================================
-- STEP 5 — ISCRIZIONI STUDENTI AI CORSI
-- ============================================================================

INSERT INTO studenti_corsi
    (studente_id, corso_universitario_id, anno_accademico, stato) VALUES
    (1, 101, '2025-2026', 'iscritto'),   -- Giulia → Basi di Dati
    (1, 102, '2025-2026', 'iscritto'),   -- Giulia → Algoritmi
    (2, 101, '2025-2026', 'iscritto'),   -- Francesco → Basi di Dati
    (2, 103, '2025-2026', 'iscritto'),   -- Francesco → Analisi I
    (3, 101, '2025-2026', 'iscritto'),   -- Chiara → Basi di Dati
    (3, 103, '2025-2026', 'iscritto');   -- Chiara → Analisi I


-- ============================================================================
-- STEP 6 — MATERIALE DIDATTICO (placeholder per test upload)
-- Il campo s3_key e testo_estratto sono placeholder: in produzione vengono
-- popolati dal flusso di upload (boto3 + PyPDF2).
-- is_processed=0 → il Document Processor non ha ancora segmentato i chunks.
-- ============================================================================

INSERT INTO materiali_didattici
    (id, corso_universitario_id, docente_id, titolo, tipo,
     s3_key, testo_estratto, is_processed) VALUES
(
    5001,
    101, 10,
    'Slide Capitolo 1 — Modello Relazionale',
    'slide',
    'didattica/corsi/101/slide_cap1_modello_relazionale.pdf',
    'Il modello relazionale è basato sul concetto di relazione matematica. Una relazione è un sottoinsieme del prodotto cartesiano di domini. Ogni relazione ha uno schema (intestazione) e un''istanza (corpo). La chiave primaria identifica univocamente ogni tupla.',
    0
),
(
    5002,
    101, 10,
    'Slide Capitolo 2 — SQL Base',
    'slide',
    'didattica/corsi/101/slide_cap2_sql_base.pdf',
    'SQL (Structured Query Language) è il linguaggio standard per interrogare basi di dati relazionali. Le istruzioni principali sono SELECT, INSERT, UPDATE e DELETE. La clausola WHERE filtra le righe. GROUP BY aggrega i risultati.',
    0
),
(
    5003,
    102, 10,
    'Dispensa — Complessità Algoritmica',
    'dispensa',
    'didattica/corsi/102/dispensa_complessita.pdf',
    'La notazione O-grande descrive il comportamento asintotico degli algoritmi. Un algoritmo O(n log n) è più efficiente di O(n^2) per input grandi. MergeSort ha complessità O(n log n) nel caso peggiore.',
    0
);


-- ============================================================================
-- STEP 7 — CHUNK SEMANTICI (per testare il RAG senza processare PDF reali)
-- Normalmente generati automaticamente dal Document Processor.
-- Qui inseriti manualmente per abilitare i test degli agenti AI.
-- embedding_sync=0 → non ancora vettorizzati nel vector store.
-- ============================================================================

INSERT INTO materiali_chunks
    (id, materiale_id, corso_universitario_id, indice_chunk,
     titolo_sezione, testo, sommario, argomenti_chiave,
     livello_difficolta, pagine_riferimento, n_token, embedding_sync) VALUES
(
    301,
    5001, 101, 0,
    'Introduzione al Modello Relazionale',
    'Il modello relazionale è basato sul concetto di relazione matematica, introdotto da E.F. Codd nel 1970. Una relazione è un sottoinsieme del prodotto cartesiano di domini. Ogni relazione ha uno schema (intestazione) che definisce gli attributi e un''istanza (corpo) che contiene le tuple.',
    'Definizione e origine del modello relazionale. Concetti di schema e istanza.',
    '["modello relazionale", "relazione", "schema", "istanza", "Codd"]',
    1, '[1, 2]', 380, 0
),
(
    302,
    5001, 101, 1,
    'Chiavi Primarie e Vincoli di Integrità',
    'La chiave primaria identifica univocamente ogni tupla in una relazione. Deve soddisfare due proprietà: unicità (nessuna altra tupla ha lo stesso valore) e non nullità (il valore non può essere NULL). Il vincolo di integrità referenziale garantisce che ogni valore di chiave esterna corrisponda a un valore esistente nella tabella referenziata.',
    'Definizione e proprietà delle chiavi primarie. Vincolo di integrità referenziale.',
    '["chiave primaria", "integrità referenziale", "chiave esterna", "vincoli", "NULL"]',
    2, '[12, 13]', 420, 0
),
(
    303,
    5001, 101, 2,
    'Normalizzazione — Forme Normali',
    'La normalizzazione è il processo di organizzare gli attributi di una relazione per ridurre la ridondanza. La Prima Forma Normale (1NF) richiede che tutti gli attributi siano atomici. La Seconda Forma Normale (2NF) elimina le dipendenze parziali. La Terza Forma Normale (3NF) elimina le dipendenze transitive.',
    'Processo di normalizzazione: 1NF, 2NF, 3NF e relative condizioni.',
    '["normalizzazione", "1NF", "2NF", "3NF", "dipendenze funzionali", "ridondanza"]',
    3, '[20, 21, 22]', 510, 0
),
(
    304,
    5002, 101, 0,
    'SELECT e Clausola WHERE',
    'L''istruzione SELECT recupera dati da una o più tabelle. La sintassi base è: SELECT colonne FROM tabella WHERE condizione. La clausola WHERE filtra le righe in base a condizioni booleane. Gli operatori disponibili sono: =, <>, <, >, BETWEEN, LIKE, IN, IS NULL. Le condizioni si combinano con AND e OR.',
    'Sintassi SELECT con filtri WHERE. Operatori di confronto e combinazioni logiche.',
    '["SELECT", "WHERE", "SQL", "filtro", "operatori", "AND", "OR"]',
    2, '[5, 6, 7]', 460, 0
),
(
    305,
    5003, 102, 0,
    'Notazione O-grande e Complessità',
    'La notazione O-grande (Big-O) descrive il limite superiore del tempo di esecuzione di un algoritmo in funzione della dimensione dell''input. O(1) indica tempo costante, O(log n) logaritmico, O(n) lineare, O(n log n) linearitmico, O(n^2) quadratico. MergeSort e HeapSort hanno complessità O(n log n) nel caso peggiore.',
    'Notazione Big-O e classificazione degli algoritmi per complessità temporale.',
    '["complessità", "Big-O", "O(n log n)", "MergeSort", "analisi algoritmi"]',
    2, '[1, 2, 3]', 390, 0
);

-- Marca i materiali come processati (chunks ora presenti)
UPDATE materiali_didattici SET is_processed = 1 WHERE id IN (5001, 5002, 5003);


-- ============================================================================
-- STEP 8 — QUIZ TIPO C (approvato dal docente — alimenta le analytics)
-- ============================================================================

INSERT INTO quiz
    (id, titolo, corso_universitario_id, studente_id, docente_id,
     creato_da, approvato, ripetibile) VALUES
(
    300,
    'Test Modello Relazionale',
    101, NULL, 10,
    'ai', 1, 1
);

INSERT INTO domande_quiz
    (id, quiz_id, testo, tipo, opzioni_json, risposta_corretta, spiegazione, ordine, chunk_id)
VALUES
(
    1001, 300,
    'Quale proprietà deve soddisfare una chiave primaria?',
    'scelta_multipla',
    '["Può contenere valori NULL", "Identifica univocamente ogni tupla", "Può avere duplicati", "È opzionale"]',
    'Identifica univocamente ogni tupla',
    'La chiave primaria deve essere unica e non nulla per ogni record della relazione.',
    1, 302
),
(
    1002, 300,
    'Quale forma normale elimina le dipendenze parziali?',
    'scelta_multipla',
    '["Prima Forma Normale (1NF)", "Seconda Forma Normale (2NF)", "Terza Forma Normale (3NF)", "Forma Normale di Boyce-Codd"]',
    'Seconda Forma Normale (2NF)',
    'La 2NF richiede che ogni attributo non-chiave dipenda interamente dalla chiave primaria, eliminando le dipendenze parziali.',
    2, 303
),
(
    1003, 300,
    'La notazione O(n log n) descrive un algoritmo:',
    'scelta_multipla',
    '["Costante", "Lineare", "Linearitmico", "Quadratico"]',
    'Linearitmico',
    'O(n log n) è detto linearitmico. È la complessità tipica degli algoritmi di ordinamento efficienti come MergeSort.',
    3, 302
);


-- ============================================================================
-- STEP 9 — PIANO PERSONALIZZATO (per testare gli agenti di studio)
-- ============================================================================

INSERT INTO piani_personalizzati
    (id, studente_id, titolo, descrizione, tipo,
     corso_universitario_id, stato) VALUES
(
    50,
    1,
    'Preparazione Esame Basi di Dati',
    'Piano per la preparazione all''esame di Basi di Dati. Focus su modello relazionale, SQL e normalizzazione.',
    'esame',
    101, 'attivo'
);

INSERT INTO piano_capitoli
    (id, piano_id, titolo, descrizione, ordine, completato) VALUES
(
    200, 50,
    'Modello Relazionale',
    'Fondamenti del modello relazionale: relazioni, schemi, chiavi e vincoli di integrità.',
    1, 0
),
(
    201, 50,
    'SQL',
    'Linguaggio SQL: DDL, DML, query con JOIN, aggregazioni e subquery.',
    2, 0
);

INSERT INTO piano_paragrafi
    (id, capitolo_id, titolo, descrizione, ordine, completato) VALUES
(
    600, 200, 'Chiavi e Vincoli',       'Chiave primaria, chiave esterna, NOT NULL, UNIQUE.',    1, 0),
(
    601, 200, 'Normalizzazione',        '1NF, 2NF, 3NF e dipendenze funzionali.',                2, 0),
(
    602, 201, 'SELECT e WHERE',         'Sintassi SELECT, filtri, operatori di confronto.',      1, 0),
(
    603, 201, 'JOIN e Aggregazioni',    'INNER JOIN, LEFT JOIN, GROUP BY, HAVING.',              2, 0);

INSERT INTO piano_contenuti
    (paragrafo_id, tipo, contenuto_json, quiz_id, chunk_ids_utilizzati, generato_al_momento) VALUES
(
    600, 'flashcard',
    '[{"domanda": "Cos''e una chiave primaria?", "risposta": "Un attributo che identifica univocamente ogni tupla. Non puo essere NULL."}, {"domanda": "Cosa garantisce il vincolo di integrita referenziale?", "risposta": "Che ogni valore di chiave esterna corrisponda a un valore esistente nella tabella referenziata."}]',
    NULL, '[302]', 0
),
(
    601, 'riassunto',
    '"La normalizzazione organizza gli attributi per ridurre la ridondanza. 1NF: attributi atomici. 2NF: no dipendenze parziali. 3NF: no dipendenze transitive."',
    NULL, '[303]', 0
);


-- ============================================================================
-- STEP 10 — LEZIONE DEL CORSO (approvata, visibile agli studenti)
-- ============================================================================

INSERT INTO lezioni_corso
    (id, corso_universitario_id, docente_id, titolo, contenuto_md,
     creato_da, approvato, chunk_ids_utilizzati) VALUES
(
    700,
    101, 10,
    'Introduzione al Modello Relazionale',
    '## Il Modello Relazionale

Il modello relazionale è stato introdotto da **E.F. Codd nel 1970** e rappresenta il fondamento delle basi di dati moderne.

### Concetti Chiave

Una **relazione** è un sottoinsieme del prodotto cartesiano di domini. È composta da:
- **Schema**: definisce il nome della relazione e i suoi attributi
- **Istanza**: l''insieme delle tuple presenti in un dato momento

### Chiavi

La **chiave primaria** identifica univocamente ogni tupla e non può contenere valori NULL.

La **chiave esterna** implementa il vincolo di integrità referenziale: ogni suo valore deve corrispondere a un valore esistente nella tabella referenziata.',
    'ai', 1,
    '[301, 302]'
);


-- Riabilita i vincoli FK
PRAGMA foreign_keys = ON;

-- ============================================================================
-- RIEPILOGO DATI INSERITI
-- ============================================================================
-- users:                6  (1 admin, 2 docenti, 3 studenti)
-- corsi_di_laurea:      3
-- corsi_universitari:   3
-- studenti_corsi:       6  (iscrizioni)
-- materiali_didattici:  3  (is_processed=1)
-- materiali_chunks:     5  (embedding_sync=0 — da vettorizzare)
-- quiz:                 1  (Tipo C, approvato)
-- domande_quiz:         3
-- piani_personalizzati: 1
-- piano_capitoli:       2
-- piano_paragrafi:      4
-- piano_contenuti:      2
-- lezioni_corso:        1  (approvata)
-- ============================================================================
