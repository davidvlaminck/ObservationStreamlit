from __future__ import annotations

import streamlit as st

from app.state import get_auth_state
from app.ui_elements import render_material_card


def render() -> None:
    st.title("Login")

    st.caption(
        "Phase 0 stub: this does not authenticate yet. "
        "In Phase 1 we'll add secure password hashing + DB-backed users."
    )

    auth = get_auth_state(st.session_state)

    render_material_card(
        "Welcome",
        "Use the button below to enter the protected area (stub).",
    )

    if st.button("Enter (stub login)", use_container_width=True):
        auth.is_authenticated = True
        st.success("You're now marked as logged in (stub).")
        st.rerun()

