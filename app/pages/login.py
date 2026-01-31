from __future__ import annotations

import streamlit as st
import base64
from datetime import datetime, timedelta, timezone

from app.state import get_auth_state, logout, set_next_route, is_dev_mode
from app.ui_elements import render_material_card, redact_db_url
from app import db, auth
from app.auth import generate_url_token, check_url_token, get_url_tokens


def render() -> None:
    query_params = st.query_params
    token = query_params.get("token")
    auth_state = get_auth_state(st.session_state)
    # Guard: als token in URL en gebruiker is ingelogd, direct door naar beveiligd
    if token and auth_state.is_authenticated and not auth_state.must_change_password:
        set_next_route(st.session_state, "Beveiligd")
        st.rerun()

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

    # Check for token in URL
    query_params = st.query_params
    token = query_params.get("token")
    st.write(f"[DEBUG] Token uit URL: {token}")
    # Workaround: if token is present in query params but not in session, regenerate it for the current user
    if token and token not in get_url_tokens() and auth_state.is_authenticated:
        try:
            decoded_token = base64.urlsafe_b64decode(token.encode()).decode()
        except Exception:
            decoded_token = token
        # Regenerate and store token for current user
        get_url_tokens()[decoded_token] = {"user_id": auth_state.user_id, "expires": datetime.now(timezone.utc) + timedelta(hours=1)}
    if token:
        try:
            decoded_token = base64.urlsafe_b64decode(token.encode()).decode()
        except Exception:
            decoded_token = token
        st.write(f"[DEBUG] Decoded token: {decoded_token}")
        st.write(f"[DEBUG] URL_TOKENS: {get_url_tokens()}")
        user_id = check_url_token(decoded_token)
        st.write(f"[DEBUG] user_id from token: {user_id}")
        st.write(f"[DEBUG] Now (UTC): {datetime.now(timezone.utc)}")
        if decoded_token in get_url_tokens():
            st.write(f"[DEBUG] Token expiry: {get_url_tokens()[decoded_token]['expires']}")
        if user_id:
            # Fetch user info from DB
            from app.db import users
            eng = db.get_engine()
            with eng.connect() as conn:
                row = conn.execute(users.select().where(users.c.id == user_id)).mappings().first()
            if row:
                auth_state.is_authenticated = True
                auth_state.user_id = row["id"]
                auth_state.email = row["email"]
                auth_state.full_name = row.get("full_name")
                auth_state.is_admin = bool(row.get("is_admin"))
                auth_state.must_change_password = bool(row.get("must_change_password"))
                st.success(f"Je bent automatisch ingelogd via token. Geldig tot: {get_url_tokens().get(decoded_token, {}).get('expires', 'onbekend')}")
                set_next_route(st.session_state, "Beveiligd")
                st.rerun()
            else:
                st.error("Token is geldig, maar gebruiker bestaat niet meer.")
        else:
            st.error("Token is ongeldig of verlopen.")

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
        except Exception:
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
            # Genereer een token-URL en zet deze direct in de URL, rerun de app
            raw_token = str(generate_url_token(user["id"]))
            token = base64.urlsafe_b64encode(raw_token.encode()).decode()
            st.query_params = {"token": token}
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
                refreshed = auth.authenticate(auth_state.email or "", new_pw)
                if refreshed:
                    auth_state.is_authenticated = True
                    auth_state.user_id = refreshed["id"]
                    auth_state.email = refreshed["email"]
                    auth_state.full_name = refreshed.get("full_name")
                    auth_state.is_admin = bool(refreshed.get("is_admin"))
                    auth_state.must_change_password = bool(refreshed.get("must_change_password"))
                else:
                    logout(st.session_state)
                    st.error("Wachtwoord aangepast, maar her-authenticatie faalde. Probeer opnieuw aan te melden.")
                    st.rerun()
                    return
                set_next_route(st.session_state, "Beveiligd")

    render_material_card(
        "Opmerking",
        "Bij een eerste opstart wordt automatisch een initiële adminaccount aangemaakt. De admin moet het tijdelijke wachtwoord bij de eerste aanmelding wijzigen.",
    )
