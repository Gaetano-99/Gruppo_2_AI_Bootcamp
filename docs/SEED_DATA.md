# Seed Data & Mock Interfaces

## Scopo del Documento
Questo file funge da "contratto dei dati" per l'intera applicazione. Fornisce esempi concreti (in formato JSON) della struttura dei dati prima che il database o le API siano completamente operativi. Le chiavi di questi JSON rispecchiano **fedelmente** le colonne del database relazionale definite in `schema.sql` e i parametri accettati da `platform_sdk/database.py`.

> **Regola di utilizzo:** Quando si chiama `db.inserisci("tabella", dati)`, i campi `dict` o `list` vengono automaticamente serializzati in JSON da `_serializza_json()`. Non è necessario chiamare `json.dumps()` manualmente.

---

## 1. Utente e Competenze (`users`, `skills`, `user_skills`)

```json
{
  "id": 1,
  "nome": "Giulia",
  "cognome": "Bianchi",
  "email": "g.bianchi@studenti.unina.it",
  "ruolo": "Studente",
  "dipartimento": "Informatica",
  "cv_testo": "Giulia Bianchi, laureanda in Informatica. Esperienza con Python e analisi dati...",
  "profilo_json": {
    "interessi": ["Data Science", "Intelligenza Artificiale"],
    "obiettivi": "Diventare Data Scientist"
  },
  "competenze": [
    {
      "skill_id": 10,
      "nome_skill": "Python",
      "categoria": "Technical",
      "livello_attuale": 3,
      "livello_target": 5
    },
    {
      "skill_id": 11,
      "nome_skill": "Machine Learning",
      "categoria": "Technical",
      "livello_attuale": 1,
      "livello_target": 4
    }
  ]
}
```

**Valori ammessi per `ruolo`:** `"Studente"`, `"Docente"`, `"Futuro Studente"` (rispettare le maiuscole — usati come gatekeeper nel routing UI).

**Valori ammessi per `categoria` (skills):** `"Technical"`, `"Soft"`, `"Domain"`.

**Range `livello_attuale` / `livello_target`:** intero da 1 a 5 (CHECK constraint su DB).

---

## 2. Catalogo Corsi e Materiali (`courses`, `materials`)

```json
{
  "id": 101,
  "titolo": "Machine Learning di Base",
  "descrizione": "Introduzione ai modelli predittivi.",
  "categoria": "Data Science",
  "durata_ore": 40,
  "livello": "intermedio",
  "docente_id": 99,
  "prerequisiti_json": [50, 51],
  "contenuto_json": {
    "moduli": ["Regressione", "Classificazione", "Clustering"],
    "obiettivi": "Saper costruire e valutare modelli predittivi di base"
  },
  "materials": [
    {
      "id": 5001,
      "course_id": 101,
      "docente_id": 99,
      "titolo_file": "Slide_Capitolo_1.pdf",
      "tipo_file": "PDF",
      "s3_key": "didattica/corsi/101/Slide_Capitolo_1.pdf",
      "testo_estratto": "Capitolo 1 — Introduzione al Machine Learning. Il learning rate è un iperparametro..."
    },
    {
      "id": 5002,
      "course_id": 101,
      "docente_id": 99,
      "titolo_file": "Lezione_1_Intro.mp4",
      "tipo_file": "Video",
      "s3_key": "didattica/corsi/101/Lezione_1_Intro.mp4",
      "testo_estratto": null
    }
  ]
}
```

**Valori ammessi per `livello`:** `"base"`, `"intermedio"`, `"avanzato"` (CHECK constraint su DB).

**Valori ammessi per `tipo_file`:** `"PDF"`, `"Video"`, `"Audio"`, `"Slide"`.

**Nota RAG:** Il campo `testo_estratto` dei materiali PDF è la **unica fonte di verità** per il Content Generation Agent. I materiali Video hanno `testo_estratto = null` fino a quando non viene implementata la trascrizione automatica.

---

## 3. Piani Formativi (`training_plans`, `training_plan_items`)

```json
{
  "id": 50,
  "user_id": 1,
  "nome": "Percorso Data Scientist 2026",
  "orizzonte": "medio",
  "stato": "attivo",
  "note_ai": "Percorso generato per colmare il gap in Statistica e Python.",
  "items": [
    {
      "id": 200,
      "plan_id": 50,
      "course_id": 101,
      "ordine": 1,
      "stato": "in_corso",
      "data_inizio_prevista": "2026-03-10",
      "data_fine_prevista": "2026-05-10",
      "data_inizio_effettiva": "2026-03-12",
      "data_completamento": null,
      "progresso": 25,
      "voto": null
    }
  ]
}
```

**Valori ammessi per `orizzonte`:** `"breve"`, `"medio"`, `"lungo"`.

**Valori ammessi per `stato` (training_plans):** `"bozza"`, `"attivo"`, `"completato"`, `"sospeso"`.

**Valori ammessi per `stato` (training_plan_items):** `"da_iniziare"`, `"in_corso"`, `"completato"`, `"saltato"`.

**Range `progresso`:** intero da 0 a 100. **Range `voto`:** intero da 1 a 100.

---

## 4. Modifiche al Piano (`plan_changes`)

Generato dall'Optimizer Agent ad ogni modifica del piano confermata dall'utente.

