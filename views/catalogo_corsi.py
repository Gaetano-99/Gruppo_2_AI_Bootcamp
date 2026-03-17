"""
views/catalogo_corsi.py
Pagina catalogo corsi di laurea per gli ospiti.
Mostra tutti i corsi disponibili con titolo e descrizione, letti dal database.
"""
import sys
import os

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st

try:
    from platform_sdk.database import db
except ImportError:
    db = None

_CSS = """
<style>
.catalog-header {
    background: linear-gradient(135deg, #003087 0%, #0057B8 100%);
    border-radius: 16px;
    padding: 32px 36px;
    margin-bottom: 32px;
    color: white;
}
.catalog-header h1 {
    color: white;
    margin: 0 0 8px 0;
    font-size: 2rem;
}
.catalog-header p {
    color: rgba(255,255,255,0.85);
    margin: 0;
    font-size: 1.05rem;
}
.facolta-header {
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #C5A028;
    margin: 28px 0 12px 0;
    padding-bottom: 6px;
    border-bottom: 2px solid #EEF4FF;
}
.corso-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 12px;
    border: 1px solid #E2EAF4;
    box-shadow: 0 2px 8px rgba(0,48,135,0.06);
    transition: box-shadow 0.2s;
}
.corso-card:hover {
    box-shadow: 0 4px 16px rgba(0,48,135,0.12);
}
.corso-nome {
    font-size: 1.05rem;
    font-weight: 700;
    color: #003087;
    margin-bottom: 6px;
}
.corso-desc {
    font-size: 0.9rem;
    color: #555;
    line-height: 1.5;
}
.badge-facolta {
    display: inline-block;
    background: #EEF4FF;
    color: #0057B8;
    font-size: 0.72rem;
    font-weight: 600;
    border-radius: 20px;
    padding: 2px 10px;
    margin-bottom: 8px;
}
</style>
"""


def mostra_catalogo():
    """Renderizza la pagina catalogo corsi per gli ospiti."""
    st.markdown(_CSS, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="catalog-header">
        <h1>📚 Catalogo Corsi di Laurea</h1>
        <p>Esplora tutti i percorsi di studio disponibili. Ogni corso è pensato per prepararti
        al meglio per il tuo futuro professionale.</p>
    </div>
    """, unsafe_allow_html=True)

    # Bottone torna alla home
    if st.button("← Torna alla home", key="btn_torna_catalogo"):
        st.session_state["ospite_pagina"] = "home"
        st.rerun()

    st.markdown("---")

    # Carica i corsi dal DB
    corsi = []
    if db is not None:
        try:
            corsi = db.trova_tutti("corsi_di_laurea", ordine="facolta ASC, nome ASC")
        except Exception as e:
            st.error(f"Errore nel caricamento dei corsi: {e}")

    if not corsi:
        st.info("Nessun corso disponibile al momento. Il catalogo è in aggiornamento.")
        return

    # Raggruppa per facoltà
    from collections import OrderedDict
    per_facolta: dict[str, list] = OrderedDict()
    for c in corsi:
        fac = c.get("facolta", "Altro")
        if fac not in per_facolta:
            per_facolta[fac] = []
        per_facolta[fac].append(c)

    # Statistiche rapide
    col1, col2 = st.columns(2)
    col1.metric("📗 Corsi disponibili", len(corsi))
    col2.metric("🏛️ Facoltà", len(per_facolta))

    st.markdown("---")

    # Rendering per facoltà, 2 colonne
    for facolta, lista_corsi in per_facolta.items():
        st.markdown(
            f'<div class="facolta-header">🏛️ {facolta}</div>',
            unsafe_allow_html=True,
        )
        cols = st.columns(2)
        for idx, corso in enumerate(lista_corsi):
            nome = corso.get("nome", "Corso senza nome")
            desc = corso.get("descrizione") or "Descrizione non disponibile."
            fac = corso.get("facolta", "")
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="corso-card">
                    <div class="badge-facolta">{fac}</div>
                    <div class="corso-nome">🎓 {nome}</div>
                    <div class="corso-desc">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    col_a, col_b = st.columns([1, 3])
    with col_a:
        if st.button("← Torna alla home", key="btn_torna_catalogo_bottom"):
            st.session_state["ospite_pagina"] = "home"
            st.rerun()
    with col_b:
        if st.button("🎯 Fai il questionario di orientamento →", key="btn_vai_quest", type="primary"):
            st.session_state["ospite_pagina"] = "questionario"
            st.rerun()
