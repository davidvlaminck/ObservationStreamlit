# Deploying with Supabase Postgres (Streamlit)

This project uses **SQLAlchemy Core** and reads the database connection from `DATABASE_URL`.

## Dependency management

- **Streamlit Cloud** uses `requirements.txt` for deployment. Only include runtime dependencies here (no test/dev tools).
- For **local development and testing**, use `requirements-dev.txt` (includes pytest, test tools, etc.).
- To install dev dependencies locally:
  ```bash
  pip install -r requirements-dev.txt
  ```
- To install only runtime dependencies (for production/Streamlit Cloud):
  ```bash
  pip install -r requirements.txt
  ```

The safest way to provide `DATABASE_URL` is via **Streamlit secrets**.

> Don’t commit passwords/keys to git. Treat anything pasted into chat/logs as compromised and rotate it.

---

## 1) Get the Supabase connection string (use the Session pooler)

In the Supabase project UI:
1. Click **Connect** in the **top bar**.
2. In the connection options, select **Pooler** and choose **Session** mode.
3. Copy the provided connection string/parameters.

Why pooler matters (practical):
- The **direct** database host like `db.<projectref>.supabase.co` can sometimes resolve to **IPv6-only** from certain networks.
- If your machine/network has **no IPv6 route**, you can get errors like:
  - `Network is unreachable` (even though your credentials are correct)
- The **pooler host** (from Connect → Pooler → Session) often works better across networks.

Recommended for production:
- Use the **pooler** connection string.
- Prefer **session mode** (good default for web apps).

The URL will look like:

```
postgresql+psycopg://USER:PASSWORD@HOST:PORT/DBNAME?sslmode=require
```

Notes:
- `sslmode=require` is commonly needed on hosted Postgres.
- Keep the URL private.

---

## 2) Install the Postgres driver

For production Postgres you need a driver. This repo uses:
- `psycopg[binary]` (psycopg v3)

This works well on Streamlit Cloud (newer Python versions) and locally.

---

## 3) Configure Streamlit secrets (local dev)

Create a local secrets file (do **not** commit it):

- Path: `.streamlit/secrets.toml`

Example:

```toml
DATABASE_URL = "postgresql+psycopg://USER:PASSWORD@HOST:PORT/DBNAME?sslmode=require"
```

Then run Streamlit as usual. The app will prefer, in order:
1. `st.secrets["DATABASE_URL"]`
2. environment variable `DATABASE_URL`
3. fallback SQLite DB in the repo root

---

## 4) Configure secrets in Streamlit Community Cloud

If you deploy via Streamlit Community Cloud:
1. Open your app settings
2. Add a secret named `DATABASE_URL`
3. Paste the Postgres URL

---

## 5) Migrations (recommended as of Phase 2)

Once you use a shared production DB, you should manage schema changes with migrations.

Planned approach:
- **Alembic** for migrations
- Keep tests using SQLite

(We’ll wire this in during Phase 2.)

---

## Troubleshooting

### “It looks like my app reset”
This usually means you’re pointing at a different DB URL than you think.

Check the effective DB configuration:
- Confirm `DATABASE_URL` is set in Streamlit secrets / environment
- Confirm you’re not accidentally using a local SQLite fallback

### SSL / connection failures
- Ensure `sslmode=require` is in the URL if Supabase requires it.
- Ensure you used the correct pooler host/port.
