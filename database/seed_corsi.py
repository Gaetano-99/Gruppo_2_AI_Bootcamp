import os
import sys
import json
import sqlite3

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import config
from src.agents.dati_corsi import CATALOGO_CORSI

def seed_corsi():
    db_path = config.DATABASE_PATH
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"Inizio popolamento di {len(CATALOGO_CORSI)} corsi in {db_path}...")

    for codice, dati in CATALOGO_CORSI.items():
        nome = dati.get("nome_completo")
        facolta = dati.get("area", "Non definita")
        tipo = dati.get("tipo")
        descrizione = dati.get("descrizione")
        materie = json.dumps(dati.get("materie_principali", []), ensure_ascii=False)
        sbocchi = json.dumps(dati.get("sbocchi_lavorativi", []), ensure_ascii=False)
        durata = dati.get("durata")

        # Check if course with same nome already exists
        cursor.execute("SELECT id FROM corsi_di_laurea WHERE nome = ?", (nome,))
        row = cursor.fetchone()

        if row:
            # Update existing
            cursor.execute('''
                UPDATE corsi_di_laurea 
                SET facolta = ?, tipo = ?, descrizione = ?, 
                    materie_principali_json = ?, sbocchi_lavorativi_json = ?, 
                    durata = ?, codice_corso = ?
                WHERE id = ?
            ''', (facolta, tipo, descrizione, materie, sbocchi, durata, codice, row[0]))
        else:
            # Insert new
            cursor.execute('''
                INSERT INTO corsi_di_laurea 
                (nome, facolta, tipo, descrizione, materie_principali_json, sbocchi_lavorativi_json, durata, codice_corso)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nome, facolta, tipo, descrizione, materie, sbocchi, durata, codice))

    conn.commit()
    conn.close()
    print("Popolamento completato con successo.")

if __name__ == "__main__":
    seed_corsi()
