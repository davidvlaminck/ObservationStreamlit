import importlib
import os
import sys
from pathlib import Path

# ensure project root is on sys.path
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def test_default_sqlite_url_anchored_to_repo_root(monkeypatch):
    """The default DB should be stable even if the working directory changes.

    This test must be hermetic: local developer Streamlit secrets (e.g. a
    `.streamlit/secrets.toml` with DATABASE_URL) should not influence unit tests.
    """
    monkeypatch.setenv("IGNORE_STREAMLIT_SECRETS", "1")
    monkeypatch.delenv("DATABASE_URL", raising=False)

    import app.db as db
    importlib.reload(db)

    # should point at <repo_root>/observations.db
    repo_root = Path(ROOT).resolve()
    expected = f"sqlite:///{(repo_root / 'observations.db').resolve()}"
    assert db.DB_URL == expected


def test_password_change_persists_across_module_reload(tmp_path, monkeypatch):
    db_file = tmp_path / "persist.db"
    db_url = f"sqlite:///{db_file}"
    monkeypatch.setenv("DATABASE_URL", db_url)

    import app.db as db
    import app.auth as auth
    importlib.reload(db)
    importlib.reload(auth)

    db.init_db()

    # get admin
    eng = db.get_engine()
    with eng.connect() as conn:
        admin = conn.execute(db.users.select().where(db.users.c.email == "admin")).mappings().first()

    # set a known password
    auth.change_password(admin["id"], "pw-before-reload")
    assert auth.authenticate("admin", "pw-before-reload") is not None

    # simulate restart
    importlib.reload(db)
    importlib.reload(auth)

    assert auth.authenticate("admin", "pw-before-reload") is not None
