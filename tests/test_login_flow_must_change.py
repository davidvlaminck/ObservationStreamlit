import importlib
import os
import sys

# ensure project root is on sys.path
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def reload_modules_with_dburl(db_url: str):
    os.environ["DATABASE_URL"] = db_url
    import app.db as db

    importlib.reload(db)
    import app.auth as auth

    importlib.reload(auth)
    return db, auth


def test_bootstrap_admin_must_change_password_can_be_cleared_and_persists(tmp_path):
    """Regression for reported bug:

    Fresh DB -> login with admin/admin -> must_change_password=True -> set new password ->
    logout -> new password must work and old password must NOT work (also after restart).

    This is the minimal core behavior; Streamlit UI should only reflect this state.
    """

    db_file = tmp_path / "fresh_bootstrap.db"
    db_url = f"sqlite:///{db_file}"
    db, auth = reload_modules_with_dburl(db_url)

    db.init_db()

    u = auth.authenticate("admin", "admin")
    assert u is not None
    assert u["must_change_password"] is True

    # user picks a new password
    auth.change_password(u["id"], "new-pass-1")

    # old password should be invalid immediately
    assert auth.authenticate("admin", "admin") is None
    assert auth.authenticate("admin", "new-pass-1") is not None

    # simulate restart
    db2, auth2 = reload_modules_with_dburl(db_url)
    db2.init_db()

    assert auth2.authenticate("admin", "admin") is None
    assert auth2.authenticate("admin", "new-pass-1") is not None
