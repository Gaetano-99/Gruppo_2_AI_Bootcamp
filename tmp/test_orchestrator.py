"""
Script di test da riga di comando per l'Architettura Agentica.

Permette di chattare direttamente con l'Orchestratore dal terminale,
simulando l'ambiente Streamlit tramite un mock di st.session_state.

Comandi speciali disponibili durante la chat:
    /corso <id> [nome]  → simula la navigazione su un corso (inietta contesto)
    /contesto           → mostra il contesto di sessione corrente
    /verifica           → controlla il DB: ultimi piani, paragrafi e quiz realmente salvati
    /reset              → azzera agente, memoria e contesto (nuova sessione)
    /help               → mostra questo elenco
    esci | quit | q     → termina il programma
"""

import sys
import os
import sqlite3
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# MOCK di Streamlit — deve avvenire PRIMA di qualsiasi import del progetto.
# Il nuovo orchestratore usa st.session_state internamente; fuori da Streamlit
# quella variabile non esiste e causerebbe un AttributeError immediato.
# ---------------------------------------------------------------------------
_session_state_store: dict = {}

_mock_st = MagicMock()
_mock_st.session_state = _session_state_store
sys.modules["streamlit"] = _mock_st

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# Ora possiamo importare in sicurezza
from src.agents.orchestrator import (
    chat_con_orchestratore,
    aggiorna_contesto_sessione,
    reset_sessione_chat,
)

# ---------------------------------------------------------------------------
# Costanti UI
# ---------------------------------------------------------------------------
_SEP = "─" * 60
_UTENTE  = "🧑‍🎓 Tu"
_AGENTE  = "🤖 Lea"
_SISTEMA = "⚙️  Sistema"
_ERRORE  = "❌ Errore"


# ===========================================================================
# Helpers
# ===========================================================================

def _stampa_header():
    print(f"\n{'='*60}")
    print("   🎓 TERMINALE AGENTICO — LearnAI")
    print(f"{'='*60}")
    print("Digita /help per vedere i comandi disponibili.\n")


def _stampa_verifica_db():
    """Interroga direttamente il DB e mostra l'ultimo piano e i quiz realmente salvati.

    Questo è lo strumento anti-allucinazione: confronta ciò che l'agente dice
    di aver fatto con ciò che esiste effettivamente nel database.
    """
    try:
        # Trova il path del DB relativo alla root del progetto
        db_path = os.path.join(_ROOT, "learnai.db")
        if not os.path.exists(db_path):
            # Prova path alternativi comuni
            for candidate in ["data/learnai.db", "src/learnai.db", "learnai.db"]:
                full = os.path.join(_ROOT, candidate)
                if os.path.exists(full):
                    db_path = full
                    break
            else:
                print(f"\n{_SISTEMA}: DB non trovato. Percorso atteso: {db_path}\n")
                return

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        user_id = _session_state_store.get("user", {}).get("user_id", 1)

        print(f"\n{_SEP}")
        print(f"{_SISTEMA} VERIFICA DB (studente_id={user_id})")
        print(_SEP)

        # Ultimo piano creato dall'utente corrente
        piano = cur.execute(
            "SELECT id, titolo, corso_universitario_id, created_at "
            "FROM piani_personalizzati WHERE studente_id=? ORDER BY id DESC LIMIT 1",
            [user_id]
        ).fetchone()

        if not piano:
            print("  Nessun piano trovato nel DB per questo utente.")
            conn.close()
            print(_SEP + "\n")
            return

        print(f"  Ultimo piano  : ID {piano['id']} — '{piano['titolo']}' (corso {piano['corso_universitario_id']})")
        print(f"  Creato il     : {piano['created_at']}")

        # Paragrafi del piano
        paragrafi = cur.execute("""
            SELECT pp.id, pp.titolo,
                   COUNT(pc.id) as n_contenuti,
                   GROUP_CONCAT(pc.tipo, ', ') as tipi_contenuto
            FROM piano_paragrafi pp
            JOIN piano_capitoli cap ON pp.capitolo_id = cap.id
            LEFT JOIN piano_contenuti pc ON pc.paragrafo_id = pp.id
            WHERE cap.piano_id = ?
            GROUP BY pp.id
        """, [piano['id']]).fetchall()

        print(f"\n  Sezioni ({len(paragrafi)}):")
        for p in paragrafi:
            tipi = p['tipi_contenuto'] or "nessun contenuto"
            print(f"    ID {p['id']:4d} | {p['titolo'][:45]:<45s} | contenuti: {tipi}")

        # Chunk RAG usati — verifica tracciabilità
        chunk_verifica = cur.execute("""
            SELECT pc.chunk_ids_utilizzati
            FROM piano_contenuti pc
            JOIN piano_paragrafi pp ON pc.paragrafo_id = pp.id
            JOIN piano_capitoli cap ON pp.capitolo_id = cap.id
            WHERE cap.piano_id = ? AND pc.tipo = 'lezione'
            LIMIT 1
        """, [piano['id']]).fetchone()

        if chunk_verifica and chunk_verifica['chunk_ids_utilizzati']:
            import json as _json
            try:
                ids = _json.loads(chunk_verifica['chunk_ids_utilizzati'])
                print(f"\n  RAG tracciabilità: {len(ids)} chunk usati → IDs {ids[:5]}{'...' if len(ids)>5 else ''}")
                # Verifica che i chunk esistano davvero
                for cid in ids[:3]:
                    exists = cur.execute("SELECT 1 FROM materiali_chunks WHERE id=?", [cid]).fetchone()
                    print(f"    chunk {cid}: {'✓ presente in materiali_chunks' if exists else '✗ NON TROVATO — allucinazione RAG!'}")
            except Exception:
                print(f"  RAG: chunk_ids non parsabili → {chunk_verifica['chunk_ids_utilizzati'][:60]}")
        else:
            print("\n  ⚠ Nessun chunk RAG tracciato — il corso è stato generato senza materiali!")

        # Quiz salvati
        quiz_rows = cur.execute("""
            SELECT q.id, q.titolo, COUNT(dq.id) as n_domande
            FROM quiz q
            LEFT JOIN domande_quiz dq ON dq.quiz_id = q.id
            WHERE q.studente_id = ?
            GROUP BY q.id
            ORDER BY q.id DESC LIMIT 5
        """, [user_id]).fetchall()

        if quiz_rows:
            print(f"\n  Quiz recenti:")
            for q in quiz_rows:
                stato = "✓" if q['n_domande'] > 0 else "⚠ VUOTO"
                print(f"    ID {q['id']:4d} | {q['titolo'][:45]:<45s} | {q['n_domande']} domande {stato}")
        else:
            print("\n  Nessun quiz trovato per questo utente.")

        conn.close()
        print(_SEP + "\n")

    except Exception as exc:
        print(f"\n{_SISTEMA}: Errore durante la verifica DB: {exc}\n")


