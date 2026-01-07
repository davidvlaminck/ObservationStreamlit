from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
import secrets
import time

from app.db import get_engine, users, get_user_by_email, hash_password, verify_password


class AuthLocked(Exception):
    """Raised when an account is temporarily locked due to repeated failed attempts."""


# Simple in-memory login attempt tracker. For single-process deployments this is sufficient.
LOGIN_ATTEMPTS: dict[str, dict] = {}
MAX_ATTEMPTS = 5
WINDOW_SECONDS = 60
LOCK_SECONDS = 300


def _record_failed_attempt(email: str) -> None:
    now = time.time()
    entry = LOGIN_ATTEMPTS.get(email)
    if not entry:
        LOGIN_ATTEMPTS[email] = {"count": 1, "first": now, "locked_until": 0}
        return
    # if currently locked and lock expired, reset
    if entry.get("locked_until", 0) and now >= entry["locked_until"]:
        LOGIN_ATTEMPTS[email] = {"count": 1, "first": now, "locked_until": 0}
        return
    entry["count"] += 1
    # if within window and exceed max attempts, set locked_until
    if now - entry["first"] <= WINDOW_SECONDS and entry["count"] >= MAX_ATTEMPTS:
        entry["locked_until"] = now + LOCK_SECONDS


def _clear_attempts(email: str) -> None:
    if email in LOGIN_ATTEMPTS:
        del LOGIN_ATTEMPTS[email]


def _is_locked(email: str) -> bool:
    entry = LOGIN_ATTEMPTS.get(email)
    if not entry:
        return False
    locked_until = entry.get("locked_until", 0)
    if locked_until and time.time() < locked_until:
        return True
    # expired lock -> clear
    if locked_until and time.time() >= locked_until:
        del LOGIN_ATTEMPTS[email]
        return False
    return False


def authenticate(email: str, password: str) -> Optional[dict]:
    # simple lockout check
    if _is_locked(email):
        raise AuthLocked("Account temporarily locked due to repeated failed login attempts")

    engine = get_engine()
    with engine.connect() as conn:
        row = get_user_by_email(conn, email)
        if not row:
            # no such user
            return None
        if not verify_password(password, row["password_hash"]):
            _record_failed_attempt(email)
            return None
        # success: clear attempts
        _clear_attempts(email)
        # update last_login_at
        conn.execute(users.update().where(users.c.id == row["id"]).values(last_login_at=datetime.now(timezone.utc)))
        conn.commit()
        return dict(row)


def create_user(email: str, full_name: str, is_admin: bool = False, created_by_id: Optional[int] = None, temp_password: Optional[str] = None) -> dict:
    engine = get_engine()
    with engine.connect() as conn:
        # check for existing email
        existing = get_user_by_email(conn, email)
        if existing:
            raise ValueError("email_exists")

        pw = temp_password if temp_password is not None else secrets.token_urlsafe(10)
        pw_hash = hash_password(pw)
        ins = users.insert().values(
            email=email,
            password_hash=pw_hash,
            full_name=full_name,
            is_active=True,
            is_admin=is_admin,
            must_change_password=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            created_by_id=created_by_id,
        )
        res = conn.execute(ins)
        conn.commit()
        new_id = res.inserted_primary_key[0]
        return {"id": new_id, "email": email, "full_name": full_name, "temp_password": pw}


def reset_password(user_id: int) -> str:
    engine = get_engine()
    with engine.connect() as conn:
        temp = secrets.token_urlsafe(10)
        pw_hash = hash_password(temp)
        conn.execute(users.update().where(users.c.id == user_id).values(password_hash=pw_hash, must_change_password=True, updated_at=datetime.now(timezone.utc)))
        conn.commit()
        return temp


def change_password(user_id: int, new_password: str) -> None:
    engine = get_engine()
    with engine.connect() as conn:
        pw_hash = hash_password(new_password)
        conn.execute(users.update().where(users.c.id == user_id).values(password_hash=pw_hash, must_change_password=False, updated_at=datetime.now(timezone.utc)))
        conn.commit()
