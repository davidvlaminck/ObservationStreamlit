# Development Phases (roadmap)

This document breaks the `spec.md` requirements into incremental phases. Each phase ends with a runnable/demoable slice of the app.

Key themes from `spec.md` woven through the phases:
- **Streamlit + `streamlit-elements`**: Prefer Material UI components for key screens; keep a minimal fallback using standard Streamlit widgets.
- **Responsive UI (mobile/tablet)**: Treat narrow-viewport usability as a requirement, not a polish item.
- **Flemish UI**: User-facing labels/messages should be in **Dutch (Belgium)**.

---

## Testing strategy (in phases)
We’ll use two categories of automated tests:

- **Unit tests (fast, no DB):** pure functions (password hashing, input validation, auth/session-state transitions, query-building logic).
- **Integration tests (slower, uses DB):** verify Core schema constraints, migrations, and real queries against a real database.
  - Default integration DB in development: **SQLite in-memory**.
  - Production parity (optional later): run the same integration tests against **PostgreSQL** in CI.

**Phase-by-phase testing expectations**
- **Phase 0:**
  - A minimal “app imports” smoke test (import modules without side effects).
  - Optional: basic navigation smoke test (router/page registry returns expected pages).
- **Phase 1 (auth):**
  - Unit tests: password hashing/verification; username/password validation; login/logout state transitions.
  - Optional integration tests: `users.username` uniqueness; user lookup by username.
- **Phase 2 (DB layer):**
  - Unit tests: DB URL/config parsing and “SQLite dev vs Postgres prod” configuration switching.
  - Integration tests: schema creation/migrations apply cleanly from an empty DB.
- **Phase 3 (queries/filters):**
  - Unit tests: filter validation and query builder parameterization (no SQL string concatenation).
  - Integration tests: representative queries return expected rows for seeded sample data.
- **Phase 4 (display/UI):**
  - Unit tests: formatting helpers; empty-state logic.
  - Optional: snapshot-ish tests for “view model” mappers (convert DB rows to display-ready structures).
- **Phase 5 (data entry):**
  - Unit tests: input normalization/validation.
  - Integration tests: inserts/updates enforce constraints.
- **Phase 6 (hardening):**
  - Integration tests: performance guardrails (row limits/timeouts), error handling for DB unavailability.

> Note: Streamlit UI rendering tests are usually low ROI early; we’ll keep most logic behind testable functions and focus UI testing on critical flows.

---

## Phase 0 — Foundations (skeleton + responsive layout baseline)
**Goal:** The app starts cleanly, has a maintainable structure, and doesn’t assume a wide desktop screen.

**Scope**
- Streamlit app entrypoint and basic page layout.
- Navigation structure: unauthenticated (login) area vs authenticated area (stub).
- Establish an initial UI approach:
  - standard Streamlit layout as baseline
  - **introduce `streamlit-elements` in a small, low-risk way** (e.g., one card/header component) to validate the dependency
- Configuration approach (local dev + production): environment variables and/or Streamlit secrets.
- Dependency manifest and minimal README.

**Deliverables**
- App starts via Streamlit without errors.
- Placeholder pages for login and a protected area.
- No secrets committed to source control.

**Acceptance Criteria**
- `streamlit run main.py` loads a UI without stack traces.
- Login page is visible; “protected” content is not accessible without auth state.
- On a narrow viewport, content doesn’t require horizontal scrolling for primary flows.

---

## Phase 1 — User authentication + session management (minimal DB for users)
**Goal:** Users can log in securely and remain authenticated via session state.

**Scope**
- Username/password login (email used as username).
- Secure password hashing (salted hash) and verification.
- Session management in Streamlit (persist login during the session).
- Logout flow.
- **Admin-managed account creation** only (registration UI deferred). Admin creates accounts using a "New user" flow that generates a one-time temporary password shown to the admin for out-of-band delivery. `must_change_password` enforces password change on first login.
- Minimal DB persistence for authentication (just enough to store/validate users).
- UI for auth built with **standard Streamlit first**, then optionally enhanced with `streamlit-elements` components (e.g., nicer form layout).
- All user-facing strings for auth pages in **Flemish (Dutch, Belgium)**.

**DB portability note (SQLite dev vs Postgres prod)**
- Even though this phase only needs a small `users` table, implement it using the **same DB access approach planned for Phase 2** (recommended: **SQLAlchemy engine + parameter binding**, Core-first).
- This keeps the code portable: switching from `sqlite:///...` locally to `postgresql+psycopg://...` in production should be primarily a **configuration change** (DB URL/secrets), not a rewrite.

**Deliverables**
- Basic user schema/table (email + password hash + metadata).
- Minimal DB configuration for the users/auth store (e.g., SQLite in dev; Postgres compatible).
- Login form + logout control.
- Basic protected-page gating.
- Documented manual user creation workflow (admin "New user" flow) and a simple script/utility to create an initial admin account.
- When the app starts against an empty DB, the system should create an initial admin user automatically. The initial admin email/password are read from environment variables `INITIAL_ADMIN_EMAIL` and `INITIAL_ADMIN_PASSWORD` when set; otherwise the default credentials `admin` / `admin` will be used. The initial admin account is created with `must_change_password=true` so the administrator is forced to choose a new password on first login.

**Acceptance Criteria**
- Invalid credentials fail without revealing details.
- Valid credentials grant access to protected area.
- Logout removes access immediately.
- Passwords are never stored or logged as plaintext.
- User accounts persist across app restarts (i.e., not in-memory only).
- Login flow remains usable on mobile (touch-friendly spacing; no horizontal scroll).

