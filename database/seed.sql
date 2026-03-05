-- ============================================================================
-- LearnAI Platform — Seed Data
-- Università Federico II / Deloitte — Digita Academy 2025
-- ============================================================================
-- Dati di test per sviluppo locale. NON usare in produzione.
--
-- CREDENZIALI DI TEST (password: "password123" per tutti gli utenti):
--   Admin   → admin@learnai.it
--   Docenti → m.rossi@unina.it | a.ferrari@unina.it
--   Studenti→ g.bianchi@studenti.unina.it | m.esposito@studenti.unina.it
--             s.deluca@studenti.unina.it
--
-- COPERTURA DEI FLUSSI:
--   ✅ Struttura universitaria (3 CDL, 2 docenti, 3 corsi, 3 studenti)
--   ✅ Materiali didattici processati + chunks semantici
--   ✅ Quiz Tipo A (piano privato), B (corso privato), C (approvato docente)
--   ✅ Tentativi e risposte (analytics docente attive)
--   ✅ Piano esame con struttura gerarchica completa (capitoli/paragrafi/contenuti)
--   ✅ Piano libero (senza corso universitario)
--   ✅ Lezione corso approvata + bozza non approvata
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ============================================================================
-- STEP 1A: ADMIN
-- ============================================================================

INSERT INTO admin (id, nome, cognome, email, password_hash) VALUES
(1, 'Admin', 'LearnAI', 'admin@learnai.it',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMfM9pBj3hQ.zZz3sNXJd6Q2Gy');

-- ============================================================================
-- STEP 1A: CORSI DI LAUREA
-- ============================================================================

INSERT INTO corsi_di_laurea (id, nome, facolta) VALUES
(1, 'Ingegneria Informatica',           'Ingegneria'),
(2, 'Scienze e Tecnologie Informatiche','Scienze MM.FF.NN.'),
(3, 'Ingegneria Gestionale',            'Ingegneria');

-- ============================================================================
-- STEP 1A: DOCENTI
-- ============================================================================
-- password: "password123"

INSERT INTO docenti (id, nome, cognome, email, password_hash, matricola_docente, dipartimento, stato) VALUES
(1, 'Mario',  'Rossi',   'm.rossi@unina.it',   '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMfM9pBj3hQ.zZz3sNXJd6Q2Gy',
   'DOC-2018-011', 'Ingegneria Elettrica e Tecnologie dell''Informazione', 'active'),
(2, 'Anna',   'Ferrari', 'a.ferrari@unina.it', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMfM9pBj3hQ.zZz3sNXJd6Q2Gy',
   'DOC-2020-034', 'Ingegneria Elettrica e Tecnologie dell''Informazione', 'active');

-- ============================================================================
-- STEP 1B: STUDENTI
-- ============================================================================
-- password: "password123"
-- profilo_json: campo usato dall'Onboarding Assistant per memorizzare
--   interessi, obiettivo professionale, stile di apprendimento

INSERT INTO studenti (id, nome, cognome, email, password_hash, data_nascita, corso_di_laurea_id, anno_corso, stato) VALUES
(1, 'Giulia', 'Bianchi',  'g.bianchi@studenti.unina.it',  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMfM9pBj3hQ.zZz3sNXJd6Q2Gy',
   '2002-04-15', 1, 2, 'active'),
(2, 'Marco',  'Esposito', 'm.esposito@studenti.unina.it', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMfM9pBj3hQ.zZz3sNXJd6Q2Gy',
   '2001-09-22', 1, 3, 'active'),
(3, 'Sara',   'De Luca',  's.deluca@studenti.unina.it',   '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMfM9pBj3hQ.zZz3sNXJd6Q2Gy',
   '2003-01-08', 2, 1, 'active');

-- ============================================================================
-- STEP 1B: CORSI UNIVERSITARI
-- ============================================================================

INSERT INTO corsi_universitari (id, nome, descrizione, docente_id, cfu, ore_lezione, anno_di_corso, semestre, livello, attivo) VALUES
(1, 'Basi di Dati',
   'Progettazione e gestione di basi di dati relazionali. SQL, normalizzazione, transazioni.',
   1, 9, 72, 2, 1, 'intermedio', 1),
(2, 'Algoritmi e Strutture Dati',
   'Fondamenti di algoritmi, complessità computazionale, strutture dati classiche.',
   1, 9, 72, 2, 2, 'intermedio', 1),
(3, 'Machine Learning',
   'Introduzione al machine learning supervisionato e non supervisionato. Python, scikit-learn.',
   2, 6, 48, 3, 1, 'avanzato', 1);

-- ============================================================================
-- STEP 1C: MAPPING CDL ↔ CORSI UNIVERSITARI
-- ============================================================================

INSERT INTO corsi_laurea_universitari (corso_di_laurea_id, corso_universitario_id, obbligatorio) VALUES
-- Ingegneria Informatica
(1, 1, 1),  -- Basi di Dati: obbligatorio
(1, 2, 1),  -- Algoritmi: obbligatorio
(1, 3, 0),  -- Machine Learning: a scelta
-- Scienze Informatiche
(2, 1, 1),  -- Basi di Dati: obbligatorio
(2, 3, 1),  -- Machine Learning: obbligatorio
-- Ingegneria Gestionale
(3, 1, 0);  -- Basi di Dati: a scelta

-- ============================================================================
-- STEP 1C: ISCRIZIONI STUDENTI AI CORSI
-- ============================================================================
-- Giulia (studente_id=1): iscritta a Basi di Dati e Machine Learning
-- Marco  (studente_id=2): ha completato Basi di Dati (voto 28), iscritto ad Algoritmi
-- Sara   (studente_id=3): iscritta a Basi di Dati (primo anno, appena iniziato)

INSERT INTO studenti_corsi (studente_id, corso_universitario_id, anno_accademico, stato, voto, data_completamento) VALUES
(1, 1, '2025-2026', 'iscritto',    NULL, NULL),
(1, 3, '2025-2026', 'iscritto',    NULL, NULL),
(2, 1, '2024-2025', 'completato',  28,   '2025-02-10'),
(2, 2, '2025-2026', 'iscritto',    NULL, NULL),
(3, 1, '2025-2026', 'iscritto',    NULL, NULL);

-- ============================================================================
-- STEP 3A: MATERIALI DIDATTICI
-- ============================================================================
-- Basi di Dati (corso 1): 2 materiali processati (is_processed=1)
-- Machine Learning (corso 3): 1 materiale processato, 1 non ancora (is_processed=0)

INSERT INTO materiali_didattici (id, corso_universitario_id, docente_id, titolo, tipo, s3_key, testo_estratto, is_processed, caricato_il) VALUES
-- Basi di Dati
(1, 1, 1,
   'Slide Capitolo 1 — Modello Relazionale',
   'pdf',
   'didattica/corsi/1/slide_cap1_modello_relazionale.pdf',
   'Il modello relazionale è basato sul concetto di relazione matematica. Una relazione è un sottoinsieme del prodotto cartesiano di domini. Ogni relazione ha uno schema che ne descrive la struttura e un''istanza che contiene i dati effettivi. La chiave primaria identifica univocamente ogni tupla...',
   1, '2025-09-05 09:00:00'),
(2, 1, 1,
   'Slide Capitolo 2 — SQL e Algebra Relazionale',
   'pdf',
   'didattica/corsi/1/slide_cap2_sql.pdf',
   'SQL (Structured Query Language) è il linguaggio standard per interrogare basi di dati relazionali. I comandi principali sono SELECT, INSERT, UPDATE e DELETE. L''algebra relazionale fornisce le basi formali per le operazioni sulle relazioni: selezione, proiezione, join, unione...',
   1, '2025-09-05 10:00:00'),
-- Machine Learning
(3, 3, 2,
   'Slide Capitolo 1 — Introduzione al Machine Learning',
   'pdf',
   'didattica/corsi/3/slide_cap1_intro_ml.pdf',
   'Il machine learning è una branca dell''intelligenza artificiale che consente ai sistemi di apprendere automaticamente dai dati. Si divide in: apprendimento supervisionato (classificazione, regressione), non supervisionato (clustering, riduzione dimensionalità) e per rinforzo...',
   1, '2025-09-10 09:00:00'),
(4, 3, 2,
   'Dispensa — Algoritmi di Ottimizzazione',
   'dispensa',
   'didattica/corsi/3/dispensa_ottimizzazione.pdf',
   NULL,
   0, '2025-10-01 14:00:00');  -- non ancora processato: is_processed=0

-- ============================================================================
-- STEP 3A: CHUNKS SEMANTICI
-- ============================================================================
-- Materiale 1 (Modello Relazionale): 3 chunks
-- Materiale 2 (SQL): 3 chunks
-- Materiale 3 (Intro ML): 3 chunks
-- Materiale 4: non processato → nessun chunk

INSERT INTO materiali_chunks (id, materiale_id, corso_universitario_id, indice_chunk, titolo_sezione, testo, sommario, argomenti_chiave, livello_difficolta, pagine_riferimento, n_token) VALUES
-- Chunks materiale 1: Modello Relazionale
(1, 1, 1, 0,
   'Concetti fondamentali del modello relazionale',
   'Il modello relazionale organizza i dati in relazioni (tabelle). Ogni relazione è caratterizzata da uno schema (nome + attributi) e da un''istanza (insieme di tuple). Gli attributi hanno un dominio che ne definisce i valori ammissibili. Il modello fu introdotto da E.F. Codd nel 1970 e rimane il paradigma dominante per i DBMS commerciali.',
   'Introduzione al modello relazionale: relazioni, schemi, istanze e domini.',
   '["modello relazionale", "relazione", "schema", "tupla", "dominio", "Codd"]',
   1, '[3, 4]', 380),
(2, 1, 1, 1,
   'Chiavi primarie e integrità referenziale',
   'Una chiave è un insieme minimale di attributi che identifica univocamente ogni tupla. La chiave primaria (PK) è quella scelta dal progettista. Il vincolo di integrità referenziale (FK) garantisce che ogni valore di chiave esterna corrisponda a un valore esistente nella tabella referenziata. La violazione di questi vincoli è impedita dal DBMS.',
   'Chiavi primarie, chiavi esterne e vincoli di integrità referenziale.',
   '["chiave primaria", "chiave esterna", "integrità referenziale", "vincoli", "PK", "FK"]',
   2, '[5, 6, 7]', 420),
(3, 1, 1, 2,
   'Normalizzazione: 1NF, 2NF, 3NF',
   'La normalizzazione è il processo di organizzazione degli attributi per ridurre la ridondanza. La Prima Forma Normale (1NF) richiede che ogni attributo contenga valori atomici. La Seconda Forma Normale (2NF) elimina le dipendenze parziali dalla chiave. La Terza Forma Normale (3NF) elimina le dipendenze transitive. La forma normale di Boyce-Codd (BCNF) è una versione più restrittiva della 3NF.',
   'Le forme normali (1NF, 2NF, 3NF, BCNF) e il processo di normalizzazione.',
   '["normalizzazione", "1NF", "2NF", "3NF", "BCNF", "dipendenze funzionali", "ridondanza"]',
   3, '[10, 11, 12, 13]', 510),

-- Chunks materiale 2: SQL
(4, 2, 1, 0,
   'Comandi SQL fondamentali: SELECT e proiezione',
   'Il comando SELECT recupera dati da una o più tabelle. La clausola WHERE filtra le righe in base a condizioni booleane. La clausola ORDER BY ordina i risultati. DISTINCT elimina i duplicati. La proiezione permette di selezionare solo alcune colonne. Esempio: SELECT nome, cognome FROM studenti WHERE anno_corso = 2 ORDER BY cognome ASC.',
   'Sintassi e uso di SELECT, WHERE, ORDER BY, DISTINCT per interrogare il database.',
   '["SQL", "SELECT", "WHERE", "ORDER BY", "DISTINCT", "proiezione", "filtro"]',
   1, '[18, 19, 20]', 390),
(5, 2, 1, 1,
   'JOIN: combinare più tabelle',
   'Il JOIN combina righe di due tabelle basandosi su una condizione. INNER JOIN restituisce solo le righe con corrispondenza in entrambe le tabelle. LEFT JOIN include anche le righe della tabella sinistra senza corrispondenza (NULL a destra). RIGHT JOIN e FULL OUTER JOIN completano il quadro. Il NATURAL JOIN effettua il join su attributi con lo stesso nome.',
   'Tipi di JOIN (INNER, LEFT, RIGHT, FULL) per combinare tabelle nel database.',
   '["JOIN", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL JOIN", "NATURAL JOIN"]',
   2, '[22, 23, 24]', 440),
(6, 2, 1, 2,
   'Aggregazione: GROUP BY e funzioni aggregate',
   'Le funzioni aggregate calcolano un valore su un insieme di righe: COUNT() conta le righe, SUM() somma valori numerici, AVG() calcola la media, MAX() e MIN() trovano il massimo e il minimo. La clausola GROUP BY raggruppa le righe per uno o più attributi. HAVING filtra i gruppi in base a condizioni sulle funzioni aggregate (a differenza di WHERE che filtra le righe).',
   'Funzioni aggregate (COUNT, SUM, AVG, MAX, MIN) e clausole GROUP BY e HAVING.',
   '["GROUP BY", "HAVING", "COUNT", "SUM", "AVG", "MAX", "MIN", "aggregazione"]',
   2, '[26, 27, 28]', 460),

-- Chunks materiale 3: Machine Learning
(7, 3, 3, 0,
   'Apprendimento supervisionato: classificazione e regressione',
   'Nell''apprendimento supervisionato il modello viene addestrato su un dataset etichettato (features + label). La classificazione predice una categoria discreta (es: spam/non-spam). La regressione predice un valore continuo (es: prezzo di un immobile). Il processo prevede: raccolta dati, feature engineering, scelta del modello, training, valutazione su test set.',
   'Concetti base dell''apprendimento supervisionato: classificazione e regressione.',
   '["apprendimento supervisionato", "classificazione", "regressione", "training set", "test set", "label"]',
   2, '[5, 6, 7]', 470),
(8, 3, 3, 1,
   'Overfitting, underfitting e regolarizzazione',
   'L''overfitting si verifica quando il modello memorizza il training set senza generalizzare (alta varianza). L''underfitting accade quando il modello è troppo semplice per catturare la struttura dei dati (alto bias). La regolarizzazione (L1/Lasso, L2/Ridge) aggiunge un termine di penalità alla funzione di costo per ridurre la complessità del modello. La cross-validation permette di stimare le performance su dati non visti.',
   'Overfitting, underfitting, regolarizzazione L1/L2 e cross-validation.',
   '["overfitting", "underfitting", "regolarizzazione", "Lasso", "Ridge", "cross-validation", "bias-variance"]',
   3, '[12, 13, 14]', 530),
(9, 3, 3, 2,
   'Metriche di valutazione: accuracy, precision, recall, F1',
   'La scelta della metrica dipende dal problema. L''accuracy misura la percentuale di predizioni corrette ma è fuorviante con classi sbilanciate. La precision misura quante predizioni positive sono corrette. La recall (o sensitivity) misura quante istanze positive sono state trovate. L''F1-score è la media armonica di precision e recall. La confusion matrix visualizza tutti i casi: TP, TN, FP, FN.',
   'Metriche di valutazione dei modelli: accuracy, precision, recall, F1, confusion matrix.',
   '["accuracy", "precision", "recall", "F1-score", "confusion matrix", "metriche", "classi sbilanciate"]',
   2, '[18, 19]', 490);

-- ============================================================================
-- STEP 2: QUIZ
-- ============================================================================
-- Tipo C (id=1): quiz ufficiale Basi di Dati, approvato dal docente → alimenta analytics
-- Tipo B (id=2): quiz privato di Giulia su Basi di Dati → NON visibile al docente
-- Tipo A (id=3): quiz nel piano personalizzato di Giulia → NON collegato a corso

INSERT INTO quiz (id, titolo, corso_universitario_id, studente_id, docente_id, creato_da, approvato, ripetibile) VALUES
(1, 'Test Ufficiale — Modello Relazionale e SQL',   1, NULL, 1, 'ai',     1, 0), -- Tipo C
(2, 'Ripasso Personale — Chiavi e Normalizzazione',  1, 1,    NULL, 'ai',  0, 1), -- Tipo B
(3, 'Quiz Piano Studio — Intro Machine Learning',    NULL, 1, NULL, 'ai',  0, 1); -- Tipo A

-- ============================================================================
-- STEP 3A: DOMANDE QUIZ
-- ============================================================================
-- Quiz 1 (Tipo C, approvato): 4 domande collegate ai chunks di Basi di Dati
-- Quiz 2 (Tipo B, Giulia): 2 domande
-- Quiz 3 (Tipo A, piano): 2 domande

INSERT INTO domande_quiz (id, quiz_id, testo, tipo, opzioni_json, risposta_corretta, spiegazione, ordine, chunk_id) VALUES
-- Quiz 1: Test Ufficiale
(1,  1, 'Quale proprietà deve avere una chiave primaria?',
   'scelta_multipla',
   '["Può contenere valori NULL", "Identifica univocamente ogni tupla", "Può avere duplicati", "È sempre un numero intero"]',
   'Identifica univocamente ogni tupla',
   'La chiave primaria deve essere unica e non nulla per ogni record. Garantisce l''identificazione univoca di ogni tupla nella relazione.',
   1, 2),
(2,  1, 'Il vincolo di integrità referenziale garantisce che:',
   'scelta_multipla',
   '["La chiave primaria sia unica", "Ogni FK corrisponda a un valore esistente nella tabella referenziata", "Le tuple siano ordinate", "Gli attributi abbiano domini compatibili"]',
   'Ogni FK corrisponda a un valore esistente nella tabella referenziata',
   'L''integrità referenziale impedisce di avere valori di chiave esterna che non corrispondono ad alcuna chiave primaria nella tabella referenziata.',
   2, 2),
(3,  1, 'La 3NF (Terza Forma Normale) elimina:',
   'scelta_multipla',
   '["Le dipendenze parziali", "Le dipendenze transitive", "I valori NULL", "Gli attributi multivalore"]',
   'Le dipendenze transitive',
   'La 2NF elimina le dipendenze parziali. La 3NF va oltre ed elimina le dipendenze transitive: ogni attributo non chiave deve dipendere direttamente dalla chiave primaria, non da altri attributi non chiave.',
   3, 3),
(4,  1, 'Il comando SQL per filtrare gruppi aggregati è:',
   'scelta_multipla',
   '["WHERE", "HAVING", "GROUP BY", "ORDER BY"]',
   'HAVING',
   'WHERE filtra le righe prima dell''aggregazione. HAVING filtra i gruppi dopo l''aggregazione con GROUP BY. Non possono essere usati in modo intercambiabile.',
   4, 6),
-- Quiz 2: Ripasso Giulia
(5,  2, 'Cos''è una relazione nel modello relazionale?',
   'scelta_multipla',
   '["Un''associazione tra oggetti reali", "Un sottoinsieme del prodotto cartesiano di domini", "Un tipo di JOIN tra tabelle", "Un vincolo di integrità"]',
   'Un sottoinsieme del prodotto cartesiano di domini',
   'Nel modello relazionale, una relazione è formalmente un sottoinsieme del prodotto cartesiano degli insiemi di valori definiti dai domini degli attributi.',
   1, 1),
(6,  2, 'La BCNF è una versione più restrittiva di:',
   'vero_falso',
   NULL,
   'true',
   'Vero. La Boyce-Codd Normal Form (BCNF) è più restrittiva della 3NF: richiede che per ogni dipendenza funzionale X→Y, X sia una superchiave. Esistono relazioni in 3NF ma non in BCNF.',
   2, 3),
-- Quiz 3: Piano Giulia (Machine Learning)
(7,  3, 'Nell''apprendimento supervisionato, la regressione predice:',
   'scelta_multipla',
   '["Una categoria discreta", "Un valore continuo", "Un cluster di dati", "Una regola associativa"]',
   'Un valore continuo',
   'La classificazione predice categorie discrete. La regressione predice valori continui, come il prezzo di un immobile o la temperatura futura.',
   1, 7),
(8,  3, 'L''overfitting è caratterizzato da:',
   'scelta_multipla',
   '["Alta varianza, buona generalizzazione", "Alta varianza, scarsa generalizzazione", "Alto bias, scarsa generalizzazione", "Bassa varianza, alto bias"]',
   'Alta varianza, scarsa generalizzazione',
   'Un modello in overfitting memorizza il training set (alta varianza) ma non generalizza ai dati nuovi (scarsa performance sul test set). È il contrario dell''underfitting (alto bias).',
   2, 8);

-- ============================================================================
-- STEP 2: TENTATIVI QUIZ E RISPOSTE
-- ============================================================================
-- Giulia ha completato il quiz ufficiale (Tipo C) → alimenta analytics docente
-- Marco ha completato il quiz ufficiale → alimenta analytics docente
-- Giulia ha completato il ripasso personale (Tipo B) → privato

-- Tentativo 1: Giulia, Quiz Ufficiale (punteggio 75%)
INSERT INTO tentativi_quiz (id, quiz_id, studente_id, punteggio, aree_deboli_json, completato, created_at) VALUES
(1, 1, 1, 75.0, '["normalizzazione", "HAVING", "dipendenze funzionali"]', 1, '2025-10-15 10:30:00');

INSERT INTO risposte_domande (tentativo_id, domanda_id, risposta_data, corretta) VALUES
(1, 1, 'Identifica univocamente ogni tupla', 1),  -- corretta
(1, 2, 'La chiave primaria sia unica',       0),  -- sbagliata
(1, 3, 'Le dipendenze transitive',           1),  -- corretta
(1, 4, 'WHERE',                              0);  -- sbagliata

-- Tentativo 2: Marco, Quiz Ufficiale (punteggio 100%)
INSERT INTO tentativi_quiz (id, quiz_id, studente_id, punteggio, aree_deboli_json, completato, created_at) VALUES
(2, 1, 2, 100.0, '[]', 1, '2025-10-15 11:00:00');

INSERT INTO risposte_domande (tentativo_id, domanda_id, risposta_data, corretta) VALUES
(2, 1, 'Identifica univocamente ogni tupla',                          1),
(2, 2, 'Ogni FK corrisponda a un valore esistente nella tabella referenziata', 1),
(2, 3, 'Le dipendenze transitive',                                    1),
(2, 4, 'HAVING',                                                      1);

-- Tentativo 3: Sara, Quiz Ufficiale (punteggio 50%)
INSERT INTO tentativi_quiz (id, quiz_id, studente_id, punteggio, aree_deboli_json, completato, created_at) VALUES
(3, 1, 3, 50.0, '["integrità referenziale", "normalizzazione", "SQL aggregazione"]', 1, '2025-10-16 09:15:00');

INSERT INTO risposte_domande (tentativo_id, domanda_id, risposta_data, corretta) VALUES
(3, 1, 'Identifica univocamente ogni tupla', 1),  -- corretta
(3, 2, 'La chiave primaria sia unica',       0),  -- sbagliata
(3, 3, 'I valori NULL',                      0),  -- sbagliata
(3, 4, 'GROUP BY',                           0);  -- sbagliata

-- Tentativo 4: Giulia, Ripasso Personale (Tipo B — privato)
INSERT INTO tentativi_quiz (id, quiz_id, studente_id, punteggio, aree_deboli_json, completato, created_at) VALUES
(4, 2, 1, 50.0, '["prodotto cartesiano", "BCNF"]', 1, '2025-10-14 16:00:00');

INSERT INTO risposte_domande (tentativo_id, domanda_id, risposta_data, corretta) VALUES
(4, 5, 'Un''associazione tra oggetti reali', 0),  -- sbagliata
(4, 6, 'true',                               1);  -- corretta

-- ============================================================================
-- STEP 3B: PIANI PERSONALIZZATI
-- ============================================================================
-- Piano 1: Giulia, tipo 'esame', Basi di Dati → struttura gerarchica completa
-- Piano 2: Marco, tipo 'libero', crescita personale su Python avanzato

INSERT INTO piani_personalizzati (id, studente_id, titolo, descrizione, tipo, corso_universitario_id, stato, created_at, aggiornato_il) VALUES
(1, 1,
   'Preparazione Esame Basi di Dati',
   'Piano strutturato per la preparazione all''esame di Basi di Dati del Prof. Rossi. Focus su normalizzazione e SQL avanzato, aree più critiche dai risultati del test.',
   'esame', 1, 'attivo',
   '2025-10-16 08:00:00', '2025-10-16 08:00:00'),
(2, 2,
   'Approfondimento Python per Data Science',
   'Piano libero per consolidare le competenze Python orientate all''analisi dati, in preparazione al corso di Machine Learning del prossimo semestre.',
   'libero', NULL, 'attivo',
   '2025-10-10 09:00:00', '2025-10-10 09:00:00');

-- ============================================================================
-- PIANO MATERIALI UTILIZZATI
-- ============================================================================
-- Piano 1 (Giulia, esame BdD): usa chunks di entrambi i materiali di BdD
-- Piano 2 (Marco, libero): usa chunks di ML (più vicino al suo obiettivo)

INSERT INTO piano_materiali_utilizzati (piano_id, chunk_id) VALUES
(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6),  -- piano Giulia: tutti i chunks BdD
(2, 7), (2, 8), (2, 9);                             -- piano Marco: tutti i chunks ML

-- ============================================================================
-- PIANO CAPITOLI
-- ============================================================================
-- Piano 1 (Giulia): 2 capitoli
-- Piano 2 (Marco): 1 capitolo

INSERT INTO piano_capitoli (id, piano_id, titolo, descrizione, ordine, completato) VALUES
(1, 1, 'Modello Relazionale e Normalizzazione',
   'Fondamenti teorici: relazioni, chiavi, vincoli di integrità e forme normali.',
   1, 0),
(2, 1, 'SQL Pratico',
   'Padronanza del linguaggio SQL: query di base, JOIN e aggregazioni.',
   2, 0),
(3, 2, 'Python per l''Analisi Dati',
   'Librerie Python fondamentali per il data science: NumPy, Pandas, visualizzazione.',
   1, 0);

-- ============================================================================
-- PIANO PARAGRAFI
-- ============================================================================

INSERT INTO piano_paragrafi (id, capitolo_id, titolo, descrizione, ordine, completato) VALUES
-- Capitolo 1 (Modello Relazionale)
(1, 1, 'Concetti base del modello relazionale',   'Relazioni, schemi, istanze, domini.',                    1, 1), -- completato
(2, 1, 'Chiavi e vincoli di integrità',            'PK, FK, NOT NULL, UNIQUE e integrità referenziale.',     2, 0),
(3, 1, 'Normalizzazione (1NF → BCNF)',             'Forme normali e dipendenze funzionali.',                  3, 0),
-- Capitolo 2 (SQL)
(4, 2, 'SELECT, WHERE, ORDER BY',                  'Interrogazioni di base e filtri.',                        1, 0),
(5, 2, 'JOIN tra tabelle',                         'INNER JOIN, LEFT JOIN e varianti.',                       2, 0),
(6, 2, 'GROUP BY, HAVING e aggregazioni',          'Funzioni aggregate e raggruppamenti.',                    3, 0),
-- Capitolo 3 (Python - piano Marco)
(7, 3, 'NumPy e operazioni vettoriali',            'Array, operazioni matriciali, broadcasting.',             1, 0),
(8, 3, 'Pandas per la manipolazione dei dati',     'DataFrame, Series, merge, groupby.',                     2, 0);

-- ============================================================================
-- PIANO CONTENUTI
-- ============================================================================
-- Paragrafo 1 (completato): ha una lezione già generata
-- Paragrafo 2: ha lezione + flashcard
-- Paragrafo 3: ha lezione + quiz (quiz Tipo A, id=3 per il piano ML)
-- Paragrafi rimanenti: vuoti (contenuto generato on-demand)

INSERT INTO piano_contenuti (id, paragrafo_id, tipo, contenuto_json, quiz_id, chunk_ids_utilizzati, generato_al_momento) VALUES
-- Paragrafo 1: lezione (pre-generata, completata)
(1, 1, 'lezione',
   '{"testo": "## Modello Relazionale\n\nIl modello relazionale organizza i dati in **relazioni** (tabelle). Ogni relazione è caratterizzata da:\n\n- **Schema**: nome della relazione + lista degli attributi con i rispettivi domini\n- **Istanza**: insieme di tuple (righe) che soddisfano lo schema\n\n### Concetti chiave\n\n**Dominio**: insieme di valori ammissibili per un attributo (es: interi, stringhe, date).\n\n**Tupla**: una singola riga della relazione. Ogni tupla assegna un valore a ogni attributo.\n\n**Grado**: numero di attributi della relazione.\n\n**Cardinalità**: numero di tuple nell''istanza corrente.\n\n> 📌 Il modello relazionale fu introdotto da E.F. Codd nel 1970 e rimane il paradigma dominante nei DBMS commerciali (Oracle, PostgreSQL, MySQL, SQLite)."}',
   NULL, '[1]', 0),

-- Paragrafo 2: lezione + flashcard
(2, 2, 'lezione',
   '{"testo": "## Chiavi e Vincoli di Integrità\n\n### Chiave Primaria (PK)\nUn insieme **minimale** di attributi che identifica univocamente ogni tupla. Deve essere:\n- **Unica**: non possono esistere due tuple con la stessa PK\n- **Non nulla**: nessun attributo della PK può essere NULL\n\n### Chiave Esterna (FK)\nUn attributo (o insieme) che referenzia la PK di un''altra relazione. Implementa il **vincolo di integrità referenziale**: ogni valore FK deve corrispondere a un valore PK esistente nella tabella referenziata.\n\n### Altri vincoli\n- **NOT NULL**: l''attributo non può essere NULL\n- **UNIQUE**: i valori devono essere distinti (ma ammette NULL)\n- **CHECK**: condizione booleana sul valore dell''attributo"}',
   NULL, '[2]', 0),
(3, 2, 'flashcard',
   '[{"domanda": "Cosè una chiave primaria?", "risposta": "Un insieme minimale di attributi che identifica univocamente ogni tupla. Deve essere unica e non nulla."},
     {"domanda": "Cosè il vincolo di integrita referenziale?", "risposta": "Garantisce che ogni valore di chiave esterna corrisponda a un valore esistente nella chiave primaria della tabella referenziata."},
     {"domanda": "Qual e la differenza tra PRIMARY KEY e UNIQUE?", "risposta": "Entrambe garantiscono l unicita, ma PRIMARY KEY non ammette NULL mentre UNIQUE si. Ogni tabella ha una sola PK ma puo avere piu constraint UNIQUE."},
     {"domanda": "Quando si verifica una violazione dell integrita referenziale?", "risposta": "Quando si inserisce un valore FK che non esiste come PK nella tabella referenziata, o si elimina una riga della tabella referenziata senza gestire le FK collegate."}]',
   NULL, '[2]', 0),

