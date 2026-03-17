-- ============================================================================
-- Data Population PARTE 3 — Quiz Tipo C, Tentativi, Risposte, Lezioni, Piani
-- ============================================================================
PRAGMA foreign_keys = OFF;

-- ============================================================================
-- QUIZ TIPO C (approvati dal docente — alimentano analytics)
-- Ogni nuovo corso ha 1 quiz con 4 domande
-- ============================================================================
INSERT OR IGNORE INTO quiz (id, titolo, corso_universitario_id, studente_id, docente_id, creato_da, approvato, ripetibile) VALUES
(500, 'Test — Programmazione Java Base',        110, NULL, 200, 'ai', 1, 1),
(501, 'Test — Design Pattern',                  111, NULL, 200, 'ai', 1, 1),
(502, 'Test — Reti e Protocolli',               112, NULL, 204, 'ai', 1, 1),
(503, 'Test — Sistemi Operativi',               113, NULL, 208, 'ai', 1, 1),
(504, 'Test — Ingegneria del Software',         114, NULL, 211, 'ai', 1, 1),
(505, 'Test — Meccanica e Termodinamica',       115, NULL, 203, 'ai', 1, 1),
(506, 'Test — Elettromagnetismo',               116, NULL, 212, 'ai', 1, 1),
(507, 'Test — Probabilita e Statistica',        119, NULL, 215, 'ai', 1, 1),
(508, 'Test — Machine Learning',                120, NULL, 219, 'ai', 1, 1),
(509, 'Test — Economia Aziendale',              121, NULL, 209, 'ai', 1, 1),
(510, 'Test — Fondamenti di Informatica',       125, NULL, 216, 'ai', 1, 1),
(511, 'Test — Deep Learning',                   126, NULL, 224, 'ai', 1, 1),
(512, 'Test — NLP',                             129, NULL, 229, 'ai', 1, 1),
(513, 'Test — Elettronica Digitale',            118, NULL, 210, 'ai', 1, 1),
(514, 'Test — Ricerca Operativa',               122, NULL, 205, 'ai', 1, 1),
(515, 'Test — Bioingegneria',                   123, NULL, 207, 'ai', 1, 1);

-- ============================================================================
-- DOMANDE QUIZ (4 per quiz, ID 2000+)
-- ============================================================================

-- Quiz 500: Programmazione I
INSERT OR IGNORE INTO domande_quiz (id, quiz_id, testo, tipo, opzioni_json, risposta_corretta, spiegazione, ordine, chunk_id) VALUES
(2001, 500, 'Quale tra questi NON e un tipo primitivo in Java?', 'scelta_multipla', '["int", "String", "boolean", "double"]', 'String', 'String e una classe, non un tipo primitivo. I tipi primitivi sono int, double, boolean, char, long, float, short e byte.', 1, 1001),
(2002, 500, 'Quale struttura di controllo e piu adatta per iterazioni con contatore?', 'scelta_multipla', '["while", "do-while", "for", "switch"]', 'for', 'Il ciclo for e progettato per iterazioni contate grazie alla sua sintassi con inizializzazione, condizione e incremento.', 2, 1002),
(2003, 500, 'Cosa garantisce l''incapsulamento?', 'scelta_multipla', '["Ereditarieta multipla", "Nascondere i dettagli implementativi", "Esecuzione parallela", "Compilazione piu veloce"]', 'Nascondere i dettagli implementativi', 'L''incapsulamento nasconde lo stato interno dell''oggetto e ne controlla l''accesso tramite metodi pubblici.', 3, 1003),
(2004, 500, 'A cosa serve il costruttore di una classe?', 'scelta_multipla', '["Distruggere l''oggetto", "Inizializzare l''oggetto", "Compilare la classe", "Gestire le eccezioni"]', 'Inizializzare l''oggetto', 'Il costruttore viene invocato alla creazione dell''oggetto e ne inizializza lo stato.', 4, 1003);

-- Quiz 501: Programmazione II
INSERT OR IGNORE INTO domande_quiz (id, quiz_id, testo, tipo, opzioni_json, risposta_corretta, spiegazione, ordine, chunk_id) VALUES
(2005, 501, 'Cosa garantisce il pattern Singleton?', 'scelta_multipla', '["Creazione rapida di oggetti", "Un''unica istanza della classe", "Ereditarieta multipla", "Thread safety automatica"]', 'Un''unica istanza della classe', 'Il Singleton limita l''istanziazione a un unico oggetto condiviso globalmente.', 1, 1005),
(2006, 501, 'Quale wildcard Java accetta solo sottotipi di T?', 'scelta_multipla', '["? super T", "? extends T", "? instanceof T", "? implements T"]', '? extends T', 'Il wildcard upper-bounded ? extends T accetta T e tutte le sue sottoclassi.', 2, 1004),
(2007, 501, 'Il pattern Observer implementa una dipendenza:', 'scelta_multipla', '["Uno-a-uno", "Uno-a-molti", "Molti-a-molti", "Nessuna dipendenza"]', 'Uno-a-molti', 'Observer stabilisce una relazione uno-a-molti: un soggetto notifica tutti gli osservatori registrati.', 3, 1006),
(2008, 501, 'Quale principio favorisce il pattern Strategy?', 'scelta_multipla', '["Single Responsibility", "Open-Closed", "Liskov Substitution", "Interface Segregation"]', 'Open-Closed', 'Strategy permette di aggiungere nuovi algoritmi senza modificare il codice esistente, rispettando il principio open-closed.', 4, 1006);

-- Quiz 502: Reti
INSERT OR IGNORE INTO domande_quiz (id, quiz_id, testo, tipo, opzioni_json, risposta_corretta, spiegazione, ordine, chunk_id) VALUES
(2009, 502, 'Quanti livelli ha il modello TCP/IP?', 'scelta_multipla', '["3", "4", "5", "7"]', '4', 'Il modello TCP/IP ha 4 livelli: accesso alla rete, internet, trasporto e applicazione.', 1, 1007),
(2010, 502, 'Quale protocollo offre trasporto affidabile?', 'scelta_multipla', '["UDP", "TCP", "IP", "ARP"]', 'TCP', 'TCP garantisce consegna affidabile e ordinata dei dati tramite conferme e ritrasmissioni.', 2, 1008),
(2011, 502, 'Quale codice HTTP indica risorsa non trovata?', 'scelta_multipla', '["200", "301", "404", "500"]', '404', 'Il codice 404 Not Found indica che il server non ha trovato la risorsa richiesta.', 3, 1009),
(2012, 502, 'Cosa fa il DNS?', 'scelta_multipla', '["Cripta il traffico", "Traduce nomi in IP", "Comprime i dati", "Autentica gli utenti"]', 'Traduce nomi in IP', 'Il DNS risolve nomi di dominio leggibili in indirizzi IP numerici.', 4, 1009);

