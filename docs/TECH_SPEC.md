# Technical Specifications

## Scopo del Documento
Questo file definisce il manifesto tecnologico e operativo del progetto. Il suo obiettivo è stabilire un "perimetro tecnico" rigoroso entro il quale gli sviluppatori e gli agenti IA devono operare, garantendo coerenza, sicurezza e standardizzazione in tutto il ciclo di vita del software.

## Contenuto del Documento
In questo file verranno definiti:
- **Stack Tecnologico:** L'elenco esatto di linguaggi, framework e database adottati, incluse le versioni specifiche.
- **Requisiti di Sicurezza:** Le policy per la gestione dei dati sensibili, l'autenticazione e la crittografia (es. gestione rigorosa dei segreti tramite file `.env`).
- **Vincoli di Performance:** I limiti operativi e i requisiti di scalabilità o latenza del sistema.
- **Integrazioni Esterne:** La mappatura delle API di terze parti e dei servizi cloud integrati nell'architettura.


*Nota: Questa è una versione preliminare (Draft) basata sul file `requirements.txt` iniziale. Verrà aggiornata in seguito alla stesura definitiva del `PRD.md`.*

## 1. Stack Tecnologico
[cite_start]L'applicazione è sviluppata in un ambiente unificato basato su Python[cite: 5, 8].
- [cite_start]**Linguaggio Base:** Python (standard PEP 8)[cite: 5].
- **Interfaccia Utente (Frontend/Fullstack):** `streamlit` (>=1.30.0). Utilizzato per creare rapidamente l'interfaccia interattiva dell'E-Learning senza separare frontend e backend.
- **Data Manipulation & Analisi:** `pandas` (>=2.1.0) per la manipolazione strutturata dei dati (es. anagrafiche, progressi) e `openpyxl` (>=3.1.0) per l'export/import di report in formato Excel.
- **Data Visualization:** `plotly` (>=5.18.0) per la renderizzazione di grafici interattivi (es. dashboard dei progressi degli studenti).

## 2. Intelligenza Artificiale & Document Processing
La piattaforma integra funzionalità avanzate di AI Generativa per assistere l'apprendimento:
- **Core AI Framework:** `langchain` (>=0.3.0) per l'orchestrazione dei prompt e `langgraph` (>=0.2.0) per la gestione di agenti AI con stato (es. un tutor virtuale che ricorda la conversazione).
- **Elaborazione Materiale Didattico:** `PyPDF2` (>=3.0.0) per l'estrazione e l'analisi del testo dalle dispense PDF fornite nei corsi (RAG - Retrieval-Augmented Generation).

## 3. Integrazioni Esterne e Cloud
[cite_start]L'infrastruttura si affida ai servizi cloud di Amazon Web Services (AWS)[cite: 8]:
- **Integrazione Cloud Base:** `boto3` (>=1.34.0) per l'interazione diretta con i servizi AWS (es. Amazon S3 per l'archiviazione di video, PDF o immagini dei corsi).
- **Integrazione AI Cloud:** `langchain-aws` (>=0.2.0) per l'accesso ai modelli linguistici ospitati su Amazon Bedrock.

## 4. Requisiti di Sicurezza
- [cite_start]**Gestione dei Segreti:** È severamente vietato scrivere chiavi API (AWS, LLM, ecc.) o password in chiaro nel codice sorgente[cite: 9]. 
- [cite_start]**Variabili d'Ambiente:** Tutte le configurazioni sensibili devono risiedere nel file `.env`, che verrà caricato a runtime esclusivamente tramite la libreria `python-dotenv` (>=1.0.0)[cite: 10]. Il file `.env` deve essere inserito nel `.gitignore`.

## 5. Vincoli di Performance (To Be Defined)
*Questa sezione verrà espansa dopo aver definito il PRD.*
- **Streamlit State:** Lo stato dell'utente (session state) deve essere gestito in modo ottimizzato per evitare il ricaricamento non necessario di componenti pesanti (es. video player o grafici Plotly).
- **Latenza AI:** Le chiamate a LangChain/AWS Bedrock dovranno implementare meccanismi di streaming per fornire feedback in tempo reale allo studente, riducendo la latenza percepita.