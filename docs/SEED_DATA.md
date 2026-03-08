# Seed Data & Mock Interfaces

## Scopo del Documento
Questo file funge da "contratto dei dati" per l'intera applicazione. Fornisce esempi concreti (in formato JSON) della struttura dei dati prima che il database sia completamente operativo. Le chiavi di questi JSON rispecchiano fedelmente le colonne definite in `schema.sql`. È un file vitale per il *vibecoding*: impedisce all'IA di inventare nomi di variabili o campi inesistenti durante la generazione di componenti UI o query.

---

### 1. Utente Studente (`users` — ruolo='studente')

I campi `matricola_docente` e `dipartimento` sono assenti: non vanno inclusi nel payload, nemmeno come `null`. I campi specifici del ruolo opposto non esistono per quell'utente.

```json
{
  "id": 1,
  "nome": "Giulia",
  "cognome": "Bianchi",
  "email": "g.bianchi@studenti.unina.it",
  "password_hash": "$2b$12$...",
  "ruolo": "studente",
  "stato": "active",
  "created_at": "2025-09-01T09:00:00",
  "data_nascita": "2001-04-15",
  "telefono": "+39 333 1234567",
  "matricola_studente": "N86001234",
  "corso_di_laurea_id": 3,
  "anno_corso": 2
}
```

---

### 2. Utente Docente (`users` — ruolo='docente')

I campi `data_nascita`, `telefono`, `matricola_studente`, `corso_di_laurea_id` e `anno_corso` sono assenti: appartengono al ruolo studente.

```json
{
  "id": 10,
  "nome": "Mario",
  "cognome": "Rossi",
  "email": "m.rossi@unina.it",
  "password_hash": "$2b$12$...",
  "ruolo": "docente",
  "stato": "active",
  "created_at": "2021-10-01T08:00:00",
  "matricola_docente": "DOC-2021-042",
  "dipartimento": "Ingegneria Informatica"
}
```

---

### 3. Utente Admin (`users` — ruolo='admin')

L'admin non ha campi ruolo-specifici. Record inserito manualmente — non esiste flusso di registrazione self-service per questo ruolo.

```json
{
  "id": 99,
  "nome": "Anna",
  "cognome": "Verdi",
  "email": "a.verdi@unina.it",
  "password_hash": "$2b$12$...",
  "ruolo": "admin",
  "stato": "active",
  "created_at": "2020-01-01T00:00:00"
}
```

---

### 4. Corso di Laurea (`corsi_di_laurea`)

```json
{
  "id": 3,
  "nome": "Ingegneria Informatica",
  "facolta": "Ingegneria",
  "created_at": "2020-01-01T00:00:00"
}
```

---

### 5. Corso Universitario (`corsi_universitari`)

`docente_id` referenzia `users.id` di un utente con `ruolo='docente'`.

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

### 6. Iscrizione Studente a Corso (`studenti_corsi`)

`studente_id` referenzia `users.id` di un utente con `ruolo='studente'`.

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

### 7. Materiale Didattico (`materiali_didattici`)

`docente_id` referenzia `users.id` di un utente con `ruolo='docente'`.

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

### 8. Chunk Semantico (`materiali_chunks`)

`embedding_sync=0` indica che il chunk non è ancora stato vettorizzato nel vector store esterno (es. ChromaDB). Il campo `id` di questo record è usato come `document_id` nella collection vettoriale corrispondente al corso.

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
  "embedding_sync": 0,
  "created_at": "2025-09-05T15:00:00"
}
```

---

### 9. Quiz (`quiz`) — Tipo C (approvato dal docente)

`docente_id` referenzia `users.id` con `ruolo='docente'`. `studente_id` è NULL per i quiz Tipo C.

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

### 10. Domanda Quiz (`domande_quiz`)

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

### 11. Tentativo Quiz (`tentativi_quiz`)

`studente_id` referenzia `users.id` con `ruolo='studente'`.

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

### 12. Piano Personalizzato (`piani_personalizzati`)

`studente_id` referenzia `users.id` con `ruolo='studente'`.

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

### 13. Capitolo del Piano (`piano_capitoli`)

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

### 14. Paragrafo del Piano (`piano_paragrafi`)

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

### 15. Contenuto del Piano — Flashcard (`piano_contenuti`)

Il campo `contenuto_json` delle flashcard può essere generato in formati diversi dai vari agenti AI.
Il codice di rendering in `views/studente.py` riconosce tutti i formati seguenti — **non normalizzare
a un solo formato in DB**: accettare e gestire tutti.

**Formato 1 — lista diretta (formato storico):**
```json
[
  { "domanda": "Cos'è una chiave primaria?", "risposta": "Un attributo che identifica univocamente ogni tupla." },
  { "domanda": "Cosa garantisce l'integrità referenziale?", "risposta": "Che ogni FK corrisponda a una PK esistente." }
]
```

**Formato 2 — wrapper `cards` (output ContentGen corrente):**
```json
{
  "cards": [
    { "fronte": "Cos'è una chiave primaria?", "retro": "Un attributo che identifica univocamente ogni tupla." },
    { "fronte": "Cosa garantisce l'integrità referenziale?", "retro": "Che ogni FK corrisponda a una PK esistente." }
  ]
}
```

**Formato 3 — wrapper `flashcard`:**
```json
{
  "flashcard": [
    { "front": "What is a primary key?", "back": "An attribute that uniquely identifies each tuple." }
  ]
}
```

**Campi alternativi riconosciuti per fronte/retro:**
- Fronte: `fronte` | `front` | `domanda`
- Retro: `retro` | `back` | `risposta`

**Record completo di esempio (`contenuto_json` come stringa serializzata):**
```json
{
  "id": 900,
  "paragrafo_id": 600,
  "tipo": "flashcard",
  "contenuto_json": "{\"cards\": [{\"fronte\": \"Cos'è una chiave primaria?\", \"retro\": \"Un attributo che identifica univocamente ogni tupla.\"}]}",
  "quiz_id": null,
  "chunk_ids_utilizzati": "[301, 302]",
  "generato_al_momento": 0,
  "created_at": "2025-10-05T08:05:00"
}
```

> **Nota implementativa — reveal interattivo:** Le flashcard usano `st.button` + `st.session_state`
> per il toggle fronte/retro. Non usare `<input type="checkbox">` in HTML Streamlit: viene
> sanitizzato dal renderer e il CSS `:checked ~` non funziona. Vedi `STATE_MANAGEMENT.md §3b`.

---

### 16. Lezione del Corso (`lezioni_corso`)

`docente_id` referenzia `users.id` con `ruolo='docente'`.

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

---

## Note Trasversali

**Convenzione sul campo `ruolo`:** Nel database il valore è sempre minuscolo (`'studente'`, `'docente'`, `'admin'`). In `st.session_state.user_role` viene capitalizzato all'ingresso in `app.py` (`user["ruolo"].capitalize()`). Non normalizzare il valore in altri punti del codice.

**Campi FK e validazione ruolo:** SQLite non impone CHECK constraint cross-tabella. Ogni volta che si inserisce un record con `studente_id` o `docente_id`, il codice in `db_handler.py` deve verificare che `users.ruolo` corrisponda al ruolo atteso prima dell'INSERT. Questo vale per: `studenti_corsi`, `quiz`, `tentativi_quiz`, `piani_personalizzati`, `materiali_didattici`, `lezioni_corso`.

**`embedding_sync` nei chunks:** Il campo funziona esattamente come `is_processed` nei materiali. Prima di vettorizzare un chunk, verificare sempre `embedding_sync=0`. Se `embedding_sync=1` il vettore esiste già nel vector store — non rielaborare.
