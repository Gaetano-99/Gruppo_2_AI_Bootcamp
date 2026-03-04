# ============================================================================
# LearnAI Platform SDK — Utility
# Funzioni di supporto usate trasversalmente nel progetto.
# ============================================================================

import json
import os
from datetime import datetime, timedelta


def carica_json(percorso: str) -> dict | list:
    """
    Carica un file JSON e lo restituisce come dizionario o lista Python.

    Parametri:
        percorso: percorso del file JSON

    Ritorna:
        Il contenuto del file come dict o list

    Esempio:
        dati = carica_json("data/sample_data.json")
    """
    with open(percorso, "r", encoding="utf-8") as f:
        return json.load(f)


def salva_json(dati, percorso: str):
    """
    Salva un dizionario o lista in un file JSON.

    Parametri:
        dati:     dizionario o lista da salvare
        percorso: percorso del file JSON

    Esempio:
        salva_json({"nome": "Mario"}, "data/output.json")
    """
    os.makedirs(os.path.dirname(percorso), exist_ok=True)
    with open(percorso, "w", encoding="utf-8") as f:
        json.dump(dati, f, ensure_ascii=False, indent=2)


def parse_json_sicuro(testo: str) -> dict | list | None:
    """
    Prova a parsare una stringa JSON in modo sicuro.
    Restituisce None se il parsing fallisce.

    Parametri:
        testo: stringa JSON da parsare

    Ritorna:
        dict/list se il parsing riesce, None altrimenti
    """
    try:
        return json.loads(testo)
    except (json.JSONDecodeError, TypeError):
        return None


def data_oggi() -> str:
    """Restituisce la data di oggi in formato YYYY-MM-DD."""
    return datetime.now().strftime("%Y-%m-%d")


def data_tra(giorni: int) -> str:
    """
    Restituisce una data futura in formato YYYY-MM-DD.

    Parametri:
        giorni: numero di giorni da oggi

    Esempio:
        inizio = data_oggi()           # "2025-03-01"
        fine = data_tra(30)            # "2025-03-31"
    """
    return (datetime.now() + timedelta(days=giorni)).strftime("%Y-%m-%d")


def formatta_lista_per_prompt(items: list[dict], campi: list[str]) -> str:
    """
    Formatta una lista di dizionari come testo leggibile, utile per
    costruire contesti da passare all'LLM.

    Parametri:
        items: lista di dizionari
        campi: quali campi includere

    Ritorna:
        Testo formattato

    Esempio:
        corsi = db.trova_tutti("courses")
        testo = formatta_lista_per_prompt(corsi, ["id", "titolo", "livello", "durata_ore"])
        # Output:
        # - [1] Fondamenti di Python (base, 20h)
        # - [2] SQL per Business (base, 15h)
    """
    righe = []
    for item in items:
        valori = [str(item.get(c, "")) for c in campi]
        if len(valori) >= 2:
            riga = f"- [{valori[0]}] {valori[1]}"
            if len(valori) > 2:
                riga += f" ({', '.join(valori[2:])})"
            righe.append(riga)
        else:
            righe.append(f"- {', '.join(valori)}")
    return "\n".join(righe)
