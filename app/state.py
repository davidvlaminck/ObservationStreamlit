from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


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


def get_auth_state(session_state: dict) -> AuthState:
    state = session_state.get(AUTH_STATE_KEY)
    if isinstance(state, AuthState):
        return state
    state = AuthState(is_authenticated=False)
    session_state[AUTH_STATE_KEY] = state
    return state


def logout(session_state: dict) -> None:
    session_state[AUTH_STATE_KEY] = AuthState(is_authenticated=False)
