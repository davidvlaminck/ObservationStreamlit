from __future__ import annotations

import streamlit as st

from app.pages import home, login, protected, users
from app.state import get_auth_state, pop_next_route


def render_sidebar() -> str:
    """Return the selected route label."""

    auth = get_auth_state(st.session_state)

    st.sidebar.title("Menu")

    routes = ["Home"]

    # If user must change password, keep navigation minimal and point them to login.
    if auth.is_authenticated and auth.must_change_password:
        routes.append("Aanmelden")
        return st.sidebar.radio("Ga naar", routes, index=1, label_visibility="collapsed")

    if auth.is_authenticated:
        routes.append("Beveiligd")
        if auth.is_admin:
            routes.append("Admin: Gebruikers")
    else:
        routes.append("Aanmelden")

    # Apply one-time override if present
    override = pop_next_route(st.session_state)
    if override in routes:
        index = routes.index(override)
        return st.sidebar.radio("Ga naar", routes, index=index, label_visibility="collapsed")

    # Mobile/tablet note: Streamlit's sidebar collapses into a hamburger menu.
    # Keep route names short to fit smaller screens.
    return st.sidebar.radio("Ga naar", routes, label_visibility="collapsed")


def render_route(route: str) -> None:
    auth = get_auth_state(st.session_state)

    # Enforce forced password change: user can only access the login screen.
    if auth.is_authenticated and auth.must_change_password and route != "Aanmelden":
        st.warning("Je moet eerst je wachtwoord wijzigen voordat je verder kan.")
        login.render()
        return

    if route == "Home":
        home.render()
        return

    if route == "Aanmelden":
        login.render()
        return

    if route == "Beveiligd":
        if not auth.is_authenticated:
            st.warning("Meld je aan om deze pagina te bekijken.")
            login.render()
            return
        protected.render()
        return

    if route == "Admin: Gebruikers":
        if not auth.is_authenticated or not auth.is_admin:
            st.warning("Adminrechten vereist")
            return
        users.render()
        return

    st.error(f"Onbekende pagina: {route}")
