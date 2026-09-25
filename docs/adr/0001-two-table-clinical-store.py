# ADR 0001: Two-Table Clinical Store Schema (`patients` + `patient_corrections`)

## Status
Accepted

## Context
Prior to this feature, application restarts reset all clinical data back to the baseline CSV, while in-session edits directly overwrote records without preserving prior states, timestamps, or clinical justifications. We were constrained to standard-library `sqlite3` without an ORM or external migration tooling, requiring persistence, referential integrity, domain validation hooks, and audit mechanics to be engineered via raw SQL.

## Decision
We adopted a two-table relational schema:
- `patients`: Stores exactly one row per patient representing their active snapshot, enabling direct, high-speed queries for dashboards and directory views.
- `patient_corrections`: An append-only audit ledger recording `patient_id`, `field_name`, `old_value`, `new_value`, mandatory `reason`, and an ISO `recorded_at` timestamp.

A foreign key links `patient_corrections(patient_id)` to `patients(patient_id)`. Snapshot mutations and audit log insertions are wrapped in an atomic `with conn:` transaction block, ensuring changes and their forensic log entries commit or roll back together.

## Rejected Alternative
**Single Versioned-Rows Table:** We considered storing all states in a single table where every update appends a new row with an incremental `version_id`. This was rejected because UI read operations (cohort aggregations, directory rendering, risk evaluation) occur on every rerun and vastly outnumber write operations. A single versioned table would force every read path to execute subqueries, self-joins, or `GROUP BY MAX(version_id)` filtering. The two-table model keeps the frequent read path a clean, fast `SELECT * FROM patients`.

## Consequences
### Positive (Gained)
- Fast, non-blocking reads for cohort aggregations and dashboard rendering without subquery or grouping overhead.
- Clear separation between current state and historical forensic records.
- Atomic commit guarantees preventing snapshot and audit trail divergence.

### Negative & Deferred (Trade-offs)
- Demographic and identity fields (`name`, `gender`, `patient_id`) cannot be modified; `ALLOWED_FIELDS` strictly restricts edits to vitals, age, and city.
- Batch CSV uploads skip existing `patient_id` matches and cannot apply bulk updates or corrections.
- Single-writer file locking in SQLite limits concurrent write scalability under multi-user operational load.