-- Quiz 503: Sistemi Operativi
INSERT OR IGNORE INTO domande_quiz (id, quiz_id, testo, tipo, opzioni_json, risposta_corretta, spiegazione, ordine, chunk_id) VALUES
(2013, 503, 'Quale algoritmo di scheduling assegna un quanto di tempo fisso?', 'scelta_multipla', '["FCFS", "SJF", "Round Robin", "Priority"]', 'Round Robin', 'Round Robin assegna a ogni processo un quanto di tempo (time slice) uguale, ruotando tra i processi pronti.', 1, 1010),
(2014, 503, 'Cosa protegge un mutex?', 'scelta_multipla', '["La memoria virtuale", "La sezione critica", "Il file system", "La rete"]', 'La sezione critica', 'Il mutex garantisce mutua esclusione: solo un thread alla volta puo eseguire la sezione critica.', 2, 1011),
(2015, 503, 'Cosa avviene durante un page fault?', 'scelta_multipla', '["Il processo termina", "La pagina viene caricata da disco", "La CPU si spegne", "Il thread viene creato"]', 'La pagina viene caricata da disco', 'Un page fault indica che la pagina richiesta non e in RAM e va caricata dalla memoria secondaria.', 3, 1012),
(2016, 503, 'Quale condizione e necessaria per il deadlock?', 'scelta_multipla', '["Preemption", "Attesa circolare", "Scheduling FCFS", "Paginazione"]', 'Attesa circolare', 'Il deadlock richiede quattro condizioni simultanee, tra cui l''attesa circolare di risorse.', 4, 1011);

-- Quiz 504: Ingegneria del Software
INSERT OR IGNORE INTO domande_quiz (id, quiz_id, testo, tipo, opzioni_json, risposta_corretta, spiegazione, ordine, chunk_id) VALUES
(2017, 504, 'Quale modello propone iterazioni brevi (sprint)?', 'scelta_multipla', '["Waterfall", "V-Model", "Scrum/Agile", "Spirale"]', 'Scrum/Agile', 'Scrum organizza il lavoro in sprint di durata fissa (2-4 settimane) con obiettivi incrementali.', 1, 1013),
(2018, 504, 'Quale diagramma UML modella la struttura statica?', 'scelta_multipla', '["Sequenza", "Classi", "Stato", "Attivita"]', 'Classi', 'Il diagramma delle classi mostra classi, attributi, metodi e relazioni tra di esse.', 2, 1014),
(2019, 504, 'Cosa caratterizza il TDD?', 'scelta_multipla', '["Test dopo il deploy", "Test scritti prima del codice", "Solo test manuali", "Nessun test unitario"]', 'Test scritti prima del codice', 'Il TDD prevede: scrivere il test (rosso), implementare il codice (verde), rifattorizzare.', 3, 1015),
(2020, 504, 'Quale livello di test verifica l''interazione tra moduli?', 'scelta_multipla', '["Unit test", "Integration test", "Acceptance test", "Smoke test"]', 'Integration test', 'L''integration test verifica che i moduli funzionino correttamente quando interagiscono tra loro.', 4, 1015);

-- Quiz 505: Fisica I
INSERT OR IGNORE INTO domande_quiz (id, quiz_id, testo, tipo, opzioni_json, risposta_corretta, spiegazione, ordine, chunk_id) VALUES
(2021, 505, 'La seconda legge di Newton afferma:', 'scelta_multipla', '["F = mv", "F = ma", "F = mg/2", "F = m/a"]', 'F = ma', 'La forza risultante e uguale al prodotto della massa per l''accelerazione.', 1, 1017),
(2022, 505, 'L''entropia di un sistema isolato:', 'scelta_multipla', '["Diminuisce sempre", "Non cambia mai", "Non decresce mai", "E sempre zero"]', 'Non decresce mai', 'Il secondo principio afferma che l''entropia di un sistema isolato non puo diminuire.', 2, 1018),
(2023, 505, 'Nel moto uniformemente accelerato, l''accelerazione e:', 'scelta_multipla', '["Variabile", "Nulla", "Costante", "Infinita"]', 'Costante', 'Per definizione, il MUA ha accelerazione costante nel tempo.', 3, 1016),
(2024, 505, 'Quale principio enuncia che azione e reazione sono uguali e opposte?', 'scelta_multipla', '["Primo principio", "Secondo principio", "Terzo principio", "Principio di Archimede"]', 'Terzo principio', 'Il terzo principio di Newton afferma che a ogni azione corrisponde una reazione uguale e contraria.', 4, 1017);

-- Quiz 506: Fisica II
INSERT OR IGNORE INTO domande_quiz (id, quiz_id, testo, tipo, opzioni_json, risposta_corretta, spiegazione, ordine, chunk_id) VALUES
(2025, 506, 'La forza di Coulomb e proporzionale a:', 'scelta_multipla', '["Il prodotto delle cariche", "La somma delle cariche", "La massa delle cariche", "La velocita delle cariche"]', 'Il prodotto delle cariche', 'F = kq1q2/r^2: la forza dipende dal prodotto delle cariche e dall''inverso del quadrato della distanza.', 1, 1046),
(2026, 506, 'Chi unifica elettricita e magnetismo?', 'scelta_multipla', '["Newton", "Faraday", "Maxwell", "Einstein"]', 'Maxwell', 'Le equazioni di Maxwell unificano i fenomeni elettrici e magnetici predicendo le onde elettromagnetiche.', 2, 1048),
(2027, 506, 'La legge di Lenz afferma che la corrente indotta:', 'scelta_multipla', '["Amplifica la causa", "Si oppone alla causa", "E sempre nulla", "E costante"]', 'Si oppone alla causa', 'La legge di Lenz stabilisce che la corrente indotta si oppone alla variazione di flusso che l''ha generata.', 3, 1048),
(2028, 506, 'Quale dispositivo produce un campo magnetico uniforme?', 'scelta_multipla', '["Condensatore", "Resistenza", "Solenoide", "Diodo"]', 'Solenoide', 'Un solenoide percorso da corrente genera un campo magnetico approssimativamente uniforme al suo interno.', 4, 1047);

