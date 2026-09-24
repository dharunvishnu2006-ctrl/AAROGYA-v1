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