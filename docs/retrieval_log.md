| Feature | Twin | What I retrieved | What I looked up | Rung | Note |
| --- | --- | --- | --- | --- | --- |
| A1: Centralized clinical thresholds | AutoPilot ML X config | Frozen dataclass pattern for immutable application constants; decoupling domain thresholds from scoring logic | WHO adult hypertension guidelines (140/90 mmHg) and ADA fasting glucose criteria (126 mg/dL) | 1 | Retrieved structure and clinical rules quickly; needed rung 1 nudges on circular rationale wording, missing import in `analytics.py`, and fixing boundary comparisons from `>` to `>=`. |

| Feature | Twin | What I retrieved | What I looked up | Rung | Note |
| --- | --- | --- | --- | --- | --- |
| A2: Typed patient records, validated at the boundary | AutoPilot ML X: Telemetry ingestion / dataclass `__post_init__` | Fail-fast boundary validation; raising `ValueError`; `clinical_config` range checks; exact gender mapping | Nothing external; empirical discovery via runtime traceback inspection | 1 | Nudge-heavy: fixed 2 typos, caught `numpy.int64` vs `int`, resolved CSV pulse-pressure flaws (P007/P031), scoped banner to A2 and pipeline to A3. |

| Problem | Context | Rung | Key Decision | Corrections / Findings |
| --- | --- | --- | --- | --- |
| **Streamlit + SQLite Threading** | Concurrency safety across reruns | **2** | Per-run connections with one-time cached init latch; rejected `check_same_thread=False` | Prompt pointed to concurrency issues; wrapped run-scoped connection in `try...finally` to fix `st.rerun()` leaks |
| **Audit Ledger Design** | Two-table snapshot vs. single versioned table | **1** | Two-table model (`patients` + `patient_corrections`) inside atomic transactions | Caught and rejected no-op updates (`new == old`); enforced non-empty justification at storage layer |
| **UI Rewiring Regressions** | Integration into `app.py` | **1** | Consumed literal string return (`"Low"`, `"Medium"`, `"High"`) from `score_patient_risk()` | Fixed `"Moderate"` typo, restored dropped `hospital_id`, normalized city names to fix silent Bangalore 0% occupancy |