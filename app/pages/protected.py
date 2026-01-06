from __future__ import annotations

import streamlit as st

from app.state import get_auth_state, logout
from app.ui_elements import render_material_card


def render() -> None:
    auth = get_auth_state(st.session_state)

    st.title("Protected")
    st.caption("Phase 0 stub: protected area placeholder.")

    render_material_card(
        "Protected content",
        "If you can see this, the app routing and session gating are working.",
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Log out", type="primary", use_container_width=True):
            logout(st.session_state)
            st.rerun()
    with col2:
        st.button("Do nothing", disabled=True, use_container_width=True)

