from __future__ import annotations

import sys
from pathlib import Path


def _ensure_repo_on_syspath() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))


def _mask_database_url(url: str) -> str:
    """Return a redacted DB URL safe for printing.

    We deliberately avoid printing passwords/tokens into terminal output.
    """

    try:
        from sqlalchemy.engine import make_url

        u = make_url(url)
        safe = u._replace(password="***")
        return str(safe)
    except Exception:
        # Fallback: try to remove anything between ':' and '@' in userinfo
        if ":" in url and "@" in url:
            prefix, rest = url.split(":", 1)
            if "@" in rest:
                _, after = rest.split("@", 1)
                return prefix + ":***@" + after
        return "<redacted>"


def main() -> int:
    """Small DB connectivity smoke test.

    - Uses DATABASE_URL from environment if present.
    - Otherwise (when run under Streamlit) DATABASE_URL is read via app.db from st.secrets.
    - Prints DB dialect + a simple SELECT 1.

    This script does not create tables or mutate data.

    Security: this script never prints credentials.
    """

    _ensure_repo_on_syspath()

    from app import db

    url = db.DB_URL
    # Always redact credentials for safety.
    print(f"DATABASE_URL (effective): {_mask_database_url(url)}")

    eng = db.get_engine()
    print(f"SQLAlchemy dialect: {eng.dialect.name}")

    with eng.connect() as conn:
        value = conn.exec_driver_sql("SELECT 1").scalar_one()
        print(f"SELECT 1 => {value}")

    print("OK: connection succeeded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
