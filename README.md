# ObservationStreamlit

Streamlit app developed in phases (see `spec/phases.md`).

## Phase 0 (current)
- App skeleton + configuration helpers
- Simple navigation (Home/Login/Protected)
- Protected area gated by session state (stub auth)
- UI direction: Streamlit + **streamlit-elements** (Material UI components)

> Phase 0 **does not implement real authentication** or a database yet.

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
