-- ============================================================================
-- Data Population PARTE 2 — Iscrizioni, Materiali, Chunks
-- ============================================================================
PRAGMA foreign_keys = OFF;

-- ============================================================================
-- ISCRIZIONI STUDENTI (diversificate per percorso)
-- Ogni studente ha 2-4 corsi, con mix di iscritto/completato
-- ============================================================================
INSERT OR IGNORE INTO studenti_corsi (studente_id, corso_universitario_id, anno_accademico, stato, voto) VALUES
-- Lorenzo (CDL1, anno 2) — forte su programmazione
(300, 110, '2024-2025', 'completato', 28),
(300, 111, '2024-2025', 'completato', 26),
(300, 115, '2024-2025', 'completato', 24),
(300, 113, '2025-2026', 'iscritto', NULL),
(300, 112, '2025-2026', 'iscritto', NULL),
-- Alessia (CDL1, anno 3) — avanzata
(301, 110, '2023-2024', 'completato', 30),
(301, 111, '2023-2024', 'completato', 29),
(301, 113, '2024-2025', 'completato', 27),
(301, 114, '2025-2026', 'iscritto', NULL),
(301, 120, '2025-2026', 'iscritto', NULL),
-- Mattia (CDL1, anno 1) — appena iniziato
(302, 110, '2025-2026', 'iscritto', NULL),
(302, 115, '2025-2026', 'iscritto', NULL),
-- Sofia (CDL2, anno 2) — informatica pura
(303, 110, '2024-2025', 'completato', 27),
(303, 125, '2024-2025', 'completato', 25),
(303, 113, '2025-2026', 'iscritto', NULL),
(303, 119, '2025-2026', 'iscritto', NULL),
-- Riccardo (CDL2, anno 1) — primo anno
(304, 110, '2025-2026', 'iscritto', NULL),
(304, 125, '2025-2026', 'iscritto', NULL),
-- Emma (CDL2, anno 3) — senior informatica
(305, 110, '2023-2024', 'completato', 31),
(305, 111, '2023-2024', 'completato', 28),
(305, 113, '2024-2025', 'completato', 30),
(305, 120, '2025-2026', 'iscritto', NULL),
(305, 129, '2025-2026', 'iscritto', NULL),
-- Federico (CDL3, anno 2) — elettronica
(306, 115, '2024-2025', 'completato', 25),
(306, 116, '2024-2025', 'completato', 23),
(306, 118, '2025-2026', 'iscritto', NULL),
(306, 127, '2025-2026', 'iscritto', NULL),
-- Beatrice (CDL3, anno 1)
(307, 115, '2025-2026', 'iscritto', NULL),
(307, 116, '2025-2026', 'iscritto', NULL),
-- Diego (CDL4, anno 2) — gestionale
(308, 121, '2024-2025', 'completato', 26),
(308, 110, '2024-2025', 'completato', 22),
(308, 119, '2025-2026', 'iscritto', NULL),
(308, 122, '2025-2026', 'iscritto', NULL),
-- Alice (CDL4, anno 1)
(309, 110, '2025-2026', 'iscritto', NULL),
(309, 121, '2025-2026', 'iscritto', NULL),
-- Gabriele (CDL5, anno 2) — sci. informatiche
(310, 110, '2024-2025', 'completato', 29),
(310, 111, '2024-2025', 'completato', 27),
(310, 125, '2024-2025', 'completato', 26),
(310, 112, '2025-2026', 'iscritto', NULL),
-- Viola (CDL5, anno 3)
(311, 110, '2023-2024', 'completato', 30),
(311, 111, '2023-2024', 'completato', 28),
(311, 113, '2024-2025', 'completato', 26),
(311, 120, '2025-2026', 'iscritto', NULL),
-- Leonardo (CDL6, anno 2) — biomedica
(312, 115, '2024-2025', 'completato', 24),
(312, 116, '2024-2025', 'completato', 22),
(312, 123, '2025-2026', 'iscritto', NULL),
-- Anna (CDL6, anno 1)
(313, 115, '2025-2026', 'iscritto', NULL),
(313, 127, '2025-2026', 'iscritto', NULL),
-- Edoardo (CDL7, anno 2) — data science
(314, 119, '2024-2025', 'completato', 29),
(314, 110, '2024-2025', 'completato', 27),
(314, 120, '2025-2026', 'iscritto', NULL),
(314, 126, '2025-2026', 'iscritto', NULL),
-- Camilla (CDL7, anno 1)
(315, 110, '2025-2026', 'iscritto', NULL),
(315, 119, '2025-2026', 'iscritto', NULL),
-- Samuele (CDL1, anno 2)
(316, 110, '2024-2025', 'completato', 25),
(316, 115, '2024-2025', 'completato', 21),
(316, 111, '2025-2026', 'iscritto', NULL),
(316, 113, '2025-2026', 'iscritto', NULL),
-- Ginevra (CDL4, anno 3) — gestionale avanzata
(317, 121, '2023-2024', 'completato', 28),
(317, 110, '2023-2024', 'completato', 24),
(317, 119, '2024-2025', 'completato', 27),
(317, 122, '2025-2026', 'iscritto', NULL),
-- Filippo (CDL7, anno 2) — data science
(318, 119, '2024-2025', 'completato', 30),
(318, 110, '2024-2025', 'completato', 28),
(318, 120, '2025-2026', 'iscritto', NULL),
(318, 129, '2025-2026', 'iscritto', NULL),
-- Noemi (CDL2, anno 2)
(319, 110, '2024-2025', 'completato', 26),
(319, 125, '2024-2025', 'completato', 24),
(319, 111, '2025-2026', 'iscritto', NULL),
(319, 113, '2025-2026', 'iscritto', NULL);

