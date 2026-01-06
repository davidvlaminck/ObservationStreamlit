# Development Phases (roadmap)

This document breaks the `spec.md` requirements into incremental phases. Each phase ends with a runnable/demoable slice of the app.

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
- **Phase 1 (auth):**
  - Unit tests: password hashing/verification; username/password validation; login/logout state transitions.
  - Optional integration tests: `users.username` uniqueness; user lookup by username.
- **Phase 2 (DB layer):**
  - Unit tests: DB URL/config parsing and “SQLite dev vs Postgres prod” configuration switching.
  - Integration tests: migrations apply cleanly from empty DB; schema matches expectations.
- **Phase 3 (queries/filters):**
  - Unit tests: filter validation and query builder parameterization (no SQL string concatenation).
  - Integration tests: representative queries return expected rows for seeded sample data.
- **Phase 4 (display):**
  - Unit tests: formatting helpers (if any); empty-state logic.
- **Phase 5 (hardening):**
  - Integration tests: performance guardrails (row limits/timeouts), error handling for DB unavailability.

> Note: Streamlit UI rendering tests are usually low ROI early; we’ll keep most logic behind testable functions and focus UI testing only on critical flows.

---

## Phase 0 — Foundations (skeleton + configuration)
**Goal:** The app runs locally and has a clear structure that supports subsequent phases.

**Scope**
- Streamlit app entrypoint and basic page layout.
- Navigation structure: unauthenticated (login) area vs authenticated area (stub).
- Configuration approach (local dev + production): environment variables and/or Streamlit secrets.
- Dependency manifest and minimal README.

**Deliverables**
- App starts via Streamlit without errors.
- Placeholder pages for login and a protected area.
- No secrets committed to source control.

**Acceptance Criteria**
- `streamlit run main.py` loads a UI without stack traces.
- Login page is visible; “protected” content is not accessible without auth state.

---

## Phase 1 — User authentication + session management (includes minimal DB for users)
**Goal:** Users can log in securely and remain authenticated via session state.

**Scope**
- Username/password login.
- Secure password hashing (salted hash) and verification.
- Session management in Streamlit (persist login during the session).
- Logout flow.
- **Manual account creation** only (registration UI deferred).
- **Minimal DB persistence for authentication** (just enough to store/validate users).

**DB portability note (SQLite dev vs Postgres prod)**
- Even though this phase only needs a small `users` table, implement it using the **same DB access approach planned for Phase 2** (recommended: **SQLAlchemy engine + parameter binding**, Core-first).
- This keeps the code portable: switching from `sqlite:///...` locally to `postgresql+psycopg://...` in production should be primarily a **configuration change** (DB URL/secrets), not a rewrite.

**Deliverables**
- Basic user schema/table (username + password hash + metadata).
- Minimal DB configuration for the users/auth store (e.g., SQLite in dev; Postgres compatible).
- Login form + logout control.
- Basic protected-page gating.
- Documented manual user creation workflow (script/SQL).

**Acceptance Criteria**
- Invalid credentials fail without revealing details.
- Valid credentials grant access to protected area.
- Logout removes access immediately.
- Passwords are never stored or logged in as plaintext.
- User accounts persist across app restarts (i.e., not in-memory only).

---

## Phase 2 — Database layer hardening + standardization (for all app data)
**Goal:** The app can connect to the chosen database reliably and reuse a single, robust DB layer across features.

**Scope**
- Standard DB configuration for dev/prod (e.g., SQLite locally, PostgreSQL in production) and credentials management.
- Central connection/engine creation and reuse across the whole app.
- Error handling for connection and query issues.
- Basic operational diagnostics.
- (Recommended) Introduce migrations (e.g., Alembic) once production DB support matters.

**ORM guidance**
- Prefer a **hybrid approach**:
  - Use **SQLAlchemy Core / parameterized SQL** by default (especially for analytics-style queries).
  - Add **SQLAlchemy ORM models** only where they simplify CRUD workflows and relationships.
- This provides most of the cross-database benefit (SQLite ↔ Postgres) without forcing all queries into ORM patterns.

**Deliverables**
- Single “DB connection” module/function used everywhere (including auth and data access).
- Clear DB URL/driver configuration for both SQLite and Postgres.
- User-friendly error message when DB is unreachable/misconfigured.
- (Optional) A simple “DB ok” diagnostic indicator.

**Acceptance Criteria**
- DB credentials are provided via environment variables/secrets.
- Switching from SQLite (dev) to Postgres (prod) does not require code changes beyond configuration.
- Misconfiguration/down DB results in a clear error instead of a crash.
- Connection reuse avoids reconnecting on every interaction where feasible.

---

## Phase 3 — Data fetching + filtering (safe queries)
**Goal:** Authenticated users can fetch real data and refine it with filters.

**Scope**
- Implement a first “core dataset” query.
- Filter UI to refine results (depends on schema; typically date range, categorical selects, text search).
- Parameterized queries / safe ORM patterns.
- Input validation.

**Deliverables**
- A data-access function that returns a DataFrame/list of rows.
- Filter widgets and wiring to the query.
- Pagination and/or row limits to protect performance.

**Acceptance Criteria**
- Filters correctly change the result set.
- Queries use parameter binding (no SQL string concatenation from user input).
- Typical queries return within the performance target (e.g., < 3 seconds) for normal filter ranges.

---

## Phase 4 — Data display (tables + charts)
**Goal:** Fetched data is presented clearly.

**Scope**
- Table view of results.
- At least one summarizing chart.
- Loading and empty states.

**Deliverables**
- User-friendly table (formatting, row counts, optional sorting).
- One chart appropriate to the dataset (trend, distribution, breakdown).
- Clear “no results” messaging.

**Acceptance Criteria**
- Users can interpret results without reading logs or raw SQL.
- Empty result sets are handled gracefully.
- UI remains responsive with imposed row limits/pagination.

---

## Phase 5 — Performance + security hardening (production readiness)
**Goal:** Meet non-functional requirements and prepare for deployment.

**Scope**
- Performance tuning: caching where safe, query optimization, indexes guidance, timeouts.
- Security hardening: input sanitization/validation, least-privileged DB user, avoid sensitive logging.
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

## Phase 6 — Future enhancements (optional)
**Goal:** Add features listed under “Future Phases” without destabilizing core functionality.

**Possible scope (pick as needed)**
- User self-registration and password recovery.
- Advanced visualization options.
- Third-party API integration with caching and rate limiting.

**Acceptance Criteria**
- New features don’t weaken authentication or expose data.
- Permissions/roles are introduced if needed before adding sensitive capabilities (e.g., exports/admin tools).
