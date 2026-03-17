-- ============================================================================
-- Data Population — Corsi Umanistici e Giuridici
-- ============================================================================
PRAGMA foreign_keys = OFF;

-- ============================================================================
-- CORSI DI LAUREA
-- ============================================================================
INSERT OR IGNORE INTO corsi_di_laurea (id, nome, facolta) VALUES
(8,  'Giurisprudenza',                        'Giurisprudenza'),
(9,  'Lettere Moderne',                       'Lettere e Filosofia'),
(10, 'Filosofia',                             'Lettere e Filosofia'),
(11, 'Scienze Politiche e Relazioni Internazionali', 'Scienze Politiche'),
(12, 'Scienze della Comunicazione',           'Sociologia');

-- ============================================================================
-- DOCENTI UMANISTICI/GIURIDICI (ID 230-244)
-- ============================================================================
INSERT OR IGNORE INTO users (id, nome, cognome, email, password_hash, ruolo, stato, matricola_docente, dipartimento) VALUES
(230, 'Giovanni',   'De Santis',   'g.desantis@unina.it',    'placeholder_hash', 'docente', 'active', 'DOC-2017-201', 'Giurisprudenza'),
(231, 'Maria',      'Caputo',      'm.caputo@unina.it',      'placeholder_hash', 'docente', 'active', 'DOC-2016-202', 'Giurisprudenza'),
(232, 'Raffaele',   'Esposito',    'r.esposito@unina.it',    'placeholder_hash', 'docente', 'active', 'DOC-2019-203', 'Giurisprudenza'),
(233, 'Patrizia',   'Ruocco',      'p.ruocco@unina.it',      'placeholder_hash', 'docente', 'active', 'DOC-2018-204', 'Studi Umanistici'),
(234, 'Massimo',    'Ferrante',    'm.ferrante@unina.it',    'placeholder_hash', 'docente', 'active', 'DOC-2015-205', 'Studi Umanistici'),
(235, 'Alessandra', 'Piscitelli',  'a.piscitelli@unina.it',  'placeholder_hash', 'docente', 'active', 'DOC-2020-206', 'Studi Umanistici'),
(236, 'Carlo',      'Iannone',     'c.iannone@unina.it',     'placeholder_hash', 'docente', 'active', 'DOC-2017-207', 'Filosofia'),
(237, 'Teresa',     'Amabile',     't.amabile@unina.it',     'placeholder_hash', 'docente', 'active', 'DOC-2019-208', 'Filosofia'),
(238, 'Franco',     'Scognamiglio','f.scognamiglio@unina.it', 'placeholder_hash', 'docente', 'active', 'DOC-2016-209', 'Scienze Politiche'),
(239, 'Daniela',    'Coppola',     'd.coppola@unina.it',     'placeholder_hash', 'docente', 'active', 'DOC-2021-210', 'Scienze Politiche'),
(240, 'Vincenzo',   'Aiello',      'v.aiello@unina.it',      'placeholder_hash', 'docente', 'active', 'DOC-2018-211', 'Scienze Sociali'),
(241, 'Luisa',      'Cirillo',     'l.cirillo@unina.it',     'placeholder_hash', 'docente', 'active', 'DOC-2020-212', 'Scienze Sociali'),
(242, 'Enrico',     'Prisco',      'e.prisco@unina.it',      'placeholder_hash', 'docente', 'active', 'DOC-2022-213', 'Giurisprudenza'),
(243, 'Rosanna',    'Langella',    'r.langella@unina.it',    'placeholder_hash', 'docente', 'active', 'DOC-2019-214', 'Studi Umanistici'),
(244, 'Salvatore',  'Montella',    's.montella@unina.it',    'placeholder_hash', 'docente', 'active', 'DOC-2017-215', 'Scienze Politiche');

-- ============================================================================
-- CORSI UNIVERSITARI (ID 130-149)
-- ============================================================================
INSERT OR IGNORE INTO corsi_universitari (id, nome, descrizione, docente_id, cfu, ore_lezione, anno_di_corso, semestre, livello, attivo) VALUES
-- Giurisprudenza
(130, 'Diritto Privato',                    'Principi generali del diritto civile: persone, obbligazioni, contratti, proprieta, responsabilita civile.',           230, 12, 96, 1, 1, 'base', 1),
(131, 'Diritto Costituzionale',             'Fonti del diritto, organi costituzionali, diritti fondamentali, giustizia costituzionale.',                             231, 12, 96, 1, 2, 'base', 1),
(132, 'Diritto Penale',                     'Principi di legalita, tipicita, antigiuridicita e colpevolezza. Reati contro la persona e il patrimonio.',              232, 9,  72, 2, 1, 'intermedio', 1),
(133, 'Diritto dell''Unione Europea',       'Istituzioni UE, fonti del diritto europeo, mercato interno, liberta fondamentali e cittadinanza europea.',              242, 9,  72, 3, 1, 'avanzato', 1),
(134, 'Diritto Commerciale',                'Imprenditore, societa di persone e capitali, titoli di credito, procedure concorsuali.',                                230, 9,  72, 2, 2, 'intermedio', 1),
-- Lettere Moderne
(135, 'Letteratura Italiana',               'Dalle origini al Novecento: Dante, Petrarca, Boccaccio, Manzoni, Pirandello, Montale.',                                233, 12, 96, 1, 1, 'base', 1),
(136, 'Linguistica Generale',               'Fonetica, morfologia, sintassi, semantica e pragmatica. Universali linguistici e variazione.',                          234, 9,  72, 1, 2, 'base', 1),
(137, 'Storia Medievale',                   'Dalla caduta dell''Impero Romano al Rinascimento. Feudalesimo, comuni, crociate, peste nera.',                          243, 9,  72, 2, 1, 'intermedio', 1),
(138, 'Letteratura Latina',                 'Testi fondamentali della latinita: Cicerone, Virgilio, Ovidio, Seneca, Tacito.',                                        235, 9,  72, 2, 2, 'intermedio', 1),
-- Filosofia
(139, 'Storia della Filosofia Antica',      'Da Talete a Plotino: presocratici, Socrate, Platone, Aristotele, stoicismo, epicureismo.',                              236, 12, 96, 1, 1, 'base', 1),
(140, 'Filosofia Morale',                   'Etica normativa: utilitarismo, deontologia kantiana, etica delle virtu. Dilemmi morali contemporanei.',                 237, 9,  72, 2, 1, 'intermedio', 1),
(141, 'Logica e Filosofia del Linguaggio',  'Logica proposizionale e predicativa, teoria degli atti linguistici, significato e riferimento.',                        236, 9,  72, 2, 2, 'intermedio', 1),
-- Scienze Politiche
(142, 'Scienza Politica',                   'Sistemi politici, democrazia, partiti, elezioni, opinione pubblica e comunicazione politica.',                          238, 9,  72, 1, 1, 'base', 1),
(143, 'Relazioni Internazionali',           'Realismo, liberalismo, costruttivismo. ONU, NATO, UE. Conflitti, diplomazia e cooperazione.',                           239, 9,  72, 2, 1, 'intermedio', 1),
(144, 'Economia Politica',                  'Microeconomia e macroeconomia: domanda/offerta, PIL, inflazione, politiche fiscali e monetarie.',                       244, 9,  72, 1, 2, 'base', 1),
-- Scienze della Comunicazione
(145, 'Teoria della Comunicazione',         'Modelli comunicativi, mass media, comunicazione digitale, semiotica e cultura visuale.',                                240, 9,  72, 1, 1, 'base', 1),
(146, 'Sociologia dei Media',               'Effetti dei media, gatekeeping, agenda setting, social media e trasformazione della sfera pubblica.',                   241, 9,  72, 2, 1, 'intermedio', 1),
(147, 'Diritto dell''Informazione',         'Liberta di stampa, diffamazione, privacy, diritto all''oblio, regolamentazione dei media digitali.',                    231, 6,  48, 2, 2, 'intermedio', 1);

