"""
Script di test da riga di comando per il Motore di Raccomandazione.

Uso:
    python tests/test_recommender.py              → testa tutti gli studenti nel DB
    python tests/test_recommender.py --id 1       → testa solo lo studente con ID 1
    python tests/test_recommender.py --id 1 --n 3 → limita a 3 raccomandazioni

Output:
    Per ogni studente mostra le raccomandazioni con breakdown dettagliato
    dei tre segnali (curriculum, engagement, semantico) e la motivazione UI.
"""

import sys
import os
import argparse
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Mock Streamlit — deve avvenire PRIMA di qualsiasi import del progetto
# ---------------------------------------------------------------------------
sys.modules["streamlit"] = MagicMock()

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.services.recommender import raccomanda_corsi, RaccomandazioneCorso
from platform_sdk.database import db

# ---------------------------------------------------------------------------
# Costanti UI
# ---------------------------------------------------------------------------
_SEP   = "─" * 65
_SEP_L = "═" * 65


def _barra(valore: float, larghezza: int = 20) -> str:
    """Genera una barra ASCII proporzionale al valore (0.0 – 1.0)."""
    riempimento = int(round(valore * larghezza))
    return f"[{'█' * riempimento}{'░' * (larghezza - riempimento)}] {valore:.2f}"


def _stampa_raccomandazione(r: RaccomandazioneCorso, posizione: int) -> None:
    print(f"\n  #{posizione}  {r.corso_nome}")
    print(f"       Score totale  : {_barra(r.score_totale)}")
    print(f"       Curriculum    : {_barra(r.breakdown.curriculum)}  (peso 40%)")
    print(f"       Engagement    : {_barra(r.breakdown.engagement)}  (peso 35%)")
    print(f"       Semantico     : {_barra(r.breakdown.semantico)}   (peso 25%)")
    if r.tag:
        print(f"       Tag           : {', '.join(r.tag)}")
    print(f"       Motivazione   : {r.motivazione}")


def _stampa_studente(studente_id: int, top_n: int) -> None:
    # Carica dati studente
    risultati = db.trova_tutti("users", {"id": studente_id})
    if not risultati:
        print(f"\n⚠  Studente ID {studente_id} non trovato nel DB.")
        return

    s = risultati[0]
    nome_completo = f"{s.get('nome', '?')} {s.get('cognome', '?')}"

    # Carica corso di laurea
    laurea = "—"
    if s.get("corso_di_laurea_id"):
        cdl = db.trova_tutti("corsi_di_laurea", {"id": s["corso_di_laurea_id"]})
        if cdl:
            laurea = cdl[0]["nome"]

    # Corsi iscritti
    iscrizioni = db.trova_tutti("studenti_corsi", {"studente_id": studente_id})
    nomi_iscritti = []
    for i in iscrizioni:
        corsi = db.trova_tutti("corsi_universitari", {"id": i["corso_universitario_id"]})
        if corsi:
            nomi_iscritti.append(corsi[0]["nome"])

    # Piani generati
    piani = db.trova_tutti("piani_personalizzati", {"studente_id": studente_id})

    print(f"\n{_SEP_L}")
    print(f"  👤  {nome_completo}  (ID {studente_id})")
    print(f"{_SEP_L}")
    print(f"  Corso di laurea  : {laurea}")
    print(f"  Anno di corso    : {s.get('anno_corso') or '—'}")
    print(f"  Corsi iscritti   : {', '.join(nomi_iscritti) if nomi_iscritti else 'nessuno'}")
    print(f"  Piani generati   : {len(piani)}")

    if piani:
        # Mostra i titoli dei piani come sintesi degli interessi
        titoli_unici = list({p["titolo"] for p in piani if p.get("titolo")})[:5]
        for t in titoli_unici:
            print(f"    • {t}")

    print(f"\n  📚  RACCOMANDAZIONI (top {top_n}):")
    print(_SEP)

    raccomandazioni = raccomanda_corsi(studente_id, top_n=top_n)

    if not raccomandazioni:
        print("\n  Nessuna raccomandazione disponibile.")
        print("  Possibili cause:")
        print("    - Lo studente è già iscritto a tutti i corsi attivi")
        print("    - Non ci sono corsi attivi nel DB")
        print("    - Lo studente non ha né percorso di laurea né piani generati")
        return

    for i, r in enumerate(raccomandazioni, start=1):
        _stampa_raccomandazione(r, i)

    print()


def _carica_tutti_gli_studenti() -> list[int]:
    """Restituisce gli ID di tutti gli utenti con ruolo studente."""
    studenti = db.trova_tutti("users", {"ruolo": "studente"})
    return [s["id"] for s in studenti]


def main():
    parser = argparse.ArgumentParser(
        description="Testa il motore di raccomandazione corsi LearnAI."
    )
    parser.add_argument(
        "--id", type=int, default=None,
        help="ID dello studente da testare (default: tutti gli studenti)"
    )
    parser.add_argument(
        "--n", type=int, default=5,
        help="Numero massimo di raccomandazioni per studente (default: 5)"
    )
    args = parser.parse_args()

    print(f"\n{'='*65}")
    print("   🎓  TEST MOTORE RACCOMANDAZIONE — LearnAI")
    print(f"{'='*65}")

    if args.id:
        studenti_ids = [args.id]
    else:
        studenti_ids = _carica_tutti_gli_studenti()
        if not studenti_ids:
            print("\n⚠  Nessuno studente trovato nel DB.")
            return
        print(f"\n  Studenti trovati: {len(studenti_ids)} → {studenti_ids}")

    for sid in studenti_ids:
        try:
            _stampa_studente(sid, top_n=args.n)
        except Exception as exc:
            print(f"\n❌  Errore per studente {sid}: {exc}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*65}")
    print("  Test completato.")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
