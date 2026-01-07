from __future__ import annotations

import streamlit as st

from app.pages import home, login, protected, users
from app.state import get_auth_state


def render_sidebar() -> str:
    """Return the selected route label."""

    auth = get_auth_state(st.session_state)

    st.sidebar.title("Navigation")

    routes = ["Home"]
    if auth.is_authenticated:
        routes.append("Protected")
        if auth.is_admin:
            routes.append("Admin: Users")
    else:
        routes.append("Login")

    # Mobile/tablet note: Streamlit's sidebar collapses into a hamburger menu.
    # Keep route names short to fit smaller screens.
    return st.sidebar.radio("Go to", routes, label_visibility="collapsed")


def render_route(route: str) -> None:
    auth = get_auth_state(st.session_state)

    if route == "Home":
        home.render()
        return

    if route == "Login":
        login.render()
        return

    if route == "Protected":
        if not auth.is_authenticated:
            st.warning("Please log in to access this page.")
            login.render()
            return
        protected.render()
        return

    if route == "Admin: Users":
        if not auth.is_authenticated or not auth.is_admin:
            st.warning("Admin access required")
            return
        users.render()
        return

    st.error(f"Unknown route: {route}")