-- ============================================================================
-- MAPPATURA CDL ↔ CORSI
-- ============================================================================
-- CDL 8: Giurisprudenza
INSERT OR IGNORE INTO corsi_laurea_universitari (corso_di_laurea_id, corso_universitario_id, obbligatorio) VALUES
(8, 130, 1), (8, 131, 1), (8, 132, 1), (8, 133, 1), (8, 134, 1),
(8, 144, 0), (8, 147, 0);

-- CDL 9: Lettere Moderne
INSERT OR IGNORE INTO corsi_laurea_universitari (corso_di_laurea_id, corso_universitario_id, obbligatorio) VALUES
(9, 135, 1), (9, 136, 1), (9, 137, 1), (9, 138, 1),
(9, 139, 0), (9, 140, 0);

-- CDL 10: Filosofia
INSERT OR IGNORE INTO corsi_laurea_universitari (corso_di_laurea_id, corso_universitario_id, obbligatorio) VALUES
(10, 139, 1), (10, 140, 1), (10, 141, 1),
(10, 135, 0), (10, 136, 0), (10, 137, 0);

-- CDL 11: Scienze Politiche
INSERT OR IGNORE INTO corsi_laurea_universitari (corso_di_laurea_id, corso_universitario_id, obbligatorio) VALUES
(11, 142, 1), (11, 143, 1), (11, 144, 1), (11, 131, 1),
(11, 130, 0), (11, 145, 0);

-- CDL 12: Scienze della Comunicazione
INSERT OR IGNORE INTO corsi_laurea_universitari (corso_di_laurea_id, corso_universitario_id, obbligatorio) VALUES
(12, 145, 1), (12, 146, 1), (12, 147, 1), (12, 136, 1),
(12, 142, 0), (12, 140, 0);

-- ============================================================================
-- STUDENTI UMANISTICI/GIURIDICI (ID 320-339)
-- ============================================================================
INSERT OR IGNORE INTO users (id, nome, cognome, email, password_hash, ruolo, stato, matricola_studente, corso_di_laurea_id, anno_corso) VALUES
-- CDL 8: Giurisprudenza
(320, 'Marco',     'Adinolfi',    'm.adinolfi@studenti.unina.it',   'placeholder_hash', 'studente', 'active', 'N86020001', 8, 2),
(321, 'Francesca', 'Calabrese',   'f.calabrese@studenti.unina.it',  'placeholder_hash', 'studente', 'active', 'N86020002', 8, 1),
(322, 'Antonio',   'Pellegrino',  'a.pellegrino@studenti.unina.it', 'placeholder_hash', 'studente', 'active', 'N86020003', 8, 3),
(323, 'Chiara',    'Sannino',     'c.sannino@studenti.unina.it',    'placeholder_hash', 'studente', 'active', 'N86020004', 8, 2),
-- CDL 9: Lettere Moderne
(324, 'Davide',    'Iervolino',   'd.iervolino@studenti.unina.it',  'placeholder_hash', 'studente', 'active', 'N86020005', 9, 2),
(325, 'Giulia',    'Caiazzo',     'g.caiazzo@studenti.unina.it',    'placeholder_hash', 'studente', 'active', 'N86020006', 9, 1),
(326, 'Matteo',    'Perrotta',    'm.perrotta@studenti.unina.it',   'placeholder_hash', 'studente', 'active', 'N86020007', 9, 3),
-- CDL 10: Filosofia
(327, 'Elena',     'Di Maio',     'e.dimaio@studenti.unina.it',     'placeholder_hash', 'studente', 'active', 'N86020008', 10, 2),
(328, 'Luca',      'Tramontano',  'l.tramontano@studenti.unina.it', 'placeholder_hash', 'studente', 'active', 'N86020009', 10, 1),
-- CDL 11: Scienze Politiche
(329, 'Sara',      'Napolitano',  's.napolitano@studenti.unina.it', 'placeholder_hash', 'studente', 'active', 'N86020010', 11, 2),
(330, 'Roberto',   'Falanga',     'r.falanga@studenti.unina.it',    'placeholder_hash', 'studente', 'active', 'N86020011', 11, 1),
(331, 'Valentina', 'Pinto',       'v.pinto@studenti.unina.it',      'placeholder_hash', 'studente', 'active', 'N86020012', 11, 3),
-- CDL 12: Scienze della Comunicazione
(332, 'Andrea',    'Criscuolo',   'a.criscuolo@studenti.unina.it',  'placeholder_hash', 'studente', 'active', 'N86020013', 12, 2),
(333, 'Ilaria',    'Manzo',       'i.manzo@studenti.unina.it',      'placeholder_hash', 'studente', 'active', 'N86020014', 12, 1),
(334, 'Simone',    'Auriemma',    's.auriemma@studenti.unina.it',   'placeholder_hash', 'studente', 'active', 'N86020015', 12, 3);

-- ============================================================================
-- ISCRIZIONI STUDENTI
-- ============================================================================
INSERT OR IGNORE INTO studenti_corsi (studente_id, corso_universitario_id, anno_accademico, stato, voto) VALUES
-- Marco Adinolfi (CDL8 Giurisp., anno 2)
(320, 130, '2024-2025', 'completato', 27),
(320, 131, '2024-2025', 'completato', 25),
(320, 132, '2025-2026', 'iscritto', NULL),
(320, 134, '2025-2026', 'iscritto', NULL),
-- Francesca Calabrese (CDL8, anno 1)
(321, 130, '2025-2026', 'iscritto', NULL),
(321, 131, '2025-2026', 'iscritto', NULL),
-- Antonio Pellegrino (CDL8, anno 3) — senior giurisprudenza
(322, 130, '2023-2024', 'completato', 30),
(322, 131, '2023-2024', 'completato', 28),
(322, 132, '2024-2025', 'completato', 29),
(322, 133, '2025-2026', 'iscritto', NULL),
(322, 134, '2025-2026', 'iscritto', NULL),
-- Chiara Sannino (CDL8, anno 2)
(323, 130, '2024-2025', 'completato', 24),
(323, 131, '2024-2025', 'completato', 22),
(323, 132, '2025-2026', 'iscritto', NULL),
-- Davide Iervolino (CDL9 Lettere, anno 2)
(324, 135, '2024-2025', 'completato', 28),
(324, 136, '2024-2025', 'completato', 26),
(324, 137, '2025-2026', 'iscritto', NULL),
(324, 138, '2025-2026', 'iscritto', NULL),
-- Giulia Caiazzo (CDL9, anno 1)
(325, 135, '2025-2026', 'iscritto', NULL),
(325, 136, '2025-2026', 'iscritto', NULL),
-- Matteo Perrotta (CDL9, anno 3)
(326, 135, '2023-2024', 'completato', 31),
(326, 136, '2023-2024', 'completato', 29),
(326, 137, '2024-2025', 'completato', 27),
(326, 138, '2025-2026', 'iscritto', NULL),
-- Elena Di Maio (CDL10 Filosofia, anno 2)
(327, 139, '2024-2025', 'completato', 29),
(327, 140, '2025-2026', 'iscritto', NULL),
(327, 141, '2025-2026', 'iscritto', NULL),
-- Luca Tramontano (CDL10, anno 1)
(328, 139, '2025-2026', 'iscritto', NULL),
-- Sara Napolitano (CDL11 Sci. Politiche, anno 2)
(329, 142, '2024-2025', 'completato', 26),
(329, 144, '2024-2025', 'completato', 24),
(329, 143, '2025-2026', 'iscritto', NULL),
(329, 131, '2025-2026', 'iscritto', NULL),
-- Roberto Falanga (CDL11, anno 1)
(330, 142, '2025-2026', 'iscritto', NULL),
(330, 144, '2025-2026', 'iscritto', NULL),
-- Valentina Pinto (CDL11, anno 3)
(331, 142, '2023-2024', 'completato', 30),
(331, 144, '2023-2024', 'completato', 27),
(331, 143, '2024-2025', 'completato', 28),
(331, 131, '2025-2026', 'iscritto', NULL),
-- Andrea Criscuolo (CDL12 Comunicazione, anno 2)
(332, 145, '2024-2025', 'completato', 25),
(332, 136, '2024-2025', 'completato', 23),
(332, 146, '2025-2026', 'iscritto', NULL),
(332, 147, '2025-2026', 'iscritto', NULL),
-- Ilaria Manzo (CDL12, anno 1)
(333, 145, '2025-2026', 'iscritto', NULL),
(333, 136, '2025-2026', 'iscritto', NULL),
-- Simone Auriemma (CDL12, anno 3)
(334, 145, '2023-2024', 'completato', 28),
(334, 136, '2023-2024', 'completato', 26),
(334, 146, '2024-2025', 'completato', 27),
(334, 147, '2025-2026', 'iscritto', NULL);

