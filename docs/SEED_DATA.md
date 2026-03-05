# Seed Data & Mock Interfaces

## Scopo del Documento
Questo file funge da "contratto dei dati" per l'intera applicazione. Fornisce esempi concreti (in formato JSON) della struttura dei dati prima che il database sia completamente operativo. Le chiavi di questi JSON rispecchiano fedelmente le colonne definite in `schema.sql`. È un file vitale per il *vibecoding*: impedisce all'IA di inventare nomi di variabili o campi inesistenti durante la generazione di componenti UI o query.

---

### 1. Studente (`studenti`)

```json
{
  "id": 1,
  "nome": "Giulia",
  "cognome": "Bianchi",
  "email": "g.bianchi@studenti.unina.it",
  "password_hash": "$2b$12$...",
  "data_nascita": "2001-04-15",
  "telefono": "+39 333 1234567",
  "corso_di_laurea_id": 3,
  "anno_corso": 2,
  "stato": "active",
  "created_at": "2025-09-01T09:00:00"
}
```

---

### 2. Docente (`docenti`)

```json
{
  "id": 10,
  "nome": "Mario",
  "cognome": "Rossi",
  "email": "m.rossi@unina.it",
  "password_hash": "$2b$12$...",
  "matricola_docente": "DOC-2021-042",
  "dipartimento": "Ingegneria Informatica",
  "stato": "active",
  "created_at": "2021-10-01T08:00:00"
}
```

---

### 3. Corso di Laurea (`corsi_di_laurea`)

```json
{
  "id": 3,
  "nome": "Ingegneria Informatica",
  "facolta": "Ingegneria",
  "created_at": "2020-01-01T00:00:00"
}
```

---

### 4. Corso Universitario (`corsi_universitari`)

```json
{
  "id": 101,
  "nome": "Basi di Dati",
  "descrizione": "Fondamenti di progettazione e gestione di basi di dati relazionali.",
  "docente_id": 10,
  "cfu": 9,
  "ore_lezione": 72,
  "anno_di_corso": 2,
  "semestre": 1,
  "livello": "intermedio",
  "attivo": 1,
  "created_at": "2025-09-01T00:00:00"
}
```

---

### 5. Iscrizione Studente a Corso (`studenti_corsi`)

```json
{
  "id": 500,
  "studente_id": 1,
  "corso_universitario_id": 101,
  "anno_accademico": "2025-2026",
  "stato": "iscritto",
  "voto": null,
  "data_iscrizione": "2025-09-15T10:00:00",
  "data_completamento": null
}
```

---

### 6. Materiale Didattico (`materiali_didattici`)

```json
{
  "id": 5001,
  "corso_universitario_id": 101,
  "docente_id": 10,
  "titolo": "Slide Capitolo 1 — Modello Relazionale",
  "tipo": "pdf",
  "s3_key": "didattica/corsi/101/slide_cap1.pdf",
  "testo_estratto": "Il modello relazionale è basato sul concetto di relazione...",
  "is_processed": 1,
  "caricato_il": "2025-09-05T14:30:00"
}
```

---

### 7. Chunk Semantico (`materiali_chunks`)

```json
{
  "id": 301,
  "materiale_id": 5001,
  "corso_universitario_id": 101,
  "indice_chunk": 2,
  "titolo_sezione": "Chiavi primarie e vincoli di integrità",
  "testo": "Una chiave primaria identifica univocamente ogni tupla in una relazione...",
  "sommario": "Definizione e ruolo delle chiavi primarie nel modello relazionale.",
  "argomenti_chiave": ["chiave primaria", "integrità referenziale", "vincoli"],
  "livello_difficolta": 2,
  "pagine_riferimento": [12, 13],
  "n_token": 420,
  "created_at": "2025-09-05T15:00:00"
}
```

---

### 8. Quiz (`quiz`) — Tipo C (approvato dal docente)

