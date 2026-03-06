"""
LearnAI Platform — Script di Re-inizializzazione Database

Uso:
    python database/init_db.py

Effetti:
    1. Elimina il file learnai.db se esiste
    2. Ricrea il DB applicando Nuovo_schema.sql
    3. Carica i dati seed da seed.sql
    4. Stampa un riepilogo degli utenti inseriti per ruolo
"""

import os
import sqlite3
import sys

# Permette l'import di config dalla root del progetto
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import config

DB_PATH = config.DATABASE_PATH
SCHEMA_PATH = config.SCHEMA_PATH
SEED_PATH = config.SEED_PATH


def main():
    # 1. Elimina il DB esistente
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"[OK] Eliminato: {DB_PATH}")
    else:
        print(f"[INFO] Nessun DB precedente trovato: {DB_PATH}")

    # Assicura che la cartella database/ esista
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        # 2. Applica lo schema
        if not os.path.exists(SCHEMA_PATH):
            print(f"[ERRORE] File schema non trovato: {SCHEMA_PATH}")
            sys.exit(1)

        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        print(f"[OK] Schema applicato: {SCHEMA_PATH}")

        # 3. Carica il seed
        if not os.path.exists(SEED_PATH):
            print(f"[WARN] Seed non trovato: {SEED_PATH} (procedo senza dati iniziali)")
        else:
            with open(SEED_PATH, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
            print(f"[OK] Seed caricato: {SEED_PATH}")

        conn.commit()

        # 4. Riepilogo
        print("\n--- Riepilogo utenti inseriti ---")
        for ruolo in ("admin", "docente", "studente"):
            cur = conn.execute(
                "SELECT COUNT(*) as n FROM users WHERE ruolo = ?", [ruolo]
            )
            n = cur.fetchone()["n"]
            print(f"  {ruolo:<12}: {n}")

        cur = conn.execute("SELECT COUNT(*) as n FROM users")
        total = cur.fetchone()["n"]
        print(f"  {'TOTALE':<12}: {total}")
        print("\n[OK] Database inizializzato con successo!")
        print(f"     Path: {DB_PATH}\n")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
