from __future__ import annotations

import streamlit as st

from app.state import get_auth_state, logout, set_next_route, is_dev_mode
from app.ui_elements import render_material_card, redact_db_url
from app import db, auth


def render() -> None:
    st.title("Aanmelden")

    # Ensure DB is initialized and initial admin exists
    db.init_db()

    # Diagnostics (dev-only)
    if is_dev_mode():
        with st.expander("Diagnose", expanded=False):
            st.caption("Welke database gebruikt deze run?")
            st.code(redact_db_url(db.DB_URL))

            try:
                from sqlalchemy import select

                eng = db.get_engine()
                with eng.connect() as conn:
                    admin_row = conn.execute(select(db.users).where(db.users.c.email == "admin")).mappings().first()
                if admin_row:
                    st.caption("Admin account toestand (uit DB)")
                    st.json(
                        {
                            "id": admin_row.get("id"),
                            "email": admin_row.get("email"),
                            "must_change_password": bool(admin_row.get("must_change_password")),
                            "updated_at": str(admin_row.get("updated_at")),
                            "last_login_at": str(admin_row.get("last_login_at")),
                        }
                    )
            except Exception as e:
                st.caption("Diagnose info niet beschikbaar")
                st.write(str(e))

    auth_state = get_auth_state(st.session_state)

    # If already authenticated and everything is OK, offer logout and stop.
    if auth_state.is_authenticated and not auth_state.must_change_password:
        st.success(f"Je bent aangemeld als {auth_state.email}.")
        if st.button("Afmelden", type="secondary"):
            logout(st.session_state)
            st.rerun()
        return

    # If authenticated but forced to change password, show warning and allow logout,
    # but DO NOT return — the change-password form below must remain accessible.
    if auth_state.is_authenticated and auth_state.must_change_password:
        st.warning("Je bent aangemeld, maar je moet eerst je wachtwoord wijzigen voordat je verder kan.")
        if st.button("Afmelden", type="secondary"):
            logout(st.session_state)
            st.rerun()

    with st.form("login_form"):
        email = st.text_input("E-mail")
        password = st.text_input("Wachtwoord", type="password")
        submit = st.form_submit_button("Aanmelden")

    if submit:
        try:
            user = auth.authenticate(email, password)
        except auth.AuthLocked:
            st.error("Te veel mislukte pogingen. Deze account is tijdelijk geblokkeerd.")
            st.info("Admin herstel (zonder e-mail): reset je wachtwoord via de CLI: `python scripts/create_admin.py --email <email> --reset`")
            return

        if not user:
            st.error("Ongeldige aanmeldgegevens")
            st.info("Wachtwoord vergeten? Een admin kan je wachtwoord resetten in Admin → Gebruikers.")
            st.info("Als je zelf de admin bent en je kan niet meer inloggen: `python scripts/create_admin.py --email <email> --reset`")
            return

        # populate session
        auth_state.is_authenticated = True
        auth_state.user_id = user["id"]
        auth_state.email = user["email"]
        auth_state.full_name = user.get("full_name")
        auth_state.is_admin = bool(user.get("is_admin"))
        auth_state.must_change_password = bool(user.get("must_change_password"))

        if auth_state.must_change_password:
            st.info("Je logt in met een tijdelijk wachtwoord. Kies nu een nieuw wachtwoord.")
        else:
            # Send user to protected page after normal login
            set_next_route(st.session_state, "Beveiligd")
            st.rerun()

    # If user must change password, show change form
    if auth_state.is_authenticated and auth_state.must_change_password:
        with st.form("change_pw"):
            new_pw = st.text_input("Nieuw wachtwoord", type="password")
            new_pw2 = st.text_input("Herhaal nieuw wachtwoord", type="password")
            submit2 = st.form_submit_button("Wachtwoord instellen")
        if submit2:
            if not new_pw or new_pw != new_pw2:
                st.error("Wachtwoorden komen niet overeen of zijn leeg")
            else:
                auth.change_password(auth_state.user_id, new_pw)

                # Re-authenticate to refresh session flags from DB, then route to protected
                refreshed = auth.authenticate(auth_state.email or "", new_pw)
                if refreshed:
                    auth_state.is_authenticated = True
                    auth_state.user_id = refreshed["id"]
                    auth_state.email = refreshed["email"]
                    auth_state.full_name = refreshed.get("full_name")
                    auth_state.is_admin = bool(refreshed.get("is_admin"))
                    auth_state.must_change_password = bool(refreshed.get("must_change_password"))
                else:
                    # Fallback: clear session so user can log in again
                    logout(st.session_state)
                    st.error("Wachtwoord aangepast, maar her-authenticatie faalde. Probeer opnieuw aan te melden.")
                    st.rerun()
                    return

                set_next_route(st.session_state, "Beveiligd")
                st.success("Wachtwoord aangepast. Je bent nu aangemeld.")
                st.rerun()

    render_material_card(
        "Opmerking",
        "Bij een eerste opstart wordt automatisch een initiële adminaccount aangemaakt. De admin moet het tijdelijke wachtwoord bij de eerste aanmelding wijzigen.",
    )