```json
{
  "id": 300,
  "titolo": "Test — Modello Relazionale",
  "corso_universitario_id": 101,
  "studente_id": null,
  "docente_id": 10,
  "creato_da": "ai",
  "approvato": 1,
  "ripetibile": 0,
  "created_at": "2025-10-01T09:00:00"
}
```

---

### 9. Domanda Quiz (`domande_quiz`)

```json
{
  "id": 1001,
  "quiz_id": 300,
  "testo": "Quale tra le seguenti è una proprietà della chiave primaria?",
  "tipo": "scelta_multipla",
  "opzioni_json": ["Può contenere NULL", "Identifica univocamente ogni tupla", "Può essere duplicata", "È opzionale"],
  "risposta_corretta": "Identifica univocamente ogni tupla",
  "spiegazione": "La chiave primaria deve essere unica e non nulla per ogni record della relazione.",
  "ordine": 1,
  "chunk_id": 301
}
```

---

### 10. Tentativo Quiz (`tentativi_quiz`)

```json
{
  "id": 800,
  "quiz_id": 300,
  "studente_id": 1,
  "punteggio": 72.5,
  "aree_deboli_json": ["integrità referenziale", "forme normali"],
  "completato": 1,
  "created_at": "2025-10-10T11:00:00"
}
```

---

### 11. Piano Personalizzato (`piani_personalizzati`)

```json
{
  "id": 50,
  "studente_id": 1,
  "titolo": "Preparazione Esame Basi di Dati",
  "descrizione": "Piano per la preparazione all'esame di Basi di Dati, con focus su normalizzazione e SQL avanzato.",
  "tipo": "esame",
  "corso_universitario_id": 101,
  "stato": "attivo",
  "created_at": "2025-10-05T08:00:00",
  "aggiornato_il": "2025-10-12T16:30:00"
}
```

---

### 12. Capitolo del Piano (`piano_capitoli`)

```json
{
  "id": 200,
  "piano_id": 50,
  "titolo": "Modello Relazionale e Algebra",
  "descrizione": "Fondamenti del modello relazionale, operatori dell'algebra relazionale.",
  "ordine": 1,
  "completato": 0,
  "created_at": "2025-10-05T08:01:00"
}
```

---

### 13. Paragrafo del Piano (`piano_paragrafi`)

```json
{
  "id": 600,
  "capitolo_id": 200,
  "titolo": "Chiavi e Vincoli di Integrità",
  "descrizione": "Chiave primaria, chiave esterna, vincoli NOT NULL e UNIQUE.",
  "ordine": 2,
  "completato": 0,
  "created_at": "2025-10-05T08:02:00"
}
```

---

### 14. Contenuto del Piano — Flashcard (`piano_contenuti`)

```json
{
  "id": 900,
  "paragrafo_id": 600,
  "tipo": "flashcard",
  "contenuto_json": [
    { "domanda": "Cos'è una chiave primaria?", "risposta": "Un attributo o insieme di attributi che identifica univocamente ogni tupla." },
    { "domanda": "Cosa garantisce il vincolo di integrità referenziale?", "risposta": "Che ogni valore di chiave esterna corrisponda a un valore esistente nella tabella referenziata." }
  ],
  "quiz_id": null,
  "chunk_ids_utilizzati": [301, 302],
  "generato_al_momento": 0,
  "created_at": "2025-10-05T08:05:00"
}
```

---

### 15. Lezione del Corso (`lezioni_corso`)

```json
{
  "id": 700,
  "corso_universitario_id": 101,
  "docente_id": 10,
  "titolo": "Introduzione al Modello Relazionale",
  "contenuto_md": "## Il Modello Relazionale\nIl modello relazionale organizza i dati in **relazioni** (tabelle)...",
  "creato_da": "ai",
  "approvato": 1,
  "chunk_ids_utilizzati": [301, 302, 303],
  "created_at": "2025-09-20T10:00:00",
  "aggiornato_il": "2025-09-22T14:00:00"
}
```