---

## Phase 2 — Database layer hardening + standardization (for all app data)
**Goal:** The app can connect to the chosen database reliably and reuse a single, robust DB layer across features.

**Scope**
- Standard DB configuration for dev/prod (e.g., SQLite locally, PostgreSQL in production) and credentials management.
- Central connection/engine creation and reuse across the whole app.
- Error handling for connection and query issues.
- Basic operational diagnostics.
- (Recommended) Introduce migrations (e.g., Alembic) once production DB support matters.

**Important decision**: The project will not add SMTP/email invite or password-reset delivery in Phase 2 — the admin-temp-password (manual) workflow will remain the supported user onboarding and reset method initially.

**SQLAlchemy approach (Core-first)**
- Use **SQLAlchemy Core** (Tables, columns, `select()`, parameter binding) for schema and queries.
- Use **Alembic** for migrations.
- Keep the option open to introduce ORM models later only if/when CRUD complexity warrants it.

**Deliverables**
- Single “DB connection” module/function used everywhere (including auth and data access).
- Clear DB URL/driver configuration for both SQLite and Postgres.
- Error handling for connection and query issues.
- (Optional) A simple “DB ok” diagnostic indicator.

**Acceptance Criteria**
- DB credentials are provided via environment variables/secrets.
- Switching from SQLite (dev) to Postgres (prod) does not require code changes beyond configuration.
- Misconfiguration/down DB results in a clear error instead of a crash.
- Connection reuse avoids reconnecting on every interaction where feasible.

---

## Phase 3 — Data fetching + filtering (safe queries + mobile-friendly filters)
**Goal:** Authenticated users can fetch real data and refine it with filters.

**Scope**
- Implement a first “core dataset” query.
- Filter UI to refine results (depends on schema; typically date range, categorical selects, text search).
- Parameterized queries (Core) and safe input validation.
- Define a mobile-friendly filter layout:
  - avoid 3+ columns of controls
  - prefer stacked controls, accordions, or a “Filters” panel/drawer pattern (where feasible)
- Begin using `streamlit-elements` for key interactive UI areas where it improves usability.

**Deliverables**
- A data-access function that returns a DataFrame/list of rows.
- Filter widgets and wiring to the query.
- Pagination and/or row limits to protect performance.

**Acceptance Criteria**
- Filters correctly change the result set.
- Queries use parameter binding (no SQL string concatenation from user input).
- Typical queries return within the performance target (e.g., < 3 seconds) for normal filter ranges.
- Filter controls are usable on a narrow viewport without requiring horizontal scrolling.

---

## Phase 4 — Data display (tables + charts + responsive results)
**Goal:** Fetched data is presented clearly on desktop and smaller screens.

**Scope**
- Table view of results.
- At least one summarizing chart.
- Loading and empty states.
- Responsive UI behaviors:
  - small screens: pagination and/or a simplified “card list” view when tables become unreadable
  - charts: responsive containers; avoid tiny unreadable labels
- Apply Flemish UI strings across the data display.

**Deliverables**
- User-friendly table (formatting, row counts, optional sorting).
- One chart appropriate to the dataset (trend, distribution, breakdown).
- Clear “no results” messaging.

**Acceptance Criteria**
- Users can interpret results without reading logs or raw SQL.
- Empty result sets are handled gracefully.
- UI remains responsive with imposed row limits/pagination.
- Results remain readable on mobile/tablet (reasonable fallbacks; no “impossible to tap/scroll” views).

---

## Phase 5 — Data entry (fast tablet/mobile workflow; optional voice input exploration)
**Goal:** Users can enter new data quickly with minimal taps/clicks on tablet/mobile.

**Scope**
- Fast data entry UI:
  - short forms with sensible defaults
  - large touch targets
  - minimal navigation steps
- Data validation and friendly inline errors (Flemish).
- Optional spike: investigate voice input feasibility (depends on hosting/device/browser constraints).
  - If feasible, prototype a small “dictation to text” → “parse” workflow behind a feature toggle.

**Deliverables**
- One end-to-end “create new record” flow.
- Validation rules + error messages.
- Documentation of what’s feasible for voice input in the chosen deployment environment.

**Acceptance Criteria**
- Creating a record is possible in a small number of interactions.
- Validation errors are clear and actionable.
- Writes are safely parameterized and respect DB constraints.

---

## Phase 6 — Performance + security hardening (production readiness)
**Goal:** Meet non-functional requirements and prepare for deployment.

**Scope**
- Performance tuning: caching where safe, query optimization, indexes guidance, timeouts.
- Security hardening: input validation, least-privileged DB user, avoid sensitive logging.
- Deployment guidance: HTTPS termination and environment/secrets configuration.

**Deliverables**
- Caching strategy for repeated queries/reference data.
- Query timeouts and sensible limits.
- A short security checklist in the repo.
- Deployment notes (how HTTPS is handled in your chosen hosting).

**Acceptance Criteria**
- Typical data loads meet the target time (e.g., under 3 seconds).
- SQL injection risks are mitigated by parameterization and validation.
- Clear path to HTTPS usage in deployment (even if provided by a reverse proxy or platform).

---

## Phase 7 — Future enhancements (optional)
**Goal:** Add features listed under “Future Phases” without destabilizing core functionality.

**Possible scope (pick as needed)**
- User self-registration and password recovery.
- Advanced visualization options.
- Integration with third-party APIs for enhanced functionality.

**Acceptance Criteria**
- New features don’t weaken authentication or expose data.
- Permissions/roles are introduced if needed before adding sensitive capabilities (e.g., exports/admin tools).