-- Paragrafo 3: lezione (normalizzazione)
(4, 3, 'lezione',
   '{"testo": "## Normalizzazione\n\nLa normalizzazione riduce la **ridondanza** e previene le **anomalie** di inserimento, aggiornamento e cancellazione.\n\n### 1NF — Prima Forma Normale\nOgni attributo deve contenere valori **atomici** (indivisibili). Non sono ammessi attributi multivalore o gruppi ripetuti.\n\n### 2NF — Seconda Forma Normale\nDeve essere in 1NF. Ogni attributo non chiave deve dipendere **funzionalmente** dall''intera chiave primaria, non da una parte di essa (nessuna dipendenza parziale).\n\n### 3NF — Terza Forma Normale\nDeve essere in 2NF. Ogni attributo non chiave deve dipendere **direttamente** dalla PK, non transitivamente tramite altri attributi non chiave.\n\n### BCNF — Boyce-Codd Normal Form\nVersione più restrittiva della 3NF. Per ogni dipendenza funzionale X→Y, X deve essere una superchiave."}',
   NULL, '[3]', 0),

-- Paragrafo 7: quiz nel piano di Marco (Machine Learning)
(5, 7, 'lezione',
   '{"testo": "## NumPy — Operazioni Vettoriali\n\nNumPy e la libreria fondamentale per il calcolo numerico in Python. Introduce ndarray, un array N-dimensionale omogeneo molto piu efficiente delle liste Python standard.\n\n### Creazione di array\nimport numpy as np\na = np.array([1, 2, 3, 4, 5])\nb = np.zeros((3, 3))\nc = np.linspace(0, 1, 100)\n\n### Broadcasting\nNumPy estende automaticamente array di forme diverse per operazioni elemento per elemento. Permette operazioni vettoriali senza loop Python espliciti."}',
   NULL, '[7, 8]', 1);  -- generato on-demand

