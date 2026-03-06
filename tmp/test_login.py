import sys
sys.path.insert(0, '.')
from werkzeug.security import check_password_hash
from platform_sdk.database import db

tests = [
    # original credentials
    ('m.rossi@unina.it', 'docente123'),
    ('g.bianchi@studenti.unina.it', 'studente123'),
    ('a.verdi@unina.it', 'admin123'),
    # variants with uppercase and extra spaces
    (' M.Rossi@unina.IT ', 'docente123'),
    ('G.BIanchi@studenti.unina.it', 'studente123'),
    ('a.Verdi@unina.it  ', 'admin123'),
]

# helper that exercises verifica_credenziali instead of direct DB access
from src.core.auth import verifica_credenziali

for email, pwd in tests:
    sessione = verifica_credenziali(email, pwd)
    ok = bool(sessione)
    ruolo = sessione['ruolo'] if sessione else 'N/A'
    uid = sessione['user_id'] if sessione else 'N/A'
    print(f"{email} ({ruolo}): {'OK' if ok else 'FAIL'} - ID={uid}")