-- ============================================================================
-- MATERIALI DIDATTICI (1 per corso)
-- ============================================================================
INSERT OR IGNORE INTO materiali_didattici (id, corso_universitario_id, docente_id, titolo, tipo, s3_key, testo_estratto, is_processed) VALUES
(6101, 130, 230, 'Dispensa — Diritto Privato: Principi Generali',       'dispensa', 'didattica/corsi/130/dispensa_diritto_privato.pdf',    'Principi generali del diritto civile, capacita giuridica, persone fisiche e giuridiche, obbligazioni e contratti.', 1),
(6102, 131, 231, 'Slide — Diritto Costituzionale',                      'slide',    'didattica/corsi/131/slide_dir_costituzionale.pdf',    'Fonti del diritto italiano, gerarchia delle fonti, organi costituzionali, diritti fondamentali e Corte Costituzionale.', 1),
(6103, 132, 232, 'Dispensa — Diritto Penale: Parte Generale',           'dispensa', 'didattica/corsi/132/dispensa_dir_penale.pdf',         'Principio di legalita, elementi del reato, tipicita, antigiuridicita, colpevolezza, dolo e colpa, tentativo e concorso.', 1),
(6104, 133, 242, 'Slide — Diritto dell''Unione Europea',                'slide',    'didattica/corsi/133/slide_dir_ue.pdf',                'Trattati fondativi, istituzioni UE, regolamenti e direttive, mercato interno, liberta di circolazione.', 1),
(6105, 135, 233, 'Dispensa — Letteratura Italiana: Dalle Origini al 300','dispensa','didattica/corsi/135/dispensa_lett_italiana.pdf',       'Origini della letteratura italiana, Scuola Siciliana, Dolce Stil Novo, Dante e la Commedia, Petrarca e il Canzoniere, Boccaccio e il Decameron.', 1),
(6106, 136, 234, 'Slide — Linguistica Generale',                        'slide',    'didattica/corsi/136/slide_linguistica.pdf',            'Fonetica e fonologia, morfologia flessiva e derivazionale, sintassi generativa, semantica lessicale e pragmatica.', 1),
(6107, 137, 243, 'Dispensa — Storia Medievale',                         'dispensa', 'didattica/corsi/137/dispensa_storia_medievale.pdf',    'Caduta Impero Romano, regni romano-barbarici, Carlo Magno, feudalesimo, crociate, comuni, peste nera, Rinascimento.', 1),
(6108, 139, 236, 'Dispensa — Filosofia Antica',                         'dispensa', 'didattica/corsi/139/dispensa_filosofia_antica.pdf',    'Presocratici, Socrate e il metodo maieutico, Platone e la teoria delle idee, Aristotele e la metafisica, stoicismo ed epicureismo.', 1),
(6109, 140, 237, 'Slide — Filosofia Morale',                            'slide',    'didattica/corsi/140/slide_filosofia_morale.pdf',       'Utilitarismo di Bentham e Mill, imperativo categorico kantiano, etica delle virtu di MacIntyre, etica applicata contemporanea.', 1),
(6110, 142, 238, 'Slide — Scienza Politica',                            'slide',    'didattica/corsi/142/slide_scienza_politica.pdf',       'Sistemi politici, democrazia rappresentativa, partiti politici, sistemi elettorali, opinione pubblica, populismo.', 1),
(6111, 143, 239, 'Dispensa — Relazioni Internazionali',                 'dispensa', 'didattica/corsi/143/dispensa_relaz_internaz.pdf',      'Teorie delle RI: realismo, liberalismo, costruttivismo. ONU, NATO, UE, conflitti, diplomazia, cooperazione internazionale.', 1),
(6112, 144, 244, 'Slide — Economia Politica',                           'slide',    'didattica/corsi/144/slide_economia_politica.pdf',      'Domanda e offerta, equilibrio di mercato, PIL, inflazione, disoccupazione, politica fiscale e monetaria, Keynes.', 1),
(6113, 145, 240, 'Slide — Teoria della Comunicazione',                  'slide',    'didattica/corsi/145/slide_teoria_comunicazione.pdf',   'Modello di Shannon-Weaver, scuola di Palo Alto, semiotica, mass media, comunicazione digitale, cultura visuale.', 1),
(6114, 146, 241, 'Dispensa — Sociologia dei Media',                     'dispensa', 'didattica/corsi/146/dispensa_sociologia_media.pdf',    'Agenda setting, gatekeeping, spirale del silenzio, uses and gratifications, social media e sfera pubblica digitale.', 1);

-- ============================================================================
-- CHUNKS (3 per corso principale)
-- ============================================================================

-- Diritto Privato (130)
INSERT OR IGNORE INTO materiali_chunks (id, materiale_id, corso_universitario_id, indice_chunk, titolo_sezione, testo, sommario, argomenti_chiave, livello_difficolta, pagine_riferimento, n_token, embedding_sync) VALUES
(1100, 6101, 130, 0, 'Soggetti del Diritto',
 'La capacita giuridica si acquista alla nascita. La capacita d''agire si acquista a 18 anni. Le persone giuridiche (societa, associazioni, fondazioni) sono soggetti di diritto distinti dai loro membri. La rappresentanza permette di agire in nome e per conto di altri.',
 'Capacita giuridica e d''agire, persone giuridiche e rappresentanza.',
 '["capacita giuridica", "capacita d''agire", "persone giuridiche", "rappresentanza", "diritto civile"]', 1, '[1,2,3]', 300, 0),
(1101, 6101, 130, 1, 'Obbligazioni e Contratti',
 'L''obbligazione e un vincolo giuridico tra debitore e creditore. Le fonti sono: contratto, fatto illecito, ogni altro atto idoneo (art. 1173 c.c.). Il contratto e l''accordo tra due o piu parti per costituire, regolare o estinguere un rapporto giuridico patrimoniale. Requisiti essenziali: accordo, causa, oggetto, forma.',
 'Obbligazioni, fonti e requisiti essenziali del contratto.',
 '["obbligazioni", "contratto", "debitore", "creditore", "causa", "art. 1173"]', 2, '[15,16,17]', 340, 0),
(1102, 6101, 130, 2, 'Responsabilita Civile',
 'L''art. 2043 c.c. sancisce il principio del neminem laedere: chi cagiona un danno ingiusto e obbligato al risarcimento. Elementi: fatto, danno, nesso causale, colpa o dolo. La responsabilita oggettiva prescinde dalla colpa (es. danno da cose in custodia, art. 2051).',
 'Responsabilita extracontrattuale, art. 2043 e responsabilita oggettiva.',
 '["responsabilita civile", "art. 2043", "danno ingiusto", "risarcimento", "colpa", "dolo"]', 2, '[25,26,27]', 320, 0);

-- Diritto Costituzionale (131)
INSERT OR IGNORE INTO materiali_chunks (id, materiale_id, corso_universitario_id, indice_chunk, titolo_sezione, testo, sommario, argomenti_chiave, livello_difficolta, pagine_riferimento, n_token, embedding_sync) VALUES
(1103, 6102, 131, 0, 'Fonti del Diritto',
 'La gerarchia delle fonti: Costituzione, leggi costituzionali, leggi ordinarie, regolamenti, usi. Il principio di gerarchia: la fonte inferiore non puo contrastare quella superiore. Il principio di competenza assegna materie a fonti specifiche.',
 'Gerarchia delle fonti del diritto italiano.',
 '["fonti del diritto", "gerarchia", "Costituzione", "leggi", "regolamenti"]', 1, '[1,2,3]', 290, 0),
