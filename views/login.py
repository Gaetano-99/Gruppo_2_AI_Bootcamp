# ============================================================================
# LearnAI Platform — Pagina di Login
# Università Federico II di Napoli
#
# Funzionalità:
#   - Autenticazione via email + password (hash SHA-256)
#   - Blocco account dopo 5 tentativi falliti (15 minuti)
#   - Routing automatico per ruolo dopo login riuscito
#   - Palette colori ufficiale Federico II
# ============================================================================

import sys
import os
from datetime import datetime, timezone

import streamlit as st
from werkzeug.security import check_password_hash

# ---------------------------------------------------------------------------
# Path setup — permette import dalla root del progetto
# ---------------------------------------------------------------------------
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from platform_sdk.database import db


# ---------------------------------------------------------------------------
# Costanti
# ---------------------------------------------------------------------------
_MAX_TENTATIVI: int = 5
_MINUTI_BLOCCO: int = 15


# ---------------------------------------------------------------------------
# CSS — Palette Federico II
# ---------------------------------------------------------------------------
_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Source+Sans+3:wght@300;400;600&display=swap');

:root {
    --blue:       #003087;
    --blue-dark:  #001A4D;
    --blue-mid:   #1351A8;
    --red:        #C8102E;
    --gold:       #C5A028;
    --light:      #F0F4F8;
    --gray:       #5A6A7E;
    --border:     #C8D5E3;
    --white:      #FFFFFF;
}

/* App background */
.stApp {
    background: linear-gradient(160deg, #EEF2F8 0%, #F6F8FC 100%) !important;
    font-family: 'Source Sans 3', sans-serif !important;
}

/* Nascondi elementi Streamlit non necessari */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; }

/* ---- HERO STRIP ---- */
.hero-strip {
    background: linear-gradient(135deg, #001A4D 0%, #003087 55%, #1351A8 100%);
    padding: 20px 40px;
    display: flex;
    align-items: center;
    gap: 18px;
    border-bottom: 3px solid #C5A028;
    margin: -1rem -1rem 0 -1rem;
}
.hero-strip .logo-text {
    color: #fff;
    font-family: 'Playfair Display', serif;
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: -0.3px;
    line-height: 1.1;
}
.hero-strip .logo-sub {
    color: rgba(255,255,255,0.7);
    font-size: 0.75rem;
    font-weight: 300;
    letter-spacing: 0.5px;
    margin-top: 2px;
}
.hero-strip .badge {
    background: #C5A028;
    color: #001A4D;
    font-size: 0.65rem;
    font-weight: 700;
    padding: 3px 9px;
    border-radius: 20px;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-left: auto;
}

/* ---- CARD LOGIN ---- */
.login-card {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 44px 48px 40px;
    box-shadow: 0 8px 40px rgba(0,48,135,0.13);
    border-top: 5px solid #003087;
    max-width: 420px;
    margin: 48px auto 0;
}
.login-card-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.65rem;
    color: #001A4D;
    margin: 0 0 4px 0;
    font-weight: 700;
}
.login-card-sub {
    color: #5A6A7E;
    font-size: 0.9rem;
    font-weight: 300;
    margin-bottom: 28px;
}
.login-divider {
    height: 1px;
    background: #C8D5E3;
    margin: 24px 0;
}

/* ---- INPUT OVERRIDES ---- */
.stTextInput label {
    font-weight: 600 !important;
    color: #001A4D !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.2px;
}
.stTextInput input {
    border: 1.5px solid #C8D5E3 !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 0.95rem !important;
    background: #EBEBEB !important;
    color: #1a2535 !important;
    color: #1a2535 !important;
    transition: border-color 0.18s, box-shadow 0.18s;
}
.stTextInput input:focus {
    border-color: #003087 !important;
    box-shadow: 0 0 0 3px rgba(0,48,135,0.1) !important;
}

