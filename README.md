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
pip install uv
uv pip install -r requirements.txt
```

---

## Run the app

```bash
APP_ENV=prod streamlit run main.py
```

Then open the URL Streamlit prints (usually `http://localhost:8501`).

---

## Admin bootstrap & account management

On first startup (when the database has no users) the app will automatically create an initial administrator account. By default the account is created with the email `admin` and password `admin` and the account will be marked `must_change_password=true` so the admin is forced to pick a new password on first login.

You can override the default initial admin credentials by setting the environment variables `INITIAL_ADMIN_EMAIL` and `INITIAL_ADMIN_PASSWORD` before first run. Example:

```bash
export INITIAL_ADMIN_EMAIL=you@example.com
export INITIAL_ADMIN_PASSWORD=some-temporary-password
streamlit run main.py
```

Alternatively you can use the included CLI helper to create or reset the admin without starting the app (useful for headless servers):

```bash
python scripts/create_admin.py --email admin@example.com --password temporarypw
# or to reset the existing admin's password:
python scripts/create_admin.py --email admin@example.com --reset
```

When the admin creates or resets a user's temporary password in the Admin → Users page, the temporary password is displayed once and there is a convenient Copy button to copy it to the clipboard. The app does not send emails — the admin is responsible for communicating the temporary password to the user out-of-band.

---

## Database location (avoiding accidental resets)

By default, the app uses a local SQLite database file named `observations.db` **in the repository root**.

Why this matters: a relative SQLite URL like `sqlite:///./observations.db` depends on the process working directory. If you start Streamlit from a different folder (IDE run config, service, etc.), it can silently create a different DB file and it may look like your users/passwords were “reset”.

To explicitly control the DB, set `DATABASE_URL`, for example:

```bash
export DATABASE_URL=sqlite:////home/davidlinux/PycharmProjects/ObservationStreamlit/observations.db
streamlit run main.py
```

---

## Database migraties (Alembic)

Deze app gebruikt Alembic voor database migraties. Dit maakt het mogelijk om je schema future-proof te beheren, zowel lokaal als op Supabase/Postgres.

### Migratie uitvoeren (lokaal of productie)
1. Zorg dat je `DATABASE_URL` correct staat (in `.streamlit/secrets.toml` of als environment variable).
2. Genereer een nieuwe migratie op basis van je model:
   ```bash
   alembic revision --autogenerate -m "Jouw migratiebeschrijving"
   ```
3. Voer de migratie uit:
   ```bash
   alembic upgrade head
   ```

### Migratie recovery & rollback

#### Rollback migratie
Wil je een migratie terugdraaien (rollback), gebruik:
```bash
alembic downgrade -1
```
Of naar een specifieke revision:
```bash
alembic downgrade <revision_id>
```

#### Backup maken vóór migratie
Voor Supabase/Postgres:
- Maak een export via het Supabase dashboard (of via `pg_dump`):
  ```bash
  pg_dump --dbname=<DATABASE_URL> --file=backup.sql
  ```
- Herstel met:
  ```bash
  psql --dbname=<DATABASE_URL> --file=backup.sql
  ```

#### Bij mislukte migratie
- Controleer je migratiebestand en database status.
- Herstel eventueel met een backup.
- Voer een rollback uit en probeer de migratie opnieuw.
- Check of je `DATABASE_URL` en rechten correct zijn.

Meer info: zie Alembic docs en Supabase backup handleiding.

### Best practices
- Gebruik altijd de pooler connection string van Supabase.
- Test migraties eerst lokaal (SQLite) voordat je ze op productie draait.
- Commit alleen migratiebestanden, nooit je secrets.
- Bij schemawijzigingen: maak een nieuwe Alembic migration en voer deze uit vóór je de app update.

### Troubleshooting
- Foutmelding `Tenant or user not found`: check je `DATABASE_URL` en credentials.
- Foutmelding `No changes detected`: je model en database zijn al in sync.
- Foutmelding over permissions: controleer of je Supabase user voldoende rechten heeft.

Meer info: zie `docs/DEPLOY_SUPABASE.md` voor Supabase-setup en connection string tips.

---

## Testing

Run the unit tests with pytest:

```bash
pytest -q
```

---

## Notes
- If `streamlit-elements` is installed, some UI will render using Material UI widgets.
- If it is not installed, the app falls back to standard Streamlit widgets.

---

## Specs
- `spec/spec.md`  overall requirements
- `spec/phases.md`  development roadmap
- `spec/data_model.md`  schema draft (fill this in before Phase 2/3)

---

## Belangrijke beperking: login is niet persistent

Streamlit session state is alleen geldig zolang het tabblad open is en de app actief blijft. Zodra je de pagina refresht, het tabblad sluit, of de server herstart, ben je uitgelogd. Ook na enkele minuten inactiviteit kan de session state verloren gaan.

**Oplossingen voor productie:**
- Gebruik een externe authenticatieprovider (OAuth, JWT, Auth0, Firebase, etc.) die persistentie biedt via cookies/tokens.
- Bouw een eigen backend die een JWT of session-cookie zet en bij elke page-load controleert.
- Voor dev/test kun je een tijdelijke URL-token gebruiken, maar dit is niet veilig voor productie.

Meer info: zie de Streamlit docs over session state en authenticatie.

## Veilige login-token via HTTPOnly cookie (backend API)

Deze app bevat een minimal backend-auth API (`scripts/auth_api.py`) die login-tokens veilig in een HTTPOnly cookie zet. Dit voorkomt dat tokens uitlekken via JavaScript of URL's.

**Hoe werkt het?**
- Start de backend: `uvicorn scripts.auth_api:app --reload`
- Streamlit frontend doet login via POST `/login` (email, password)
- Backend zet een HTTPOnly cookie met een login-token (8 uur geldig)
- Frontend checkt login-status via GET `/session`
- Bij logout: POST `/logout` wist de cookie

**Let op:**
- In deze demo worden tokens in-memory opgeslagen. Gebruik in productie een database of Redis.
- Zet `secure=True` in `set_cookie` voor productie (alleen HTTPS).
- Je kunt de backend uitbreiden met echte gebruikersauthenticatie en database-integratie.

Meer info: zie `scripts/auth_api.py` voor de API-endpoints.
