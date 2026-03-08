# ============================================================================
# LearnAI Platform — Entry Point
# Università Federico II di Napoli
#
# Avvio: streamlit run app.py
#
# Routing basato su st.session_state["user"]:
#   None           → pagina di login
#   ruolo=studente → views/studente.py
#   ruolo=docente  → views/docente.py  (futura implementazione)
#   ruolo=admin    → views/admin.py    (futura implementazione)
# ============================================================================

import streamlit as st

# ---------------------------------------------------------------------------
# Configurazione pagina — deve essere il PRIMO comando Streamlit
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="LearnAI – Federico II",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Import views (dopo set_page_config)
# ---------------------------------------------------------------------------
from views.login import mostra_login
from views.studente import mostra_homepage_studente


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------
def main():
    # Gatekeeper — standard STATE_MANAGEMENT.md
    if not st.session_state.get("is_logged_in"):
        mostra_login()
        return

    ruolo = st.session_state.get("user_role", "")  # 'Studente' | 'Docente' | 'Admin'

    if ruolo == "Studente":
        mostra_homepage_studente()
    elif ruolo == "Docente":
        st.info("🚧 Pagina docente in costruzione.")
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()
    elif ruolo == "Admin":
        st.info("🚧 Pagina admin in costruzione.")
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()
    else:
        st.error("Ruolo non riconosciuto. Effettua il logout.")
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()


if __name__ == "__main__":
    main()
