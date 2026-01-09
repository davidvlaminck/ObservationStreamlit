import streamlit as st

from app.config import load_config
from app.router import render_route, render_sidebar
from app import db


def main() -> None:
    cfg = load_config()

    st.set_page_config(
        page_title=cfg.app_name,
        page_icon="🛰️",
        layout="wide",  # Streamlit will still behave reasonably on mobile; we avoid wide-only assumptions in layout.
        initial_sidebar_state="auto",
    )

    # Ensure DB is initialized once per run (stable DB_URL anchored in app.db)
    db.init_db()

    route = render_sidebar()
    render_route(route)


if __name__ == "__main__":
    main()