```json
{
  "id": 10,
  "plan_id": 50,
  "user_id": 1,
  "data_modifica": "2026-03-04T10:30:00",
  "tipo_modifica": "rischedulazione",
  "dettagli_json": {
    "item_id": 200,
    "vecchia_data_fine": "2026-05-10",
    "nuova_data_fine": "2026-06-15",
    "motivo_ai": "L'utente ha segnalato un periodo di esami sovrapposto"
  },
  "motivazione": "Richiesta dell'utente tramite chat: 'Posso spostare il corso di ML a giugno?'"
}
```

**Valori ammessi per `tipo_modifica`:** `"aggiunta"`, `"rimozione"`, `"rischedulazione"`, `"sostituzione"`.

---

## 5. Assessment e Quiz (`assessments`)

Generati dinamicamente dall'Adaptive Content Generation Engine esclusivamente dai `materials` del docente.

```json
{
  "id": 300,
  "user_id": 1,
  "tipo": "quiz",
  "domande_json": [
    {
      "id_domanda": "q_1",
      "testo": "Cos'è il learning rate?",
      "opzioni": ["Un parametro del modello", "Un iperparametro", "Una metrica di valutazione"],
      "risposta_corretta": "Un iperparametro",
      "material_riferimento_id": 5001
    },
    {
      "id_domanda": "q_2",
      "testo": "Quale algoritmo è più adatto per la classificazione binaria?",
      "opzioni": ["K-Means", "Regressione Logistica", "PCA"],
      "risposta_corretta": "Regressione Logistica",
      "material_riferimento_id": 5001
    }
  ],
  "risultati_json": {
    "punteggio_totale": 85,
    "aree_forti": ["Teoria base del ML"],
    "aree_deboli": ["Ottimizzazione degli iperparametri"]
  },
  "aspirazioni_json": null
}
```

**Valori ammessi per `tipo`:** `"iniziale"`, `"quiz"`, `"intermedio"`, `"finale"`.

---

## 6. Log di Monitoraggio (`progress_log`, `notifications`)

Generati dall'AI-Driven Progress Monitoring Agent per rilevare ritardi o successi.

```json
{
  "log": {
    "id": 1005,
    "user_id": 1,
    "plan_item_id": 200,
    "evento": "in_ritardo",
    "dettagli": "L'utente non accede al corso 101 da oltre 14 giorni."
  },
  "notifica_generata": {
    "id": 40,
    "user_id": 1,
    "tipo": "ritardo",
    "titolo": "Sembra che tu sia rimasto indietro!",
    "messaggio": "Ciao Giulia, ho notato che non accedi al corso di Machine Learning da 2 settimane. Vuoi riprogrammare le scadenze?",
    "letto": 0
  }
}
```

**Valori ammessi per `evento` (progress_log):** `"iniziato"`, `"completato"`, `"in_ritardo"`, `"abbandonato"`.

**Valori ammessi per `tipo` (notifications):** `"promemoria"`, `"ritardo"`, `"completamento"`, `"suggerimento"`.

**Campo `letto`:** `0` = non letto, `1` = letto (INTEGER su SQLite, non BOOLEAN).

---

## 7. Survey (`surveys`)

Generata e analizzata dallo Smart Survey Lifecycle Manager.

```json
{
  "id": 20,
  "user_id": 1,
  "course_id": 101,
  "tipo": "gradimento_corso",
  "domande_json": [
    {
      "id_domanda": "s_1",
      "testo": "Come valuteresti la chiarezza delle spiegazioni del docente?",
      "scala": "1-5"
    },
    {
      "id_domanda": "s_2",
      "testo": "Quali argomenti ti hanno creato più difficoltà?",
      "tipo_risposta": "testo_libero"
    }
  ],
  "risposte_json": [
    {"id_domanda": "s_1", "risposta": 4},
    {"id_domanda": "s_2", "risposta": "L'ottimizzazione del gradiente è risultata poco chiara"}
  ],
  "sentiment_score": 0.65,
  "aree_miglioramento_json": {
    "punti_critici": ["Spiegazione dell'ottimizzazione"],
    "punti_di_forza": ["Esempi pratici", "Materiale ben organizzato"]
  }
}
```

**Valori ammessi per `tipo`:** `"gradimento_corso"`, `"piattaforma"`, `"periodico"`.

**Range `sentiment_score`:** float da -1.0 (molto negativo) a 1.0 (molto positivo).

---

## 8. Skill Gap Analysis (`skill_gap_analyses`)

Generata dalla Competency Gap Analysis AI.

```json
{
  "id": 5,
  "user_id": 1,
  "ruolo_target": "Data Scientist Junior",
  "gap_json": [
    {
      "skill": "Machine Learning",
      "livello_attuale": 1,
      "livello_richiesto": 4,
      "gap": 3,
      "priorita": "alta"
    },
    {
      "skill": "Statistica",
      "livello_attuale": 2,
      "livello_richiesto": 4,
      "gap": 2,
      "priorita": "media"
    },
    {
      "skill": "Python",
      "livello_attuale": 3,
      "livello_richiesto": 4,
      "gap": 1,
      "priorita": "bassa"
    }
  ],
  "raccomandazioni_json": [
    {
      "course_id": 101,
      "titolo": "Machine Learning di Base",
      "motivo": "Colma il gap principale su ML (da livello 1 a 4)"
    },
    {
      "course_id": 85,
      "titolo": "Statistica per Data Science",
      "motivo": "Consolida le basi statistiche necessarie"
    }
  ],
  "punteggio_prontezza": 38
}
```

**Range `punteggio_prontezza`:** intero da 0 (nessuna preparazione) a 100 (pronto per il ruolo target).
