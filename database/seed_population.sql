-- ============================================================================
-- LearnAI Platform — Data Population per Demo Cliente
-- ============================================================================
PRAGMA foreign_keys = OFF;

-- ============================================================================
-- PARTE 1 — CORSI DI LAUREA (aggiunti ai 3 esistenti)
-- ============================================================================
INSERT OR IGNORE INTO corsi_di_laurea (id, nome, facolta) VALUES
(4, 'Ingegneria Gestionale',         'Ingegneria'),
(5, 'Scienze e Tecnologie Informatiche', 'Scienze MMFFNN'),
(6, 'Ingegneria Biomedica',          'Ingegneria'),
(7, 'Data Science e Intelligenza Artificiale', 'Scienze MMFFNN');

-- ============================================================================
-- PARTE 2 — DOCENTI (~30, ID 200-229)
-- Hash password: pbkdf2:sha256:600000$placeholder — in produzione rigenerare
-- ============================================================================
INSERT OR IGNORE INTO users (id, nome, cognome, email, password_hash, ruolo, stato, matricola_docente, dipartimento) VALUES
(200, 'Alessandro',  'Mancini',    'a.mancini@unina.it',     'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2020-101', 'Ingegneria Informatica'),
(201, 'Francesca',   'De Luca',    'f.deluca@unina.it',      'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2018-102', 'Matematica e Applicazioni'),
(202, 'Roberto',     'Colombo',    'r.colombo@unina.it',     'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2019-103', 'Ingegneria Elettrica'),
(203, 'Valentina',   'Greco',      'v.greco@unina.it',       'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2021-104', 'Fisica'),
(204, 'Marco',       'Fontana',    'm.fontana@unina.it',     'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2017-105', 'Ingegneria Informatica'),
(205, 'Silvia',      'Moretti',    's.moretti@unina.it',     'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2020-106', 'Ingegneria Gestionale'),
(206, 'Andrea',      'Barbieri',   'a.barbieri@unina.it',    'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2016-107', 'Matematica e Applicazioni'),
(207, 'Lucia',       'Ricci',      'l.ricci@unina.it',       'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2022-108', 'Ingegneria Biomedica'),
(208, 'Giuseppe',    'Conti',      'g.conti@unina.it',       'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2015-109', 'Ingegneria Informatica'),
(209, 'Elena',       'Marchetti',  'e.marchetti@unina.it',   'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2019-110', 'Scienze Economiche'),
(210, 'Davide',      'Ferrara',    'd.ferrara@unina.it',     'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2021-111', 'Ingegneria Elettrica'),
(211, 'Chiara',      'Leone',      'c.leone@unina.it',       'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2020-112', 'Ingegneria Informatica'),
(212, 'Stefano',     'Galli',      's.galli@unina.it',       'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2018-113', 'Fisica'),
(213, 'Paola',       'Santoro',    'p.santoro@unina.it',     'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2017-114', 'Ingegneria Biomedica'),
(214, 'Luca',        'Caruso',     'l.caruso@unina.it',      'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2023-115', 'Ingegneria Gestionale'),
(215, 'Martina',     'Pellegrini', 'm.pellegrini@unina.it',  'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2019-116', 'Matematica e Applicazioni'),
(216, 'Fabio',       'Vitale',     'f.vitale@unina.it',      'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2016-117', 'Ingegneria Informatica'),
(217, 'Sara',        'Lombardi',   's.lombardi@unina.it',    'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2022-118', 'Scienze Economiche'),
(218, 'Antonio',     'Costa',      'a.costa@unina.it',       'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2020-119', 'Ingegneria Elettrica'),
(219, 'Federica',    'Rinaldi',    'f.rinaldi@unina.it',     'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2021-120', 'Ingegneria Informatica'),
(220, 'Nicola',      'Benedetti',  'n.benedetti@unina.it',   'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2018-121', 'Ingegneria Biomedica'),
(221, 'Giulia',      'Testa',      'g.testa@unina.it',       'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2023-122', 'Ingegneria Gestionale'),
(222, 'Pietro',      'Marini',     'p.marini@unina.it',      'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2017-123', 'Fisica'),
(223, 'Ilaria',      'Fabbri',     'i.fabbri@unina.it',      'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2019-124', 'Matematica e Applicazioni'),
(224, 'Tommaso',     'Grassi',     't.grassi@unina.it',      'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2020-125', 'Ingegneria Informatica'),
(225, 'Aurora',      'Palmieri',   'a.palmieri@unina.it',    'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2022-126', 'Ingegneria Biomedica'),
(226, 'Matteo',      'Serra',      'm.serra@unina.it',       'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2016-127', 'Scienze Economiche'),
(227, 'Giorgia',     'Valentini',  'g.valentini@unina.it',   'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2021-128', 'Ingegneria Gestionale'),
(228, 'Simone',      'Ruggiero',   's.ruggiero@unina.it',    'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2018-129', 'Ingegneria Elettrica'),
(229, 'Claudia',     'Sorrentino', 'c.sorrentino@unina.it',  'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'docente', 'active', 'DOC-2023-130', 'Ingegneria Informatica');

-- ============================================================================
-- PARTE 3 — NUOVI STUDENTI (ID 300-319) con profili diversificati
-- ============================================================================
INSERT OR IGNORE INTO users (id, nome, cognome, email, password_hash, ruolo, stato, matricola_studente, corso_di_laurea_id, anno_corso) VALUES
-- CDL 1: Ingegneria Informatica
(300, 'Lorenzo',  'Amato',      'l.amato@studenti.unina.it',      'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'studente', 'active', 'N86010001', 1, 2),
(301, 'Alessia',  'Marino',     'a.marino@studenti.unina.it',     'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'studente', 'active', 'N86010002', 1, 3),
(302, 'Mattia',   'Parisi',     'm.parisi@studenti.unina.it',     'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'studente', 'active', 'N86010003', 1, 1),
-- CDL 2: Informatica
(303, 'Sofia',    'Ferraro',    's.ferraro@studenti.unina.it',    'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'studente', 'active', 'N86010004', 2, 2),
(304, 'Riccardo', 'Gallo',      'r.gallo@studenti.unina.it',     'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'studente', 'active', 'N86010005', 2, 1),
(305, 'Emma',     'Gentile',    'e.gentile@studenti.unina.it',   'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'studente', 'active', 'N86010006', 2, 3),
-- CDL 3: Ingegneria Elettronica
(306, 'Federico', 'Silvestri',  'f.silvestri@studenti.unina.it',  'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'studente', 'active', 'N86010007', 3, 2),
(307, 'Beatrice', 'Pagano',     'b.pagano@studenti.unina.it',    'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'studente', 'active', 'N86010008', 3, 1),
-- CDL 4: Ingegneria Gestionale
(308, 'Diego',    'Vitali',     'd.vitali@studenti.unina.it',    'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'studente', 'active', 'N86010009', 4, 2),
(309, 'Alice',    'Sala',       'a.sala@studenti.unina.it',      'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'studente', 'active', 'N86010010', 4, 1),
-- CDL 5: Scienze e Tecnologie Informatiche
(310, 'Gabriele', 'Marchetti',  'g.marchetti@studenti.unina.it', 'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'studente', 'active', 'N86010011', 5, 2),
(311, 'Viola',    'De Angelis', 'v.deangelis@studenti.unina.it', 'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'studente', 'active', 'N86010012', 5, 3),
-- CDL 6: Ingegneria Biomedica
(312, 'Leonardo', 'Monti',      'l.monti@studenti.unina.it',     'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'studente', 'active', 'N86010013', 6, 2),
(313, 'Anna',     'Guerra',     'a.guerra@studenti.unina.it',    'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'studente', 'active', 'N86010014', 6, 1),
-- CDL 7: Data Science e IA
(314, 'Edoardo',  'Bianco',     'e.bianco@studenti.unina.it',    'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'studente', 'active', 'N86010015', 7, 2),
(315, 'Camilla',  'Rossi',      'c.rossi@studenti.unina.it',     'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'studente', 'active', 'N86010016', 7, 1),
-- Mix extra
(316, 'Samuele',  'Riva',       's.riva@studenti.unina.it',      'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'studente', 'active', 'N86010017', 1, 2),
(317, 'Ginevra',  'Palumbo',    'g.palumbo@studenti.unina.it',   'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'studente', 'active', 'N86010018', 4, 3),
(318, 'Filippo',  'Basile',     'f.basile@studenti.unina.it',    'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'studente', 'active', 'N86010019', 7, 2),
(319, 'Noemi',    'Rizzi',      'n.rizzi@studenti.unina.it',     'pbkdf2:sha256:600000$X7k9Lm$8a4b2c1d3e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b', 'studente', 'active', 'N86010020', 2, 2);

-- Completa users 100-104 con dati mancanti
UPDATE users SET matricola_docente='DOC-2022-100', dipartimento='Ingegneria Informatica' WHERE id=100 AND matricola_docente IS NULL;
UPDATE users SET matricola_studente='N86008001', corso_di_laurea_id=1, anno_corso=2 WHERE id=101 AND matricola_studente IS NULL;
UPDATE users SET matricola_docente='DOC-2021-099', dipartimento='Matematica e Applicazioni' WHERE id=102 AND matricola_docente IS NULL;
UPDATE users SET matricola_studente='N86008002', corso_di_laurea_id=2, anno_corso=1 WHERE id=103 AND matricola_studente IS NULL;
UPDATE users SET matricola_studente='N86008003', corso_di_laurea_id=3, anno_corso=2 WHERE id=104 AND matricola_studente IS NULL;

-- ============================================================================
-- PARTE 4 — NUOVI CORSI UNIVERSITARI (ID 110-129)
-- ============================================================================
INSERT OR IGNORE INTO corsi_universitari (id, nome, descrizione, docente_id, cfu, ore_lezione, anno_di_corso, semestre, livello, attivo) VALUES
(110, 'Programmazione I',                 'Fondamenti di programmazione imperativa e orientata agli oggetti in Java.',                           200, 12, 96,  1, 1, 'base', 1),
(111, 'Programmazione II',                'Programmazione avanzata: generics, design pattern, strutture dati in Java.',                          200, 9,  72,  1, 2, 'intermedio', 1),
(112, 'Reti di Calcolatori',              'Architetture di rete, protocolli TCP/IP, sicurezza e applicazioni distribuite.',                      204, 9,  72,  2, 2, 'intermedio', 1),
(113, 'Sistemi Operativi',                'Gestione processi, memoria, file system. Programmazione concorrente in C.',                           208, 9,  72,  2, 1, 'intermedio', 1),
(114, 'Ingegneria del Software',          'Ciclo di vita del software, UML, pattern architetturali, testing e qualita.',                         211, 9,  72,  3, 1, 'avanzato', 1),
(115, 'Fisica I',                         'Meccanica classica, termodinamica, onde. Esperimenti di laboratorio.',                                203, 9,  72,  1, 1, 'base', 1),
(116, 'Fisica II',                        'Elettromagnetismo, ottica, introduzione alla fisica moderna.',                                        212, 9,  72,  1, 2, 'base', 1),
(117, 'Calcolo Numerico',                 'Metodi numerici per equazioni, interpolazione, integrazione e sistemi lineari.',                      206, 6,  48,  2, 2, 'intermedio', 1),
(118, 'Elettronica Digitale',             'Circuiti logici combinatori e sequenziali, FPGA, linguaggio VHDL.',                                   210, 9,  72,  2, 1, 'intermedio', 1),
(119, 'Probabilita e Statistica',         'Variabili aleatorie, distribuzioni, stima parametrica, test di ipotesi.',                             215, 6,  48,  2, 1, 'intermedio', 1),
(120, 'Machine Learning',                 'Apprendimento supervisionato e non supervisionato, reti neurali, validazione modelli.',               219, 9,  72,  3, 1, 'avanzato', 1),
(121, 'Economia e Gestione delle Imprese','Strategia aziendale, analisi di bilancio, marketing e operations management.',                        209, 9,  72,  2, 1, 'intermedio', 1),
(122, 'Ricerca Operativa',                'Programmazione lineare, grafi, ottimizzazione combinatoria e metaeuristiche.',                         205, 6,  48,  3, 1, 'avanzato', 1),
(123, 'Bioingegneria Elettronica',        'Sensori biomedici, acquisizione segnali biologici, strumentazione clinica.',                           207, 9,  72,  2, 2, 'intermedio', 1),
(124, 'Elaborazione di Segnali Biomedici','Filtraggio, analisi spettrale, ECG/EEG/EMG digitali.',                                                213, 9,  72,  3, 1, 'avanzato', 1),
(125, 'Fondamenti di Informatica',        'Logica, automi, linguaggi formali, complessita computazionale.',                                      216, 9,  72,  1, 1, 'base', 1),
(126, 'Deep Learning',                    'Reti convoluzionali, ricorrenti, transformer, tecniche di addestramento avanzate.',                   224, 6,  48,  3, 2, 'avanzato', 1),
(127, 'Analisi Matematica II',            'Funzioni di piu variabili, integrali multipli, serie, equazioni differenziali.',                      201, 9,  72,  2, 1, 'intermedio', 1),
(128, 'Controlli Automatici',             'Sistemi dinamici, stabilita, controllori PID, analisi in frequenza.',                                  218, 9,  72,  3, 2, 'avanzato', 1),
(129, 'Natural Language Processing',      'Tokenizzazione, word embeddings, modelli sequenziali, LLM e applicazioni.',                           229, 6,  48,  3, 2, 'avanzato', 1);

-- ============================================================================
-- PARTE 5 — MAPPATURA CORSI DI LAUREA ↔ CORSI UNIVERSITARI
-- ============================================================================

-- CDL 1: Ingegneria Informatica (obbligatori principali + facoltativi)
INSERT OR IGNORE INTO corsi_laurea_universitari (corso_di_laurea_id, corso_universitario_id, obbligatorio) VALUES
(1, 110, 1), (1, 111, 1), (1, 112, 1), (1, 113, 1), (1, 114, 1),
(1, 115, 1), (1, 127, 1),
(1, 117, 0), (1, 119, 0), (1, 120, 0), (1, 126, 0);

-- CDL 2: Informatica
INSERT OR IGNORE INTO corsi_laurea_universitari (corso_di_laurea_id, corso_universitario_id, obbligatorio) VALUES
(2, 110, 1), (2, 111, 1), (2, 125, 1), (2, 113, 1),
(2, 119, 1), (2, 112, 0), (2, 120, 0), (2, 129, 0);

-- CDL 3: Ingegneria Elettronica
INSERT OR IGNORE INTO corsi_laurea_universitari (corso_di_laurea_id, corso_universitario_id, obbligatorio) VALUES
(3, 115, 1), (3, 116, 1), (3, 118, 1), (3, 128, 1), (3, 127, 1),
(3, 117, 0), (3, 112, 0);

-- CDL 4: Ingegneria Gestionale
INSERT OR IGNORE INTO corsi_laurea_universitari (corso_di_laurea_id, corso_universitario_id, obbligatorio) VALUES
(4, 121, 1), (4, 122, 1), (4, 119, 1), (4, 110, 1), (4, 115, 1),
(4, 117, 0), (4, 114, 0);

-- CDL 5: Scienze e Tecnologie Informatiche
INSERT OR IGNORE INTO corsi_laurea_universitari (corso_di_laurea_id, corso_universitario_id, obbligatorio) VALUES
(5, 110, 1), (5, 111, 1), (5, 125, 1), (5, 112, 1), (5, 113, 1),
(5, 119, 1), (5, 120, 0), (5, 126, 0), (5, 129, 0);

-- CDL 6: Ingegneria Biomedica
INSERT OR IGNORE INTO corsi_laurea_universitari (corso_di_laurea_id, corso_universitario_id, obbligatorio) VALUES
(6, 115, 1), (6, 116, 1), (6, 123, 1), (6, 124, 1), (6, 127, 1),
(6, 118, 0), (6, 119, 0);

-- CDL 7: Data Science e IA
INSERT OR IGNORE INTO corsi_laurea_universitari (corso_di_laurea_id, corso_universitario_id, obbligatorio) VALUES
(7, 119, 1), (7, 120, 1), (7, 126, 1), (7, 129, 1), (7, 110, 1),
(7, 125, 0), (7, 122, 0);

PRAGMA foreign_keys = ON;
