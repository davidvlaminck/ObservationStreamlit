from app.state import get_auth_state, logout


def test_logout_clears_auth_state():
    session = {}
    auth = get_auth_state(session)
    auth.is_authenticated = True
    auth.user_id = 123
    auth.email = "admin"
    auth.is_admin = True
    auth.must_change_password = False

    logout(session)

    auth2 = get_auth_state(session)
    assert auth2.is_authenticated is False
    assert auth2.user_id is None
    assert auth2.email is None
    assert auth2.is_admin is False
    assert auth2.must_change_password is False

