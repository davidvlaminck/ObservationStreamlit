# ObservationStreamlit

Streamlit app developed in phases (see `spec/phases.md`).

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

## Current status (Phase 1 foundation)
- App skeleton + configuration helpers
- Simple navigation (Home/Login/Protected)
- **Real authentication + database (SQLite via SQLAlchemy Core)**
- Admin bootstrap (initial `admin/admin` with forced password change)
- Admin → Users page for creating users and setting temporary passwords (no email/SMTP)
- UI direction: Streamlit + **streamlit-elements** (Material UI components)

> Earlier in the project, “Phase 0” referred to a stub-only version (no DB/auth). The current codebase has moved beyond that.

---

## Production database (Supabase Postgres)

This app can run on SQLite (local/tests) and Postgres (production). For Supabase setup, see:
- `docs/DEPLOY_SUPABASE.md`

Supabase UI hint: in the project dashboard, click **Connect** in the top bar and select **Pooler → Session** to get the correct connection string.

**Important:** put your `DATABASE_URL` in Streamlit secrets (local `.streamlit/secrets.toml` and/or Streamlit Cloud secrets). Do not commit credentials.

---

## Setup (using uv)
You said you normally do:

```bash
pip install uv
uv pip install ...
```

That works fine here.

### 1) Create/activate a local venv
If you already use `.venv/`, keep using it:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies with uv

```bash
uv pip install -r requirements-dev.txt  # for dev/test
uv pip install -r requirements.txt      # for prod/Streamlit Cloud
```

---

## Secrets and configuration

- **Never commit secrets!**
- Local: put your `DATABASE_URL` in `.streamlit/secrets.toml` (see example in that file).
- On Streamlit Cloud: add the same key in the app’s secrets UI.
- The password should not be wrapped in brackets and must be URL-encoded if it contains special characters.

---

## Troubleshooting

- If you see `ModuleNotFoundError: No module named 'psycopg2'`, ensure `psycopg[binary]` is in your requirements file.
- If you see database connection errors, double-check your `DATABASE_URL` and network access.
- If you see `StreamlitAPIException` about query params, ensure you are only using the new `st.query_params` API (not experimental).
- If you see `.idea/` or `.venv/` in your git changes, ensure they are in `.gitignore`.

---

## Requirements files

- `requirements.txt`: runtime dependencies only (for production/Streamlit Cloud)
- `requirements-dev.txt`: superset of `requirements.txt` + dev/test tools (pytest, mypy, alembic, etc.)
- Keep these in sync and remove unused packages regularly.

---

## Running tests

- Run all tests with:
  ```bash
  pytest
  ```
- Add new tests in the `tests/` directory. Use fixtures for DB setup/teardown.

---

## Deployment

- For Streamlit Cloud, push to GitHub and connect the repo.
- Add your secrets in the Streamlit Cloud UI.
- The app will auto-deploy on push.

---

## Security notes

- Passwords are hashed with PBKDF2.
- No email-based password reset (admin sets temp passwords).
- All secrets must be kept out of version control.

---

For more details, see the `spec/` and `docs/` directories.