-- Quiz 507: Probabilita e Statistica
INSERT OR IGNORE INTO domande_quiz (id, quiz_id, testo, tipo, opzioni_json, risposta_corretta, spiegazione, ordine, chunk_id) VALUES
(2029, 507, 'Il teorema di Bayes collega:', 'scelta_multipla', '["Media e varianza", "Probabilita a priori e a posteriori", "Frequenza e ampiezza", "Entropia e energia"]', 'Probabilita a priori e a posteriori', 'Bayes aggiorna la probabilita di un evento alla luce di nuove evidenze osservate.', 1, 1019),
(2030, 507, 'Quale distribuzione modella il numero di successi in n prove?', 'scelta_multipla', '["Normale", "Binomiale", "Esponenziale", "Uniforme"]', 'Binomiale', 'La distribuzione binomiale conta i successi in n prove di Bernoulli indipendenti.', 2, 1020),
(2031, 507, 'L''errore di tipo I consiste nel:', 'scelta_multipla', '["Accettare H0 falsa", "Rifiutare H0 vera", "Rifiutare H1 vera", "Accettare H1 falsa"]', 'Rifiutare H0 vera', 'L''errore di tipo I e un falso positivo: rifiutare l''ipotesi nulla quando e vera.', 3, 1021),
(2032, 507, 'La varianza misura:', 'scelta_multipla', '["La media", "La moda", "La dispersione", "La frequenza"]', 'La dispersione', 'La varianza quantifica quanto i valori si discostano dalla media.', 4, 1020);

-- Quiz 508: Machine Learning
INSERT OR IGNORE INTO domande_quiz (id, quiz_id, testo, tipo, opzioni_json, risposta_corretta, spiegazione, ordine, chunk_id) VALUES
(2033, 508, 'Il gradient descent serve a:', 'scelta_multipla', '["Aumentare la loss", "Minimizzare la loss function", "Generare dati", "Visualizzare i risultati"]', 'Minimizzare la loss function', 'Il gradient descent aggiorna iterativamente i parametri nella direzione opposta al gradiente per minimizzare la loss.', 1, 1022),
(2034, 508, 'Random Forest combina:', 'scelta_multipla', '["Reti neurali", "Molti alberi decisionali", "Regressioni lineari", "SVM multipli"]', 'Molti alberi decisionali', 'Random Forest e un metodo ensemble che aggrega le predizioni di molti alberi addestrati su sottocampioni.', 2, 1023),
(2035, 508, 'La cross-validation k-fold serve a:', 'scelta_multipla', '["Addestrare piu velocemente", "Stimare le performance su dati non visti", "Ridurre il dataset", "Eliminare le feature"]', 'Stimare le performance su dati non visti', 'La k-fold CV suddivide i dati in k parti, usando a turno ciascuna come test set per stimare la generalizzazione.', 3, 1024),
(2036, 508, 'Il backpropagation calcola:', 'scelta_multipla', '["I pesi iniziali", "I gradienti della loss", "Le feature di input", "L''output finale"]', 'I gradienti della loss', 'Il backpropagation propaga l''errore all''indietro attraverso la rete calcolando i gradienti per ogni peso.', 4, 1024);

-- Quiz 509: Economia Aziendale
INSERT OR IGNORE INTO domande_quiz (id, quiz_id, testo, tipo, opzioni_json, risposta_corretta, spiegazione, ordine, chunk_id) VALUES
(2037, 509, 'L''analisi SWOT valuta:', 'scelta_multipla', '["Solo i costi", "Forze, debolezze, opportunita e minacce", "Solo il fatturato", "Solo i concorrenti"]', 'Forze, debolezze, opportunita e minacce', 'SWOT e l''acronimo di Strengths, Weaknesses, Opportunities, Threats.', 1, 1025),
(2038, 509, 'Le 4P del marketing sono:', 'scelta_multipla', '["People, Process, Price, Place", "Product, Price, Place, Promotion", "Plan, Produce, Price, Promote", "Product, People, Price, Profit"]', 'Product, Price, Place, Promotion', 'Il marketing mix classico comprende Prodotto, Prezzo, Distribuzione e Promozione.', 2, 1026),
(2039, 509, 'Il ROE misura:', 'scelta_multipla', '["La liquidita", "La redditivita del capitale proprio", "Il fatturato", "L''indebitamento"]', 'La redditivita del capitale proprio', 'Il ROE (Return On Equity) indica il rendimento del capitale investito dai soci.', 3, 1027),
(2040, 509, 'Le cinque forze di Porter analizzano:', 'scelta_multipla', '["Il bilancio", "La competitivita del settore", "I tassi di interesse", "Le risorse umane"]', 'La competitivita del settore', 'Il modello di Porter valuta la rivalita, i nuovi entranti, i sostituti, il potere di fornitori e clienti.', 4, 1025);

-- Quiz 510: Fondamenti Informatica
INSERT OR IGNORE INTO domande_quiz (id, quiz_id, testo, tipo, opzioni_json, risposta_corretta, spiegazione, ordine, chunk_id) VALUES
(2041, 510, 'Un DFA riconosce linguaggi:', 'scelta_multipla', '["Context-free", "Regolari", "Context-sensitive", "Tutti"]', 'Regolari', 'Un automa finito deterministico riconosce esattamente la classe dei linguaggi regolari.', 1, 1028),
(2042, 510, 'La gerarchia di Chomsky ha:', 'scelta_multipla', '["2 livelli", "3 livelli", "4 livelli", "5 livelli"]', '4 livelli', 'La gerarchia ha 4 livelli: tipo 0 (ricorsivamente enumerabili), 1 (context-sensitive), 2 (context-free), 3 (regolari).', 2, 1029),
(2043, 510, 'Il problema P vs NP chiede se:', 'scelta_multipla', '["Tutti i problemi sono risolvibili", "P = NP o P != NP", "NP e vuoto", "P contiene problemi indecidibili"]', 'P = NP o P != NP', 'Chiede se ogni problema verificabile in tempo polinomiale sia anche risolvibile in tempo polinomiale.', 3, 1030),
(2044, 510, 'La macchina di Turing e:', 'scelta_multipla', '["Un computer reale", "Un modello computazionale teorico", "Un linguaggio di programmazione", "Un protocollo di rete"]', 'Un modello computazionale teorico', 'La MdT e un modello astratto che definisce i limiti teorici della computazione.', 4, 1030);

