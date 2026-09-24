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