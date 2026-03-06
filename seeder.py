from werkzeug.security import generate_password_hash
from platform_sdk.database import db

def aggiungi_nuovi_utenti():
    password_criptata = generate_password_hash("Docente2")
    password_criptata2 = generate_password_hash("Studente2") 
    password_criptata3 = generate_password_hash("Studente3")
    nuovi_utenti = [
        # Un altro docente
        {"nome": "Anna", "cognome": "Neri", "email": "annaneri@unina.it", "password_hash": password_criptata, "ruolo": "docente", "stato": "active"},
        
        # Altri due studenti
        {"nome": "Marco", "cognome": "Gialli", "email": "studente2@studenti.unina.it", "password_hash": password_criptata2, "ruolo": "studente", "stato": "active"},
        {"nome": "Elena", "cognome": "Blu", "email": "studente3@studenti.unina.it", "password_hash": password_criptata3, "ruolo": "studente", "stato": "active"}
    ]
    
    for u in nuovi_utenti:
        db.inserisci("users", u)
    
    print("Nuovi account inseriti con successo!")

if __name__ == "__main__":
    aggiungi_nuovi_utenti()