-- Quiz 511: Deep Learning
INSERT OR IGNORE INTO domande_quiz (id, quiz_id, testo, tipo, opzioni_json, risposta_corretta, spiegazione, ordine, chunk_id) VALUES
(2045, 511, 'A cosa serve il pooling nelle CNN?', 'scelta_multipla', '["Aumentare la risoluzione", "Ridurre la dimensionalita", "Aggiungere rumore", "Inizializzare i pesi"]', 'Ridurre la dimensionalita', 'Il pooling (max o average) riduce le dimensioni spaziali delle feature map, diminuendo i parametri.', 1, 1031),
(2046, 511, 'Le LSTM risolvono il problema del:', 'scelta_multipla', '["Overfitting", "Vanishing gradient", "Underfitting", "Bias"]', 'Vanishing gradient', 'Le LSTM usano meccanismi di gate per preservare il gradiente su sequenze lunghe.', 2, 1032),
(2047, 511, 'Il dropout serve per:', 'scelta_multipla', '["Velocizzare il training", "Regolarizzare il modello", "Aumentare i parametri", "Caricare i dati"]', 'Regolarizzare il modello', 'Il dropout spegne neuroni random durante il training per prevenire co-adattamento e overfitting.', 3, 1033),
(2048, 511, 'Quale architettura usa self-attention?', 'scelta_multipla', '["CNN", "RNN", "Transformer", "Autoencoder"]', 'Transformer', 'I Transformer usano il meccanismo di self-attention per processare tutte le posizioni in parallelo.', 4, 1032);

-- Quiz 512: NLP
INSERT OR IGNORE INTO domande_quiz (id, quiz_id, testo, tipo, opzioni_json, risposta_corretta, spiegazione, ordine, chunk_id) VALUES
(2049, 512, 'Word2Vec apprende:', 'scelta_multipla', '["Regole grammaticali", "Rappresentazioni dense delle parole", "Alberi sintattici", "Traduzioni automatiche"]', 'Rappresentazioni dense delle parole', 'Word2Vec mappa ogni parola in un vettore denso nello spazio semantico tramite CBOW o Skip-gram.', 1, 1034),
(2050, 512, 'BERT usa:', 'scelta_multipla', '["Autoregressive modeling", "Masked language modeling", "Machine translation", "Image captioning"]', 'Masked language modeling', 'BERT maschera token casuali e li predice dal contesto bidirezionale.', 2, 1035),
(2051, 512, 'La NER identifica:', 'scelta_multipla', '["Il sentiment", "Le entita nel testo", "Le traduzioni", "I sinonimi"]', 'Le entita nel testo', 'Named Entity Recognition riconosce e classifica entita come persone, luoghi, organizzazioni.', 3, 1036),
(2052, 512, 'BPE sta per:', 'scelta_multipla', '["Binary Pair Encoding", "Byte Pair Encoding", "Balanced Point Estimation", "Best Prediction Error"]', 'Byte Pair Encoding', 'BPE e un algoritmo di tokenizzazione subword usato da molti LLM moderni.', 4, 1034);

-- Quiz 513: Elettronica Digitale
INSERT OR IGNORE INTO domande_quiz (id, quiz_id, testo, tipo, opzioni_json, risposta_corretta, spiegazione, ordine, chunk_id) VALUES
(2053, 513, 'Le leggi di De Morgan collegano:', 'scelta_multipla', '["AND e OR tramite negazione", "Tensione e corrente", "Frequenza e periodo", "Bit e byte"]', 'AND e OR tramite negazione', 'De Morgan: NOT(A AND B) = NOT A OR NOT B e NOT(A OR B) = NOT A AND NOT B.', 1, 1037),
(2054, 513, 'Quale elemento ha memoria?', 'scelta_multipla', '["Porta AND", "Multiplexer", "Flip-flop", "Sommatore"]', 'Flip-flop', 'Il flip-flop e l''elemento base dei circuiti sequenziali, in grado di memorizzare un bit.', 2, 1039),
(2055, 513, 'Le mappe di Karnaugh servono a:', 'scelta_multipla', '["Progettare memorie", "Semplificare espressioni booleane", "Misurare tensioni", "Testare circuiti"]', 'Semplificare espressioni booleane', 'Le K-map raggruppano gli 1 adiacenti per ottenere la forma booleana minima.', 3, 1038),
(2056, 513, 'VHDL e un linguaggio per:', 'scelta_multipla', '["Programmazione web", "Descrizione di circuiti digitali", "Analisi dati", "Machine learning"]', 'Descrizione di circuiti digitali', 'VHDL permette di descrivere, simulare e sintetizzare circuiti digitali su FPGA e ASIC.', 4, 1039);

-- Quiz 514: Ricerca Operativa
INSERT OR IGNORE INTO domande_quiz (id, quiz_id, testo, tipo, opzioni_json, risposta_corretta, spiegazione, ordine, chunk_id) VALUES
(2057, 514, 'Il metodo del simplesso esplora:', 'scelta_multipla', '["Tutti i punti interni", "I vertici del poliedro", "Solo l''origine", "I punti casuali"]', 'I vertici del poliedro', 'Il simplesso si muove di vertice in vertice migliorando la funzione obiettivo ad ogni passo.', 1, 1040),
(2058, 514, 'Dijkstra trova:', 'scelta_multipla', '["Il flusso massimo", "Il cammino minimo", "Il taglio minimo", "Il ciclo hamiltoniano"]', 'Il cammino minimo', 'L''algoritmo di Dijkstra calcola il cammino di costo minimo da un nodo sorgente a tutti gli altri.', 2, 1041),
(2059, 514, 'Il TSP e un problema:', 'scelta_multipla', '["P", "NP-completo", "Indecidibile", "Lineare"]', 'NP-completo', 'Il Travelling Salesman Problem e NP-hard e la sua versione decisionale e NP-completa.', 3, 1042),
(2060, 514, 'Il simulated annealing e:', 'scelta_multipla', '["Un metodo esatto", "Una metaeuristica", "Un algoritmo di ordinamento", "Un protocollo di rete"]', 'Una metaeuristica', 'Il SA e una metaeuristica ispirata al raffreddamento dei metalli per esplorare soluzioni sub-ottime.', 4, 1042);

-- Quiz 515: Bioingegneria
INSERT OR IGNORE INTO domande_quiz (id, quiz_id, testo, tipo, opzioni_json, risposta_corretta, spiegazione, ordine, chunk_id) VALUES
(2061, 515, 'Gli elettrodi Ag/AgCl si usano per:', 'scelta_multipla', '["Misurare la pressione", "Acquisire biopotenziali", "Generare raggi X", "Analizzare il sangue"]', 'Acquisire biopotenziali', 'Gli elettrodi Ag/AgCl sono lo standard per l''acquisizione di ECG, EEG e EMG.', 1, 1043),
(2062, 515, 'Il CMRR misura:', 'scelta_multipla', '["La velocita del segnale", "La reiezione del modo comune", "La frequenza di taglio", "La resistenza"]', 'La reiezione del modo comune', 'Il CMRR indica quanto l''amplificatore attenua i disturbi comuni rispetto al segnale differenziale.', 2, 1044),
(2063, 515, 'La corrente di dispersione massima per tipo CF e:', 'scelta_multipla', '["100 microA", "50 microA", "10 microA", "1 mA"]', '10 microA', 'Per apparecchi di tipo CF (applicati direttamente al cuore) il limite e 10 microA.', 3, 1045),
(2064, 515, 'L''isolamento galvanico serve a:', 'scelta_multipla', '["Aumentare il segnale", "Separare il circuito paziente dalla rete", "Ridurre la frequenza", "Comprimere i dati"]', 'Separare il circuito paziente dalla rete', 'L''isolamento galvanico protegge il paziente impedendo il passaggio di corrente dalla rete elettrica.', 4, 1045);

