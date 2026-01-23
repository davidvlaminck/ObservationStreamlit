from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class AuthState:
    """Authentication/session state.

    Phase 0: minimal boolean gate.
    Phase 1: store authenticated user identity.
    """

    is_authenticated: bool = False
    user_id: Optional[int] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_admin: bool = False
    must_change_password: bool = False


AUTH_STATE_KEY = "auth_state"
ROUTE_OVERRIDE_KEY = "route_override"


def is_dev_mode() -> bool:
    """Return True when running in a development environment.

    We use this to show/hide diagnostic panels in the UI.
    """

    return (os.environ.get("APP_ENV", "dev") or "dev").strip().lower() == "dev"


def get_auth_state(session_state: dict) -> AuthState:
    state = session_state.get(AUTH_STATE_KEY)
    if isinstance(state, AuthState):
        return state
    state = AuthState(is_authenticated=False)
    session_state[AUTH_STATE_KEY] = state
    return state


def logout(session_state: dict) -> None:
    session_state[AUTH_STATE_KEY] = AuthState(is_authenticated=False)


def set_next_route(session_state: dict, route: str) -> None:
    """Request a one-time route change on the next render."""
    session_state[ROUTE_OVERRIDE_KEY] = route


def pop_next_route(session_state: dict) -> str | None:
    """Consume the one-time route override (if any)."""
    return session_state.pop(ROUTE_OVERRIDE_KEY, None)


def is_admin(session_state: dict) -> bool:
    state = get_auth_state(session_state)
    return bool(state.is_authenticated and state.is_admin)