(1104, 6102, 131, 1, 'Organi Costituzionali',
 'Il Parlamento esercita la funzione legislativa. Il Governo la funzione esecutiva. Il Presidente della Repubblica e garante della Costituzione. La Corte Costituzionale giudica la legittimita delle leggi. La magistratura esercita la funzione giurisdizionale.',
 'Parlamento, Governo, PdR, Corte Costituzionale e Magistratura.',
 '["Parlamento", "Governo", "Presidente della Repubblica", "Corte Costituzionale", "separazione poteri"]', 2, '[10,11,12]', 310, 0),
(1105, 6102, 131, 2, 'Diritti Fondamentali',
 'La Parte I della Costituzione (artt. 1-54) sancisce i diritti fondamentali: liberta personale (art. 13), liberta di pensiero (art. 21), diritto al lavoro (art. 4), diritto alla salute (art. 32), diritto all''istruzione (art. 34). Sono inviolabili e tutelati dalla Corte Costituzionale.',
 'Diritti fondamentali della Costituzione italiana.',
 '["diritti fondamentali", "liberta personale", "art. 13", "art. 21", "Costituzione"]', 2, '[20,21,22]', 330, 0);

-- Diritto Penale (132)
INSERT OR IGNORE INTO materiali_chunks (id, materiale_id, corso_universitario_id, indice_chunk, titolo_sezione, testo, sommario, argomenti_chiave, livello_difficolta, pagine_riferimento, n_token, embedding_sync) VALUES
(1106, 6103, 132, 0, 'Principio di Legalita',
 'Nullum crimen, nulla poena sine lege. Il principio di legalita (art. 25 Cost.) richiede che il reato e la pena siano previsti dalla legge prima della commissione del fatto. Corollari: riserva di legge, tassativita, irretroattivita, divieto di analogia in malam partem.',
 'Principio di legalita e suoi corollari nel diritto penale.',
 '["legalita", "nullum crimen", "art. 25", "irretroattivita", "riserva di legge"]', 2, '[1,2,3]', 310, 0),
(1107, 6103, 132, 1, 'Elementi del Reato',
 'Il reato e composto da: fatto tipico (condotta, evento, nesso causale), antigiuridicita (assenza di cause di giustificazione: legittima difesa, stato di necessita) e colpevolezza (dolo = volonta; colpa = negligenza). Il tentativo punisce chi compie atti idonei diretti in modo non equivoco.',
 'Struttura del reato: tipicita, antigiuridicita, colpevolezza.',
 '["reato", "tipicita", "antigiuridicita", "colpevolezza", "dolo", "colpa", "tentativo"]', 3, '[10,11,12]', 350, 0),
(1108, 6103, 132, 2, 'Concorso di Persone',
 'Il concorso di persone nel reato (artt. 110 ss. c.p.) si verifica quando piu soggetti partecipano alla realizzazione dello stesso reato. Si distingue tra autore, coautore, istigatore e complice. La pena e uguale per tutti, salvo attenuanti o aggravanti specifiche.',
 'Concorso di persone: autore, istigatore, complice.',
 '["concorso", "coautore", "istigatore", "complice", "art. 110", "partecipazione"]', 3, '[20,21,22]', 320, 0);

-- Letteratura Italiana (135)
INSERT OR IGNORE INTO materiali_chunks (id, materiale_id, corso_universitario_id, indice_chunk, titolo_sezione, testo, sommario, argomenti_chiave, livello_difficolta, pagine_riferimento, n_token, embedding_sync) VALUES
(1109, 6105, 135, 0, 'Dante e la Divina Commedia',
 'La Commedia e un poema allegorico in terzine dantesche (ABA BCB). Tre cantiche: Inferno, Purgatorio, Paradiso, ciascuna di 33 canti (piu 1 introduttivo). Il viaggio di Dante attraverso i tre regni e allegoria del cammino dell''anima verso Dio. Virgilio guida nell''Inferno e Purgatorio, Beatrice nel Paradiso.',
 'Struttura e allegoria della Divina Commedia di Dante.',
 '["Dante", "Divina Commedia", "Inferno", "Purgatorio", "Paradiso", "allegoria", "terzine"]', 2, '[1,2,3]', 340, 0),
(1110, 6105, 135, 1, 'Petrarca e il Canzoniere',
 'Il Canzoniere (Rerum vulgarium fragmenta) raccoglie 366 componimenti, prevalentemente sonetti. Tema centrale: l''amore per Laura, figura idealizzata. Lo stile e raffinato, con attenzione al labor limae. Petrarca introduce l''introspezione psicologica nella lirica italiana.',
 'Il Canzoniere di Petrarca: struttura, temi e stile.',
 '["Petrarca", "Canzoniere", "Laura", "sonetto", "lirica", "introspezione"]', 2, '[10,11,12]', 310, 0),
(1111, 6105, 135, 2, 'Boccaccio e il Decameron',
 'Il Decameron e una raccolta di 100 novelle narrate da 10 giovani durante la peste del 1348. La cornice narrativa e uno dei primi esempi di metanarrazione. I temi spaziano dall''ingegno alla fortuna, dall''amore alla critica sociale. La prosa di Boccaccio fonda la tradizione narrativa italiana.',
 'Il Decameron: cornice narrativa, temi e importanza letteraria.',
 '["Boccaccio", "Decameron", "novelle", "peste", "cornice narrativa", "prosa"]', 2, '[20,21,22]', 330, 0);

-- Filosofia Antica (139)
INSERT OR IGNORE INTO materiali_chunks (id, materiale_id, corso_universitario_id, indice_chunk, titolo_sezione, testo, sommario, argomenti_chiave, livello_difficolta, pagine_riferimento, n_token, embedding_sync) VALUES
(1112, 6108, 139, 0, 'I Presocratici',
 'I presocratici cercano l''arche, il principio primo. Talete: acqua. Anassimandro: apeiron (illimitato). Eraclito: divenire e logos. Parmenide: l''essere e e non puo non essere. Democrito: atomi e vuoto. La physis (natura) e l''oggetto della loro indagine.',
 'I presocratici e la ricerca del principio primo.',
 '["presocratici", "arche", "Talete", "Eraclito", "Parmenide", "Democrito", "physis"]', 1, '[1,2,3]', 300, 0),
(1113, 6108, 139, 1, 'Platone e la Teoria delle Idee',
 'Per Platone la realta vera e il mondo delle Idee (eide), modelli perfetti e immutabili. Il mondo sensibile ne e copia imperfetta. L''anima, immortale, conosce le Idee per reminiscenza. Il mito della caverna illustra il passaggio dall''ignoranza alla conoscenza. La Repubblica delinea lo Stato ideale guidato dai filosofi.',
 'Platone: Idee, reminiscenza, mito della caverna, Repubblica.',
 '["Platone", "Idee", "reminiscenza", "caverna", "Repubblica", "anima"]', 2, '[10,11,12]', 340, 0),
(1114, 6108, 139, 2, 'Aristotele',
 'Aristotele critica la separazione platonica delle Idee. La sostanza e composta di materia e forma (ilemorfismo). Le quattro cause: materiale, formale, efficiente, finale. La logica aristotelica (sillogismo) fonda il ragionamento deduttivo. L''etica del giusto mezzo: la virtu e medieta tra eccesso e difetto.',
 'Aristotele: sostanza, quattro cause, logica, etica del giusto mezzo.',
 '["Aristotele", "sostanza", "ilemorfismo", "quattro cause", "sillogismo", "giusto mezzo"]', 2, '[20,21,22]', 330, 0);

