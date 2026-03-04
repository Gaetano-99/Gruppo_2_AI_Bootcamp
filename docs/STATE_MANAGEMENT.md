# State Management

## Scopo del Documento
Questo file definisce le regole per la gestione dello stato dell'applicazione (sia frontend che backend). In una piattaforma di E-Learning, lo stato cambia continuamente (es. progresso video, risposte ai quiz, stato di login). Questo documento serve a evitare che l'IA o gli sviluppatori utilizzino pattern o librerie diverse per gestire dati temporanei o globali, garantendo coerenza, performance e stabilità.

## Contenuto del Documento
In questo file verranno definiti:
- **Tecnologie Scelte:** Le librerie o i pattern ufficiali per lo stato globale e locale .
- **Stato Utente e Autenticazione:** Come viene archiviato e aggiornato lo stato di login, il ruolo (Studente vs Insegnante) e i permessi.
- **Tracking dei Progressi:** La strategia esatta per sincronizzare lo stato temporaneo (es. a che minuto si trova un video) con il salvataggio persistente nel database.
- **Stati UI (Loading & Error):** Le convenzioni su come rappresentare e gestire uniformemente i caricamenti e gli errori in tutta l'applicazione.