-- ============================================================================
-- MATERIALI DIDATTICI per i nuovi corsi (1 per corso, ID 6000+)
-- ============================================================================
INSERT OR IGNORE INTO materiali_didattici (id, corso_universitario_id, docente_id, titolo, tipo, s3_key, testo_estratto, is_processed) VALUES
(6001, 110, 200, 'Slide — Introduzione alla Programmazione Java',          'slide',    'didattica/corsi/110/slide_intro_java.pdf',           'Introduzione ai concetti fondamentali della programmazione in Java: variabili, tipi, strutture di controllo, array, metodi e classi.', 1),
(6002, 111, 200, 'Slide — Design Pattern in Java',                         'slide',    'didattica/corsi/111/slide_design_pattern.pdf',        'Pattern creazionali, strutturali e comportamentali. Singleton, Factory, Observer, Strategy, Decorator.', 1),
(6003, 112, 204, 'Dispensa — Protocolli di Rete TCP/IP',                   'dispensa', 'didattica/corsi/112/dispensa_tcpip.pdf',              'Modello ISO/OSI e TCP/IP. Livelli di rete, trasporto e applicazione. HTTP, DNS, TCP, UDP, IP, routing.', 1),
(6004, 113, 208, 'Slide — Sistemi Operativi: Processi e Thread',           'slide',    'didattica/corsi/113/slide_processi_thread.pdf',       'Gestione dei processi, scheduling, thread, sincronizzazione, deadlock, semafori e mutex.', 1),
(6005, 114, 211, 'Dispensa — Ingegneria del Software e UML',               'dispensa', 'didattica/corsi/114/dispensa_uml.pdf',                'Modellazione UML: diagrammi dei casi d uso, classi, sequenza, stato. Pattern architetturali MVC, microservizi.', 1),
(6006, 115, 203, 'Slide — Meccanica e Termodinamica',                      'slide',    'didattica/corsi/115/slide_meccanica.pdf',             'Cinematica, dinamica del punto, leggi di Newton, lavoro ed energia, termodinamica: primo e secondo principio.', 1),
(6007, 116, 212, 'Slide — Elettromagnetismo',                              'slide',    'didattica/corsi/116/slide_elettromagnetismo.pdf',     'Campo elettrico, potenziale, condensatori, correnti, campo magnetico, induzione, equazioni di Maxwell.', 1),
(6008, 117, 206, 'Dispensa — Metodi Numerici',                             'dispensa', 'didattica/corsi/117/dispensa_metodi_numerici.pdf',    'Errori numerici, interpolazione polinomiale, integrazione numerica, metodi iterativi per sistemi lineari.', 1),
(6009, 118, 210, 'Slide — Circuiti Logici e VHDL',                         'slide',    'didattica/corsi/118/slide_circuiti_logici.pdf',       'Algebra booleana, porte logiche, circuiti combinatori e sequenziali, flip-flop, contatori, linguaggio VHDL.', 1),
(6010, 119, 215, 'Dispensa — Probabilita e Statistica',                    'dispensa', 'didattica/corsi/119/dispensa_probabilita.pdf',        'Spazio campionario, probabilita condizionata, variabili aleatorie, distribuzioni notevoli, stima e test.', 1),
(6011, 120, 219, 'Slide — Fondamenti di Machine Learning',                 'slide',    'didattica/corsi/120/slide_ml_fondamenti.pdf',         'Regressione, classificazione, SVM, alberi decisionali, ensemble, reti neurali, bias-varianza, cross-validation.', 1),
(6012, 121, 209, 'Slide — Economia e Strategia Aziendale',                 'slide',    'didattica/corsi/121/slide_economia_imprese.pdf',      'Catena del valore, analisi SWOT, strategie competitive, marketing mix, bilancio e indicatori finanziari.', 1),
(6013, 122, 205, 'Dispensa — Programmazione Lineare e Grafi',              'dispensa', 'didattica/corsi/122/dispensa_ricerca_operativa.pdf',  'Simplesso, dualita, programmazione intera, grafi: cammini minimi, flusso massimo, TSP.', 1),
(6014, 123, 207, 'Slide — Sensori e Strumentazione Biomedica',             'slide',    'didattica/corsi/123/slide_bioingegneria.pdf',         'Trasduttori, sensori di pressione e temperatura, elettrodi per biopotenziali, amplificatori per strumentazione.', 1),
(6015, 124, 213, 'Dispensa — Analisi Segnali ECG ed EEG',                  'dispensa', 'didattica/corsi/124/dispensa_segnali_bio.pdf',        'Acquisizione ECG, filtraggio, analisi spettrale, rilevamento QRS, segnali EEG e classificazione.', 1),
(6016, 125, 216, 'Slide — Automi e Linguaggi Formali',                     'slide',    'didattica/corsi/125/slide_automi.pdf',                'Automi finiti deterministici e non, espressioni regolari, grammatiche context-free, macchina di Turing.', 1),
(6017, 126, 224, 'Slide — Reti Neurali Profonde',                          'slide',    'didattica/corsi/126/slide_deep_learning.pdf',         'CNN, RNN, LSTM, Transformer, attention, transfer learning, tecniche di regolarizzazione e ottimizzazione.', 1),
(6018, 127, 201, 'Dispensa — Analisi Matematica II',                       'dispensa', 'didattica/corsi/127/dispensa_analisi2.pdf',           'Funzioni di piu variabili, derivate parziali, gradiente, integrali multipli, teoremi di Green e Stokes.', 1),
(6019, 128, 218, 'Slide — Controlli Automatici',                           'slide',    'didattica/corsi/128/slide_controlli.pdf',             'Modellazione sistemi, funzione di trasferimento, stabilita BIBO, diagrammi di Bode, Nyquist, controllori PID.', 1),
(6020, 129, 229, 'Slide — Introduzione al NLP',                            'slide',    'didattica/corsi/129/slide_nlp.pdf',                   'Tokenizzazione, word2vec, GloVe, modelli seq2seq, attention, BERT, GPT, applicazioni: sentiment, NER, QA.', 1);