-- ============================================================================
-- TENTATIVI QUIZ con punteggi realistici e diversificati
-- Ogni studente fa 2-5 tentativi su quiz dei propri corsi
-- Mix: alcuni bravi (70-100), alcuni medi (40-65), alcuni a rischio (<40)
-- ============================================================================
INSERT OR IGNORE INTO tentativi_quiz (id, quiz_id, studente_id, punteggio, aree_deboli_json, completato, created_at) VALUES
-- Lorenzo (300) — bravo in programmazione
(100, 500, 300, 85.0, '[]', 1, '2026-02-15 10:00:00'),
(101, 500, 300, 95.0, '[]', 1, '2026-03-01 10:00:00'),
(102, 503, 300, 60.0, '["deadlock", "sincronizzazione"]', 1, '2026-03-10 10:00:00'),
(103, 502, 300, 55.0, '["DNS", "HTTP"]', 1, '2026-03-12 10:00:00'),
-- Alessia (301) — top student
(104, 500, 301, 100.0, '[]', 1, '2026-01-20 10:00:00'),
(105, 503, 301, 90.0, '[]', 1, '2026-02-10 10:00:00'),
(106, 504, 301, 80.0, '["TDD"]', 1, '2026-03-05 10:00:00'),
(107, 508, 301, 75.0, '["backpropagation"]', 1, '2026-03-14 10:00:00'),
-- Mattia (302) — primo anno, in difficolta
(108, 500, 302, 30.0, '["classi", "costruttore", "incapsulamento"]', 1, '2026-03-01 10:00:00'),
(109, 500, 302, 40.0, '["classi", "costruttore"]', 1, '2026-03-10 10:00:00'),
(110, 505, 302, 25.0, '["Newton", "termodinamica", "entropia"]', 1, '2026-03-12 10:00:00'),
-- Sofia (303) — brava informatica
(111, 500, 303, 80.0, '[]', 1, '2026-02-01 10:00:00'),
(112, 510, 303, 70.0, '["Turing", "NP"]', 1, '2026-02-20 10:00:00'),
(113, 503, 303, 65.0, '["memoria virtuale", "page fault"]', 1, '2026-03-10 10:00:00'),
(114, 507, 303, 75.0, '["test di ipotesi"]', 1, '2026-03-15 10:00:00'),
-- Riccardo (304) — primo anno, medio
(115, 500, 304, 50.0, '["incapsulamento", "metodi"]', 1, '2026-03-01 10:00:00'),
(116, 510, 304, 45.0, '["Chomsky", "Turing", "P vs NP"]', 1, '2026-03-10 10:00:00'),
-- Emma (305) — eccellente
(117, 500, 305, 100.0, '[]', 1, '2025-12-15 10:00:00'),
(118, 503, 305, 95.0, '[]', 1, '2026-01-20 10:00:00'),
(119, 508, 305, 90.0, '[]', 1, '2026-03-05 10:00:00'),
(120, 512, 305, 85.0, '[]', 1, '2026-03-14 10:00:00'),
-- Federico (306) — medio in elettronica
(121, 505, 306, 60.0, '["termodinamica"]', 1, '2026-02-10 10:00:00'),
(122, 506, 306, 50.0, '["Maxwell", "induzione"]', 1, '2026-02-28 10:00:00'),
(123, 513, 306, 55.0, '["VHDL", "flip-flop"]', 1, '2026-03-10 10:00:00'),
-- Beatrice (307) — prima anno, in difficolta
(124, 505, 307, 35.0, '["Newton", "cinematica", "termodinamica"]', 1, '2026-03-05 10:00:00'),
(125, 506, 307, 20.0, '["Coulomb", "Gauss", "Maxwell", "induzione"]', 1, '2026-03-12 10:00:00'),
-- Diego (308) — gestionale, forte economia
(126, 509, 308, 90.0, '[]', 1, '2026-02-01 10:00:00'),
(127, 500, 308, 55.0, '["incapsulamento", "OOP"]', 1, '2026-02-15 10:00:00'),
(128, 507, 308, 70.0, '["test di ipotesi"]', 1, '2026-03-10 10:00:00'),
(129, 514, 308, 65.0, '["simplesso", "dualita"]', 1, '2026-03-14 10:00:00'),
-- Alice (309) — primo anno gestionale
(130, 500, 309, 40.0, '["costruttore", "metodi", "classi"]', 1, '2026-03-05 10:00:00'),
(131, 509, 309, 55.0, '["ROE", "bilancio"]', 1, '2026-03-12 10:00:00'),
-- Gabriele (310) — bravo sci. informatiche
(132, 500, 310, 90.0, '[]', 1, '2026-01-15 10:00:00'),
(133, 501, 310, 85.0, '[]', 1, '2026-02-20 10:00:00'),
(134, 510, 310, 80.0, '["NP"]', 1, '2026-03-01 10:00:00'),
(135, 502, 310, 70.0, '["DNS"]', 1, '2026-03-14 10:00:00'),
-- Viola (311) — top sci. informatiche
(136, 500, 311, 95.0, '[]', 1, '2026-01-10 10:00:00'),
(137, 503, 311, 88.0, '[]', 1, '2026-02-15 10:00:00'),
(138, 508, 311, 82.0, '["SVM"]', 1, '2026-03-10 10:00:00'),
-- Leonardo (312) — medio biomedica
(139, 505, 312, 55.0, '["termodinamica", "entropia"]', 1, '2026-02-01 10:00:00'),
(140, 506, 312, 45.0, '["Maxwell", "Faraday"]', 1, '2026-02-20 10:00:00'),
(141, 515, 312, 60.0, '["CMRR", "isolamento"]', 1, '2026-03-10 10:00:00'),
-- Anna (313) — primo anno biomedica, fatica
(142, 505, 313, 30.0, '["Newton", "cinematica", "termodinamica"]', 1, '2026-03-05 10:00:00'),
-- Edoardo (314) — forte data science
(143, 507, 314, 88.0, '[]', 1, '2026-01-20 10:00:00'),
(144, 500, 314, 75.0, '["OOP"]', 1, '2026-02-10 10:00:00'),
(145, 508, 314, 92.0, '[]', 1, '2026-03-05 10:00:00'),
(146, 511, 314, 80.0, '["dropout"]', 1, '2026-03-14 10:00:00'),
-- Camilla (315) — primo anno IA
(147, 500, 315, 60.0, '["classi", "OOP"]', 1, '2026-03-01 10:00:00'),
(148, 507, 315, 50.0, '["Bayes", "test di ipotesi"]', 1, '2026-03-12 10:00:00'),
-- Samuele (316) — medio programmazione
(149, 500, 316, 65.0, '["incapsulamento"]', 1, '2026-02-15 10:00:00'),
(150, 505, 316, 45.0, '["termodinamica", "Newton"]', 1, '2026-03-01 10:00:00'),
(151, 501, 316, 50.0, '["Observer", "Strategy"]', 1, '2026-03-10 10:00:00'),
(152, 503, 316, 55.0, '["deadlock", "memoria virtuale"]', 1, '2026-03-14 10:00:00'),
-- Ginevra (317) — senior gestionale, brava
(153, 509, 317, 88.0, '[]', 1, '2026-01-20 10:00:00'),
(154, 500, 317, 70.0, '["OOP"]', 1, '2026-02-10 10:00:00'),
(155, 507, 317, 82.0, '[]', 1, '2026-03-01 10:00:00'),
(156, 514, 317, 75.0, '["TSP"]', 1, '2026-03-14 10:00:00'),
-- Filippo (318) — forte data science
(157, 507, 318, 95.0, '[]', 1, '2026-01-15 10:00:00'),
(158, 508, 318, 88.0, '[]', 1, '2026-03-05 10:00:00'),
(159, 512, 318, 80.0, '["NER"]', 1, '2026-03-12 10:00:00'),
-- Noemi (319) — medio informatica
(160, 500, 319, 70.0, '["OOP"]', 1, '2026-02-01 10:00:00'),
(161, 510, 319, 55.0, '["Chomsky", "NP"]', 1, '2026-02-20 10:00:00'),
(162, 501, 319, 60.0, '["Strategy", "pattern"]', 1, '2026-03-10 10:00:00'),
(163, 503, 319, 50.0, '["page fault", "deadlock"]', 1, '2026-03-14 10:00:00'),
-- Studenti originali: Giulia (1) — aggiunge tentativi sui nuovi quiz
(164, 500, 1, 72.0, '["OOP"]', 1, '2026-03-01 10:00:00'),
(165, 507, 1, 58.0, '["Bayes", "varianza"]', 1, '2026-03-08 10:00:00'),
-- Francesco (2) — medio
(166, 500, 2, 45.0, '["classi", "costruttore", "incapsulamento"]', 1, '2026-03-05 10:00:00'),
-- Chiara (3) — buona
(167, 500, 3, 78.0, '["incapsulamento"]', 1, '2026-03-02 10:00:00');