-- Scienza Politica (142)
INSERT OR IGNORE INTO materiali_chunks (id, materiale_id, corso_universitario_id, indice_chunk, titolo_sezione, testo, sommario, argomenti_chiave, livello_difficolta, pagine_riferimento, n_token, embedding_sync) VALUES
(1115, 6110, 142, 0, 'Sistemi Politici e Democrazia',
 'Un sistema politico e l''insieme di istituzioni e processi che producono decisioni collettive vincolanti. La democrazia rappresentativa prevede elezioni periodiche, pluralismo, stato di diritto. Si distingue tra sistemi parlamentari (Italia, UK), presidenziali (USA) e semipresidenziali (Francia).',
 'Sistemi politici: democrazia parlamentare, presidenziale, semipresidenziale.',
 '["democrazia", "sistema parlamentare", "presidenziale", "elezioni", "pluralismo"]', 1, '[1,2,3]', 310, 0),
(1116, 6110, 142, 1, 'Partiti e Sistemi Elettorali',
 'I partiti politici aggregano interessi e competono per il potere. Il sistema proporzionale favorisce la rappresentativita, il maggioritario la governabilita. Il bipartitismo (USA, UK) si oppone al multipartitismo (Italia, Germania). La legge di Duverger collega sistema elettorale e sistema partitico.',
 'Partiti, sistemi elettorali e legge di Duverger.',
 '["partiti", "proporzionale", "maggioritario", "Duverger", "bipartitismo", "elettorale"]', 2, '[10,11,12]', 320, 0),
(1117, 6110, 142, 2, 'Opinione Pubblica e Comunicazione Politica',
 'L''opinione pubblica e l''insieme degli orientamenti dei cittadini su questioni politiche. I sondaggi la misurano. I media la influenzano (agenda setting). Il populismo sfrutta la contrapposizione popolo/elite. I social media hanno trasformato la comunicazione politica diretta.',
 'Opinione pubblica, sondaggi, agenda setting e populismo.',
 '["opinione pubblica", "sondaggi", "agenda setting", "populismo", "social media", "comunicazione politica"]', 2, '[20,21,22]', 300, 0);

-- Teoria della Comunicazione (145)
INSERT OR IGNORE INTO materiali_chunks (id, materiale_id, corso_universitario_id, indice_chunk, titolo_sezione, testo, sommario, argomenti_chiave, livello_difficolta, pagine_riferimento, n_token, embedding_sync) VALUES
(1118, 6113, 145, 0, 'Modelli Comunicativi',
 'Il modello di Shannon-Weaver (1949): mittente, codifica, canale, decodifica, destinatario, rumore. Il modello di Jakobson aggiunge le funzioni del linguaggio. La Scuola di Palo Alto afferma che non si puo non comunicare (primo assioma della comunicazione).',
 'Modelli di Shannon-Weaver, Jakobson e Scuola di Palo Alto.',
 '["Shannon-Weaver", "Jakobson", "Palo Alto", "modello comunicativo", "codifica"]', 1, '[1,2,3]', 300, 0),
(1119, 6113, 145, 1, 'Semiotica e Mass Media',
 'La semiotica studia i segni e i processi di significazione. Saussure distingue significante e significato. Peirce classifica i segni in icone, indici e simboli. I mass media (stampa, TV, radio) sono caratterizzati da comunicazione unidirezionale verso un pubblico ampio e indifferenziato.',
 'Semiotica di Saussure e Peirce, caratteristiche dei mass media.',
 '["semiotica", "Saussure", "Peirce", "significante", "significato", "mass media"]', 2, '[10,11,12]', 310, 0),
(1120, 6113, 145, 2, 'Comunicazione Digitale',
 'Il web 2.0 trasforma l''utente da fruitore passivo a prosumer. I social media introducono comunicazione molti-a-molti. L''algoritmo dei feed crea filter bubble e echo chamber. Il digital divide separa chi ha accesso alla tecnologia da chi no.',
 'Web 2.0, social media, filter bubble e digital divide.',
 '["web 2.0", "prosumer", "social media", "filter bubble", "echo chamber", "digital divide"]', 2, '[20,21,22]', 290, 0);

-- Sociologia dei Media (146)
INSERT OR IGNORE INTO materiali_chunks (id, materiale_id, corso_universitario_id, indice_chunk, titolo_sezione, testo, sommario, argomenti_chiave, livello_difficolta, pagine_riferimento, n_token, embedding_sync) VALUES
(1121, 6114, 146, 0, 'Teorie degli Effetti dei Media',
 'L''agenda setting (McCombs e Shaw, 1972): i media non dicono cosa pensare ma su cosa pensare. Il gatekeeping: i giornalisti selezionano le notizie. La spirale del silenzio (Noelle-Neumann): chi si sente in minoranza tace, rafforzando l''opinione dominante.',
 'Agenda setting, gatekeeping e spirale del silenzio.',
 '["agenda setting", "gatekeeping", "spirale del silenzio", "McCombs", "effetti media"]', 2, '[1,2,3]', 310, 0),
(1122, 6114, 146, 1, 'Uses and Gratifications',
 'L''approccio uses and gratifications (Katz, 1974) ribalta la prospettiva: non cosa fanno i media alle persone, ma cosa fanno le persone con i media. Il pubblico e attivo e sceglie i media per soddisfare bisogni: informazione, intrattenimento, identita personale, integrazione sociale.',
 'Teoria di uses and gratifications e pubblico attivo.',
 '["uses and gratifications", "Katz", "pubblico attivo", "bisogni", "intrattenimento"]', 2, '[10,11,12]', 300, 0),
(1123, 6114, 146, 2, 'Social Media e Sfera Pubblica',
 'I social media hanno trasformato la sfera pubblica di Habermas. La disintermediazione elimina i gatekeepers tradizionali. Le fake news si diffondono piu velocemente delle notizie verificate. La polarizzazione politica online e amplificata dagli algoritmi di raccomandazione.',
 'Social media, disintermediazione, fake news e polarizzazione.',
 '["social media", "Habermas", "sfera pubblica", "fake news", "disintermediazione", "polarizzazione"]', 3, '[20,21,22]', 320, 0);

-- ============================================================================
-- QUIZ TIPO C (approvati)
-- ============================================================================
INSERT OR IGNORE INTO quiz (id, titolo, corso_universitario_id, studente_id, docente_id, creato_da, approvato, ripetibile) VALUES
(520, 'Test — Diritto Privato',             130, NULL, 230, 'ai', 1, 1),
(521, 'Test — Diritto Costituzionale',      131, NULL, 231, 'ai', 1, 1),
(522, 'Test — Diritto Penale',              132, NULL, 232, 'ai', 1, 1),
(523, 'Test — Letteratura Italiana',         135, NULL, 233, 'ai', 1, 1),
(524, 'Test — Filosofia Antica',             139, NULL, 236, 'ai', 1, 1),
(525, 'Test — Scienza Politica',             142, NULL, 238, 'ai', 1, 1),
(526, 'Test — Teoria della Comunicazione',   145, NULL, 240, 'ai', 1, 1),
(527, 'Test — Sociologia dei Media',         146, NULL, 241, 'ai', 1, 1);

-- ============================================================================
-- DOMANDE QUIZ (4 per quiz)
-- ============================================================================

-- Quiz 520: Diritto Privato
INSERT OR IGNORE INTO domande_quiz (id, quiz_id, testo, tipo, opzioni_json, risposta_corretta, spiegazione, ordine, chunk_id) VALUES
(2100, 520, 'A che eta si acquista la capacita d''agire?', 'scelta_multipla', '["14 anni", "16 anni", "18 anni", "21 anni"]', '18 anni', 'La capacita d''agire si acquista al compimento della maggiore eta (18 anni).', 1, 1100),
(2101, 520, 'Quanti sono i requisiti essenziali del contratto?', 'scelta_multipla', '["2", "3", "4", "5"]', '4', 'Art. 1325 c.c.: accordo, causa, oggetto e forma (quando prescritta dalla legge).', 2, 1101),
(2102, 520, 'L''art. 2043 c.c. disciplina:', 'scelta_multipla', '["Il contratto", "La responsabilita extracontrattuale", "La successione", "Il matrimonio"]', 'La responsabilita extracontrattuale', 'L''art. 2043 sancisce l''obbligo di risarcimento per danno ingiusto (neminem laedere).', 3, 1102),
(2103, 520, 'La responsabilita oggettiva prescinde da:', 'scelta_multipla', '["Il danno", "Il nesso causale", "La colpa", "Il fatto"]', 'La colpa', 'Nella responsabilita oggettiva non e necessario provare la colpa del danneggiante.', 4, 1102);

