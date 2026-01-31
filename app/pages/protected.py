from __future__ import annotations

import streamlit as st

from app.state import get_auth_state, logout, is_dev_mode
from app.ui_elements import render_material_card, redact_db_url
from app import db


def render() -> None:
    auth = get_auth_state(st.session_state)

    st.title("Beveiligd")
    st.caption("Fase 0 stub: placeholder voor beveiligde zone.")

    st.write("\nGa naar:")
    if st.button("Observaties bekijken"):
        st.session_state["route_override"] = "Observaties"
        st.rerun()

    # Diagnostics (dev-only)
    if is_dev_mode():
        with st.expander("Diagnose", expanded=False):
            st.caption("Welke database gebruikt deze run?")
            st.code(redact_db_url(db.DB_URL))

            try:
                from sqlalchemy import select

                eng = db.get_engine()
                with eng.connect() as conn:
                    row = conn.execute(select(db.users).where(db.users.c.email == auth.email)).mappings().first() if auth.email else None
                if row:
                    st.caption("Huidige gebruiker (uit DB)")
                    st.json(
                        {
                            "id": row.get("id"),
                            "email": row.get("email"),
                            "must_change_password": bool(row.get("must_change_password")),
                            "is_admin": bool(row.get("is_admin")),
                            "updated_at": str(row.get("updated_at")),
                            "last_login_at": str(row.get("last_login_at")),
                        }
                    )
            except Exception as e:
                st.caption("Diagnose info niet beschikbaar")
                st.write(str(e))

    render_material_card(
        "Beveiligde inhoud",
        "Als je dit ziet, werken de routing en sessiecontrole.",
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Afmelden", type="primary", use_container_width=True):
            logout(st.session_state)
            st.rerun()
    with col2:
        st.button("Doe niets", disabled=True, use_container_width=True)
