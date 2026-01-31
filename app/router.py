from __future__ import annotations

import streamlit as st

from app.pages import home, login, protected, users, categories
from app.state import get_auth_state, pop_next_route


def get_token_from_url():
    """Extract the token from the URL query parameters, if present."""
    query_params = st.query_params
    token = query_params.get("token")
    return token


def set_token_in_url(token: str):
    """Set the token in the URL query parameters using Streamlit's query_params API."""
    query_params = dict(st.query_params)
    query_params["token"] = token
    st.query_params = query_params


def render_sidebar() -> str:
    """Render the sidebar navigation and handle route selection."""
    auth = get_auth_state(st.session_state)
    token = get_token_from_url()

    st.sidebar.title("Menu")

    routes = ["Home"]

    # If user must change password, keep navigation minimal and point them to login.
    if auth.is_authenticated and auth.must_change_password:
        routes.append("Aanmelden")
        idx = 1
    elif auth.is_authenticated:
        routes.append("Beveiligd")
        if auth.is_admin:
            routes.append("Admin: Gebruikers")
            routes.append("Admin: Categorieën")
        idx = 0
    else:
        routes.append("Aanmelden")
        idx = 1

    # Apply one-time override if present
    override = pop_next_route(st.session_state)
    if override in routes:
        idx = routes.index(override)

    selected = st.sidebar.radio("Ga naar", routes, index=idx, label_visibility="collapsed")

    # Zet de token in de URL bij elke navigatie
    if token:
        set_token_in_url(token)

    return selected


def render_route(route: str) -> None:
    """Render the main content area based on the selected route."""
    auth = get_auth_state(st.session_state)
    token = get_token_from_url()
    if token:
        set_token_in_url(token)

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
            st.warning("Je moet ingelogd zijn om deze pagina te bekijken.")
            login.render()
            return
        protected.render()
        return

    if route == "Admin: Gebruikers":
        if not auth.is_authenticated or not auth.is_admin:
            st.warning("Alleen admins mogen gebruikers beheren.")
            login.render()
            return
        users.render()
        return

    if route == "Admin: Categorieën":
        if not auth.is_authenticated or not auth.is_admin:
            st.warning("Alleen admins mogen categorieën beheren.")
            login.render()
            return
        categories.render()
        return

    # Default fallback
    home.render()