def _stampa_help():
    print(f"\n{_SEP}")
    print("COMANDI SPECIALI:")
    print("  /corso <id> [nome]  → naviga su un corso (inietta contesto di pagina)")
    print("  /contesto           → mostra il contesto di sessione corrente")
    print("  /verifica           → controlla il DB: cosa è stato REALMENTE salvato")
    print("  /reset              → nuova sessione (azzera memoria e contesto)")
    print("  /help               → mostra questo messaggio")
    print("  esci | quit | q     → termina")
    print(f"{_SEP}\n")


def _stampa_contesto():
    """Mostra il contenuto corrente di session_state in modo leggibile."""
    contesto = _session_state_store.get("_orch_contesto_sessione", {})
    thread   = _session_state_store.get("_orch_thread_id", "(non ancora creato)")

    print(f"\n{_SEP}")
    print(f"{_SISTEMA} CONTESTO DI SESSIONE")
    print(f"  Thread ID : {thread}")

    if not contesto:
        print("  Contesto  : vuoto (nessun corso selezionato)")
    else:
        print(f"  Corso     : ID {contesto.get('corso_id', '—')} — {contesto.get('corso_nome', '—')}")
        paragrafi = contesto.get("ultimi_paragrafi", [])
        if paragrafi:
            print(f"  Paragrafi generati ({len(paragrafi)}):")
            for p in paragrafi:
                print(f"    - ID {p['id']}: {p['titolo']}")
        else:
            print("  Paragrafi : nessuno generato ancora")
    print(f"{_SEP}\n")


def _gestisci_comando(riga: str) -> bool:
    """
    Gestisce i comandi speciali che iniziano con '/'.

    Returns:
        True se il comando è stato riconosciuto e gestito (non inviare all'agente).
        False se non è un comando speciale.
    """
    parti = riga.strip().split(maxsplit=2)
    cmd   = parti[0].lower()

    if cmd == "/help":
        _stampa_help()
        return True

    if cmd == "/contesto":
        _stampa_contesto()
        return True

    if cmd == "/verifica":
        _stampa_verifica_db()
        return True

    if cmd == "/reset":
        reset_sessione_chat()
        # reset anche del mock store
        _session_state_store.clear()
        print(f"\n{_SISTEMA}: Sessione azzerata. Memoria, thread e contesto rimossi.\n")
        return True

    if cmd == "/corso":
        if len(parti) < 2:
            print(f"\n{_ERRORE}: Uso corretto → /corso <id> [nome opzionale]\n")
            return True
        try:
            corso_id = int(parti[1])
        except ValueError:
            print(f"\n{_ERRORE}: L'ID corso deve essere un numero intero.\n")
            return True
        corso_nome = parti[2] if len(parti) > 2 else f"Corso {corso_id}"
        aggiorna_contesto_sessione(corso_id=corso_id, corso_nome=corso_nome)
        print(f"\n{_SISTEMA}: Contesto aggiornato → corso ID {corso_id} — '{corso_nome}'\n")
        return True

    return False  # non è un comando speciale


# ===========================================================================
# Loop principale
# ===========================================================================

def avvia_terminale():
    _stampa_header()
    _stampa_help()

    # Simula un utente loggato in session_state
    _session_state_store["user"] = {"user_id": 99, "nome": "Tester CLI"}

    while True:
        try:
            riga = input(f"{_UTENTE}: ").strip()

            if not riga:
                continue

            # Uscita
            if riga.lower() in ("esci", "quit", "q", "exit"):
                print(f"\n👋 Chiusura del terminale. A presto!\n")
                break

            # Comandi speciali
            if riga.startswith("/"):
                _gestisci_comando(riga)
                continue

            # Messaggio normale → invia all'agente
            print(f"\n⏳ {_SISTEMA}: L'agente sta ragionando...\n")
            risposta = chat_con_orchestratore(messaggio_utente=riga)
            print(f"{_AGENTE}:\n{risposta}\n")
            print(_SEP)

        except KeyboardInterrupt:
            print(f"\n\n👋 Uscita forzata. Ciao!\n")
            break
        except Exception as exc:
            print(f"\n{_ERRORE}: {exc}\n")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    avvia_terminale()