-- Quiz 521: Diritto Costituzionale
INSERT OR IGNORE INTO domande_quiz (id, quiz_id, testo, tipo, opzioni_json, risposta_corretta, spiegazione, ordine, chunk_id) VALUES
(2104, 521, 'Quale organo giudica la legittimita delle leggi?', 'scelta_multipla', '["Parlamento", "Governo", "Corte Costituzionale", "Consiglio di Stato"]', 'Corte Costituzionale', 'La Corte Costituzionale e il giudice delle leggi: verifica la conformita alla Costituzione.', 1, 1104),
(2105, 521, 'L''art. 21 della Costituzione tutela:', 'scelta_multipla', '["Il lavoro", "La salute", "La liberta di pensiero", "L''istruzione"]', 'La liberta di pensiero', 'Art. 21: "Tutti hanno diritto di manifestare liberamente il proprio pensiero."', 2, 1105),
(2106, 521, 'La fonte piu alta nella gerarchia e:', 'scelta_multipla', '["La legge ordinaria", "Il regolamento", "La Costituzione", "Il decreto legge"]', 'La Costituzione', 'La Costituzione e al vertice della gerarchia delle fonti del diritto.', 3, 1103),
(2107, 521, 'Chi esercita la funzione legislativa?', 'scelta_multipla', '["Il Governo", "Il Parlamento", "Il PdR", "La Magistratura"]', 'Il Parlamento', 'Art. 70 Cost.: "La funzione legislativa e esercitata collettivamente dalle due Camere."', 4, 1104);

-- Quiz 522: Diritto Penale
INSERT OR IGNORE INTO domande_quiz (id, quiz_id, testo, tipo, opzioni_json, risposta_corretta, spiegazione, ordine, chunk_id) VALUES
(2108, 522, 'Il principio nullum crimen sine lege significa:', 'scelta_multipla', '["Tutti i crimini sono uguali", "Non esiste reato senza legge che lo preveda", "La pena e sempre uguale", "Il giudice decide il reato"]', 'Non esiste reato senza legge che lo preveda', 'Il principio di legalita richiede che il reato sia previsto dalla legge prima del fatto.', 1, 1106),
(2109, 522, 'Il dolo e:', 'scelta_multipla', '["Negligenza", "Volonta e previsione dell''evento", "Caso fortuito", "Forza maggiore"]', 'Volonta e previsione dell''evento', 'Il dolo consiste nella coscienza e volonta di realizzare il fatto tipico.', 2, 1107),
(2110, 522, 'La legittima difesa e:', 'scelta_multipla', '["Un''aggravante", "Una causa di giustificazione", "Un reato autonomo", "Una circostanza attenuante"]', 'Una causa di giustificazione', 'La legittima difesa esclude l''antigiuridicita del fatto.', 3, 1107),
(2111, 522, 'L''istigatore nel concorso di persone e chi:', 'scelta_multipla', '["Esegue il reato", "Aiuta materialmente", "Determina altri a commettere il reato", "Subisce il reato"]', 'Determina altri a commettere il reato', 'L''istigatore induce o rafforza la decisione altrui di commettere il reato.', 4, 1108);

-- Quiz 523: Letteratura Italiana
INSERT OR IGNORE INTO domande_quiz (id, quiz_id, testo, tipo, opzioni_json, risposta_corretta, spiegazione, ordine, chunk_id) VALUES
(2112, 523, 'Quante cantiche ha la Divina Commedia?', 'scelta_multipla', '["2", "3", "4", "5"]', '3', 'La Commedia ha tre cantiche: Inferno, Purgatorio e Paradiso.', 1, 1109),
(2113, 523, 'Chi guida Dante nel Paradiso?', 'scelta_multipla', '["Virgilio", "Beatrice", "San Bernardo", "Ulisse"]', 'Beatrice', 'Beatrice guida Dante nel Paradiso, sostituendo Virgilio che lo accompagna nelle prime due cantiche.', 2, 1109),
(2114, 523, 'Il Canzoniere di Petrarca e dedicato a:', 'scelta_multipla', '["Beatrice", "Laura", "Fiammetta", "Silvia"]', 'Laura', 'Laura e la donna amata e idealizzata nel Canzoniere di Petrarca.', 3, 1110),
(2115, 523, 'Quante novelle contiene il Decameron?', 'scelta_multipla', '["50", "80", "100", "120"]', '100', 'Il Decameron raccoglie 100 novelle narrate da 10 giovani in 10 giornate.', 4, 1111);

-- Quiz 524: Filosofia Antica
INSERT OR IGNORE INTO domande_quiz (id, quiz_id, testo, tipo, opzioni_json, risposta_corretta, spiegazione, ordine, chunk_id) VALUES
(2116, 524, 'Per Talete il principio primo (arche) e:', 'scelta_multipla', '["Il fuoco", "L''aria", "L''acqua", "La terra"]', 'L''acqua', 'Talete di Mileto identifica nell''acqua il principio originario di tutte le cose.', 1, 1112),
(2117, 524, 'Il mito della caverna e di:', 'scelta_multipla', '["Aristotele", "Platone", "Socrate", "Epicuro"]', 'Platone', 'Il mito della caverna (Repubblica, Libro VII) illustra il percorso dalla doxa all''episteme.', 2, 1113),
(2118, 524, 'L''ilemorfismo aristotelico unisce:', 'scelta_multipla', '["Anima e corpo", "Materia e forma", "Bene e male", "Essere e divenire"]', 'Materia e forma', 'Per Aristotele ogni sostanza e composta di materia (hyle) e forma (morphe).', 3, 1114),
(2119, 524, 'L''etica aristotelica del giusto mezzo definisce la virtu come:', 'scelta_multipla', '["Eccesso", "Difetto", "Medieta tra estremi", "Astinenza"]', 'Medieta tra estremi', 'La virtu e la disposizione a scegliere il medio tra l''eccesso e il difetto.', 4, 1114);

-- Quiz 525: Scienza Politica
INSERT OR IGNORE INTO domande_quiz (id, quiz_id, testo, tipo, opzioni_json, risposta_corretta, spiegazione, ordine, chunk_id) VALUES
(2120, 525, 'L''Italia ha un sistema politico:', 'scelta_multipla', '["Presidenziale", "Semipresidenziale", "Parlamentare", "Direttoriale"]', 'Parlamentare', 'L''Italia e una repubblica parlamentare: il Governo deve avere la fiducia del Parlamento.', 1, 1115),
(2121, 525, 'La legge di Duverger collega:', 'scelta_multipla', '["PIL e inflazione", "Sistema elettorale e sistema partitico", "Destra e sinistra", "Media e politica"]', 'Sistema elettorale e sistema partitico', 'Duverger teorizza che il maggioritario favorisce il bipartitismo, il proporzionale il multipartitismo.', 2, 1116),
(2122, 525, 'L''agenda setting afferma che i media:', 'scelta_multipla', '["Dicono cosa pensare", "Dicono su cosa pensare", "Non influenzano nessuno", "Creano partiti"]', 'Dicono su cosa pensare', 'I media non determinano le opinioni ma i temi su cui il pubblico si concentra.', 3, 1117),
(2123, 525, 'Il populismo si basa sulla contrapposizione:', 'scelta_multipla', '["Nord e Sud", "Popolo e elite", "Stato e mercato", "Destra e sinistra"]', 'Popolo e elite', 'Il populismo contrappone un popolo virtuoso a un''elite corrotta o distante.', 4, 1117);

