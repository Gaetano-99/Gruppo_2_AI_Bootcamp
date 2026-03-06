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
for email, pwd in tests:
    u = db.trova_uno('users', {'email': email})
    ok = check_password_hash(u['password_hash'], pwd) if u else False
    ruolo = u['ruolo'] if u else 'N/A'
    uid = u['id'] if u else 'N/A'
    print(f"{email} ({ruolo}): {'OK' if ok else 'FAIL'} - ID={uid}")