-- ============================================================================
-- RISPOSTE DOMANDE (4 per tentativo per i tentativi principali)
-- Coerenti con i punteggi: se 75% → 3 corrette su 4
-- Selezione rappresentativa per popolare "argomenti con errori" e "domande difficili"
-- ============================================================================

-- Tentativo 100: Lorenzo su quiz 500 (85% → 3/4 corrette, 1 parziale contata come sbaglio)
INSERT OR IGNORE INTO risposte_domande (id, tentativo_id, domanda_id, risposta_data, corretta) VALUES
(500, 100, 2001, 'String', 1),
(501, 100, 2002, 'for', 1),
(502, 100, 2003, 'Nascondere i dettagli implementativi', 1),
(503, 100, 2004, 'Distruggere l''oggetto', 0);

-- Tentativo 102: Lorenzo su quiz 503 (60% → 2/4 corrette + parziale)
INSERT OR IGNORE INTO risposte_domande (id, tentativo_id, domanda_id, risposta_data, corretta) VALUES
(504, 102, 2013, 'Round Robin', 1),
(505, 102, 2014, 'La sezione critica', 1),
(506, 102, 2015, 'Il processo termina', 0),
(507, 102, 2016, 'Preemption', 0);

-- Tentativo 108: Mattia su quiz 500 (30% → 1/4)
INSERT OR IGNORE INTO risposte_domande (id, tentativo_id, domanda_id, risposta_data, corretta) VALUES
(508, 108, 2001, 'String', 1),
(509, 108, 2002, 'switch', 0),
(510, 108, 2003, 'Ereditarieta multipla', 0),
(511, 108, 2004, 'Distruggere l''oggetto', 0);

-- Tentativo 110: Mattia su quiz 505 (25% → 1/4)
INSERT OR IGNORE INTO risposte_domande (id, tentativo_id, domanda_id, risposta_data, corretta) VALUES
(512, 110, 2021, 'F = ma', 1),
(513, 110, 2022, 'Diminuisce sempre', 0),
(514, 110, 2023, 'Variabile', 0),
(515, 110, 2024, 'Primo principio', 0);

-- Tentativo 111: Sofia su quiz 500 (80% → 3/4)
INSERT OR IGNORE INTO risposte_domande (id, tentativo_id, domanda_id, risposta_data, corretta) VALUES
(516, 111, 2001, 'String', 1),
(517, 111, 2002, 'for', 1),
(518, 111, 2003, 'Nascondere i dettagli implementativi', 1),
(519, 111, 2004, 'Compilare la classe', 0);

-- Tentativo 115: Riccardo su quiz 500 (50% → 2/4)
INSERT OR IGNORE INTO risposte_domande (id, tentativo_id, domanda_id, risposta_data, corretta) VALUES
(520, 115, 2001, 'String', 1),
(521, 115, 2002, 'while', 0),
(522, 115, 2003, 'Nascondere i dettagli implementativi', 1),
(523, 115, 2004, 'Gestire le eccezioni', 0);

-- Tentativo 124: Beatrice su quiz 505 (35% → 1/4)
INSERT OR IGNORE INTO risposte_domande (id, tentativo_id, domanda_id, risposta_data, corretta) VALUES
(524, 124, 2021, 'F = ma', 1),
(525, 124, 2022, 'E sempre zero', 0),
(526, 124, 2023, 'Nulla', 0),
(527, 124, 2024, 'Primo principio', 0);

-- Tentativo 125: Beatrice su quiz 506 (20% → quasi nulla)
INSERT OR IGNORE INTO risposte_domande (id, tentativo_id, domanda_id, risposta_data, corretta) VALUES
(528, 125, 2025, 'La somma delle cariche', 0),
(529, 125, 2026, 'Maxwell', 1),
(530, 125, 2027, 'Amplifica la causa', 0),
(531, 125, 2028, 'Condensatore', 0);

