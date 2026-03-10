"""
src/core/auth.py
Responsabilità: autenticazione backend, totalmente disaccoppiata dalla UI.

Funzioni esportate:
    verifica_credenziali(email, password) -> dict | None
        Interroga la tabella `users` e verifica il password hash.
        Ritorna un dizionario UserSession se autenticato, None altrimenti.
        Il chiamante (app.py o un futuro API layer) gestisce la risposta.
"""

from __future__ import annotations

import sys
import os
from typing import TypedDict

# ---------------------------------------------------------------------------
# Path setup — permette import dalla root in qualsiasi contesto di esecuzione
# ---------------------------------------------------------------------------
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from werkzeug.security import check_password_hash
from platform_sdk.database import db


# ---------------------------------------------------------------------------
# Tipo di ritorno — stato utente autenticato
# ---------------------------------------------------------------------------

class UserSession(TypedDict):
    """Rappresenta la sessione di un utente autenticato.

    Campi:
        user_id:  PK della tabella users.
        email:    Email dell'utente.
        nome:     Nome dell'utente.
        cognome:  Cognome dell'utente.
        ruolo:    Ruolo ('studente' | 'docente' | 'admin').
    """
    user_id: int
    email: str
    nome: str
    cognome: str
    ruolo: str


# ---------------------------------------------------------------------------
# Funzione pubblica
# ---------------------------------------------------------------------------

def verifica_credenziali(email: str, password: str) -> UserSession | None:
    """Verifica le credenziali dell'utente sulla tabella `users`.

    Il confronto dell'email non è sensibile a maiuscole/minuscole e vengono
    rimossi eventuali spazi bianchi di troppo sia in testa che in coda.

    Args:
        email:    Email inserita dall'utente.
        password: Password in chiaro inserita dall'utente.

    Returns:
        Un ``UserSession`` se le credenziali sono corrette e l'account è attivo,
        ``None`` in tutti gli altri casi (email non trovata, password errata,
        account sospeso).

    Esempio:
        sessione = verifica_credenziali("m.Rossi@unina.IT ", "docente123")
        if sessione:
            print(sessione["ruolo"])   # "docente"
        else:
            print("Credenziali errate")
    """
    # Normalizziamo l'email per confronto: tagliamo spazi e utilizziamo
    # sempre minuscole. Assumiamo che le email salvate nel DB siano già
    # normalized in questo modo (la popolazione iniziale segue questa
    # convenzione).
    email_norm = email.strip().lower()

    utente = db.trova_uno("users", {"email": email_norm})

    if utente is None:
        return None

    if not check_password_hash(utente["password_hash"], password):
        return None

    if utente.get("stato") != "active":
        return None

    return UserSession(
        user_id=utente["id"],
        email=utente["email"],
        nome=utente["nome"],
        cognome=utente["cognome"],
        ruolo=utente["ruolo"],
    )
