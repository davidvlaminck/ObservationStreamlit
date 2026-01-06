# Data model (draft)

Use this document to describe the data model *before* we commit to a specific implementation (SQLAlchemy Core vs ORM). The goal is clarity: tables/entities, fields, relationships, indexes, and the key queries the app needs.

> Tip: if you don’t know something yet, write `TBD` rather than guessing.

---

## 1) Goals and usage
- **Primary use-cases** (what users do in the app):
  - TBD
- **Primary outputs** (what you display):
  - tables? charts? aggregates?
- **Key filters** (these usually drive indexes):
  - date/time range: TBD
  - categorical fields: TBD
  - text search: TBD

---

## 2) Environments / portability
- Local dev DB: SQLite
- Production DB: PostgreSQL
- Portability constraints (features to avoid early because they’re DB-specific):
  - PostgreSQL-only JSON queries? FTS? timezone-heavy logic? `ILIKE`? upserts?
  - TBD

---

## 3) Entities / tables

### `users`
**Purpose:** authenticate users.

Columns:
- `id`: integer / UUID? (PK)
- `username`: string (unique, required)
- `password_hash`: string (required)
- `created_at`: timestamp
- `is_active`: boolean

Constraints / indexes:
- unique (`username`)

Notes:
- Password hashing handled in application code; DB stores only the hash.

---

### `TBD_observations` (rename)
**Purpose:** core domain table (measurements / events / observations).

Columns:
- `id`: PK
- `observed_at`: timestamp (required)
- `source_id`: FK? (optional)
- `value`: numeric?
- `unit`: string?
- `quality_flag`: string?
- ...

Relationships:
- belongs to `TBD_source`?
- belongs to `TBD_station`?

Constraints / indexes:
- index on (`observed_at`)
- indexes for common filters: TBD

---

### `TBD_station` / `TBD_source` / lookup tables
Describe any dimension tables that drive filter pickers.

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

