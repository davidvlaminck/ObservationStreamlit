from __future__ import annotations

import streamlit as st

from app.ui_elements import render_material_card


def render() -> None:
    st.title("Home")
    st.write("Phase 0: skeleton app.")

    render_material_card(
        "What’s next",
        "Phase 1 adds real login. Phase 2 standardizes the DB layer. Phase 3 adds real queries and filters.",
    )