-- ============================================================================
-- MATERIALI CHUNKS (3 chunks per corso, ID 1000+)
-- Keyword diversificate per alimentare il segnale semantico del recommender
-- ============================================================================

-- Corso 110: Programmazione I
INSERT OR IGNORE INTO materiali_chunks (id, materiale_id, corso_universitario_id, indice_chunk, titolo_sezione, testo, sommario, argomenti_chiave, livello_difficolta, pagine_riferimento, n_token, embedding_sync) VALUES
(1001, 6001, 110, 0, 'Variabili e Tipi in Java',
 'In Java ogni variabile ha un tipo dichiarato. I tipi primitivi sono: int, double, boolean, char, long, float, short, byte. Le variabili di riferimento puntano a oggetti allocati nell''heap. Il tipo determina le operazioni ammesse e la quantita di memoria occupata.',
 'Tipi primitivi e variabili di riferimento in Java.',
 '["Java", "variabili", "tipi primitivi", "programmazione", "oggetti", "heap"]', 1, '[1,2,3]', 320, 0),
(1002, 6001, 110, 1, 'Strutture di Controllo',
 'Le strutture di controllo guidano il flusso del programma. if-else per le scelte condizionali. Il ciclo for per iterazioni contate, while per iterazioni condizionali. switch-case per selezione multipla. break e continue modificano il flusso dei cicli.',
 'Strutture condizionali e cicli in Java.',
 '["if-else", "for", "while", "switch", "controllo flusso", "Java"]', 1, '[10,11,12]', 290, 0),
(1003, 6001, 110, 2, 'Classi e Metodi',
 'Una classe definisce un tipo di dato astratto con attributi (campi) e comportamenti (metodi). Il costruttore inizializza l''oggetto. L''incapsulamento si ottiene con modificatori di accesso: public, private, protected. I metodi possono essere static o di istanza.',
 'Classi, metodi, incapsulamento e costruttori in Java.',
 '["classi", "metodi", "costruttore", "incapsulamento", "OOP", "Java"]', 2, '[20,21,22]', 350, 0);

-- Corso 111: Programmazione II
INSERT OR IGNORE INTO materiali_chunks (id, materiale_id, corso_universitario_id, indice_chunk, titolo_sezione, testo, sommario, argomenti_chiave, livello_difficolta, pagine_riferimento, n_token, embedding_sync) VALUES
(1004, 6002, 111, 0, 'Generics e Collezioni',
 'I generics permettono di scrivere codice parametrico rispetto al tipo. List<T>, Map<K,V>, Set<T> sono le principali collezioni. Il type erasure elimina i tipi a runtime. I wildcard (? extends T, ? super T) aumentano la flessibilita.',
 'Generics Java e framework delle collezioni.',
 '["generics", "collezioni", "List", "Map", "type erasure", "Java"]', 2, '[1,2,3]', 310, 0),
(1005, 6002, 111, 1, 'Design Pattern Creazionali',
 'I pattern creazionali astraggono il processo di istanziazione. Singleton garantisce un''unica istanza. Factory Method delega la creazione alle sottoclassi. Abstract Factory crea famiglie di oggetti correlati. Builder separa costruzione e rappresentazione.',
 'Pattern Singleton, Factory e Builder.',
 '["design pattern", "Singleton", "Factory", "Builder", "creazionali", "OOP"]', 3, '[15,16,17]', 340, 0),
(1006, 6002, 111, 2, 'Pattern Observer e Strategy',
 'Observer implementa una dipendenza uno-a-molti: quando il soggetto cambia stato, tutti gli osservatori vengono notificati. Strategy incapsula algoritmi intercambiabili e li rende selezionabili a runtime. Entrambi favoriscono il principio open-closed.',
 'Pattern comportamentali Observer e Strategy.',
 '["Observer", "Strategy", "pattern comportamentali", "open-closed", "OOP"]', 3, '[25,26,27]', 300, 0);

