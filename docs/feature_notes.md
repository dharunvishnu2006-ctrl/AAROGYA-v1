## A1: Centralized Clinical Thresholds (`clinical_config.py`)

- **How It Was Built:** Created a frozen `ClinicalThreshold` dataclass (`value`, `source`, `rationale`) for obesity, BP, and sugar cutoffs. Documented `BMI_UNDERWEIGHT` as reference-only. Wired `score_patient_risk()` to use config `.value` with inclusive `>=` checks and compound `systolic OR diastolic` logic. Added 6 unit tests covering immutability, exact boundaries, and isolated diastolic elevation.
- **Why It Was Needed:** Eliminated scattered magic numbers to prevent threshold drift. Developers lack clinical authority to invent medical cutoffs; WHO/ADA citations ensure legal defensibility and auditability. Also fixed a clinical blind spot by catching isolated diastolic hypertension.
- **Where It's Used:** Defined in `clinical_config.py`, consumed in `analytics.py` (`score_patient_risk()`), and verified in `tests/test_clinical_config.py`.
##Glossary - Clinical Threshold: a medically established cutoff value defined by external accredited guidelines rather than arbitrary engineering choice serving as the single source of truth for clinical triage and decision support logic.

## A2 Data Sanity Audit & Fixture Corrections
- **File**: `data/patients_sample.csv`
- **P007 (Pushti Jhaveri)**: Corrected BP `107/107` -> `107/72` (resolved zero pulse pressure artifact).
- **P031 (Bahadurjit Thaker)**: Corrected BP `104/109` -> `104/68` (resolved inverted systolic <= diastolic artifact).
- **Rationale**: Strict domain invariant enforcement in `models.py` (`bp_systolic > bp_diastolic`) caught synthetic generation flaws. Fixtures updated to clinical plausibility pending generator refactoring.

# A2: Typed Patient Records, Validated at the Boundary

### Why Needed
Protects analytics from dirty or impossible clinical data (e.g., negative pulse pressures, out-of-range ages/BMIs) that cause silent statistical drift or runtime crashes.

### How Built
- **Constructor Enforcement (`models.py`):** `Person` and `Patient` check biological invariants via `clinical_config.py`; raise `ValueError` on failure.
- **Pulse Pressure Check:** Enforced `bp_systolic > bp_diastolic`; rejects $\le 0\text{ mmHg}$.
- **NumPy Scalar Coercion:** Cast values with `int(...)` and `float(...)` to fix `numpy.int64` failing `isinstance(..., int)`.
- **UI Quarantine (`app.py`):** Wrapped single-record lookup in `try/except ValueError` with an inline error banner.
- **Fixture Fix (`data/patients_sample.csv`):** Manually patched `P007` (107/72) and `P031` (104/68).
- **Unit Tests (`tests/`):** Added 11 parameterized boundary tests (22 total passing).

### Where Used
`models.Person`, `models.Patient`, and the single-patient risk lookup in `app.py`.

### Known Limitations (Deferred to A3)
- **Unvalidated Dashboard/Table Data:** `tab1` and `tab2` still aggregate raw DataFrame columns directly; full validated ingestion pipeline moves to A3.
- **Fixture Generation Debt:** Missing reproducible script for `patients_sample.csv`.

### Glossary Term
- **Pulse Pressure ($\text{PP}$):** $\text{Systolic} - \text{Diastolic}$. A reading $\le 0\text{ mmHg}$ is clinically non-viable and flags sensor malfunction or corrupt input.

## A3: Durable Clinical Storage & Immutable Audit Trail

### How It Works
- **Storage Layer (`clinical_store.py`)**: Implements a durable SQLite database backing two tables: `patients` (active state snapshot) and `patient_corrections` (append-only ledger). Schema initialization runs exactly once per application lifetime via a cached bootstrap latch.
- **Connection Lifecycle (`app.py`)**: Opens a short-lived SQLite connection per script execution run. The entire UI execution block is wrapped inside a `try...finally` statement, ensuring connections close deterministically even when `st.rerun()` raises internal control-flow exceptions.
- **Transactional Vital Corrections**: When editing vitals (`bmi`, `bp_systolic`, `bp_diastolic`, `sugar_fasting`, `age`, `city`), `correct_patient_vital()` executes inside an atomic SQLite transaction (`with conn:`). It re-validates proposed updates against `Patient` domain model invariants, updates the active snapshot, and writes an immutable audit record containing old value, new value, clinical justification, and UTC timestamp.
- **Defensive Storage Invariants**: Storage logic rejects no-op submissions (`new_value == old_value`), rejects unapproved vital fields, and requires a non-empty clinical justification string at the database layer.

### Why It Was Built This Way
- **Cold Restart Resilience**: Clinical decision support systems cannot rely on ephemeral in-memory collections or browser session state. Data must persist across server restarts, updates, and unexpected process crashes.
- **Forensic Audit Integrity**: Medical data governance demands a tamper-evident audit log. Rejecting no-op updates prevents accidental double-clicks from generating phantom entries, and enforcing justification requirements at the storage engine level ensures non-UI callers cannot bypass clinical review standards.
- **Deterministic Concurrency**: SQLite file-locking breaks if multiple threads share a single connection object across Streamlit script runs. Short-lived, run-scoped connections prevent cursor race conditions without requiring external third-party pooling dependencies.

### Where In The Codebase
- `clinical_store.py`: `get_connection()`, `init_db()`, `insert_patient()`, `correct_patient_vital()`, `get_patient()`, `get_all_patients()`, `get_patient_history()`, `get_all_history()`.
- `app.py`: Database bootstrap latch (`bootstrap_database`), sidebar batch CSV upload, record correction form, and the dedicated "Audit Log" tab.
- `tests/test_clinical_store.py`: Unit and integration test suite verifying table creation, deduplication constraints, no-op rejections, rollback behavior, and cross-restart disk persistence.

---

## Known Limitations

### Resolved Limitations
- **[Resolved in A3] Cohort Dashboard Direct-Memory Bypass**: The dashboard and patient directory tabs no longer render from ephemeral in-memory DataFrames. All views query SQLite directly on each run, ensuring displayed metrics reflect persistent state.

### Active Limitations
- **Batch CSV Ingestion Cannot Correct Existing Records**: 
  The batch CSV upload pipeline strictly performs deduplication via primary key constraint checks (`sqlite3.IntegrityError`). Existing `patient_id` rows are skipped rather than overwritten. This is an intentional design boundary: bulk overwrites via CSV bypass individual clinical justifications and tamper-evident audit logging. Updates to existing patients must be performed record-by-record via the Clinical Actions sidebar.
- **Single-Writer SQLite Contention**: 
  SQLite relies on database-level file locks during write transactions. While performant for single-clinic CDS stations and concurrent reads, high-frequency simultaneous write attempts from multiple concurrent users will queue and can raise operational lock timeouts. Scaling beyond single-facility concurrency requires migrating the storage engine to a client-server RDBMS (e.g., PostgreSQL).

---

## Glossary

### Append-Only Ledger
A data storage pattern in which records, once written, are strictly immutable. Existing rows cannot be modified, overwritten, or deleted; all historical state changes and corrections are appended as new chronological entries with associated metadata (timestamps, previous values, subsequent values, and user justifications). In AAROGYA, this pattern is implemented in the `patient_corrections` table to maintain a forensically defensible clinical history.