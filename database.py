# ============================================================================
# LearnAI Platform SDK — Modulo Database
# Helper semplificato per operazioni SQLite.
#
# Uso:
#   from platform_sdk.database import db
#
#   db.init()                                      # Crea tabelle e carica dati iniziali
#   db.inserisci("users", {"nome": "Mario"})       # INSERT
#   db.trova_uno("users", {"id": 1})               # SELECT ... LIMIT 1
#   db.trova_tutti("users")                         # SELECT *
#   db.aggiorna("users", {"id": 1}, {"ruolo": "Senior"})  # UPDATE
#   db.elimina("users", {"id": 1})                 # DELETE
#   db.esegui("SELECT * FROM users WHERE ruolo = ?", ["Senior"])  # Query custom
#   db.conta("users", {"dipartimento": "IT"})       # COUNT
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
        # Assicuriamoci che la cartella esista
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
            db.init()  # Eseguire una sola volta, all'inizio
        """
        conn = self._connetti()
        try:
            # Esegui lo schema SQL se esiste
            if os.path.exists(config.SCHEMA_PATH):
                with open(config.SCHEMA_PATH, "r", encoding="utf-8") as f:
                    conn.executescript(f.read())
                print(f"✅ Schema caricato da {config.SCHEMA_PATH}")
            else:
                print(f"⚠️  File schema non trovato: {config.SCHEMA_PATH}")

            # Esegui il seed SQL se esiste
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
            tabella: nome della tabella (es: "users")
            dati:    dizionario con i dati da inserire

        Ritorna:
            L'ID della riga inserita

        Esempio:
            user_id = db.inserisci("users", {
                "nome": "Mario",
                "cognome": "Rossi",
                "email": "m.rossi@test.it",
                "ruolo": "Junior Analyst"
            })
            print(f"Utente creato con ID: {user_id}")
        """
        # Converti eventuali dict/list in JSON
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
            db.inserisci_molti("user_skills", [
                {"user_id": 1, "skill_id": 1, "livello_attuale": 3},
                {"user_id": 1, "skill_id": 2, "livello_attuale": 2},
                {"user_id": 1, "skill_id": 3, "livello_attuale": 4},
            ])
        """
        if not lista_dati:
            return 0

        # Usa le chiavi del primo elemento per definire le colonne
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
            utente = db.trova_uno("users", {"email": "m.rossi@test.it"})
            if utente:
                print(f"Trovato: {utente['nome']} {utente['cognome']}")
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
            ordine:  colonna per l'ordinamento (es: "nome ASC")
            limite:  numero massimo di risultati

        Ritorna:
            Lista di dizionari

        Esempio:
            utenti_it = db.trova_tutti("users", {"dipartimento": "IT"}, ordine="cognome ASC")
            for u in utenti_it:
                print(f"- {u['nome']} {u['cognome']}")
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
            n_utenti = db.conta("users")
            n_completati = db.conta("training_plan_items", {"stato": "completato"})
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
            db.aggiorna("users", {"id": 1}, {"ruolo": "Senior Analyst"})
            db.aggiorna("training_plan_items", {"id": 5}, {
                "stato": "completato",
                "data_completamento": "2025-03-15"
            })
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
            db.elimina("notifications", {"user_id": 1, "letto": 1})
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

        Parametri:
            sql:       la query SQL (usare ? per i parametri)
            parametri: lista di valori per i placeholder ?

        Ritorna:
            Lista di dizionari con i risultati (per SELECT)

        Esempio:
            risultati = db.esegui(
                "SELECT u.nome, c.titolo, tpi.stato "
                "FROM training_plan_items tpi "
                "JOIN training_plans tp ON tpi.plan_id = tp.id "
                "JOIN users u ON tp.user_id = u.id "
                "JOIN courses c ON tpi.course_id = c.id "
                "WHERE tpi.stato = ?",
                ["in_corso"]
            )
        """
        conn = self._connetti()
        try:
            cursor = conn.execute(sql, parametri or [])
            # Se è una SELECT, restituisci i risultati
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
        Così potete passare direttamente dizionari Python e verranno
        salvati come JSON nel database.
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