-- Corso 112: Reti di Calcolatori
INSERT OR IGNORE INTO materiali_chunks (id, materiale_id, corso_universitario_id, indice_chunk, titolo_sezione, testo, sommario, argomenti_chiave, livello_difficolta, pagine_riferimento, n_token, embedding_sync) VALUES
(1007, 6003, 112, 0, 'Modello TCP/IP e Livelli',
 'Il modello TCP/IP ha quattro livelli: accesso alla rete, internet, trasporto e applicazione. Ogni livello offre servizi al livello superiore tramite interfacce ben definite. L''incapsulamento aggiunge header a ogni livello.',
 'Architettura a livelli del modello TCP/IP.',
 '["TCP/IP", "modello a livelli", "incapsulamento", "protocolli", "rete"]', 2, '[1,2,3]', 280, 0),
(1008, 6003, 112, 1, 'TCP e UDP',
 'TCP offre trasporto affidabile, orientato alla connessione, con controllo di flusso e congestione. UDP e senza connessione, piu veloce ma inaffidabile. TCP usa three-way handshake (SYN, SYN-ACK, ACK). Le porte identificano i processi.',
 'Confronto tra TCP e UDP, three-way handshake.',
 '["TCP", "UDP", "three-way handshake", "trasporto", "porte", "connessione"]', 2, '[10,11,12]', 320, 0),
(1009, 6003, 112, 2, 'HTTP e DNS',
 'HTTP e il protocollo applicativo del web. Metodi: GET, POST, PUT, DELETE. I codici di stato indicano l''esito (200 OK, 404 Not Found, 500 Server Error). DNS traduce nomi di dominio in indirizzi IP attraverso una gerarchia distribuita.',
 'Protocollo HTTP e sistema DNS.',
 '["HTTP", "DNS", "web", "REST", "codici di stato", "dominio"]', 2, '[20,21,22]', 300, 0);

-- Corso 113: Sistemi Operativi
INSERT OR IGNORE INTO materiali_chunks (id, materiale_id, corso_universitario_id, indice_chunk, titolo_sezione, testo, sommario, argomenti_chiave, livello_difficolta, pagine_riferimento, n_token, embedding_sync) VALUES
(1010, 6004, 113, 0, 'Processi e Scheduling',
 'Un processo e un programma in esecuzione con proprio spazio di indirizzamento. Lo scheduler della CPU assegna il processore usando algoritmi come FCFS, SJF, Round Robin, priorita. Il context switch salva e ripristina lo stato del processo.',
 'Gestione processi e algoritmi di scheduling CPU.',
 '["processi", "scheduling", "Round Robin", "context switch", "CPU", "FCFS"]', 2, '[1,2,3]', 310, 0),
(1011, 6004, 113, 1, 'Thread e Sincronizzazione',
 'I thread condividono lo spazio di indirizzamento del processo. La programmazione concorrente richiede sincronizzazione per evitare race condition. I semafori (Dijkstra) e i mutex proteggono le sezioni critiche. Il deadlock si verifica con attesa circolare.',
 'Thread, concorrenza, semafori, mutex e deadlock.',
 '["thread", "sincronizzazione", "semafori", "mutex", "deadlock", "concorrenza"]', 3, '[15,16,17]', 340, 0),
(1012, 6004, 113, 2, 'Gestione della Memoria',
 'La memoria virtuale separa lo spazio logico da quello fisico. La paginazione divide la memoria in pagine di dimensione fissa. La tabella delle pagine mappa indirizzi virtuali in fisici. Il page fault attiva il caricamento da disco. Algoritmi di sostituzione: LRU, FIFO, Clock.',
 'Memoria virtuale, paginazione e page fault.',
 '["memoria virtuale", "paginazione", "page fault", "LRU", "tabella pagine"]', 3, '[25,26,27]', 350, 0);

-- Corso 114: Ingegneria del Software
INSERT OR IGNORE INTO materiali_chunks (id, materiale_id, corso_universitario_id, indice_chunk, titolo_sezione, testo, sommario, argomenti_chiave, livello_difficolta, pagine_riferimento, n_token, embedding_sync) VALUES
(1013, 6005, 114, 0, 'Ciclo di Vita del Software',
 'Il ciclo di vita del software comprende analisi dei requisiti, progettazione, implementazione, testing e manutenzione. Il modello a cascata e sequenziale. Agile propone iterazioni brevi (sprint). Scrum definisce ruoli: Product Owner, Scrum Master, Team.',
 'Modelli di ciclo di vita: cascata e Agile/Scrum.',
 '["ciclo di vita", "waterfall", "Agile", "Scrum", "sprint", "requisiti"]', 2, '[1,2,3]', 320, 0),
(1014, 6005, 114, 1, 'UML: Diagrammi Principali',
 'UML (Unified Modeling Language) offre 14 tipi di diagrammi. I piu usati: diagramma dei casi d''uso (requisiti funzionali), diagramma delle classi (struttura statica), diagramma di sequenza (interazioni temporali), diagramma di stato (ciclo di vita di un oggetto).',
 'Diagrammi UML: casi d''uso, classi, sequenza, stato.',
 '["UML", "casi d uso", "diagramma classi", "sequenza", "stato", "modellazione"]', 3, '[15,16,17]', 330, 0),
(1015, 6005, 114, 2, 'Testing e Qualita',
 'Il testing verifica che il software soddisfi i requisiti. Unit test: singole unita. Integration test: interazione tra moduli. System test: sistema completo. Il TDD (Test-Driven Development) scrive i test prima del codice. La copertura misura la completezza dei test.',
 'Livelli di testing, TDD e metriche di qualita.',
 '["testing", "unit test", "TDD", "integrazione", "copertura", "qualita"]', 3, '[25,26,27]', 310, 0);

