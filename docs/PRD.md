# Product Requirements Document (PRD)

## Scopo del Documento
Questo documento rappresenta la visione strategica e il "documento d'identità" della nostra applicazione. Serve a mantenere l'intero team di sviluppo e gli strumenti di Intelligenza Artificiale (AI coding assistants) perfettamente allineati sugli obiettivi di business e sul valore reale del prodotto.

## Contenuto del Documento
In questo file verranno definiti:
- **Visione e Obiettivi:** Il problema fondamentale che l'applicazione intende risolvere.
- **Target (User Personas):** La definizione accurata delle tipologie di utenti finali.
- **Value Proposition:** Il valore aggiunto specifico offerto a ciascuna categoria di utente.
- **Funzionalità e User Stories:** L'elenco dettagliato dei requisiti funzionali, strutturati per casi d'uso, per guidare lo sviluppo in modo mirato e misurabile.

## 1. Visione e Obiettivi

* **Problema Fondamentale:** La necessità di orientare i futuri studenti, personalizzare lo studio per gli iscritti e fornire ai docenti strumenti avanzati per la creazione di materiali e il monitoraggio delle classi.
* **Visione del Prodotto:** Sviluppo di una piattaforma E-learning innovativa per l'università Federico II, basata su un'architettura IA multiagente.
* **Obiettivi di Business (KPIs):** 

* Per gli studenti: migliorare l'apprendimento e facilitare il superamento degli esami.
* Per i docenti: facilitare lo sviluppo dei corsi in aula e ottimizzare la valutazione degli studenti.



## 2. Target (User Personas)

* **Persona 1 - Futuro Studente:** Un utente non ancora immatricolato che, dopo aver creato un account, compila questionari su interessi, ambizioni future e background.
* **Persona 2 - Studente:** Un utente immatricolato che utilizza la piattaforma quotidianamente per accedere a percorsi di studio ideali, generare materiali di ripasso (riassunti, flashcard, quiz) e monitorare la propria preparazione.
* **Persona 3 - Docente:** Il professore che carica materiali didattici (videolezioni, materiali, libri) e necessita di strumenti per creare test/slide, lanciare challenge e monitorare l'andamento della classe.

## 3. Value Proposition

* **Per il Futuro Studente:** Un "Onboarding Ai" che offre guida all'orientamento per far capire in cosa l'utente è portato e la possibilità di ottenere "Certificazioni" in materie portanti per accedere all'università senza test d'ingresso.
* **Per lo Studente:** Un'interfaccia basata su un chatbot che chiede "Cosa vuoi imparare oggi?", in grado di rispondere a domande su esami, creare percorsi di studio su misura e identificare lacune tramite l'analisi di quiz e questionari. **Il valore aggiunto e il motivo principale per cui lo studente utilizza la piattaforma è la garanzia della qualità del materiale didattico: l'IA genera contenuti per la preparazione agli esami (riassunti, flashcard, quiz) basandosi esclusivamente sulle fonti ufficiali fornite dal docente, eliminando il rischio di studiare su appunti errati o fuori programma.**
* **Per il Docente:** Un assistente virtuale che chiede "Come posso supportarti oggi?", risponde a domande sull'andamento delle classi e genera dashboard interattive per evidenziare gli argomenti più ostici del corso.

4. Ecosistema Multiagente (High-Level Concept)


La piattaforma è governata da un'architettura multiagente avanzata, in cui moduli specializzati collaborano per offrire un'esperienza iper-personalizzata a studenti e docenti.

Agent 1: ONBOARDING ASSISTANT: Un chatbot intelligente che accoglie i futuri studenti e i nuovi utenti, raccogliendo informazioni dal loro CV tramite upload. Attraverso una conversazione guidata, completa il profilo utente e salva i dati in modo strutturato, proponendo un assessment iniziale basato sulle aspirazioni.

Agent 2: INTELLIGENT LEARNING PATH SCHEDULER: Analizza il profilo dell'utente e i risultati dell'assessment, consultando il catalogo corsi. Propone percorsi formativi personalizzati su breve, medio e lungo termine, organizzando la schedulazione nel rispetto dei prerequisiti e della progressione didattica.

