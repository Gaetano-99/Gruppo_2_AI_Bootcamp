# ============================================================================
# LearnAI Platform SDK — Modulo Database
# Helper semplificato per operazioni SQLite.
#
# Uso:
#   from platform_sdk.database import db
#
#   db.init()                                             # Crea tabelle e carica dati iniziali
#   db.inserisci("users", {"nome": "Giulia"})             # INSERT
#   db.trova_uno("users", {"id": 1})                      # SELECT ... LIMIT 1
#   db.trova_tutti("corsi_universitari")                  # SELECT *
#   db.aggiorna("users", {"id": 1}, {"stato": "active"})  # UPDATE
#   db.elimina("piano_contenuti", {"id": 1})              # DELETE
#   db.esegui("SELECT * FROM users WHERE ruolo = ?", ["studente"])  # Query custom
#   db.conta("users", {"ruolo": "studente"})              # COUNT
#
# Tabelle disponibili (da schema.sql — usare SOLO questi nomi):
#   users
#   corsi_di_laurea | corsi_universitari
#   corsi_laurea_universitari | studenti_corsi
#   quiz | domande_quiz | tentativi_quiz | risposte_domande
#   materiali_didattici | materiali_chunks
#   piani_personalizzati | piano_materiali_utilizzati
#   piano_capitoli | piano_paragrafi | piano_contenuti
#   lezioni_corso
#
# VINCOLO APPLICATIVO — verifica ruolo prima degli INSERT su:
#   studenti_corsi      → studente_id  deve avere users.ruolo = 'studente'
#   quiz                → studente_id  deve avere users.ruolo = 'studente'
#                      → docente_id   deve avere users.ruolo = 'docente'
#   tentativi_quiz      → studente_id  deve avere users.ruolo = 'studente'
#   piani_personalizzati → studente_id deve avere users.ruolo = 'studente'
#   materiali_didattici → docente_id   deve avere users.ruolo = 'docente'
#   lezioni_corso       → docente_id   deve avere users.ruolo = 'docente'
# ============================================================================

import json
import os
import sqlite3
from typing import Optional

import config


