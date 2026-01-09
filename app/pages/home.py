from __future__ import annotations

import streamlit as st

from app.ui_elements import render_material_card


def render() -> None:
    st.title("Home")
    st.write("Fase 0: basisstructuur van de app.")

    render_material_card(
        "Wat volgt",
        "Fase 1 voegt echte login toe. Fase 2 standaardiseert de DB-laag. Fase 3 voegt echte queries en filters toe.",
    )
