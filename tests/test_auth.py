import importlib
import os
import sys
import time

import pytest

# ensure project root is on sys.path
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def reload_modules_with_dburl(db_url: str):
    os.environ['DATABASE_URL'] = db_url
    # reload db and auth modules so they pick up the new DATABASE_URL
    import app.db as db
    importlib.reload(db)
    import app.auth as auth
    importlib.reload(auth)
    return db, auth


def test_create_auth_change_reset_flow(tmp_path):
    # Use a temporary sqlite file for the test
    db_file = tmp_path / "test.db"
    db_url = f"sqlite:///{db_file}"
    db, auth = reload_modules_with_dburl(db_url)

    # init DB should create initial admin
    db.init_db()
    eng = db.get_engine()
    with eng.connect() as conn:
        rows = conn.execute(db.users.select()).mappings().all()
        assert len(rows) == 1
        assert rows[0]['email'] in ('admin', os.environ.get('INITIAL_ADMIN_EMAIL', 'admin'))

    # create new user
    created = auth.create_user('tester@example.com', 'Tester', is_admin=False, created_by_id=rows[0]['id'])
    assert 'temp_password' in created

    # authenticate with temp password
    u = auth.authenticate('tester@example.com', created['temp_password'])
    assert u is not None and u['email'] == 'tester@example.com'

    # change password
    auth.change_password(u['id'], 'newpassword123')
    assert auth.authenticate('tester@example.com', 'newpassword123') is not None

    # reset password
    temp = auth.reset_password(u['id'])
    assert auth.authenticate('tester@example.com', temp) is not None


def test_duplicate_email_fails(tmp_path):
    db_file = tmp_path / "dup.db"
    db_url = f"sqlite:///{db_file}"
    db, auth = reload_modules_with_dburl(db_url)
    db.init_db()
    eng = db.get_engine()
    with eng.connect() as conn:
        admin = conn.execute(db.users.select()).mappings().first()
    # create first user
    created = auth.create_user('dup@example.com', 'Dup', created_by_id=admin['id'])
    assert 'temp_password' in created
    # creating again should raise ValueError
    with pytest.raises(ValueError):
        auth.create_user('dup@example.com', 'Dup2', created_by_id=admin['id'])


def test_bad_password_and_user_not_found(tmp_path):
    db_file = tmp_path / "bad.db"
    db_url = f"sqlite:///{db_file}"
    db, auth = reload_modules_with_dburl(db_url)
    db.init_db()

    # user not found
    assert auth.authenticate('noone@example.com', 'pw') is None

    # create user and test bad password
    eng = db.get_engine()
    with eng.connect() as conn:
        admin = conn.execute(db.users.select()).mappings().first()
    created = auth.create_user('bob2@example.com', 'Bob2', created_by_id=admin['id'])
    assert auth.authenticate('bob2@example.com', 'wrongpw') is None


def test_lockout_behavior(tmp_path):
    db_file = tmp_path / "lock.db"
    db_url = f"sqlite:///{db_file}"
    db, auth = reload_modules_with_dburl(db_url)
    db.init_db()

    eng = db.get_engine()
    with eng.connect() as conn:
        admin = conn.execute(db.users.select()).mappings().first()
    created = auth.create_user('lock@example.com', 'Lock', created_by_id=admin['id'])

    # trigger MAX_ATTEMPTS failures
    from app.auth import MAX_ATTEMPTS, LOCK_SECONDS, LOGIN_ATTEMPTS, AuthLocked

    for _ in range(MAX_ATTEMPTS):
        assert auth.authenticate('lock@example.com', 'bad') is None

    # now should be locked
    with pytest.raises(AuthLocked):
        auth.authenticate('lock@example.com', 'bad')

    # artificially expire lock for test
    LOGIN_ATTEMPTS['lock@example.com']['locked_until'] = time.time() - 1
    # now authentication should still be None for wrong password
    assert auth.authenticate('lock@example.com', 'stillbad') is None


if __name__ == '__main__':
    pytest.main([__file__])