class Database:
    """
    Helper semplificato per SQLite.
    Wrappa le operazioni più comuni in metodi intuitivi.
    """

    def __init__(self, db_path: str = None):
        """Inizializza il database con il percorso specificato."""
        self.db_path = db_path or config.DATABASE_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _connetti(self) -> sqlite3.Connection:
        """Crea una connessione al database SQLite."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Restituisce righe come dizionari
        conn.execute("PRAGMA foreign_keys = ON")  # Abilita le foreign key
        return conn

    # ------------------------------------------------------------------
    # Inizializzazione
    # ------------------------------------------------------------------

    def init(self):
        """
        Inizializza il database: crea le tabelle (schema.sql) e carica
        i dati iniziali (seed.sql) se disponibili.

        Esempio:
            db.init()  # Eseguire una sola volta all'avvio dell'applicazione
        """
        conn = self._connetti()
        try:
            if os.path.exists(config.SCHEMA_PATH):
                with open(config.SCHEMA_PATH, "r", encoding="utf-8") as f:
                    conn.executescript(f.read())
                print(f"✅ Schema caricato da {config.SCHEMA_PATH}")
            else:
                print(f"⚠️  File schema non trovato: {config.SCHEMA_PATH}")

            if os.path.exists(config.SEED_PATH):
                with open(config.SEED_PATH, "r", encoding="utf-8") as f:
                    conn.executescript(f.read())
                print(f"✅ Dati seed caricati da {config.SEED_PATH}")
            else:
                print(f"ℹ️  File seed non trovato: {config.SEED_PATH} (opzionale)")

            conn.commit()
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # CRUD — Create
    # ------------------------------------------------------------------

    def inserisci(self, tabella: str, dati: dict) -> int:
        """
        Inserisce una riga in una tabella.

        Parametri:
            tabella: nome della tabella (es: "studenti")
            dati:    dizionario con i dati da inserire

        Ritorna:
            L'ID della riga inserita

        Esempio:
            studente_id = db.inserisci("users", {
                "nome": "Giulia",
                "cognome": "Bianchi",
                "email": "g.bianchi@studenti.unina.it",
                "password_hash": "$2b$12$...",
                "ruolo": "studente",
                "matricola_studente": "N86001234",
                "corso_di_laurea_id": 3,
                "anno_corso": 2
            })

            piano_id = db.inserisci("piani_personalizzati", {
                "studente_id": studente_id,
                "titolo": "Preparazione Basi di Dati",
                "tipo": "esame",
                "corso_universitario_id": 101
            })
        """
        dati_puliti = self._serializza_json(dati)
        colonne = ", ".join(dati_puliti.keys())
        placeholders = ", ".join(["?"] * len(dati_puliti))
        valori = list(dati_puliti.values())

        sql = f"INSERT INTO {tabella} ({colonne}) VALUES ({placeholders})"

        conn = self._connetti()
        try:
            cursor = conn.execute(sql, valori)
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def inserisci_molti(self, tabella: str, lista_dati: list[dict]) -> int:
        """
        Inserisce più righe in una tabella in una sola operazione.

        Parametri:
            tabella:    nome della tabella
            lista_dati: lista di dizionari (tutti con le stesse chiavi)

        Ritorna:
            Il numero di righe inserite

        Esempio:
            # Traccia i chunks usati per generare un piano
            db.inserisci_molti("piano_materiali_utilizzati", [
                {"piano_id": 50, "chunk_id": 301},
                {"piano_id": 50, "chunk_id": 302},
                {"piano_id": 50, "chunk_id": 303},
            ])

            # Inserisce le domande di un quiz
            db.inserisci_molti("domande_quiz", [
                {"quiz_id": 300, "testo": "Cos'è una chiave primaria?",
                 "tipo": "scelta_multipla", "ordine": 1, "chunk_id": 301},
                {"quiz_id": 300, "testo": "Cosa garantisce l'integrità referenziale?",
                 "tipo": "scelta_multipla", "ordine": 2, "chunk_id": 302},
            ])
        """
        if not lista_dati:
            return 0

        prima_riga = self._serializza_json(lista_dati[0])
        colonne = ", ".join(prima_riga.keys())
        placeholders = ", ".join(["?"] * len(prima_riga))

        sql = f"INSERT INTO {tabella} ({colonne}) VALUES ({placeholders})"

        righe = []
        for dati in lista_dati:
            dati_puliti = self._serializza_json(dati)
            righe.append(list(dati_puliti.values()))

        conn = self._connetti()
        try:
            conn.executemany(sql, righe)
            conn.commit()
            return len(righe)
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # CRUD — Read
    # ------------------------------------------------------------------

    def trova_uno(self, tabella: str, filtri: dict = None) -> Optional[dict]:
        """
        Trova una singola riga in una tabella.

        Parametri:
            tabella: nome della tabella
            filtri:  dizionario di condizioni (es: {"id": 1})

        Ritorna:
            Un dizionario con i dati della riga, o None se non trovata

        Esempio:
            utente = db.trova_uno("users", {"email": "g.bianchi@studenti.unina.it"})
            if utente:
                print(f"Trovato: {utente['nome']} {utente['cognome']} ({utente['ruolo']})")

            # Verifica idempotenza RAG prima di processare un materiale
            materiale = db.trova_uno("materiali_didattici", {"id": materiale_id})
            if materiale["is_processed"] == 1:
                return  # chunks già presenti — non riprocessare
        """
        where, valori = self._costruisci_where(filtri)
        sql = f"SELECT * FROM {tabella}{where} LIMIT 1"

        conn = self._connetti()
        try:
            cursor = conn.execute(sql, valori)
            riga = cursor.fetchone()
            return dict(riga) if riga else None
        finally:
            conn.close()

    def trova_tutti(self, tabella: str, filtri: dict = None,
                    ordine: str = None, limite: int = None) -> list[dict]:
        """
        Trova tutte le righe che corrispondono ai filtri.

        Parametri:
            tabella: nome della tabella
            filtri:  condizioni di ricerca (opzionale)
            ordine:  colonna per l'ordinamento (es: "ordine ASC")
            limite:  numero massimo di risultati

        Ritorna:
            Lista di dizionari

        Esempio:
            # Tutti i piani di uno studente
            piani = db.trova_tutti(
                "piani_personalizzati",
                {"studente_id": 1, "stato": "attivo"},
                ordine="created_at DESC"
            )

            # I capitoli di un piano in ordine
            capitoli = db.trova_tutti(
                "piano_capitoli",
                {"piano_id": 50},
                ordine="ordine ASC"
            )

            # I chunks di un corso (query RAG di base)
            chunks = db.trova_tutti(
                "materiali_chunks",
                {"corso_universitario_id": 101},
                ordine="indice_chunk ASC"
            )

            # Tutti i docenti della piattaforma
            docenti = db.trova_tutti("users", {"ruolo": "docente"})
        """
        where, valori = self._costruisci_where(filtri)
        sql = f"SELECT * FROM {tabella}{where}"

        if ordine:
            sql += f" ORDER BY {ordine}"
        if limite:
            sql += f" LIMIT {limite}"

        conn = self._connetti()
        try:
            cursor = conn.execute(sql, valori)
            return [dict(riga) for riga in cursor.fetchall()]
        finally:
            conn.close()

    def conta(self, tabella: str, filtri: dict = None) -> int:
        """
        Conta il numero di righe che corrispondono ai filtri.

        Parametri:
            tabella: nome della tabella
            filtri:  condizioni di ricerca (opzionale)

        Ritorna:
            Il numero di righe

        Esempio:
            n_studenti = db.conta("users", {"ruolo": "studente"})
            n_iscritti = db.conta("studenti_corsi", {"corso_universitario_id": 101})
            n_completati = db.conta("piano_paragrafi", {"piano_id": 50, "completato": 1})

            # Verifica idempotenza embedding: i chunks sono già vettorizzati?
            n_da_sync = db.conta("materiali_chunks", {"embedding_sync": 0})
            if n_da_sync == 0:
                return  # tutto già sincronizzato
        """
        where, valori = self._costruisci_where(filtri)
        sql = f"SELECT COUNT(*) as n FROM {tabella}{where}"

        conn = self._connetti()
        try:
            cursor = conn.execute(sql, valori)
            return cursor.fetchone()["n"]
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # CRUD — Update
    # ------------------------------------------------------------------

    def aggiorna(self, tabella: str, filtri: dict, dati: dict) -> int:
        """
        Aggiorna le righe che corrispondono ai filtri.

        Parametri:
            tabella: nome della tabella
            filtri:  condizioni per identificare le righe da aggiornare
            dati:    nuovi valori da impostare

        Ritorna:
            Il numero di righe aggiornate

        Esempio:
            # Approva una lezione generata dall'AI
            db.aggiorna("lezioni_corso", {"id": 700}, {"approvato": 1})

            # Approva un quiz del corso
            db.aggiorna("quiz", {"id": 300}, {"approvato": 1})

            # Segna un paragrafo del piano come completato
            db.aggiorna("piano_paragrafi", {"id": 600}, {"completato": 1})

            # Marca un materiale come processato dopo la chunking
            db.aggiorna("materiali_didattici", {"id": 5001}, {"is_processed": 1})
        """
        dati_puliti = self._serializza_json(dati)
        set_clause = ", ".join([f"{k} = ?" for k in dati_puliti.keys()])
        set_valori = list(dati_puliti.values())

        where, where_valori = self._costruisci_where(filtri)
        sql = f"UPDATE {tabella} SET {set_clause}{where}"

        conn = self._connetti()
        try:
            cursor = conn.execute(sql, set_valori + where_valori)
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # CRUD — Delete
    # ------------------------------------------------------------------

    def elimina(self, tabella: str, filtri: dict) -> int:
        """
        Elimina le righe che corrispondono ai filtri.

        Parametri:
            tabella: nome della tabella
            filtri:  condizioni per identificare le righe da eliminare

        Ritorna:
            Il numero di righe eliminate

        Esempio:
            # Rimuove un contenuto del piano non più necessario
            db.elimina("piano_contenuti", {"id": 900})

            # Rimuove l'iscrizione di uno studente a un corso
            db.elimina("studenti_corsi", {"studente_id": 1, "corso_universitario_id": 101})
        """
        where, valori = self._costruisci_where(filtri)
        if not where:
            raise ValueError("⚠️  Non puoi eliminare senza filtri! Specifica almeno una condizione.")

        sql = f"DELETE FROM {tabella}{where}"

        conn = self._connetti()
        try:
            cursor = conn.execute(sql, valori)
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Query custom
    # ------------------------------------------------------------------

    def esegui(self, sql: str, parametri: list = None) -> list[dict]:
        """
        Esegue una query SQL personalizzata.
        Usare questo metodo solo per query complesse con JOIN o aggregazioni
        che non sono esprimibili con i metodi CRUD standard.

        Parametri:
            sql:       la query SQL (usare ? per i parametri)
            parametri: lista di valori per i placeholder ?

        Ritorna:
            Lista di dizionari con i risultati (per SELECT)

        Esempio:
            # Report docente: argomenti con più errori nei quiz approvati
            risultati = db.esegui(
                "SELECT mc.argomenti_chiave, COUNT(*) as n_errori "
                "FROM risposte_domande rd "
                "JOIN domande_quiz dq ON rd.domanda_id = dq.id "
                "JOIN quiz q ON dq.quiz_id = q.id "
                "JOIN materiali_chunks mc ON dq.chunk_id = mc.id "
                "WHERE q.corso_universitario_id = ? "
                "  AND q.approvato = 1 "
                "  AND rd.corretta = 0 "
                "GROUP BY mc.argomenti_chiave "
                "ORDER BY n_errori DESC",
                [corso_id]
            )

            # Chunks rilevanti per un argomento (base per il RAG)
            chunks = db.esegui(
                "SELECT * FROM materiali_chunks "
                "WHERE corso_universitario_id = ? "
                "  AND argomenti_chiave LIKE ? "
                "ORDER BY indice_chunk ASC",
                [corso_id, f"%{argomento}%"]
            )
        """
        conn = self._connetti()
        try:
            cursor = conn.execute(sql, parametri or [])
            if sql.strip().upper().startswith("SELECT"):
                return [dict(riga) for riga in cursor.fetchall()]
            else:
                conn.commit()
                return []
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Metodi interni
    # ------------------------------------------------------------------

    def _costruisci_where(self, filtri: dict = None) -> tuple[str, list]:
        """Costruisce la clausola WHERE da un dizionario di filtri."""
        if not filtri:
            return "", []

        condizioni = []
        valori = []
        for chiave, valore in filtri.items():
            condizioni.append(f"{chiave} = ?")
            valori.append(valore)

        return " WHERE " + " AND ".join(condizioni), valori

    def _serializza_json(self, dati: dict) -> dict:
        """
        Converte eventuali dict/list nei valori in stringhe JSON.
        Permette di passare direttamente dizionari o liste Python per i campi
        JSON del DB (es: argomenti_chiave, chunk_ids_utilizzati, pagine_riferimento).
        """
        risultato = {}
        for chiave, valore in dati.items():
            if isinstance(valore, (dict, list)):
                risultato[chiave] = json.dumps(valore, ensure_ascii=False)
            else:
                risultato[chiave] = valore
        return risultato


# ---------------------------------------------------------------------------
# Istanza globale — importatela e usatela direttamente
# ---------------------------------------------------------------------------

db = Database()
