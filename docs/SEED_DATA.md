# Seed Data & Mock Interfaces

## Scopo del Documento
Questo file funge da "contratto dei dati" per l'intera applicazione. Fornisce esempi concreti (in formato JSON) della struttura dei dati prima che il database o le API siano completamente operativi. È un file vitale per il *vibe coding*, in quanto impedisce all'Intelligenza Artificiale di "allucinare" o inventare nomi di variabili inesistenti durante la generazione dei componenti UI o delle query.

## Contenuto del Documento
In questo file verranno definiti gli oggetti JSON di esempio per:
- **Utente (User):** Campi anagrafici, ruoli, preferenze e storico acquisti.
- **Corso (Course):** L'oggetto principale inclusi metadati (titolo, descrizione, prezzo, thumbnail).
- **Curriculum (Modules, Lessons, Quizzes):** La struttura annidata che mostra come i moduli contengono lezioni (video/testo) e quiz.
- **Progresso (Progress/Enrollment):** L'oggetto che traccia l'avanzamento dello studente all'interno del corso (es. percentuale di completamento, lezioni sbloccate).