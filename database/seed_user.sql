from werkzeug.security import generate_password_hash
from platform_sdk.database import db

utenti_test = [
    {
        "nome": "Mario", "cognome": "Rossi", "email": "docente1@unina.it", 
        "password_hash": generate_password_hash("test1234"), "ruolo": "docente", "stato": "active"
    },
    {
        "nome": "Luigi", "cognome": "Verdi", "email": "docente2@unina.it", 
        "password_hash": generate_password_hash("test1234"), "ruolo": "docente", "stato": "active"
    },
    {
        "nome": "Giulia", "cognome": "Bianchi", "email": "studente1@studenti.unina.it", 
        "password_hash": generate_password_hash("test1234"), "ruolo": "studente", "stato": "active"
    },
    {
        "nome": "Francesca", "cognome": "Neri", "email": "studente2@studenti.unina.it", 
        "password_hash": generate_password_hash("test1234"), "ruolo": "studente", "stato": "active"
    }
]

for u in utenti_test:
    db.inserisci("users", u)
print("Utenti di test inseriti con successo!")