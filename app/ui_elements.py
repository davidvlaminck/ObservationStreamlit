from __future__ import annotations

"""Optional UI helpers built on streamlit-elements.

We keep these isolated so the rest of the app can still run with plain Streamlit
components if streamlit-elements isn't installed.

This module also contains small helpers for safe diagnostics output.
"""

from typing import Callable

import streamlit as st


def redact_db_url(url: str) -> str:
    """Redact credentials in a DB URL for safe display."""

    try:
        from sqlalchemy.engine import make_url

        u = make_url(url)
        safe = u._replace(password="***")
        return str(safe)
    except Exception:
        # Conservative fallback
        if ":" in url and "@" in url:
            prefix, rest = url.split(":", 1)
            if "@" in rest:
                _, after = rest.split("@", 1)
                return prefix + ":***@" + after
        return "<redacted>"


def elements_available() -> bool:
    try:
        import streamlit_elements  # noqa: F401

        return True
    except ModuleNotFoundError:
        return False


def render_material_card(title: str, body: str, *, action_label: str | None = None, on_action: Callable[[], None] | None = None) -> None:
    """Render a simple info card.

    If streamlit-elements is installed, render via MUI.
    Otherwise, fall back to Streamlit primitives.
    """

    if not elements_available():
        st.subheader(title)
        st.write(body)
        if action_label and on_action:
            if st.button(action_label):
                on_action()
        return

    from streamlit_elements import elements, mui

    with elements(f"card_{title}"):
        children = [
            mui.Typography(title, variant="h6"),
            mui.Typography(body, variant="body2", sx={"mt": 1}),
        ]
        if action_label and on_action:
            # streamlit-elements callbacks are JS-side; for Phase 0 we keep it simple.
            # We'll wire true Python callbacks in later phases if needed.
            children.append(mui.Button(action_label, variant="contained", sx={"mt": 2}))

        mui.Card(mui.CardContent(*children), sx={"maxWidth": 650, "m": 1, "borderRadius": 3})