-- Tentativo 126: Diego su quiz 509 (90% → 4/4 quasi perfetto)
INSERT OR IGNORE INTO risposte_domande (id, tentativo_id, domanda_id, risposta_data, corretta) VALUES
(532, 126, 2037, 'Forze, debolezze, opportunita e minacce', 1),
(533, 126, 2038, 'Product, Price, Place, Promotion', 1),
(534, 126, 2039, 'La redditivita del capitale proprio', 1),
(535, 126, 2040, 'La competitivita del settore', 1);

-- Tentativo 142: Anna su quiz 505 (30% → 1/4)
INSERT OR IGNORE INTO risposte_domande (id, tentativo_id, domanda_id, risposta_data, corretta) VALUES
(536, 142, 2021, 'F = mv', 0),
(537, 142, 2022, 'E sempre zero', 0),
(538, 142, 2023, 'Costante', 1),
(539, 142, 2024, 'Secondo principio', 0);

-- Tentativo 145: Edoardo su quiz 508 (92% → 4/4)
INSERT OR IGNORE INTO risposte_domande (id, tentativo_id, domanda_id, risposta_data, corretta) VALUES
(540, 145, 2033, 'Minimizzare la loss function', 1),
(541, 145, 2034, 'Molti alberi decisionali', 1),
(542, 145, 2035, 'Stimare le performance su dati non visti', 1),
(543, 145, 2036, 'I gradienti della loss', 1);

-- Tentativo 148: Camilla su quiz 507 (50% → 2/4)
INSERT OR IGNORE INTO risposte_domande (id, tentativo_id, domanda_id, risposta_data, corretta) VALUES
(544, 148, 2029, 'Media e varianza', 0),
(545, 148, 2030, 'Binomiale', 1),
(546, 148, 2031, 'Accettare H0 falsa', 0),
(547, 148, 2032, 'La dispersione', 1);

-- Tentativo 116: Riccardo su quiz 510 (45% → 2/4)
INSERT OR IGNORE INTO risposte_domande (id, tentativo_id, domanda_id, risposta_data, corretta) VALUES
(548, 116, 2041, 'Regolari', 1),
(549, 116, 2042, '3 livelli', 0),
(550, 116, 2043, 'P = NP o P != NP', 1),
(551, 116, 2044, 'Un linguaggio di programmazione', 0);

-- ============================================================================
-- LEZIONI CORSO APPROVATE (1-2 per corso, ID 800+)
-- ============================================================================
INSERT OR IGNORE INTO lezioni_corso (id, corso_universitario_id, docente_id, titolo, contenuto_md, creato_da, approvato, chunk_ids_utilizzati) VALUES
(800, 110, 200, 'Introduzione a Java e alla Programmazione OOP',
'## Java: Un Linguaggio ad Oggetti

Java e un linguaggio **fortemente tipizzato** e **orientato agli oggetti**, creato da Sun Microsystems nel 1995.

### Tipi Primitivi
I tipi primitivi fondamentali: `int`, `double`, `boolean`, `char`.

### La Classe come Modello
Una classe definisce:
- **Attributi**: lo stato dell''oggetto
- **Metodi**: il comportamento
- **Costruttore**: inizializza lo stato

### Incapsulamento
I modificatori di accesso (`public`, `private`, `protected`) controllano la visibilita dei membri, proteggendo lo stato interno.',
'ai', 1, '[1001, 1002, 1003]'),

(801, 112, 204, 'Il Modello TCP/IP',
'## Architettura di Rete TCP/IP

Il modello TCP/IP organizza le comunicazioni in **4 livelli**:

### Livello Applicazione
HTTP, DNS, FTP, SMTP operano a questo livello.

### Livello Trasporto
- **TCP**: affidabile, orientato alla connessione, three-way handshake
- **UDP**: veloce, senza connessione, nessuna garanzia

### Livello Internet
IP instrada i pacchetti verso la destinazione attraverso router.

### DNS
Traduce nomi di dominio (www.example.com) in indirizzi IP.',
'ai', 1, '[1007, 1008, 1009]'),

(802, 113, 208, 'Processi, Thread e Concorrenza',
'## Gestione dei Processi

### Processi vs Thread
Un **processo** ha il proprio spazio di indirizzamento. I **thread** condividono lo spazio del processo padre.

### Scheduling
- **Round Robin**: ogni processo riceve un quanto di tempo uguale
- **SJF**: priorita al job piu corto
- **FCFS**: primo arrivato, primo servito

### Sincronizzazione
Le **race condition** si evitano con:
- **Mutex**: accesso esclusivo alla sezione critica
- **Semafori**: contatori per risorse condivise

### Deadlock
Si verifica quando processi si bloccano in attesa circolare di risorse.',
'ai', 1, '[1010, 1011, 1012]'),

(803, 120, 219, 'Introduzione al Machine Learning',
'## Cos''e il Machine Learning?

Il ML permette ai computer di **apprendere dai dati** senza essere programmati esplicitamente.

### Supervised Learning
- **Regressione**: predice valori continui (prezzi, temperature)
- **Classificazione**: assegna categorie (spam/non-spam)

### Modelli Fondamentali
- **Regressione lineare**: y = wx + b
- **SVM**: trova l''iperpiano di massimo margine
- **Random Forest**: ensemble di alberi decisionali

### Validazione
La **cross-validation k-fold** stima le performance su dati non visti, evitando overfitting.',
'ai', 1, '[1022, 1023, 1024]'),

(804, 119, 215, 'Fondamenti di Probabilita',
'## Probabilita: Concetti Base

### Spazio Campionario
L''insieme di tutti gli esiti possibili di un esperimento.

### Teorema di Bayes
P(A|B) = P(B|A) · P(A) / P(B)

Aggiorna le credenze alla luce di nuove evidenze.

### Distribuzioni Fondamentali
- **Binomiale**: successi in n prove
- **Normale**: la distribuzione a campana, fondamentale per il teorema del limite centrale
- **Poisson**: eventi rari in un intervallo

### Test di Ipotesi
Il **p-value** quantifica l''evidenza contro H0. Se p < alpha, si rifiuta H0.',
'ai', 1, '[1019, 1020, 1021]'),

(805, 121, 209, 'Strategia e Marketing',
'## Economia e Gestione delle Imprese

### Analisi Strategica
L''**analisi SWOT** e il punto di partenza: identifica forze e debolezze interne, opportunita e minacce esterne.

Le **cinque forze di Porter** analizzano la competitivita del settore.

### Marketing Mix: Le 4P
1. **Prodotto**: caratteristiche, qualita, design
2. **Prezzo**: strategia di pricing
3. **Place**: canali di distribuzione
4. **Promozione**: comunicazione e pubblicita

### Indicatori Finanziari
- **ROE**: redditivita del capitale proprio
- **ROI**: redditivita degli investimenti totali',
'ai', 1, '[1025, 1026, 1027]'),

