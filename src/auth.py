import streamlit as st
from src.ui import inject_mobile_css


def require_login():
    inject_mobile_css()

    if st.session_state.get("user"):
        return st.session_state["user"]

    st.title("🔐 Inloggen")
    st.caption("Voer je gebruikersnaam en wachtwoord in.")

    with st.form("login_form"):
        u = st.text_input("Gebruikersnaam", autocomplete="username")
        p = st.text_input("Wachtwoord", type="password", autocomplete="current-password")
        ok = st.form_submit_button("Inloggen", use_container_width=True, type="primary")

    if ok:
        users = st.secrets.get("users", {})
        if u in users and users[u].get("password") == p:
            st.session_state["user"] = {
                "name": u,
                "role": users[u].get("role", "worker"),
            }
            st.rerun()
        else:
            st.error("Onjuiste gebruikersnaam of wachtwoord.")
    st.stop()