-- Corso 115: Fisica I
INSERT OR IGNORE INTO materiali_chunks (id, materiale_id, corso_universitario_id, indice_chunk, titolo_sezione, testo, sommario, argomenti_chiave, livello_difficolta, pagine_riferimento, n_token, embedding_sync) VALUES
(1016, 6006, 115, 0, 'Cinematica del Punto',
 'La cinematica descrive il moto senza considerare le cause. Posizione, velocita e accelerazione sono le grandezze fondamentali. Il moto rettilineo uniforme ha velocita costante: x = x0 + vt. Il moto uniformemente accelerato: x = x0 + v0t + 1/2 at^2.',
 'Moto rettilineo uniforme e uniformemente accelerato.',
 '["cinematica", "velocita", "accelerazione", "moto rettilineo", "fisica"]', 1, '[1,2,3]', 290, 0),
(1017, 6006, 115, 1, 'Dinamica e Leggi di Newton',
 'La prima legge di Newton: un corpo persiste nel suo stato di moto in assenza di forze. La seconda legge: F = ma. La terza legge: azione e reazione sono uguali e opposte. La forza peso P = mg. La forza di attrito si oppone al moto.',
 'Tre leggi di Newton e forze fondamentali.',
 '["Newton", "forza", "massa", "accelerazione", "attrito", "dinamica"]', 1, '[10,11,12]', 300, 0),
(1018, 6006, 115, 2, 'Termodinamica',
 'Il primo principio della termodinamica: l''energia interna di un sistema cambia per lavoro o calore scambiati. Il secondo principio: l''entropia di un sistema isolato non decresce mai. Il rendimento di una macchina termica e sempre inferiore a 1.',
 'Primo e secondo principio della termodinamica.',
 '["termodinamica", "energia", "entropia", "calore", "lavoro", "rendimento"]', 2, '[25,26,27]', 320, 0);

-- Corso 119: Probabilita e Statistica
INSERT OR IGNORE INTO materiali_chunks (id, materiale_id, corso_universitario_id, indice_chunk, titolo_sezione, testo, sommario, argomenti_chiave, livello_difficolta, pagine_riferimento, n_token, embedding_sync) VALUES
(1019, 6010, 119, 0, 'Probabilita e Spazio Campionario',
 'La probabilita misura la verosimiglianza di un evento. Lo spazio campionario e l''insieme di tutti gli esiti possibili. La probabilita condizionata P(A|B) = P(A∩B)/P(B). Il teorema di Bayes collega probabilita a priori e a posteriori.',
 'Fondamenti di probabilita e teorema di Bayes.',
 '["probabilita", "spazio campionario", "Bayes", "probabilita condizionata"]', 2, '[1,2,3]', 300, 0),
(1020, 6010, 119, 1, 'Variabili Aleatorie e Distribuzioni',
 'Una variabile aleatoria associa un valore numerico a ogni esito. Discrete: Bernoulli, Binomiale, Poisson. Continue: Normale (Gaussiana), Esponenziale, Uniforme. Il valore atteso E[X] e la media ponderata. La varianza Var(X) misura la dispersione.',
 'Distribuzioni discrete e continue, valore atteso e varianza.',
 '["variabile aleatoria", "distribuzione normale", "Poisson", "valore atteso", "varianza"]', 2, '[10,11,12]', 320, 0),
(1021, 6010, 119, 2, 'Stima e Test di Ipotesi',
 'La stima puntuale fornisce un singolo valore per il parametro. L''intervallo di confidenza fornisce un range. I test di ipotesi confrontano H0 (ipotesi nulla) e H1 (alternativa). Il p-value misura l''evidenza contro H0. Errore di tipo I: rifiutare H0 vera.',
 'Stima parametrica, intervalli di confidenza e test di ipotesi.',
 '["stima", "intervallo di confidenza", "test di ipotesi", "p-value", "errore tipo I"]', 3, '[20,21,22]', 340, 0);

-- Corso 120: Machine Learning
INSERT OR IGNORE INTO materiali_chunks (id, materiale_id, corso_universitario_id, indice_chunk, titolo_sezione, testo, sommario, argomenti_chiave, livello_difficolta, pagine_riferimento, n_token, embedding_sync) VALUES
(1022, 6011, 120, 0, 'Regressione e Classificazione',
 'La regressione lineare modella la relazione tra variabili con una retta: y = wx + b. Il gradient descent minimizza la loss function. La classificazione assegna categorie: regressione logistica usa la funzione sigmoide per output probabilistico.',
 'Regressione lineare, gradient descent e classificazione.',
 '["regressione lineare", "gradient descent", "classificazione", "sigmoide", "loss function"]', 2, '[1,2,3]', 310, 0),
(1023, 6011, 120, 1, 'SVM e Alberi Decisionali',
 'Le Support Vector Machine trovano l''iperpiano di massimo margine. Il kernel trick proietta in spazi ad alta dimensionalita. Gli alberi decisionali partizionano lo spazio con regole if-then. Random Forest combina molti alberi per ridurre l''overfitting.',
 'SVM, kernel trick, alberi decisionali e Random Forest.',
 '["SVM", "kernel", "alberi decisionali", "Random Forest", "ensemble", "margine"]', 3, '[15,16,17]', 330, 0),
