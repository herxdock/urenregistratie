import streamlit as st
from src.auth import require_login, logout, current_user
from src.ui import inject_mobile_css

st.set_page_config(
    page_title="Urenregistratie",
    page_icon="⏱️",
    layout="centered",
    initial_sidebar_state="auto",
)

inject_mobile_css()
require_login()
user = current_user()

# Navigatie op basis van rol
pages = [
    st.Page("pages/1_Invoer.py",       title="Invoer",      icon="📝", default=True),
    st.Page("pages/4_Kalender.py",     title="Kalender",    icon="📅"),
    st.Page("pages/3_Rapporten.py",    title="Rapporten",   icon="📊"),
]
if user.get("role") == "admin":
    pages.append(st.Page("pages/2_Beheer.py", title="Beheer", icon="⚙️"))
pages.append(st.Page("pages/0_Handleiding.py", title="Handleiding", icon="ℹ️"))

pg = st.navigation(pages)

with st.sidebar:
    st.divider()
    st.caption(f"Ingelogd als **{user.get('name','')}** ({user.get('role','')})")
    if st.button("Uitloggen", use_container_width=True):
        logout()

pg.run()
