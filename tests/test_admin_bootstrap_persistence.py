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


def test_bootstrap_admin_password_changes_and_old_default_stops_working(tmp_path):
    """Repro for: fresh DB -> login as admin/admin -> change password -> logout ->
    old password should NOT work anymore.

    This matches the Streamlit flow but runs purely at the auth/db layer.
    """

    db_file = tmp_path / "fresh.db"
    db_url = f"sqlite:///{db_file}"
    db, auth = reload_modules_with_dburl(db_url)

    # fresh DB -> bootstrap admin/admin
    db.init_db()

    # authenticate using default credentials
    u = auth.authenticate("admin", "admin")
    assert u is not None
    assert u["must_change_password"] is True

    # user changes password
    auth.change_password(u["id"], "newpass1")

    # simulate logout and new login (same process)
    assert auth.authenticate("admin", "admin") is None
    assert auth.authenticate("admin", "newpass1") is not None

    # simulate app restart and login again
    db2, auth2 = reload_modules_with_dburl(db_url)
    db2.init_db()

    assert auth2.authenticate("admin", "admin") is None
    assert auth2.authenticate("admin", "newpass1") is not None