/* ---- BOTTONE ---- */
.stButton > button {
    background: linear-gradient(135deg, #003087 0%, #1351A8 100%) !important;
    color: #f1a1a1a ff !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 11px 0 !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.3px !important;
    width: 100% !important;
    transition: opacity 0.2s, transform 0.15s !important;
}
.stButton > button:hover {
    opacity: 0.91 !important;
    transform: translateY(-1px) !important;
}

/* ---- ALERT BOX ---- */
.alert-error {
    background: #FFF0F2;
    border: 1px solid #F5C6CE;
    border-left: 4px solid #C8102E;
    border-radius: 8px;
    padding: 12px 16px;
    color: #7D1A2A;
    font-size: 0.88rem;
    margin-bottom: 16px;
}
.alert-info {
    background: #EEF4FF;
    border: 1px solid #BFCFE8;
    border-left: 4px solid #003087;
    border-radius: 8px;
    padding: 12px 16px;
    color: #002266;
    font-size: 0.88rem;
    margin-bottom: 16px;
}

/* ---- CREDENZIALI DEMO ---- */
.demo-box {
    background: #F8FAFC;
    border: 1px dashed #C8D5E3;
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 0.82rem;
    color: #5A6A7E;
    margin-top: 20px;
}
.demo-box strong { color: #003087; }
</style>
"""


# ---------------------------------------------------------------------------
# Utility auth
# ---------------------------------------------------------------------------

def _controlla_blocco(utente: dict) -> str | None:
    """
    Restituisce un messaggio di errore se l'account è bloccato, None altrimenti.
    """
    bloccato_fino_a = utente.get("bloccato_fino_a")
    if bloccato_fino_a:
        try:
            dt_blocco = datetime.fromisoformat(str(bloccato_fino_a))
            if dt_blocco.tzinfo is None:
                dt_blocco = dt_blocco.replace(tzinfo=timezone.utc)
            ora = datetime.now(timezone.utc)
            if ora < dt_blocco:
                minuti_rimasti = int((dt_blocco - ora).total_seconds() // 60) + 1
                return f"Account bloccato. Riprova tra {minuti_rimasti} minuti."
        except (ValueError, TypeError):
            pass
    return None


def _registra_login_fallito(utente_id: int, tentativi_attuali: int) -> str:
    """
    Incrementa il contatore dei tentativi falliti.
    Se raggiunge il limite, blocca l'account per 15 minuti.
    Restituisce il messaggio di errore da mostrare all'utente.
    """
    nuovi_tentativi = tentativi_attuali + 1

    if nuovi_tentativi >= _MAX_TENTATIVI:
        from datetime import timedelta
        ora = datetime.now(timezone.utc)
        blocco_fino = (ora + timedelta(minutes=_MINUTI_BLOCCO)).isoformat()
        db.aggiorna(
            "users",
            {"id": utente_id},
            {"tentativi_falliti": nuovi_tentativi, "bloccato_fino_a": blocco_fino},
        )
        return f"Troppi tentativi falliti. Account bloccato per {_MINUTI_BLOCCO} minuti."
    else:
        db.aggiorna("users", {"id": utente_id}, {"tentativi_falliti": nuovi_tentativi})
        rimasti = _MAX_TENTATIVI - nuovi_tentativi
        return f"Password errata. Tentativi rimasti: {rimasti}."


def _esegui_login(email: str, password: str) -> tuple[dict | None, str | None]:
    """
    Esegue il login completo con controllo blocco, verifica password e aggiornamento DB.

    Returns:
        (utente_dict, errore_str) — uno dei due è sempre None.
    """
    if not email or not password:
        return None, "Inserisci email e password."

    # Cerca utente per email
    risultati = db.trova_tutti("users", {"email": email.strip().lower()})
    if not risultati:
        return None, "Credenziali non corrette."

    utente = risultati[0]

    # Controlla se account è sospeso
    if utente.get("stato") == "sospeso":
        return None, "Account sospeso. Contatta l'amministratore."

    # Controlla blocco temporaneo
    msg_blocco = _controlla_blocco(utente)
    if msg_blocco:
        return None, msg_blocco

    # Verifica password (Werkzeug PBKDF2 — generato con generate_password_hash)
    if not check_password_hash(utente["password_hash"], password):
        errore = _registra_login_fallito(utente["id"], utente.get("tentativi_falliti", 0))
        return None, errore

    # Login riuscito — aggiorna last_login e reset tentativi
    db.aggiorna(
        "users",
        {"id": utente["id"]},
        {
            "last_login": datetime.now(timezone.utc).isoformat(),
            "tentativi_falliti": 0,
            "bloccato_fino_a": None,
        },
    )

    return utente, None


# ---------------------------------------------------------------------------
# UI principale
# ---------------------------------------------------------------------------

def mostra_login():
    """Renderizza la pagina di login completa."""
    st.markdown(_CSS, unsafe_allow_html=True)

    # Hero strip istituzionale
    st.markdown("""
    <div class="hero-strip">
        <div>
            <div class="logo-text">🎓 LearnAI</div>
            <div class="logo-sub">Università degli Studi di Napoli Federico II</div>
        </div>
        <span class="badge">AI Platform</span>
    </div>
    """, unsafe_allow_html=True)

    # Card centrale
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("""
        <div class="login-card">
            <div class="login-card-title">Benvenuto</div>
            <div class="login-card-sub">Accedi con le credenziali istituzionali</div>
        </div>
        """, unsafe_allow_html=True)

        # Messaggi di feedback
        if st.session_state.get("_login_errore"):
            st.markdown(
                f'<div class="alert-error">⚠️ {st.session_state["_login_errore"]}</div>',
                unsafe_allow_html=True,
            )

        # Form
        email = st.text_input(
            "Email istituzionale",
            placeholder="nome.cognome@studenti.unina.it",
            key="login_email",
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="••••••••",
            key="login_password",
        )

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button("Accedi", use_container_width=True):
            utente, errore = _esegui_login(email, password)

            if errore:
                st.session_state["_login_errore"] = errore
                st.rerun()
            else:
                # Popola session_state secondo lo standard STATE_MANAGEMENT.md
                st.session_state.is_logged_in    = True
                st.session_state.current_user_id = utente["id"]
                st.session_state.user_role       = utente["ruolo"].capitalize()  # 'Studente' | 'Docente' | 'Admin'
                st.session_state.chat_history    = []
                # Dati estesi per la UI (nome, email, campi ruolo-specifici)
                st.session_state.user = {
                    "user_id":             utente["id"],
                    "nome":                utente["nome"],
                    "cognome":             utente["cognome"],
                    "email":               utente["email"],
                    "ruolo":               utente["ruolo"],
                    "matricola":           utente.get("matricola_studente") or utente.get("matricola_docente"),
                    "corso_di_laurea_id":  utente.get("corso_di_laurea_id"),
                    "anno_corso":          utente.get("anno_corso"),
                    "dipartimento":        utente.get("dipartimento"),
                }
                st.session_state.pop("_login_errore", None)
                st.rerun()

        # Box credenziali demo
        st.markdown("""
        <div class="demo-box">
            <strong>Account demo disponibili:</strong><br>
            👩‍🎓 Studente: <code>studente@studenti.unina.it</code><br>
            👨‍🏫 Docente: &nbsp;<code>docente@unina.it</code><br>
            🔑 Password: <code>test1234</code>
        </div>
        """, unsafe_allow_html=True)