(806, 125, 216, 'Automi e Calcolabilita',
'## Fondamenti di Informatica Teorica

### Automi Finiti
Un **DFA** e definito da (Q, Sigma, delta, q0, F). Riconosce i linguaggi **regolari**.

### Gerarchia di Chomsky
| Tipo | Linguaggio | Automa |
|------|-----------|--------|
| 3 | Regolare | DFA/NFA |
| 2 | Context-Free | Automa a pila |
| 1 | Context-Sensitive | LBA |
| 0 | Ric. Enumerabile | Macchina di Turing |

### La Macchina di Turing
Modello computazionale piu potente. Definisce i limiti della computazione.

### P vs NP
Il piu famoso problema aperto dell''informatica: ogni problema verificabile in tempo polinomiale e anche risolvibile in tempo polinomiale?',
'ai', 1, '[1028, 1029, 1030]'),

(807, 126, 224, 'Deep Learning: CNN e Transformer',
'## Reti Neurali Profonde

### CNN — Reti Convoluzionali
- **Convoluzione**: filtri estraggono feature locali
- **Pooling**: riduce la dimensionalita
- Architetture: LeNet, AlexNet, VGG, **ResNet**

### RNN e LSTM
Le RNN processano sequenze. Le **LSTM** risolvono il vanishing gradient con 3 gate.

### Transformer
Architettura basata su **self-attention**:
- Processa tutte le posizioni in parallelo
- Alla base di **BERT** e **GPT**

### Tecniche di Training
- **Dropout**: regolarizzazione
- **Batch Normalization**: stabilizza il training
- **Adam**: optimizer adattivo',
'ai', 1, '[1031, 1032, 1033]'),

(808, 129, 229, 'Natural Language Processing',
'## NLP: Dal Testo all''Intelligenza

### Tokenizzazione
Il testo viene spezzato in token. **BPE** (Byte Pair Encoding) e usato dai moderni LLM.

### Word Embeddings
- **Word2Vec**: CBOW e Skip-gram
- **GloVe**: co-occorrenze globali

### Modelli di Linguaggio
- **BERT**: masked LM bidirezionale
- **GPT**: autoregressive LM

### Applicazioni
- **Sentiment Analysis**: classifica il tono emotivo
- **NER**: identifica entita (persone, luoghi)
- **Question Answering**: estrae risposte da documenti',
'ai', 1, '[1034, 1035, 1036]');

-- ============================================================================
-- PIANI PERSONALIZZATI diversificati per il recommender
-- Studenti diversi hanno piani su corsi diversi → engagement diverso
-- ============================================================================
INSERT OR IGNORE INTO piani_personalizzati (id, studente_id, titolo, descrizione, tipo, corso_universitario_id, stato, created_at) VALUES
-- Lorenzo: piani su SO e Reti (engagement verso questi corsi)
(200, 300, 'Preparazione Sistemi Operativi', 'Piano di studio per l''esame di Sistemi Operativi. Focus su processi, thread e gestione memoria.', 'esame', 113, 'attivo', '2026-03-01 10:00:00'),
(201, 300, 'Ripasso Reti di Calcolatori', 'Piano per il ripasso di protocolli TCP/IP, HTTP e DNS.', 'esame', 112, 'attivo', '2026-03-08 10:00:00'),
-- Alessia: piani su Ing. Software e ML
(202, 301, 'Preparazione Ingegneria del Software', 'Piano per UML, design pattern e testing.', 'esame', 114, 'attivo', '2026-02-20 10:00:00'),
(203, 301, 'Studio Machine Learning', 'Piano per regressione, SVM e reti neurali.', 'esame', 120, 'attivo', '2026-03-10 10:00:00'),
-- Sofia: piani su SO e Statistica
(204, 303, 'Preparazione Sistemi Operativi', 'Piano per scheduling, sincronizzazione e memoria virtuale.', 'esame', 113, 'attivo', '2026-03-01 10:00:00'),
(205, 303, 'Preparazione Probabilita', 'Piano per Bayes, distribuzioni e test di ipotesi.', 'esame', 119, 'attivo', '2026-03-08 10:00:00'),
-- Emma: piani su ML e NLP (interesse IA)
(206, 305, 'Deep Dive Machine Learning', 'Piano avanzato su ensemble, reti neurali e validazione.', 'esame', 120, 'attivo', '2026-02-15 10:00:00'),
(207, 305, 'Studio NLP', 'Piano per embeddings, transformer e applicazioni NLP.', 'esame', 129, 'attivo', '2026-03-05 10:00:00'),
-- Diego: piani su Statistica e Ricerca Operativa (interesse gestionale)
(208, 308, 'Preparazione Probabilita', 'Piano per probabilita, distribuzioni e inferenza.', 'esame', 119, 'attivo', '2026-03-01 10:00:00'),
(209, 308, 'Preparazione Ricerca Operativa', 'Piano per PL, grafi e ottimizzazione combinatoria.', 'esame', 122, 'attivo', '2026-03-08 10:00:00'),
-- Edoardo: piani su ML e Deep Learning (interesse data science)
(210, 314, 'Preparazione Machine Learning', 'Piano per regressione, classificazione e validazione.', 'esame', 120, 'attivo', '2026-02-20 10:00:00'),
(211, 314, 'Studio Deep Learning', 'Piano per CNN, LSTM, Transformer e tecniche avanzate.', 'esame', 126, 'attivo', '2026-03-05 10:00:00'),
-- Leonardo: piano su Bioingegneria
(212, 312, 'Preparazione Bioingegneria', 'Piano per sensori, amplificatori e sicurezza clinica.', 'esame', 123, 'attivo', '2026-03-01 10:00:00'),
-- Filippo: piani su ML e NLP (simile a Edoardo ma con NLP)
(213, 318, 'Studio Machine Learning', 'Piano per ML supervisionato e non supervisionato.', 'esame', 120, 'attivo', '2026-02-25 10:00:00'),
(214, 318, 'Preparazione NLP', 'Piano per tokenizzazione, BERT, GPT e applicazioni.', 'esame', 129, 'attivo', '2026-03-10 10:00:00'),
-- Ginevra: piano su Ricerca Operativa
(215, 317, 'Preparazione Ricerca Operativa', 'Piano per programmazione lineare, grafi e TSP.', 'esame', 122, 'attivo', '2026-03-01 10:00:00');

PRAGMA foreign_keys = ON;