(1024, 6011, 120, 2, 'Validazione e Reti Neurali',
 'La cross-validation k-fold stima le performance su dati non visti. Il trade-off bias-varianza guida la complessita del modello. Le reti neurali sono composte da neuroni con funzioni di attivazione (ReLU, sigmoid). Il backpropagation calcola i gradienti.',
 'Cross-validation, bias-varianza e reti neurali base.',
 '["cross-validation", "bias-varianza", "reti neurali", "backpropagation", "ReLU", "deep learning"]', 3, '[25,26,27]', 350, 0);

-- Corso 121: Economia e Gestione delle Imprese
INSERT OR IGNORE INTO materiali_chunks (id, materiale_id, corso_universitario_id, indice_chunk, titolo_sezione, testo, sommario, argomenti_chiave, livello_difficolta, pagine_riferimento, n_token, embedding_sync) VALUES
(1025, 6012, 121, 0, 'Strategia Aziendale',
 'La strategia aziendale definisce gli obiettivi di lungo periodo e le risorse per raggiungerli. L''analisi SWOT valuta punti di forza, debolezze, opportunita e minacce. Le cinque forze di Porter analizzano la competitivita del settore.',
 'Strategia aziendale, analisi SWOT e modello di Porter.',
 '["strategia", "SWOT", "Porter", "competitivita", "impresa"]', 2, '[1,2,3]', 290, 0),
(1026, 6012, 121, 1, 'Marketing Mix',
 'Il marketing mix comprende le 4P: Prodotto, Prezzo, Distribuzione (Place), Promozione. La segmentazione divide il mercato in gruppi omogenei. Il targeting seleziona i segmenti piu attraenti. Il posizionamento differenzia l''offerta nella mente del consumatore.',
 'Le 4P del marketing, segmentazione e posizionamento.',
 '["marketing mix", "4P", "segmentazione", "targeting", "posizionamento"]', 2, '[10,11,12]', 310, 0),
(1027, 6012, 121, 2, 'Bilancio e Indicatori',
 'Il bilancio comprende stato patrimoniale, conto economico e rendiconto finanziario. Il ROE misura la redditivita del capitale proprio. Il ROI misura la redditivita degli investimenti. L''indice di liquidita corrente valuta la solvibilita a breve.',
 'Struttura del bilancio e principali indicatori finanziari.',
 '["bilancio", "ROE", "ROI", "liquidita", "conto economico", "finanza"]', 2, '[20,21,22]', 300, 0);

-- Corso 125: Fondamenti di Informatica
INSERT OR IGNORE INTO materiali_chunks (id, materiale_id, corso_universitario_id, indice_chunk, titolo_sezione, testo, sommario, argomenti_chiave, livello_difficolta, pagine_riferimento, n_token, embedding_sync) VALUES
(1028, 6016, 125, 0, 'Automi Finiti',
 'Un automa finito deterministico (DFA) e una quintupla (Q, Σ, δ, q0, F). Riconosce un linguaggio regolare. La funzione di transizione δ mappa stato e simbolo in un nuovo stato. Un NFA puo avere transizioni multiple per lo stesso simbolo.',
 'DFA e NFA: definizione e riconoscimento linguaggi regolari.',
 '["automi finiti", "DFA", "NFA", "linguaggio regolare", "transizione"]', 2, '[1,2,3]', 290, 0),
(1029, 6016, 125, 1, 'Grammatiche e Linguaggi',
 'Una grammatica formale e una quadrupla (V, T, P, S). Le grammatiche context-free (CFG) generano linguaggi context-free, riconosciuti da automi a pila. La gerarchia di Chomsky classifica i linguaggi in quattro livelli di complessita crescente.',
 'Grammatiche formali, CFG e gerarchia di Chomsky.',
 '["grammatica", "context-free", "Chomsky", "automi a pila", "linguaggi formali"]', 3, '[10,11,12]', 310, 0),
(1030, 6016, 125, 2, 'Macchina di Turing e Complessita',
 'La macchina di Turing e il modello computazionale piu generale. Un problema e decidibile se esiste una MdT che termina sempre. Le classi P e NP classificano i problemi per complessita temporale. Il problema P vs NP e uno dei Millennium Prize Problems.',
 'Macchina di Turing, decidibilita, classi P e NP.',
 '["Turing", "decidibilita", "P", "NP", "complessita computazionale"]', 3, '[20,21,22]', 330, 0);

-- Corso 126: Deep Learning
INSERT OR IGNORE INTO materiali_chunks (id, materiale_id, corso_universitario_id, indice_chunk, titolo_sezione, testo, sommario, argomenti_chiave, livello_difficolta, pagine_riferimento, n_token, embedding_sync) VALUES
(1031, 6017, 126, 0, 'Reti Convoluzionali (CNN)',
 'Le CNN elaborano dati con struttura a griglia (immagini). I layer convoluzionali applicano filtri per estrarre feature. Il pooling riduce la dimensionalita. Architetture celebri: LeNet, AlexNet, VGG, ResNet. Il transfer learning riusa reti pre-addestrate.',
 'CNN: convoluzione, pooling e architetture classiche.',
 '["CNN", "convoluzione", "pooling", "ResNet", "transfer learning", "immagini"]', 3, '[1,2,3]', 320, 0),
