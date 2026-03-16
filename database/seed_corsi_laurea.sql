-- ============================================================================
-- LearnAI — Seed Esteso per Catalogo Corsi di Laurea (area Ospiti)
-- Questo file popola la tabella corsi_di_laurea con dati completi.
-- Eseguire UNA SOLA VOLTA dopo il seed.sql base.
-- ============================================================================

PRAGMA foreign_keys = OFF;

-- Elimina i record esistenti e reinserisce tutto in modo idempotente
DELETE FROM corsi_di_laurea;

INSERT INTO corsi_di_laurea (id, nome, facolta, descrizione) VALUES
-- INGEGNERIA
(1,  'Ingegneria Informatica',          'Ingegneria',
     'Progettazione di sistemi hardware e software, reti, sistemi operativi e architetture degli elaboratori. Forma figure tecniche capaci di sviluppare applicazioni complesse, gestire infrastrutture IT e lavorare nell''intelligenza artificiale.'),
(2,  'Informatica',                     'Scienze MM.FF.NN.',
     'Fondamenti teorici e applicativi dell''informatica: algoritmi, intelligenza artificiale, crittografia e sicurezza informatica. Ideale per chi vuole lavorare come data scientist, software engineer o ricercatore IT.'),
(3,  'Ingegneria Elettronica',          'Ingegneria',
     'Progettazione di componenti e sistemi elettronici, microelettronica, sensori e sistemi embedded. Apre le porte all''industria automotive, ai dispositivi medici e all''elettronica di consumo.'),
(4,  'Ingegneria Meccanica',            'Ingegneria',
     'Progettazione e realizzazione di macchine, sistemi meccanici, impianti industriali e produzione manifatturiera. Cruciale per l''industria 4.0, l''automotive e l''aerospazio.'),
(5,  'Ingegneria Civile',               'Ingegneria',
     'Progettazione e costruzione di infrastrutture civili: strade, ponti, edifici e opere idrauliche. Forma professionisti per enti pubblici, imprese edili e libera professione.'),
(6,  'Ingegneria Aerospaziale',         'Ingegneria',
     'Progettazione e gestione di velivoli, veicoli spaziali e sistemi aeronautici. Forma ingegneri per l''industria aeronautica, enti spaziali (ASI/ESA) e la Difesa.'),
(7,  'Ingegneria Biomedica',            'Ingegneria',
     'Applicazione dell''ingegneria alla medicina: dispositivi medici, diagnostica per immagini e biomateriali. Ideale per chi vuole unire tecnologia e salute.'),
(8,  'Ingegneria Gestionale',           'Ingegneria',
     'Unisce competenze ingegneristiche con management aziendale, logistica, supply chain e analisi dei dati. Forma operations manager, consulenti e project manager.'),
(9,  'Ingegneria delle Telecomunicazioni', 'Ingegneria',
     'Reti di comunicazione, trasmissione dati, media digitali e tecnologie 5G/6G. Forma ingegneri per telco, broadcasting digitale e ricerca sulla rete.'),
(10, 'Architettura (Ciclo Unico)',      'Architettura',
     'Percorso abilitante alla professione di architetto: progettazione architettonica, urbanistica, restauro e costruzione sostenibile. Durata 5 anni.'),
-- ECONOMIA
(11, 'Economia Aziendale',              'Economia',
     'Fondamenti di gestione aziendale, contabilità, finanza d''impresa e strategia organizzativa. Forma manager, commercialisti, controller e analisti finanziari.'),
(12, 'Economia e Commercio',            'Economia',
     'Formazione in micro e macroeconomia, econometria, economia internazionale e politiche pubbliche. Ideale per chi vuole lavorare in enti internazionali, banche o pubblica amministrazione.'),
(13, 'Finanza',                         'Economia',
     'Formazione specialistica in finanza quantitativa, mercati dei capitali, derivati e risk management. Apre le porte all''investment banking, gestione portafogli e consulenza finanziaria.'),
