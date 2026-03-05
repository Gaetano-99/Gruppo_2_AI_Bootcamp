# Styleguide & Conventions

## Scopo del Documento
Questo file detta il regolamento stilistico e sintattico della codebase. Assicura che il codice risulti uniforme, leggibile e manutenibile, come se fosse stato scritto da un'unica entità. Rappresenta il file cruciale per "addestrare" l'Intelligenza Artificiale a generare output aderente ai nostri standard.

## Contenuto del Documento
In questo file verranno definiti:
- **Naming Conventions:** Le regole ferree per la nomenclatura di variabili, funzioni, classi e file.
- **Formattazione e Architettura:** Le direttive su indentazione, type hinting, e struttura dei singoli script.
- **Regole di Commento:** Le linee guida su dove, come e in che lingua scrivere la documentazione inline e le docstrings.
- **Messaggi di Commit:** Gli standard richiesti per la stesura dei log su Git per mantenere la history leggibile.

# Styleguide & Conventions

## Scopo del Documento
Questo file detta il regolamento stilistico e sintattico della codebase. Assicura che il codice risulti uniforme, leggibile e manutenibile, come se fosse stato scritto da un'unica entità. Rappresenta il file cruciale per "addestrare" l'Intelligenza Artificiale a generare output aderente ai nostri standard.

---

## 1. Naming Conventions

Essendo un progetto per un'università italiana, adotteremo un approccio ibrido strutturato: **Italiano per la logica di dominio, Inglese per le convenzioni standard di programmazione.**

* **Variabili e Funzioni:** `snake_case` in Italiano (es. `studente_id`, `calcola_punteggio`, `lista_corsi`). Coerente con l'SDK esistente (`trova_uno`, `chiedi_con_contesto`).
* **Classi e Modelli (Pydantic/TypedDict):** `PascalCase` in Italiano (es. `Studente`, `PianoFormativo`, `StatoAgente`).
* **File e Directory:** `snake_case` in Inglese o Italiano a seconda del modulo (es. `database.py`, `rag_engine.py`, `course_analysis.py`). Nessun carattere speciale o spazio.
* **Costanti:** `UPPER_SNAKE_CASE` in Inglese (es. `MAX_RETRIES`, `BEDROCK_MODEL_ID`).
* **Database:** Nomi delle tabelle e colonne rigorosamente in `snake_case` e al plurale per le tabelle (es. `studenti`, `corsi_universitari`), esattamente come definiti in `schema.sql`.

---

## 2. Formattazione e Architettura

* **Type Hinting Obbligatorio:** Ogni funzione deve dichiarare il tipo degli argomenti e il tipo di ritorno (Python 3.10+). 
    * *Sì:* `def recupera_piano(studente_id: int) -> dict | None:`
    * *No:* `def recupera_piano(studente_id):`
* **Gestione dello Stato UI:** Vietato l'uso di variabili globali per lo stato dell'interfaccia. Utilizzare esclusivamente `st.session_state` per i dati temporanei di Streamlit.
* **Strutture Dati Agenti:** Lo stato di LangGraph deve essere sempre tipizzato tramite `TypedDict`. Gli output strutturati del LLM devono usare `Pydantic` (BaseModel).
* **Lunghezza Linea e Formattazione:** Utilizzare formattatori standard (es. *Black* o *Ruff*). Lunghezza massima della riga consigliata: 100 caratteri.

---

## 3. Regole di Commento

* **Lingua:** Tutti i commenti e le documentazioni devono essere scritti in **Italiano**.
* **Docstrings:** Utilizzare il formato "Google Style" per documentare moduli, classi e funzioni complesse. La docstring deve spiegare *cosa* fa la funzione, gli argomenti (`Args:`) e il valore di ritorno (`Returns:`).
* **Commenti Inline:** Da usare con parsimonia. Il codice deve essere auto-esplicativo grazie a nomi di variabili chiari. Usare i commenti inline solo per spiegare il *perché* di una logica complessa o di una specifica scelta architetturale, non il *cosa*.

---

## 4. Messaggi di Commit

Adottiamo lo standard **Conventional Commits** per mantenere la history leggibile e automatizzabile. I messaggi possono essere in Italiano o Inglese, ma il prefisso deve essere standard.

**Formato:** `tipo(scopo opzionale): descrizione breve`

*Tipi ammessi:*
* `feat`: Nuova funzionalità (es. `feat(quiz): aggiunto supporto per domande aperte`)
* `fix`: Risoluzione di un bug (es. `fix(auth): corretto crash su login ospite`)
* `docs`: Modifiche alla documentazione (es. `docs: aggiornato schema DB in README`)
* `style`: Formattazione, punteggiatura (nessuna modifica alla logica)
* `refactor`: Ristrutturazione del codice senza aggiungere feature o fixare bug
* `test`: Aggiunta o modifica di test
* `chore`: Aggiornamento dipendenze, task di build (es. `chore: aggiornato requirements.txt`)