-- Quiz 526: Teoria della Comunicazione
INSERT OR IGNORE INTO domande_quiz (id, quiz_id, testo, tipo, opzioni_json, risposta_corretta, spiegazione, ordine, chunk_id) VALUES
(2124, 526, 'Il primo assioma della comunicazione (Palo Alto) afferma:', 'scelta_multipla', '["Si comunica solo a parole", "Non si puo non comunicare", "La comunicazione e sempre intenzionale", "Il silenzio non comunica"]', 'Non si puo non comunicare', 'La Scuola di Palo Alto stabilisce che ogni comportamento e comunicazione.', 1, 1118),
(2125, 526, 'Nel modello di Shannon-Weaver, il rumore e:', 'scelta_multipla', '["Il messaggio", "L''interferenza nel canale", "Il codice", "Il destinatario"]', 'L''interferenza nel canale', 'Il rumore e qualsiasi disturbo che altera il segnale durante la trasmissione.', 2, 1118),
(2126, 526, 'Un prosumer e:', 'scelta_multipla', '["Solo produttore", "Solo consumatore", "Produttore e consumatore", "Un tipo di media"]', 'Produttore e consumatore', 'Il prosumer (producer + consumer) crea e consuma contenuti, tipico del web 2.0.', 3, 1120),
(2127, 526, 'La filter bubble e causata da:', 'scelta_multipla', '["La censura statale", "Gli algoritmi dei social media", "L''analfabetismo", "La TV via cavo"]', 'Gli algoritmi dei social media', 'Gli algoritmi mostrano contenuti coerenti con le preferenze, creando bolle informative.', 4, 1120);

-- Quiz 527: Sociologia dei Media
INSERT OR IGNORE INTO domande_quiz (id, quiz_id, testo, tipo, opzioni_json, risposta_corretta, spiegazione, ordine, chunk_id) VALUES
(2128, 527, 'La spirale del silenzio afferma che:', 'scelta_multipla', '["Tutti parlano sempre", "Chi si sente in minoranza tace", "I media sono neutrali", "Il silenzio e raro"]', 'Chi si sente in minoranza tace', 'Noelle-Neumann: le persone che percepiscono la propria opinione come minoritaria tendono a tacere.', 1, 1121),
(2129, 527, 'L''approccio uses and gratifications studia:', 'scelta_multipla', '["Cosa fanno i media alle persone", "Cosa fanno le persone con i media", "Solo la TV", "Solo internet"]', 'Cosa fanno le persone con i media', 'Katz ribalta la prospettiva: il pubblico e attivo e sceglie i media per soddisfare bisogni.', 2, 1122),
(2130, 527, 'La disintermediazione nei social media significa:', 'scelta_multipla', '["Piu giornalisti", "Eliminazione dei filtri tradizionali", "Piu censura", "Meno utenti"]', 'Eliminazione dei filtri tradizionali', 'I social media bypassano i gatekeepers tradizionali, permettendo pubblicazione diretta.', 3, 1123),
(2131, 527, 'Le fake news si diffondono piu velocemente perche:', 'scelta_multipla', '["Sono scritte meglio", "Suscitano emozioni forti", "Costano meno", "Sono piu brevi"]', 'Suscitano emozioni forti', 'Le fake news generano reazioni emotive intense (paura, indignazione) che ne amplificano la condivisione.', 4, 1123);

-- ============================================================================
-- TENTATIVI QUIZ (diversificati)
-- ============================================================================
INSERT OR IGNORE INTO tentativi_quiz (id, quiz_id, studente_id, punteggio, aree_deboli_json, completato, created_at) VALUES
-- Marco Adinolfi (320, CDL8 Giurisp.) — bravo in diritto
(200, 520, 320, 85.0, '[]', 1, '2026-02-10 10:00:00'),
(201, 521, 320, 80.0, '["gerarchia fonti"]', 1, '2026-02-25 10:00:00'),
(202, 522, 320, 70.0, '["concorso persone"]', 1, '2026-03-10 10:00:00'),
-- Francesca Calabrese (321, CDL8) — primo anno, fatica
(203, 520, 321, 40.0, '["responsabilita civile", "contratto", "obbligazioni"]', 1, '2026-03-05 10:00:00'),
(204, 521, 321, 35.0, '["fonti del diritto", "organi costituzionali", "diritti fondamentali"]', 1, '2026-03-12 10:00:00'),
-- Antonio Pellegrino (322, CDL8) — top student giurisprudenza
(205, 520, 322, 100.0, '[]', 1, '2026-01-15 10:00:00'),
(206, 521, 322, 95.0, '[]', 1, '2026-02-01 10:00:00'),
(207, 522, 322, 90.0, '[]', 1, '2026-03-01 10:00:00'),
-- Chiara Sannino (323, CDL8) — media
(208, 520, 323, 60.0, '["responsabilita civile"]', 1, '2026-02-20 10:00:00'),
(209, 522, 323, 50.0, '["tentativo", "dolo", "colpa"]', 1, '2026-03-10 10:00:00'),
-- Davide Iervolino (324, CDL9 Lettere) — bravo
(210, 523, 324, 90.0, '[]', 1, '2026-02-15 10:00:00'),
(211, 523, 324, 95.0, '[]', 1, '2026-03-01 10:00:00'),
-- Giulia Caiazzo (325, CDL9) — primo anno, media
(212, 523, 325, 55.0, '["Boccaccio", "Decameron"]', 1, '2026-03-08 10:00:00'),
-- Matteo Perrotta (326, CDL9) — eccellente
(213, 523, 326, 100.0, '[]', 1, '2026-01-20 10:00:00'),
-- Elena Di Maio (327, CDL10 Filosofia) — brava
(214, 524, 327, 82.0, '["presocratici"]', 1, '2026-02-10 10:00:00'),
(215, 524, 327, 90.0, '[]', 1, '2026-03-05 10:00:00'),
-- Luca Tramontano (328, CDL10) — in difficolta
(216, 524, 328, 30.0, '["Platone", "Aristotele", "presocratici", "ilemorfismo"]', 1, '2026-03-10 10:00:00'),
-- Sara Napolitano (329, CDL11 Sci. Politiche) — brava
(217, 525, 329, 78.0, '["Duverger"]', 1, '2026-02-15 10:00:00'),
(218, 521, 329, 65.0, '["organi costituzionali"]', 1, '2026-03-10 10:00:00'),
-- Roberto Falanga (330, CDL11) — medio
(219, 525, 330, 50.0, '["agenda setting", "populismo"]', 1, '2026-03-05 10:00:00'),
-- Valentina Pinto (331, CDL11) — eccellente
(220, 525, 331, 92.0, '[]', 1, '2026-01-25 10:00:00'),
(221, 521, 331, 88.0, '[]', 1, '2026-03-05 10:00:00'),
-- Andrea Criscuolo (332, CDL12 Comunicazione) — buono
(222, 526, 332, 75.0, '["Shannon-Weaver"]', 1, '2026-02-20 10:00:00'),
(223, 527, 332, 70.0, '["spirale del silenzio"]', 1, '2026-03-10 10:00:00'),
-- Ilaria Manzo (333, CDL12) — primo anno
(224, 526, 333, 45.0, '["Palo Alto", "semiotica", "prosumer"]', 1, '2026-03-08 10:00:00'),
-- Simone Auriemma (334, CDL12) — senior bravo
(225, 526, 334, 88.0, '[]', 1, '2026-02-01 10:00:00'),
(226, 527, 334, 85.0, '[]', 1, '2026-03-01 10:00:00');

-- ============================================================================
-- RISPOSTE DOMANDE (selezione rappresentativa)
-- ============================================================================

-- Tentativo 203: Francesca su Dir. Privato (40% → 2/4)
INSERT OR IGNORE INTO risposte_domande (id, tentativo_id, domanda_id, risposta_data, corretta) VALUES
(600, 203, 2100, '18 anni', 1),
(601, 203, 2101, '3', 0),
(602, 203, 2102, 'Il contratto', 0),
(603, 203, 2103, 'La colpa', 1);

