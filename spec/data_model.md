# Data model (draft)

Use this document to describe the data model *before* we commit to a specific implementation (SQLAlchemy Core vs ORM). The goal is clarity: tables/entities, fields, relationships, indexes, and the key queries the app needs.

> Tip: if you don’t know something yet, write `TBD` rather than guessing.

---

## 1) Goals and usage
- **Primary use-cases** (what users do in the app):
  - users will authenticate. After logging in, users can either enter new (or edit) data or view existing data.
  - when entering new data, the data will be observations. These will have a category and a timestamp (date).
  - the user will enter the data on a screen that displays all people of that specific school year.
  - for each observation per person, there will be a possibility to assign a score 1,2,3,4. It's also possible to have a "?" value or to leave the value empty.
  - for each observation, there will be a comment field (optional).
  - when viewing existing data, users can filter by date range (specific date till now) and category. The results will be displayed in a table sorted by observation date
- **Primary outputs**
  - tables with filters
- **Key filters** (these usually drive indexes):
  - date/time range: filtering on dates is essential, time is not relevant
  - categorical fields: the category of observation will be key in what data to display

---

## 2) Environments / portability
- Local dev DB: SQLite
- Production DB: PostgreSQL
- Portability constraints (features to avoid early because they’re DB-specific):
  - PostgreSQL-only JSON queries? FTS? timezone-heavy logic? `ILIKE`? upserts?
  - TBD

---

## 3) Entities / tables

This section describes the concrete entities derived from the goals in section 1 (users who authenticate, people grouped by schoolyear, observations with category, score and optional comment).

### `users`
**Purpose:** authenticate users and record who created/edited observations.

Columns:
- `id`: integer PK
- `email`: string (unique, required) — used as the username/login
- `password_hash`: string (required)
- `full_name`: string (required)
- `is_active`: boolean (default true)
- `is_admin`: boolean (default false) — toggles access to admin pages (Users, Categories, Class list)
- `must_change_password`: boolean (default true for accounts created by admin with temporary password)
- `created_at`: timestamp with timezone (store UTC)
- `updated_at`: timestamp with timezone
- `last_login_at`: timestamp with timezone (optional)
- `created_by_id`: FK -> `users.id` (optional) — who created the account (admin)

Indexes / constraints:
- unique index on `email`

Notes:
- The chosen workflow is admin-created accounts with a one-time temporary password. No email/SMS is sent by the app (no SMTP in Phase 2 as decided). The admin is responsible for communicating the temporary password out-of-band. `must_change_password` forces the user to pick a new password on first login.
- Passwords must be stored hashed using a secure algorithm (bcrypt/argon2/passlib). Do not store plaintext passwords.

---

### `school_years`
**Purpose:** group people by year; UI shows people for a selected schoolyear.

Columns:
- `id`: integer PK
- `name`: string (e.g. "2025/2026") unique
- `start_year`: integer (optional)
- `end_year`: integer (optional)

Notes:
- Keep this small; seed with the active years used by the app.

---

### `persons` (or `people`)
**Purpose:** subjects/students displayed per school year.

Columns:
- `id`: integer PK
- `school_year_id`: FK -> `school_years.id` (required)
- `first_name`: string (required)
- `last_name`: string (required)
- `full_name`: string (required) — denormalized full name for display/search (e.g. "First Last"); application code must populate/update this when first/last change.
- `external_id`: string (optional) — for integration with other systems

Indexes:
- index on `school_year_id`
- optional index on `full_name` for fast name search/sorting

Notes:
- The app will display `full_name` in the UI. Since users will enter people manually, keeping a denormalized `full_name` simplifies sorting and searching in SQL without complex CONCAT expressions.

---

### `categories`
**Purpose:** lookup table for observation categories (behaviour/skill areas).

Columns:
- `id`: integer PK
- `key`: string (internal key, unique)
- `label`: string (user-facing)
- `description`: text (optional)
- `parent_id`: FK -> `categories.id` (nullable) — supports hierarchical categories
- `display_order`: integer (optional)
- `is_active`: boolean (default true)

Indexes / constraints:
- unique index on `key`

Notes:
- Categories are admin-managed lookup values used by the UI when creating observations.

---

### `observations`
**Purpose:** one row per observation event for a person in a category.

Columns:
- `id`: integer PK
- `person_id`: FK -> `persons.id` (required)
- `category_id`: FK -> `categories.id` (required)
- `observed_at`: date (store date only) (required)
- `score`: small string or smallint (allow '1','2','3','4','?', NULL) — application validates allowed values
- `comment`: text (optional)
- `created_by_id`: FK -> `users.id` (optional)
- `created_at`: timestamp with timezone (default now)
- `updated_at`: timestamp with timezone (optional)

Indexes:
- index on (`observed_at`)
- composite index for typical filters, e.g. (`observed_at`, `category_id`)
- index on (`person_id`)

Notes:
- Use `date` for `observed_at` since time-of-day is not relevant.
- `score` may later be strengthened into a DB Enum via migration.
- Saving observations overwrites existing rows for the same (person_id, category_id, observed_at) as per the chosen behavior.

---

## 4) Key queries (drive schema + indexes)
Write down the queries the UI needs. These can be English descriptions.

1. **Main browse query**:
   - Inputs: date range + filters
   - Output: rows of observations

2. **Summary chart query**:
   - Output: aggregates (e.g., by day/week/source)

3. **Distinct values for filters**:
   - e.g., list of stations, sources, tags

---

## 5) Data volume assumptions
- Expected observation rows: TBD
- Growth per day/week: TBD
- Typical query ranges: TBD

---

## 6) Migration notes (schema evolution)
- What changes do you expect soon? (new columns, new tables, renames)
- Any backfill requirements?

---

## 7) Decisions (fill in as you go)
- Primary key strategy: integer vs UUID
- Timestamp strategy: timezone-aware? stored in UTC?
- Soft delete needed? (e.g., `deleted_at`)
- Auditing needed? (created_by/updated_by)
