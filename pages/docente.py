"""Placeholder — Area Docente"""
import sys, os
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st

st.set_page_config(page_title="Area Docente", page_icon="👨‍🏫")
st.markdown("<style>[data-testid='stSidebarNav']{display:none}</style>", unsafe_allow_html=True)

if not st.session_state.get("is_logged_in"):
    st.switch_page("app.py")

st.title("👨‍🏫 Area Docente")
st.info("Sezione in costruzione.")
st.caption(f"Loggato come: **{st.session_state.get('current_user', {}).get('email', '—')}**")

with st.sidebar:
    if st.button("🚪 Logout"):
        for k in ["is_logged_in", "current_user", "user_id", "user_role"]:
            st.session_state.pop(k, None)
        st.switch_page("app.py")
