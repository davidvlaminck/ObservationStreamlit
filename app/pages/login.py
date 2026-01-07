from __future__ import annotations

import streamlit as st

from app.state import get_auth_state
from app.ui_elements import render_material_card
from app import db, auth


def render() -> None:
    st.title("Login")

    # Ensure DB is initialized and initial admin exists
    db.init_db()

    auth_state = get_auth_state(st.session_state)

    if auth_state.is_authenticated:
        st.success(f"Already logged in as {auth_state.email}")
        return

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Log in")

    if submit:
        user = auth.authenticate(email.strip(), password)
        if not user:
            st.error("Invalid credentials")
            return
        # populate session
        auth_state.is_authenticated = True
        auth_state.user_id = user["id"]
        auth_state.email = user["email"]
        auth_state.full_name = user.get("full_name")
        auth_state.is_admin = bool(user.get("is_admin"))
        auth_state.must_change_password = bool(user.get("must_change_password"))

        if auth_state.must_change_password:
            st.info("You must change your password before continuing.")

    # If user must change password, show change form
    if auth_state.is_authenticated and auth_state.must_change_password:
        with st.form("change_pw"):
            new_pw = st.text_input("New password", type="password")
            new_pw2 = st.text_input("Repeat new password", type="password")
            submit2 = st.form_submit_button("Set new password")
        if submit2:
            if not new_pw or new_pw != new_pw2:
                st.error("Passwords do not match or are empty")
            else:
                auth.change_password(auth_state.user_id, new_pw)
                auth_state.must_change_password = False
                st.success("Password updated. You are now logged in.")
                st.rerun()

    render_material_card(
        "Note",
        "If this is a first run an initial admin account will have been created. The admin must change the temporary password on first login.",
    )
