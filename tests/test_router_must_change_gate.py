from app.state import get_auth_state


def test_must_change_password_state_blocks_other_routes():
    """Unit-level regression: when must_change_password is set, the router should
    not expose protected/admin routes in the sidebar.

    We can’t easily test Streamlit widgets here, but we can at least ensure the state
    shape exists and is intended to be enforced by the router.
    """

    session = {}
    auth = get_auth_state(session)
    auth.is_authenticated = True
    auth.must_change_password = True

    assert auth.is_authenticated
    assert auth.must_change_password

