import importlib
import os
import sys

# ensure project root is on sys.path
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest


def reload_db(db_url):
    os.environ['DATABASE_URL'] = db_url
    import app.db as db
    importlib.reload(db)
    return db


@pytest.mark.integration
def test_db_init_creates_schema(tmp_path):
    db_file = tmp_path / "integ.db"
    db_url = f"sqlite:///{db_file}"
    db = reload_db(db_url)
    db.init_db()
    eng = db.get_engine()
    from sqlalchemy import inspect

    inspector = inspect(eng)
    names = inspector.get_table_names()
    assert 'users' in names
    assert 'observations' in names


@pytest.mark.integration
@pytest.mark.skip(reason="Excel export not yet implemented; placeholder for future integration test")
def test_export_creates_xlsx(tmp_path):
    # Placeholder: when export is implemented, this test will call the export function and verify the XLSX file
    pass


@pytest.mark.integration
@pytest.mark.skip(reason="Alembic migrations not configured yet; placeholder")
def test_migrations_apply():
    # Placeholder for a test that applies Alembic migrations against a test DB
    pass