-- Tentativo 204: Francesca su Dir. Costituzionale (35%)
INSERT OR IGNORE INTO risposte_domande (id, tentativo_id, domanda_id, risposta_data, corretta) VALUES
(604, 204, 2104, 'Parlamento', 0),
(605, 204, 2105, 'La liberta di pensiero', 1),
(606, 204, 2106, 'La legge ordinaria', 0),
(607, 204, 2107, 'Il Governo', 0);

-- Tentativo 216: Luca Tramontano su Filosofia (30%)
INSERT OR IGNORE INTO risposte_domande (id, tentativo_id, domanda_id, risposta_data, corretta) VALUES
(608, 216, 2116, 'Il fuoco', 0),
(609, 216, 2117, 'Platone', 1),
(610, 216, 2118, 'Anima e corpo', 0),
(611, 216, 2119, 'Eccesso', 0);

-- Tentativo 205: Antonio su Dir. Privato (100%)
INSERT OR IGNORE INTO risposte_domande (id, tentativo_id, domanda_id, risposta_data, corretta) VALUES
(612, 205, 2100, '18 anni', 1),
(613, 205, 2101, '4', 1),
(614, 205, 2102, 'La responsabilita extracontrattuale', 1),
(615, 205, 2103, 'La colpa', 1);

-- Tentativo 224: Ilaria Manzo su Comunicazione (45%)
INSERT OR IGNORE INTO risposte_domande (id, tentativo_id, domanda_id, risposta_data, corretta) VALUES
(616, 224, 2124, 'Non si puo non comunicare', 1),
(617, 224, 2125, 'Il messaggio', 0),
(618, 224, 2126, 'Solo consumatore', 0),
(619, 224, 2127, 'Gli algoritmi dei social media', 1);

-- ============================================================================
-- LEZIONI CORSO APPROVATE
-- ============================================================================
INSERT OR IGNORE INTO lezioni_corso (id, corso_universitario_id, docente_id, titolo, contenuto_md, creato_da, approvato, chunk_ids_utilizzati) VALUES
(820, 130, 230, 'Introduzione al Diritto Privato',
'## Il Diritto Privato

### Soggetti del Diritto
- **Capacita giuridica**: si acquista alla nascita
- **Capacita d''agire**: si acquista a 18 anni
- **Persone giuridiche**: soggetti distinti dai membri

### Obbligazioni
L''obbligazione e un vincolo tra **debitore** e **creditore**. Le fonti (art. 1173): contratto, fatto illecito, ogni altro atto idoneo.

### Il Contratto
Requisiti essenziali (art. 1325):
1. Accordo delle parti
2. Causa
3. Oggetto
4. Forma (quando prescritta)

### Responsabilita Civile
**Art. 2043**: chi cagiona un danno ingiusto e obbligato al risarcimento.',
'ai', 1, '[1100, 1101, 1102]'),

(821, 131, 231, 'Diritto Costituzionale: Fondamenti',
'## La Costituzione Italiana

### Gerarchia delle Fonti
Costituzione > Leggi costituzionali > Leggi ordinarie > Regolamenti > Usi

### Organi Costituzionali
| Organo | Funzione |
|--------|----------|
| Parlamento | Legislativa |
| Governo | Esecutiva |
| Magistratura | Giurisdizionale |
| PdR | Garanzia |
| Corte Cost. | Legittimita |

### Diritti Fondamentali
- Art. 13: Liberta personale
- Art. 21: Liberta di pensiero
- Art. 32: Diritto alla salute
- Art. 34: Diritto all''istruzione',
'ai', 1, '[1103, 1104, 1105]'),

(822, 135, 233, 'Le Tre Corone della Letteratura Italiana',
'## Dante, Petrarca, Boccaccio

### Dante Alighieri — La Divina Commedia
Poema in **terzine** (ABA BCB), tre cantiche di 33 canti ciascuna.
- **Inferno**: guidato da Virgilio
- **Purgatorio**: guidato da Virgilio
- **Paradiso**: guidato da Beatrice

### Francesco Petrarca — Il Canzoniere
366 componimenti dedicati a **Laura**. Introduce l''**introspezione psicologica** nella lirica.

### Giovanni Boccaccio — Il Decameron
**100 novelle** raccontate da 10 giovani durante la peste del 1348. La **cornice narrativa** fonda la tradizione novellistica.',
'ai', 1, '[1109, 1110, 1111]'),

(823, 139, 236, 'La Filosofia Antica',
'## Da Talete ad Aristotele

### I Presocratici
Cercano l''**arche** (principio primo):
- Talete: acqua
- Anassimandro: apeiron
- Eraclito: divenire e logos
- Parmenide: l''essere immutabile
- Democrito: atomi e vuoto

### Platone
- **Teoria delle Idee**: la realta vera e nel mondo intelligibile
- **Mito della caverna**: dall''ignoranza alla conoscenza
- **Reminiscenza**: l''anima ricorda cio che ha contemplato

### Aristotele
- **Ilemorfismo**: materia + forma
- **Quattro cause**: materiale, formale, efficiente, finale
- **Etica del giusto mezzo**: la virtu come medieta',
'ai', 1, '[1112, 1113, 1114]'),

(824, 142, 238, 'Fondamenti di Scienza Politica',
'## Sistemi Politici e Democrazia

### Tipi di Sistema
- **Parlamentare** (Italia, UK): il governo dipende dal parlamento
- **Presidenziale** (USA): separazione netta tra esecutivo e legislativo
- **Semipresidenziale** (Francia): presidente eletto + primo ministro

### Partiti e Sistemi Elettorali
La **legge di Duverger**:
- Maggioritario → bipartitismo
- Proporzionale → multipartitismo

### Comunicazione Politica
- **Agenda setting**: i media decidono i temi
- **Populismo**: popolo vs elite
- **Social media**: comunicazione politica diretta',
'ai', 1, '[1115, 1116, 1117]');

-- ============================================================================
-- PIANI PERSONALIZZATI
-- ============================================================================
INSERT OR IGNORE INTO piani_personalizzati (id, studente_id, titolo, descrizione, tipo, corso_universitario_id, stato, created_at) VALUES
(220, 320, 'Preparazione Diritto Penale', 'Piano per legalita, elementi del reato, concorso di persone.', 'esame', 132, 'attivo', '2026-03-01 10:00:00'),
(221, 320, 'Preparazione Diritto Commerciale', 'Piano per imprenditore, societa e procedure concorsuali.', 'esame', 134, 'attivo', '2026-03-10 10:00:00'),
(222, 322, 'Preparazione Diritto UE', 'Piano per istituzioni europee, fonti e mercato interno.', 'esame', 133, 'attivo', '2026-03-05 10:00:00'),
(223, 324, 'Preparazione Storia Medievale', 'Piano per alto e basso medioevo, feudalesimo e comuni.', 'esame', 137, 'attivo', '2026-03-01 10:00:00'),
(224, 327, 'Preparazione Filosofia Morale', 'Piano per utilitarismo, Kant ed etica delle virtu.', 'esame', 140, 'attivo', '2026-03-01 10:00:00'),
(225, 327, 'Approfondimento Logica', 'Piano per logica proposizionale e filosofia del linguaggio.', 'esame', 141, 'attivo', '2026-03-10 10:00:00'),
(226, 329, 'Preparazione Relazioni Internazionali', 'Piano per realismo, liberalismo, ONU e NATO.', 'esame', 143, 'attivo', '2026-03-05 10:00:00'),
(227, 332, 'Preparazione Sociologia dei Media', 'Piano per agenda setting, uses and gratifications, social media.', 'esame', 146, 'attivo', '2026-03-01 10:00:00'),
(228, 332, 'Preparazione Diritto Informazione', 'Piano per liberta di stampa, privacy e diritto all''oblio.', 'esame', 147, 'attivo', '2026-03-10 10:00:00');

PRAGMA foreign_keys = ON;
