from __future__ import annotations

import streamlit as st
from app.db import get_engine, get_observations, categories
from app.state import get_auth_state
from datetime import date

# Helper to fetch category options

def get_category_options(conn):
    cats = conn.execute(categories.select().order_by(categories.c.label)).mappings().all()
    return [(c["id"], c["label"]) for c in cats]


def render():
    auth_state = get_auth_state(st.session_state)
    if not auth_state.is_authenticated:
        st.warning("Je moet ingelogd zijn om observaties te bekijken.")
        return

    st.title("Observaties")
    st.caption("Filter en bekijk observaties. Resultaten zijn beperkt tot 50 per pagina.")

    with get_engine().connect() as conn:
        # Filter UI
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("Vanaf datum", value=None, key="obs_start")
            end_date = st.date_input("Tot datum", value=None, key="obs_end")
        with col2:
            cat_options = get_category_options(conn)
            category_id = st.selectbox("Categorie", options=[None] + [c[0] for c in cat_options], format_func=lambda x: dict(cat_options).get(x, "Alle categorieën"), key="obs_cat")
        with col3:
            text = st.text_input("Zoek in commentaar", value="", key="obs_text")
        # Pagination
        page = st.number_input("Pagina", min_value=1, value=1, step=1, key="obs_page")
        offset = (page - 1) * 50
        # Query
        obs = get_observations(conn, start_date=start_date, end_date=end_date, category_id=category_id, text=text, limit=50, offset=offset)
        if not obs:
            st.info("Geen observaties gevonden.")
            return
        # Display table
        st.dataframe([{k: v for k, v in o.items()} for o in obs], use_container_width=True)
        st.caption(f"Totaal getoond: {len(obs)} observaties (pagina {page})")
