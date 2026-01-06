from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AuthState:
    """Minimal authentication/session state.

    Phase 0: just a boolean gate for protected content.
    Phase 1: replace with real login + user identity.
    """

    is_authenticated: bool = False


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

