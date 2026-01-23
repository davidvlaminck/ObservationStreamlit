from __future__ import annotations

import os
from typing import Optional
import hashlib
import base64
import hmac
from pathlib import Path

from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    MetaData,
    create_engine,
    select,
    Date,
    Text,
    ForeignKey,
)
from sqlalchemy.engine import Engine
from datetime import datetime, timezone


def _default_sqlite_url() -> str:
    """Return a stable default SQLite URL.

    Using a relative URL like `sqlite:///./observations.db` depends on the process CWD.
    Streamlit can be launched from different working directories (IDE, service, etc.),
    which would silently create/use a different DB file and look like data "reset".

    We anchor the default DB to the repository root (one level above `app/`).
    """

    repo_root = Path(__file__).resolve().parents[1]
    db_path = (repo_root / "observations.db").resolve()
    return f"sqlite:///{db_path}"


def _get_database_url_from_streamlit_secrets() -> Optional[str]:
    """Try to read DATABASE_URL from Streamlit secrets.

    This is intended for actual Streamlit runs. For hermetic unit tests / CLI tools,
    you can disable secrets resolution by setting:

    - IGNORE_STREAMLIT_SECRETS=1
    """

    if os.environ.get("IGNORE_STREAMLIT_SECRETS", "").strip() in {"1", "true", "True"}:
        return None

    try:
        import streamlit as st  # type: ignore

        value = st.secrets.get("DATABASE_URL")
        if value:
            return str(value).strip() or None
    except Exception:
        return None
    return None


DB_URL = (
    os.environ.get("DATABASE_URL")
    or _get_database_url_from_streamlit_secrets()
    or _default_sqlite_url()
)

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, unique=True, nullable=False),
    Column("password_hash", String, nullable=False),
    Column("full_name", String, nullable=False),
    Column("is_active", Boolean, default=True),
    Column("is_admin", Boolean, default=False),
    Column("must_change_password", Boolean, default=True),
    Column("created_at", DateTime, default=lambda: datetime.now(timezone.utc)),
    Column("updated_at", DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)),
    Column("last_login_at", DateTime, nullable=True),
    Column("created_by_id", Integer, ForeignKey("users.id"), nullable=True),
)

school_years = Table(
    "school_years",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, unique=True),
    Column("start_year", Integer),
    Column("end_year", Integer),
)

persons = Table(
    "persons",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("school_year_id", Integer, ForeignKey("school_years.id"), nullable=False),
    Column("first_name", String, nullable=False),
    Column("last_name", String, nullable=False),
    Column("full_name", String, nullable=False),
    Column("external_id", String, nullable=True),
)

categories = Table(
    "categories",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("key", String, unique=True),
    Column("label", String),
    Column("description", Text),
    Column("parent_id", Integer, ForeignKey("categories.id")),
    Column("display_order", Integer),
    Column("is_active", Boolean, default=True),
)

observations = Table(
    "observations",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("person_id", Integer, ForeignKey("persons.id"), nullable=False),
    Column("category_id", Integer, ForeignKey("categories.id"), nullable=False),
    Column("observed_at", Date, nullable=False),
    Column("school_year_id", Integer, ForeignKey("school_years.id"), nullable=False),
    Column("score", Integer, nullable=True),
    Column("comment", Text, nullable=True),
    Column("created_at", DateTime, default=lambda: datetime.now(timezone.utc)),
    Column("updated_at", DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)),
)

login_tokens = Table(
    "login_tokens",
    metadata,
    Column("token", String, primary_key=True),
    Column("user_id", Integer, nullable=False),
    Column("expires_at", DateTime, nullable=False),
    Column("created_at", DateTime, nullable=False),
)

_engine: Optional[Engine] = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {})
    return _engine


def _pbkdf2_hash(password: str, iterations: int = 120_000) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${base64.b64encode(salt).decode()}${base64.b64encode(dk).decode()}"


def _pbkdf2_verify(password: str, stored: str) -> bool:
    try:
        algo, iterations_s, salt_b64, dk_b64 = stored.split("$")
        iterations = int(iterations_s)
        salt = base64.b64decode(salt_b64)
        dk_stored = base64.b64decode(dk_b64)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(dk, dk_stored)
    except Exception:
        return False


def init_db() -> None:
    """Create tables if they do not exist and bootstrap an initial admin if DB is empty."""
    engine = get_engine()
    metadata.create_all(engine)

    # bootstrap admin if no users exist
    with engine.connect() as conn:
        sel = select(users.c.id).limit(1)
        r = conn.execute(sel).first()
        if r is None:
            # no users exist; create initial admin
            initial_email = os.environ.get("INITIAL_ADMIN_EMAIL", "admin")
            initial_password = os.environ.get("INITIAL_ADMIN_PASSWORD", "admin")
            pw_hash = _pbkdf2_hash(initial_password)
            ins = users.insert().values(
                email=initial_email,
                password_hash=pw_hash,
                full_name="Administrator",
                is_active=True,
                is_admin=True,
                must_change_password=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            conn.execute(ins)
            conn.commit()


def get_user_by_email(conn, email: str):
    sel = select(users).where(users.c.email == email)
    return conn.execute(sel).mappings().first()


def verify_password(candidate: str, password_hash: str) -> bool:
    return _pbkdf2_verify(candidate, password_hash)


def hash_password(password: str) -> str:
    return _pbkdf2_hash(password)
