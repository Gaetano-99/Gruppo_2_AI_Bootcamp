"""
Esegue la data population per la demo cliente.
Applica i 3 file SQL e rigenera gli hash password con werkzeug.

Uso:
    python database/run_population.py
"""

import os
import sys
import sqlite3

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import config

DB_PATH = config.DATABASE_PATH
SQL_DIR = os.path.dirname(__file__)

SQL_FILES = [
    "seed_population.sql",
    "seed_population_part2.sql",
    "seed_population_part3.sql",
    "seed_population_umanistici.sql",
]


def main():
    if not os.path.exists(DB_PATH):
        print(f"[ERRORE] Database non trovato: {DB_PATH}")
        print("         Esegui prima: python database/init_db.py")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        # 1. Esegui i file SQL
        for sql_file in SQL_FILES:
            path = os.path.join(SQL_DIR, sql_file)
            if not os.path.exists(path):
                print(f"[ERRORE] File non trovato: {path}")
                sys.exit(1)
            with open(path, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
            print(f"[OK] {sql_file}")

        conn.commit()

        # 2. Rigenera gli hash password per i nuovi utenti
        print("\n[INFO] Rigenerazione hash password...")
        try:
            from werkzeug.security import generate_password_hash
        except ImportError:
            print("[WARN] werkzeug non disponibile, gli hash placeholder restano invariati.")
            print("       Installa con: pip install werkzeug")
            _print_summary(conn)
            return

        # Tutti i nuovi utenti (ID >= 200) hanno password "test1234"
        cur = conn.execute("SELECT id, ruolo FROM users WHERE id >= 200")
        users = cur.fetchall()
        if users:
            password_hash = generate_password_hash("test1234")
            conn.execute(
                "UPDATE users SET password_hash = ? WHERE id >= 200",
                [password_hash],
            )
            conn.commit()
            print(f"[OK] Hash aggiornati per {len(users)} utenti (password: test1234)")

        _print_summary(conn)

    finally:
        conn.close()


def _print_summary(conn):
    print("\n--- Riepilogo dopo population ---")
    tables = [
        "users", "corsi_di_laurea", "corsi_universitari",
        "corsi_laurea_universitari", "studenti_corsi",
        "materiali_didattici", "materiali_chunks",
        "quiz", "domande_quiz", "tentativi_quiz", "risposte_domande",
        "lezioni_corso", "piani_personalizzati",
    ]
    for t in tables:
        cur = conn.execute(f"SELECT COUNT(*) as n FROM [{t}]")
        n = cur.fetchone()["n"]
        print(f"  {t:<30}: {n}")

    # Dettaglio per ruolo
    print("\n--- Utenti per ruolo ---")
    for ruolo in ("admin", "docente", "studente"):
        cur = conn.execute("SELECT COUNT(*) as n FROM users WHERE ruolo = ?", [ruolo])
        n = cur.fetchone()["n"]
        print(f"  {ruolo:<12}: {n}")

    # Quiz Tipo C
    cur = conn.execute("SELECT COUNT(*) as n FROM quiz WHERE approvato = 1")
    n = cur.fetchone()["n"]
    print(f"\n  Quiz Tipo C (approvati): {n}")

    print("\n[OK] Data population completata!")


if __name__ == "__main__":
    main()