(1032, 6017, 126, 1, 'Reti Ricorrenti e Transformer',
 'Le RNN processano sequenze mantenendo uno stato nascosto. Le LSTM risolvono il vanishing gradient con gate di input, output e forget. I Transformer usano self-attention per processare sequenze in parallelo. L''architettura encoder-decoder e alla base di BERT e GPT.',
 'RNN, LSTM e architettura Transformer.',
 '["RNN", "LSTM", "Transformer", "attention", "BERT", "GPT", "sequenze"]', 4, '[15,16,17]', 350, 0),
(1033, 6017, 126, 2, 'Tecniche di Addestramento',
 'Il dropout spegne neuroni random durante il training per regolarizzare. Il batch normalization normalizza gli input di ogni layer. L''Adam optimizer combina momentum e adaptive learning rate. Il learning rate scheduling riduce il lr durante il training.',
 'Dropout, batch normalization, Adam e scheduling.',
 '["dropout", "batch normalization", "Adam", "learning rate", "regolarizzazione", "ottimizzazione"]', 4, '[25,26,27]', 340, 0);

-- Corso 129: NLP
INSERT OR IGNORE INTO materiali_chunks (id, materiale_id, corso_universitario_id, indice_chunk, titolo_sezione, testo, sommario, argomenti_chiave, livello_difficolta, pagine_riferimento, n_token, embedding_sync) VALUES
(1034, 6020, 129, 0, 'Tokenizzazione e Word Embeddings',
 'La tokenizzazione spezza il testo in unita (parole, subword). BPE (Byte Pair Encoding) e usato da GPT. Word2Vec apprende rappresentazioni dense: CBOW predice la parola dal contesto, Skip-gram il contesto dalla parola. GloVe usa co-occorrenze globali.',
 'Tokenizzazione, Word2Vec e GloVe.',
 '["tokenizzazione", "BPE", "Word2Vec", "GloVe", "embedding", "NLP"]', 2, '[1,2,3]', 310, 0),
(1035, 6020, 129, 1, 'Modelli Sequenziali per NLP',
 'I modelli seq2seq usano encoder-decoder per traduzione automatica. L''attention mechanism permette al decoder di focalizzarsi su parti specifiche dell''input. BERT usa masked language modeling bidirezionale. GPT usa autoregressive language modeling.',
 'Seq2seq, attention, BERT e GPT per NLP.',
 '["seq2seq", "attention", "BERT", "GPT", "traduzione", "language model"]', 3, '[15,16,17]', 330, 0),
(1036, 6020, 129, 2, 'Applicazioni NLP',
 'Sentiment analysis classifica il tono emotivo del testo. Named Entity Recognition (NER) identifica entita nel testo. Question Answering estrae risposte da documenti. I LLM (Large Language Models) come GPT-4 e Claude gestiscono task multipli via prompting.',
 'Sentiment analysis, NER, QA e LLM.',
 '["sentiment analysis", "NER", "question answering", "LLM", "GPT-4", "prompting"]', 3, '[25,26,27]', 300, 0);

-- Corso 118: Elettronica Digitale
INSERT OR IGNORE INTO materiali_chunks (id, materiale_id, corso_universitario_id, indice_chunk, titolo_sezione, testo, sommario, argomenti_chiave, livello_difficolta, pagine_riferimento, n_token, embedding_sync) VALUES
(1037, 6009, 118, 0, 'Algebra Booleana e Porte Logiche',
 'L''algebra booleana opera su valori 0 e 1. Le operazioni fondamentali sono AND, OR, NOT. Le porte logiche implementano queste operazioni in hardware. Le leggi di De Morgan collegano AND e OR tramite negazione.',
 'Algebra booleana, porte logiche e leggi di De Morgan.',
 '["algebra booleana", "porte logiche", "AND", "OR", "NOT", "De Morgan"]', 1, '[1,2,3]', 280, 0),
(1038, 6009, 118, 1, 'Circuiti Combinatori',
 'I circuiti combinatori hanno output che dipendono solo dagli input correnti. Multiplexer, demultiplexer, encoder, decoder e sommatori sono circuiti combinatori fondamentali. Le mappe di Karnaugh semplificano le espressioni booleane.',
 'Circuiti combinatori: MUX, decoder, mappe di Karnaugh.',
 '["combinatori", "multiplexer", "Karnaugh", "sommatore", "decoder"]', 2, '[10,11,12]', 300, 0),
(1039, 6009, 118, 2, 'Circuiti Sequenziali e VHDL',
 'I circuiti sequenziali hanno memoria: l''output dipende anche dallo stato precedente. Flip-flop (SR, JK, D, T) sono gli elementi base. I contatori e i registri a scorrimento sono applicazioni. VHDL e il linguaggio per la descrizione e sintesi di circuiti digitali.',
 'Flip-flop, contatori e linguaggio VHDL.',
 '["flip-flop", "circuiti sequenziali", "contatori", "VHDL", "registri"]', 3, '[20,21,22]', 320, 0);

-- Corso 122: Ricerca Operativa
INSERT OR IGNORE INTO materiali_chunks (id, materiale_id, corso_universitario_id, indice_chunk, titolo_sezione, testo, sommario, argomenti_chiave, livello_difficolta, pagine_riferimento, n_token, embedding_sync) VALUES
(1040, 6013, 122, 0, 'Programmazione Lineare',
 'La PL ottimizza una funzione lineare soggetta a vincoli lineari. Il metodo del simplesso esplora i vertici del poliedro ammissibile. La dualita collega ogni problema primale a un duale. Il teorema di dualita forte: se uno ha soluzione ottima, anche l''altro.',
 'Programmazione lineare, simplesso e dualita.',
 '["programmazione lineare", "simplesso", "dualita", "ottimizzazione", "vincoli"]', 3, '[1,2,3]', 310, 0),