-- GIURISPRUDENZA
(14, 'Giurisprudenza',                  'Giurisprudenza',
     'Formazione giuridica completa in diritto civile, penale, costituzionale, amministrativo, commerciale e internazionale. Forma avvocati, magistrati, notai e funzionari pubblici. Ciclo unico 5 anni.'),
-- MEDICINA
(15, 'Medicina e Chirurgia',            'Medicina e Chirurgia',
     'Formazione medica completa per il conseguimento dell''abilitazione alla professione di medico chirurgo. Accesso programmato nazionale, durata 6 anni.'),
(16, 'Infermieristica',                 'Medicina e Chirurgia',
     'Formazione dell''infermiere professionale per la cura e l''assistenza del paziente in ambito ospedaliero e territoriale. Triennale abilitante ad accesso programmato.'),
(17, 'Fisioterapia',                    'Medicina e Chirurgia',
     'Riabilitazione funzionale di pazienti con patologie ortopediche, neurologiche e cardiorespiratorias. Sbocchi in SSN, riabilitazione sportiva e libera professione.'),
(18, 'Farmacia',                        'Farmacia',
     'Formazione completa per la professione di farmacista: sintesi, analisi, distribuzione e counselling del farmaco. Ciclo unico 5 anni ad accesso programmato.'),
-- SCIENZE MM.FF.NN.
(19, 'Matematica',                      'Scienze MM.FF.NN.',
     'Fondamenti e applicazioni della matematica pura e applicata: analisi, algebra, geometria, probabilità e statistica. Sbocchi in ricerca, finanza quantitativa, insegnamento e informatica.'),
(20, 'Fisica',                          'Scienze MM.FF.NN.',
     'Principi fondamentali della fisica: meccanica, elettromagnetismo, fisica moderna e quantum computing. Forma ricercatori, fisici industriali e data scientist di alto profilo.'),
(21, 'Chimica',                         'Scienze MM.FF.NN.',
     'Studio delle proprietà e delle trasformazioni della materia. Apre le porte all''industria farmaceutica, chimica, alimentare e alla ricerca scientifica.'),
(22, 'Biologia',                        'Scienze MM.FF.NN.',
     'Studio degli esseri viventi, dalla cellula all''ecosistema. Sbocchi in ricerca biomedica, farmaceutica, ambientale e insegnamento.'),
-- LETTERE & SCIENZE UMANE
(23, 'Lettere e Filosofia',             'Lettere',
     'Studio approfondito di letteratura, storia, filosofia e lingue classiche. Forma insegnanti, ricercatori, giornalisti e professionisti della comunicazione culturale.'),
(24, 'Psicologia',                      'Scienze Politiche e Sociali',
     'Studio del comportamento umano, processi cognitivi e relazioni sociali. Sbocchi in clinica, aziende, sport, HR e ricerca. Accesso a magistrale per l''abilitazione alla professione.'),
(25, 'Scienze della Comunicazione',     'Scienze Politiche e Sociali',
     'Media, giornalismo, marketing digitale, comunicazione pubblica e corporate. Forma professionisti della comunicazione per agenzie, aziende e media company.'),
(26, 'Scienze dell''Educazione',        'Scienze Politiche e Sociali',
     'Pedagogia e scienze dell''educazione per la formazione di educatori, pedagogisti e professionisti del mondo scolastico ed extrascolastico.'),
-- AGRARIA
(27, 'Scienze Agrarie',                 'Agraria',
     'Formazione sulle tecniche agronomiche, zootecniche e di gestione forestale e ambientale in ottica di sostenibilità. Sbocchi come agronomo, consulente agricolo e tecnico ambientale.'),
(28, 'Scienze e Tecnologie Alimentari', 'Agraria',
     'Formazione sulle tecniche di produzione, trasformazione e controllo qualità nell''industria agroalimentare. Forma tecnologi alimentari, responsabili di produzione e ricercatori R&D.');

PRAGMA foreign_keys = ON;

-- ============================================================================
-- RIEPILOGO: 28 corsi di laurea con nome, facoltà e descrizione completa
-- ============================================================================
