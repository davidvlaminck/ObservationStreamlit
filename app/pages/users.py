from __future__ import annotations

import streamlit as st
from app.state import get_auth_state
from app.db import get_engine, users
from app.auth import create_user, reset_password
from html import escape
from app.ui_elements import elements_available


def _render_copyable_password(pw: str, key: str) -> None:
    """Render a small UI showing the password and a copy-to-clipboard control.

    Prefer streamlit-elements for consistent MUI styling if available, but keep a small
    HTML snippet to perform the actual clipboard write for compatibility.
    """
    safe_pw = escape(pw)

    if elements_available():
        # Render a simple MUI row with an outlined text field and a contained button for visuals
        try:
            from streamlit_elements import elements, mui

            with elements(f"pw_row_{key}"):
                # Text field (read-only visual)
                mui.TextField(sx={"mr": 1}, value=safe_pw, size="small", variant="outlined", InputProps={"readOnly": True})
                # Button (visual only) — clipboard handled by the small HTML snippet below
                mui.Button("Kopieer", variant="contained")
        except Exception:
            # If anything goes wrong with streamlit-elements, fall back to plain HTML snippet
            st.write(f"{safe_pw}")
            st.components.v1.html(
                f"<div><input id='pw_{key}' value='{safe_pw}' readonly style='width:200px;padding:6px' /> <button onclick=\"navigator.clipboard.writeText(document.getElementById('pw_{key}').value)\">Kopieer</button></div>",
                height=40,
            )
            return

        # Add a tiny HTML snippet to perform the copy action (works across browsers)
        copy_html = f"""
<div>
  <button id='copy_btn_{key}' style='display:none' onclick="navigator.clipboard.writeText('{safe_pw}')">Kopieer</button>
  <script>
    // find the MUI button rendered by streamlit-elements and attach a click handler that triggers the hidden button
    (function() {{
      setTimeout(function() {{
        try {{
          const btns = document.querySelectorAll('button');
          for (let b of btns) {{
            if (b.textContent && b.textContent.trim() === 'Kopieer') {{
              b.addEventListener('click', function() {{
                navigator.clipboard.writeText('{safe_pw}');
              }});
              break;
            }}
          }}
        }} catch (e) {{ /* ignore */ }}
      }}, 50);
    }})();
  </script>
</div>
"""
        st.components.v1.html(copy_html, height=40)
        return

    # Fallback: plain HTML copy widget
    html = f"""
<div>
  <input id='pw_{key}' value='{safe_pw}' readonly style='width:200px;padding:6px' />
  <button onclick="navigator.clipboard.writeText(document.getElementById('pw_{key}').value)">Kopieer</button>
</div>
"""
    st.components.v1.html(html, height=40)


def render() -> None:
    auth_state = get_auth_state(st.session_state)
    if not auth_state.is_authenticated or not auth_state.is_admin:
        st.error("Alleen voor admins")
        return

    st.title("Admin: Gebruikers")

    with st.expander("Nieuwe gebruiker aanmaken"):
        email = st.text_input("E-mail (wordt gebruikt als gebruikersnaam)")
        full_name = st.text_input("Volledige naam")
        is_admin = st.checkbox("Is admin", value=False)
        if st.button("Gebruiker aanmaken"):
            if not email or not full_name:
                st.error("E-mail en volledige naam zijn verplicht")
            else:
                try:
                    u = create_user(email.strip(), full_name.strip(), is_admin=is_admin, created_by_id=auth_state.user_id)
                except ValueError as e:
                    if str(e) == "email_exists":
                        st.error("Er bestaat al een gebruiker met dit e-mailadres.")
                    else:
                        st.error(str(e))
                else:
                    st.success(f"Gebruiker aangemaakt: {u['email']}")
                    st.info("Tijdelijk wachtwoord (kopieer en geef door aan de gebruiker):")
                    _render_copyable_password(u["temp_password"], key=f"new_{u['id']}")

    st.write("---")
    st.header("Bestaande gebruikers")
    eng = get_engine()
    with eng.connect() as conn:
        rows = conn.execute(users.select().order_by(users.c.id)).mappings().all()
        for r in rows:
            cols = st.columns([3, 1, 1])
            cols[0].text(f"{r['email']} — {r['full_name']}")
            if cols[1].button("Reset\npw", key=f"reset_{r['id']}"):
                temp = reset_password(r["id"])
                st.info("Nieuw tijdelijk wachtwoord (kopieer nu):")
                _render_copyable_password(temp, key=f"reset_{r['id']}")
            if cols[2].button("Admin\naan/uit", key=f"toggle_{r['id']}"):
                conn.execute(users.update().where(users.c.id == r["id"]).values(is_admin=not r["is_admin"]))
                conn.commit()
                st.rerun()
