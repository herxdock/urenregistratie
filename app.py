import streamlit as st
from src.auth import require_login

st.set_page_config(
    page_title="Urenregistratie",
    page_icon="⏱️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

user = require_login()

st.title("⏱️ Urenregistratie")
st.write(f"Ingelogd als **{user['name']}** ({user['role']})")

st.markdown(
    "Gebruik de **sidebar** (linksboven ☰) om te navigeren:\n\n"
    "- 📝 **Invoer** – dagelijkse shiften invullen\n"
    "- ⚙️ **Beheer** – types beheren en shiften verwijderen\n"
    "- 📊 **Rapporten** – totalen en export"
)

if st.button("Uitloggen", use_container_width=True):
    st.session_state.clear()
    st.rerun()
