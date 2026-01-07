"""CLI helper to create or reset the initial admin account.

Usage examples:
  python scripts/create_admin.py --email admin@example.com --password hunter2
  python scripts/create_admin.py --reset --email admin@example.com
"""
import argparse
import sys
import os

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import db
from app.auth import create_user, reset_password


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Create or reset admin user")
    p.add_argument("--email", required=True)
    p.add_argument("--password", required=False)
    p.add_argument("--reset", action="store_true", help="Reset password for existing user")
    args = p.parse_args(argv)

    db.init_db()
    eng = db.get_engine()
    with eng.connect() as conn:
        row = conn.execute(db.users.select().where(db.users.c.email == args.email)).mappings().first()
        if row:
            if args.reset:
                new_pw = reset_password(row['id'])
                print(f"Password reset for {args.email}. New temporary password: {new_pw}")
                return 0
            else:
                print(f"User {args.email} already exists. Use --reset to reset their password.")
                return 1
        # create user
        pw = args.password if args.password else None
        u = create_user(args.email, "Administrator", is_admin=True, created_by_id=None, temp_password=pw)
        print(f"Created admin {u['email']}. Temporary password: {u['temp_password']}")
        return 0


if __name__ == '__main__':
    raise SystemExit(main())