(1041, 6013, 122, 1, 'Grafi: Cammini e Flussi',
 'Un grafo G=(V,E) modella relazioni. Dijkstra trova il cammino minimo da sorgente singola. Bellman-Ford gestisce pesi negativi. Il teorema max-flow min-cut: il flusso massimo equivale al taglio minimo. Ford-Fulkerson calcola il flusso massimo.',
 'Cammini minimi e flusso massimo nei grafi.',
 '["grafi", "Dijkstra", "Bellman-Ford", "flusso massimo", "min-cut"]', 3, '[10,11,12]', 320, 0),
(1042, 6013, 122, 2, 'Ottimizzazione Combinatoria',
 'Il TSP (Travelling Salesman Problem) cerca il ciclo hamiltoniano di costo minimo. E NP-hard. Le metaeuristiche (simulated annealing, algoritmi genetici, tabu search) trovano soluzioni approssimate in tempo ragionevole per problemi NP-hard.',
 'TSP, NP-hard e metaeuristiche.',
 '["TSP", "NP-hard", "metaeuristiche", "simulated annealing", "algoritmi genetici"]', 4, '[20,21,22]', 300, 0);

-- Corso 123: Bioingegneria Elettronica
INSERT OR IGNORE INTO materiali_chunks (id, materiale_id, corso_universitario_id, indice_chunk, titolo_sezione, testo, sommario, argomenti_chiave, livello_difficolta, pagine_riferimento, n_token, embedding_sync) VALUES
(1043, 6014, 123, 0, 'Sensori Biomedici',
 'I trasduttori convertono grandezze fisiche in segnali elettrici. Sensori di temperatura: termistori e termocoppie. Sensori di pressione: piezoresistivi e capacitivi. Gli elettrodi per biopotenziali (Ag/AgCl) acquisiscono ECG, EEG, EMG.',
 'Trasduttori, sensori di temperatura, pressione ed elettrodi.',
 '["sensori", "trasduttori", "elettrodi", "biopotenziali", "ECG", "biomedica"]', 2, '[1,2,3]', 290, 0),
(1044, 6014, 123, 1, 'Amplificatori per Strumentazione',
 'L''amplificatore per strumentazione ha alto CMRR (Common Mode Rejection Ratio) per eliminare il rumore comune. Il circuito a tre operazionali e il design classico. Il filtro passa-banda isola le frequenze utili del segnale biologico.',
 'Amplificatori per strumentazione e filtraggio segnali.',
 '["amplificatore", "CMRR", "operazionale", "filtro", "strumentazione"]', 3, '[10,11,12]', 310, 0),
(1045, 6014, 123, 2, 'Sicurezza Elettrica in Ambito Clinico',
 'La sicurezza elettrica protegge il paziente da macroshock e microshock. La corrente di dispersione deve essere sotto 10 microA per apparecchi di tipo CF. L''isolamento galvanico separa il circuito paziente dall''alimentazione di rete.',
 'Sicurezza elettrica, corrente di dispersione e isolamento.',
 '["sicurezza elettrica", "microshock", "isolamento", "corrente dispersione", "clinico"]', 2, '[20,21,22]', 300, 0);

-- Corso 116: Fisica II
INSERT OR IGNORE INTO materiali_chunks (id, materiale_id, corso_universitario_id, indice_chunk, titolo_sezione, testo, sommario, argomenti_chiave, livello_difficolta, pagine_riferimento, n_token, embedding_sync) VALUES
(1046, 6007, 116, 0, 'Campo Elettrico',
 'La legge di Coulomb descrive la forza tra cariche: F = kq1q2/r^2. Il campo elettrico E e la forza per unita di carica. Il flusso del campo elettrico attraverso una superficie chiusa e proporzionale alla carica interna (teorema di Gauss).',
 'Legge di Coulomb, campo elettrico e teorema di Gauss.',
 '["Coulomb", "campo elettrico", "Gauss", "carica", "flusso", "elettrostatica"]', 2, '[1,2,3]', 300, 0),
(1047, 6007, 116, 1, 'Campo Magnetico',
 'Una corrente genera un campo magnetico (Biot-Savart). La forza di Lorentz agisce su cariche in moto in un campo B. La legge di Ampere collega campo magnetico e corrente concatenata. Il solenoide produce un campo uniforme al suo interno.',
 'Biot-Savart, forza di Lorentz e legge di Ampere.',
 '["campo magnetico", "Biot-Savart", "Lorentz", "Ampere", "solenoide"]', 2, '[10,11,12]', 310, 0),
(1048, 6007, 116, 2, 'Induzione e Maxwell',
 'La legge di Faraday: la variazione del flusso magnetico induce una fem. La legge di Lenz: la corrente indotta si oppone alla causa che l''ha generata. Le equazioni di Maxwell unificano elettricita e magnetismo e predicono le onde elettromagnetiche.',
 'Induzione elettromagnetica e equazioni di Maxwell.',
 '["Faraday", "induzione", "Lenz", "Maxwell", "onde elettromagnetiche"]', 3, '[20,21,22]', 320, 0);

PRAGMA foreign_keys = ON;
