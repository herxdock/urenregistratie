import streamlit as st
import extra_streamlit_components as stx
from src.ui import inject_mobile_css

COOKIE_NAME = "uren_user"
COOKIE_DAYS = 30


def current_user() -> dict:
    return st.session_state.get("user") or {}


def _try_cookie_login():
    """Poging om met een bestaande cookie in te loggen."""
    try:
        cm = stx.CookieManager(key="uren_auth")
        cookies = cm.get_all() or {}
        u = cookies.get(COOKIE_NAME)
        users = st.secrets.get("users", {})
        if u and u in users:
            st.session_state["user"] = {
                "name": u,
                "role": users[u].get("role", "worker"),
            }
            return True
    except Exception:
        pass
    return False


def require_login():
    inject_mobile_css()

    if st.session_state.get("user"):
        return st.session_state["user"]

    # Probeer cookie-login
    if _try_cookie_login():
        st.rerun()

    st.title("🔐 Inloggen")
    st.caption("Voer je gebruikersnaam en wachtwoord in.")

    users = st.secrets.get("users", {})

    with st.form("login_form"):
        u = st.text_input("Gebruikersnaam", autocomplete="username")
        p = st.text_input("Wachtwoord", type="password", autocomplete="current-password")
        remember = st.checkbox("Ingelogd blijven op dit toestel", value=True)
        ok = st.form_submit_button("Inloggen", use_container_width=True, type="primary")

    if ok:
        if u in users and users[u].get("password") == p:
            st.session_state["user"] = {
                "name": u,
                "role": users[u].get("role", "worker"),
            }
            if remember:
                try:
                    cm = stx.CookieManager(key="uren_auth")
                    cm.set(COOKIE_NAME, u, expires_at=None,
                           max_age=COOKIE_DAYS * 24 * 3600)
                except Exception:
                    pass
            st.rerun()
        else:
            st.error("Onjuiste gebruikersnaam of wachtwoord.")
    st.stop()


def logout():
    try:
        cm = stx.CookieManager(key="uren_auth")
        cm.delete(COOKIE_NAME)
    except Exception:
        pass
    st.session_state.clear()
    st.rerun()
