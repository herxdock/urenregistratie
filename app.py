import streamlit as st
from src.auth import require_login
from src.ui import inject_mobile_css

st.set_page_config(
    page_title="Urenregistratie",
    page_icon="⏱️",
    layout="centered",
    initial_sidebar_state="auto",
)

inject_mobile_css()
require_login()

# Navigatie — volgorde = volgorde in de zijbalk
pg = st.navigation([
    st.Page("pages/1_Invoer.py",       title="Invoer",      icon="📝", default=True),
    st.Page("pages/4_Kalender.py",     title="Kalender",    icon="📅"),
    st.Page("pages/3_Rapporten.py",    title="Rapporten",   icon="📊"),
    st.Page("pages/2_Beheer.py",       title="Beheer",      icon="⚙️"),
    st.Page("pages/0_Handleiding.py",  title="Handleiding", icon="ℹ️"),
])

# Uitloggen + gebruikersinfo in de zijbalk
with st.sidebar:
    st.divider()
    user = st.session_state.get("user", {})
    st.caption(f"Ingelogd als **{user.get('name','')}** ({user.get('role','')})")
    if st.button("Uitloggen", use_container_width=True):
        st.session_state.clear()
        st.rerun()

pg.run()
