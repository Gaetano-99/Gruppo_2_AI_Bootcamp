# src/agents/dati_questionario.py

QUESTIONARIO_ORIENTAMENTO = [
    {
        "id": 1,
        "domanda": "Quando affronti un problema complesso, quale approccio preferisci?",
        "opzioni": [
            "Analizzo i dati logici e numerici per trovare una soluzione.",
            "Cerco di capire il contesto umano e sociale della situazione.",
            "Provo a costruire o progettare una soluzione pratica.",
            "Valuto l'impatto economico e strategico delle possibili opzioni."
        ]
    },
    {
        "id": 2,
        "domanda": "Quale tra queste materie scolastiche hai trovato più stimolante?",
        "opzioni": [
            "Matematica, Fisica o Informatica.",
            "Letteratura, Storia o Filosofia.",
            "Scienze della Terra, Biologia o Chimica.",
            "Diritto, Economia o Lingue Straniere."
        ]
    },
    {
        "id": 3,
        "domanda": "Come descriveresti il tuo rapporto con la tecnologia?",
        "opzioni": [
            "Amo capire come funzionano i software e i sistemi informatici alla base.",
            "La uso come strumento per comunicare ed esprimere idee.",
            "Mi affascina la progettazione e l'hardware dietro i dispositivi.",
            "Mi interessa capire come l'innovazione tecnologica cambia i mercati."
        ]
    },
    {
        "id": 4,
        "domanda": "In un lavoro di gruppo, qual è di solito il tuo ruolo?",
        "opzioni": [
            "Quello che struttura il lavoro, definisce le regole e verifica i dati.",
            "Quello che media tra le persone e assicura l'armonia nel gruppo.",
            "Quello che propone soluzioni creative o costruisce il progetto materiale.",
            "Quello che coordina le risorse, i tempi e gli obiettivi da raggiungere."
        ]
    },
    {
        "id": 5,
        "domanda": "Cosa preferisci leggere nel tempo libero?",
        "opzioni": [
            "Saggi scientifici, documentari di tecnologia o sfide logiche.",
            "Romanzi, libri di psicologia o saggi storici.",
            "Riviste di architettura, design o scoperte ambientali.",
            "Notizie di attualità, finanza pubblica o relazioni internazionali."
        ]
    },
    {
        "id": 6,
        "domanda": "Immagina di voler migliorare il mondo. Su cosa ti concentreresti?",
        "opzioni": [
            "Sviluppare nuove tecnologie o algoritmi più efficienti.",
            "Promuovere l'educazione, la cultura o l'assistenza alle persone.",
            "Progettare città più sostenibili o cure mediche avanzate.",
            "Creare un sistema economico più equo ed efficiente."
        ]
    },
    {
        "id": 7,
        "domanda": "Quale di queste attività ti rilassa di più?",
        "opzioni": [
            "Risolvere puzzle, sudoku o programmare al computer.",
            "Scrivere, leggere o discutere di temi profondi.",
            "Disegnare, costruire o fare esperimenti pratici.",
            "Organizzare eventi, gestire budget o pianificare viaggi."
        ]
    },
    {
        "id": 8,
        "domanda": "Come gestisci lo studio e la memorizzazione?",
        "opzioni": [
            "Capisco i concetti logici; se capisco il perché, non devo imparare a memoria.",
            "Associo storie, parole chiave e concetti umanistici.",
            "Ho bisogno di schemi visivi, disegni o esempi pratici e fisici.",
            "Mi concentro sui punti chiave e sulle applicazioni strategiche."
        ]
    },
    {
        "id": 9,
        "domanda": "Se dovessi scegliere un programma televisivo o un documentario, quale sceglieresti?",
        "opzioni": [
            "Come è fatto un supercomputer o i segreti dell'universo.",
            "La biografia di un personaggio storico o un dibattito sociale.",
            "Le meraviglie della natura, il corpo umano o le mega-costruzioni.",
            "L'evoluzione dei mercati finanziari o le strategie aziendali."
        ]
    },
    {
        "id": 10,
        "domanda": "In quale ambiente di lavoro ti vedresti meglio?",
        "opzioni": [
            "Un laboratorio di ricerca avanzata o davanti a un computer.",
            "Una scuola, una redazione giornalistica o un centro d'aiuto.",
            "Un ospedale, una clinica, un cantiere o un parco naturale.",
            "In un ufficio aziendale, una banca o un tribunale."
        ]
    },
    {
        "id": 11,
        "domanda": "Quando ti viene spiegato un nuovo concetto, cosa chiedi per prima cosa?",
        "opzioni": [
            "'Quali sono i principi logici e matematici che lo governano?'",
            "'Come influenza le persone, la cultura o la società?'",
            "'Come posso osservarlo, toccarlo o costruirlo nella realtà?'",
            "'Quanto costa implementarlo e che vantaggio economico offre?'"
        ]
    },
    {
        "id": 12,
        "domanda": "Quale verbo ti rappresenta di più?",
        "opzioni": [
            "Calcolare / Analizzare.",
            "Comprendere / Esprimere.",
            "Costruire / Curare.",
            "Organizzare / Gestire."
        ]
    },
    {
        "id": 13,
        "domanda": "Ti affascinano di più le scoperte nel campo di:",
        "opzioni": [
            "Intelligenza Artificiale e Fisica Quantistica.",
            "Psicologia, Sociologia e Ricerca Storica.",
            "Biotecnologie, Medicina e Ingegneria dei Materiali.",
            "Criptovalute, Mercati Emergenti e Diritto Internazionale."
        ]
    },
    {
        "id": 14,
        "domanda": "Se fossi un esploratore, preferiresti esplorare:",
        "opzioni": [
            "Il cyberspazio o i dati complessi (Data Base).",
            "Culture antiche o società isolate e le loro abitudini.",
            "Grandi ecosistemi come l'oceano o il corpo umano a livello cellulare.",
            "I meccanismi segreti della macroeconomia mondiale."
        ]
    },
    {
        "id": 15,
        "domanda": "Qual è il tuo approccio ai cambiamenti imprevisti?",
        "opzioni": [
            "Trovo rapidamente un nuovo schema logico su cui basarmi.",
            "Parlo con le persone coinvolte per gestire lo stress emotivo.",
            "Provo subito a mettere in pratica soluzioni alternative e tangibili.",
            "Ricalcolo i rischi, i benefici e ottimizzo le risorse."
        ]
    },
    {
        "id": 16,
        "domanda": "Cosa ammiri di più in un leader?",
        "opzioni": [
            "La sua intelligenza analitica e la capacità di visione tecnologica.",
            "La sua capacità di ispirare, comunicare e connettersi emotivamente.",
            "La dedizione alla cura degli altri o la costruzione di opere grandiose.",
            "La capacità organizzativa, finanziaria e decisionale."
        ]
    },
    {
        "id": 17,
        "domanda": "Tra queste professioni, quale ti incuriosisce di più in segreto?",
        "opzioni": [
            "Scienziato dati / Sviluppatore.",
            "Scrittore / Psicologo.",
            "Chirurgo / Ingegnere Navale.",
            "Manager Aziendale / Avvocato."
        ]
    },
    {
        "id": 18,
        "domanda": "Se dovessi risolvere un conflitto, il tuo primo pensiero sarebbe:",
        "opzioni": [
            "Guardare ai fatti concreti ed eliminare l'emotività.",
            "Capire i sentimenti e i punti di appoggio di entrambe le parti.",
            "Agire subito per evitare danni, come curare una ferita urgente.",
            "Capire qual è l'interesse in gioco e negoziare un compromesso."
        ]
    },
    {
        "id": 19,
        "domanda": "Se potessi imparare una nuova abilità in pochi secondi, sceglieresti:",
        "opzioni": [
            "Saper programmare in qualsiasi linguaggio di coding esistente.",
            "Parlare perfettamente tutte le lingue del mondo viva e morta.",
            "Sapere come eseguire qualsiasi intervento chirurgico o progetto edile.",
            "Conoscere a memoria tutte le leggi o il mercato azionario."
        ]
    },
    {
        "id": 20,
        "domanda": "Ti viene assegnato un grande budget, per cosa lo useresti?",
        "opzioni": [
            "Ricerca di base, sistemi informatici o missioni spaziali.",
            "Sostegno alle arti, musei o educazione dell'infanzia.",
            "Realizzazione di un nuovo ospedale o un'infrastruttura green.",
            "Avviare startup, fondi di investimento o difese legali."
        ]
    },
    {
        "id": 21,
        "domanda": "Qual è il tuo strumento di lavoro preferito?",
        "opzioni": [
            "Risolutori matematici, IDE per il codice o software di logica.",
            "Quaderni, libri, microfono o strumenti per il debriefing umano.",
            "Microscopio, bisturi, attrezzi meccanici o software di disegno 3D.",
            "Fogli Excel, contratti o software per la gestione aziendale."
        ]
    },
    {
        "id": 22,
        "domanda": "Che tipo di giochi da tavolo preferisci?",
        "opzioni": [
            "Giochi di strategia pura, scacchi o astrazione matematica.",
            "Giochi di ruolo (es. D&D), narrazione o trivia di cultura generale.",
            "Giochi in cui si costruiscono risorse, città o laboratori.",
            "Giochi di negoziazione, commercio o controllo dei territori (es. Risiko, Monopoly)."
        ]
    },
    {
        "id": 23,
        "domanda": "Come gestisci i fallimenti o gli errori?",
        "opzioni": [
            "Analizzo il 'bug' logico e ritento aggiustando l'algoritmo.",
            "Ne parlo con qualcuno, analizzo le ragioni psicologiche e imparo.",
            "Riaggiusto fisicamente il prototipo o ricomincio il processo da capo.",
            "Analizzo la perdita in termini di tempo/denaro e ottimizzo il prossimo piano."
        ]
    },
    {
        "id": 24,
        "domanda": "Cosa è più importante per te durante lo studio universitario?",
        "opzioni": [
            "Imparare a risolvere problemi complessi e teorici.",
            "Esplorare il mondo, le idee, l'etica e l'animo umano.",
            "Fare molta pratica, tirocini, curare pazienti o stare in cantiere / laboratorio.",
            "Costruire un network solido e acquisire competenze spendibili nel management."
        ]
    },
    {
        "id": 25,
        "domanda": "Se fossi l'autore di un blog o canale YouTube, di cosa parleresti?",
        "opzioni": [
            "Nuove tecnologie, intelligenza artificiale o matematica applicata.",
            "Recensioni di libri storici, analisi della società o psicologia.",
            "Scoperte mediche, tutela dell'ambiente o tecniche di ingegneria pura.",
            "Economia per tutti, imprenditoria o diritti legali dei cittadini."
        ]
    },
    {
        "id": 26,
        "domanda": "Ti è mai capitato di chiederti...",
        "opzioni": [
            "'Come è stato programmato o strutturato questo algoritmo interno?'",
            "'Cosa pensava l'autore o le persone quando hanno affrontato questo evento?'",
            "'Come funziona fisicamente dentro, potrei smontarlo e ricostruirlo o curarlo?'",
            "'Quanti profitti sta generando o chi detiene il controllo di questa iniziativa?'"
        ]
    },
    {
        "id": 27,
        "domanda": "Scegli l'aggettivo che usi di più per lodare un progetto altrui:",
        "opzioni": [
            "Brillante (Logico e intelligente).",
            "Profondo (Umano e significativo).",
            "Funzionale (Pratico e ben fatto).",
            "Efficace (Strategico e vantaggioso)."
        ]
    },
    {
        "id": 28,
        "domanda": "Quale argomento delle superiori non sopportavi?",
        "opzioni": [
            "Imparare date o letteratura a memoria senza logica.",
            "Formule matematiche rigide e astratte senza una storia dietro.",
            "Studio teorico infinito senza mai un'applicazione pratica o di laboratorio.",
            "Materie scollegate dalla realtà del mondo del lavoro e dell'impresa."
        ]
    },
    {
        "id": 29,
        "domanda": "Dove pensi di poter fare davvero la differenza?",
        "opzioni": [
            "Inventando un nuovo tipo di elaborazione dati o modello logico.",
            "Aiutando concretamente chi ha bisogno di supporto psicologico o culturale.",
            "Salvando vite come medico o costruendo opere civili sicure.",
            "Guidando un'impresa di successo o difendendo i diritti delle persone in tribunale."
        ]
    },
    {
        "id": 30,
        "domanda": "Alla fine del tuo percorso di studi, il tuo obiettivo principale sarà:",
        "opzioni": [
            "Risolvere problematiche altamente tecniche ed essere un esperto ricercatore/sviluppatore.",
            "Comunicare, insegnare, o scrivere per lasciare un'impronta umana.",
            "Applicare conoscenze per guarire, produrre, coltivare o costruire fisicamente.",
            "Diventare un professionista in grado di gestire business, giustizia o finanza."
        ]
    }
]