-- ============================================================================
-- STEP 4: LEZIONI DEI CORSI
-- ============================================================================
-- Lezione 1: Basi di Dati, approvata (approvato=1) → visibile agli studenti
-- Lezione 2: Basi di Dati, bozza (approvato=0) → visibile solo al docente

INSERT INTO lezioni_corso (id, corso_universitario_id, docente_id, titolo, contenuto_md, creato_da, approvato, chunk_ids_utilizzati, created_at, aggiornato_il) VALUES
(1, 1, 1,
   'Lezione 1 — Il Modello Relazionale',
   '# Il Modello Relazionale

## Introduzione

Il modello relazionale, introdotto da E.F. Codd nel 1970, è il paradigma dominante per i sistemi di gestione di basi di dati (DBMS) commerciali. Si basa su solide fondamenta matematiche derivate dalla teoria degli insiemi e dalla logica del primo ordine.

## Struttura fondamentale

Una **relazione** è un sottoinsieme del prodotto cartesiano di uno o più domini. In pratica, corrisponde a una tabella con righe (tuple) e colonne (attributi).

### Componenti
- **Schema**: definisce la struttura (nome + attributi + domini)
- **Istanza**: i dati effettivi in un dato momento (insieme di tuple)

## Chiavi e vincoli

La **chiave primaria** identifica univocamente ogni tupla. La **chiave esterna** implementa l''integrità referenziale tra tabelle. Questi meccanismi garantiscono la coerenza e l''integrità dei dati.

## Normalizzazione

La normalizzazione organizza le relazioni per minimizzare la ridondanza attraverso le forme normali (1NF, 2NF, 3NF, BCNF).',
   'ai', 1, '[1, 2, 3]',
   '2025-09-20 10:00:00', '2025-09-22 14:00:00'),

(2, 1, 1,
   'Lezione 2 — SQL: dalle basi alle query avanzate',
   '# SQL — Structured Query Language

## Bozza in revisione

Questa lezione è in fase di revisione da parte del docente.',
   'ai', 0, '[4, 5, 6]',
   '2025-09-25 11:00:00', '2025-09-25 11:00:00');