Agent 3: CONVERSATIONAL LEARNING PLAN OPTIMIZER: Consente allo studente di visualizzare il proprio piano formativo e di richiedere modifiche tramite linguaggio naturale (es. spostare, aggiungere o rimuovere corsi). L'AI propone alternative coerenti e le applica in tempo reale.

Agent 4: AI-DRIVEN PROGRESS MONITORING AGENT: Traccia l'avanzamento formativo tramite dashboard con KPI. Identifica automaticamente situazioni critiche (ritardi o inattività), genera alert intelligenti e produce bozze di email personalizzate per i docenti, garantendo un intervento tempestivo.

Agent 5: ADAPTIVE CONTENT GENERATION ENGINE: Genera contenuti strutturati e quiz interattivi con correzione automatica. Cruciale: Questo agente adatta dinamicamente la difficoltà in base alle risposte dell'utente, ma attinge come unica "fonte di verità" esclusivamente ai materiali caricati dal docente, garantendo l'assoluta affidabilità per la preparazione agli esami.

Agent 6: SMART SURVEY LIFECYCLE MANAGER: Gestisce l'intero ciclo delle survey (post-corso o periodiche), generando domande contestualizzate. Analizza le risposte con tecniche di sentiment analysis per fornire ai docenti dashboard aggregate con insight azionabili per migliorare la didattica.

Agent 7: COMPETENCY GAP ANALYSIS AI: Visualizza il profilo competenze dell'utente rispetto a un obiettivo (es. esame target o ruolo lavorativo). Analizza il gap, produce un report visuale e raccomanda corsi o moduli specifici dal catalogo per colmare le lacune identificate.

## 5. Funzionalità e User Stories

Epic 1: Orientamento e Onboarding (Ramo Futuro Studente/Nuovo Iscritto)

User Story 1.1: Come nuovo utente, voglio fare l'upload del mio CV e interagire con l'Onboarding Assistant, in modo da completare rapidamente il mio profilo ed effettuare un assessment iniziale.

User Story 1.2: Come futuro studente, voglio che l'Intelligent Learning Path Scheduler mi proponga un percorso a breve/medio termine basato sulle mie aspirazioni, in modo da poter ottenere certificazioni propedeutiche all'immatricolazione.

Epic 2: Apprendimento e Preparazione (Ramo Studente)

User Story 2.1: Come studente, voglio usare il Conversational Learning Plan Optimizer per chiedere in linguaggio naturale di spostare o aggiungere un corso al mio piano di studi, ricevendo alternative valide e applicabili in tempo reale.

User Story 2.2: Come studente, voglio che l'Adaptive Content Generation Engine mi crei quiz e flashcard dinamici che si adattino al mio livello di difficoltà, basandosi rigorosamente sulle videolezioni del mio prof, per prepararmi all'esame in sicurezza.

User Story 2.3: Come studente, voglio utilizzare la Competency Gap Analysis AI per confrontare la mia preparazione attuale con i requisiti di un esame, in modo da ricevere raccomandazioni mirate su quali argomenti ripetere.

Epic 3: Supporto alla Didattica e Monitoraggio (Ramo Docenti)

User Story 3.1: Come docente, voglio caricare i miei materiali sulla piattaforma affinché l'Adaptive Content Generation Engine li usi come base esclusiva per generare i supporti didattici per i miei studenti.

User Story 3.2: Come docente, voglio consultare le dashboard generate dall'AI-Driven Progress Monitoring Agent, in modo da individuare immediatamente gli studenti a rischio ritardo o inattività.

User Story 3.3: Come docente, voglio che il sistema generi bozze di email personalizzate per gli studenti in difficoltà, in modo da poter intervenire tempestivamente con supporto mirato.

User Story 3.4: Come docente, voglio accedere agli insight dello Smart Survey Lifecycle Manager, in modo da capire tramite la sentiment analysis quali parti del mio corso necessitano di miglioramenti.

