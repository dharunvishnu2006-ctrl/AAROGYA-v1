import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from models import Patient

ALLOWED_FIELDS = {"age", "bmi", "bp_systolic", "bp_diastolic", "sugar_fasting", "city"}


def get_connection(db_path: str = "data/aarogya.db") -> sqlite3.Connection:
    """
    Opens and configures a SQLite database connection with row access by column name
    and enforced foreign key constraints.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """
    Initializes the schema for active patient records and the immutable audit ledger.
    """
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                patient_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                bmi REAL NOT NULL,
                bp_systolic REAL NOT NULL,
                bp_diastolic REAL NOT NULL,
                sugar_fasting REAL NOT NULL,
                city TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patient_corrections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                field_name TEXT NOT NULL,
                old_value TEXT NOT NULL,
                new_value TEXT NOT NULL,
                reason TEXT NOT NULL,
                recorded_at TEXT NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
            );
        """)


def insert_patient(conn: sqlite3.Connection, patient: Patient) -> None:
    """
    Inserts a validated Patient domain entity into persistent storage.
    Enforces that invalid entities cannot reach the database.
    """
    if not isinstance(patient, Patient):
        raise TypeError(f"Expected validated Patient instance, got {type(patient).__name__}")

    now = datetime.now(timezone.utc).isoformat()
    with conn:
        conn.execute(
            """
            INSERT INTO patients (
                patient_id, name, age, gender, bmi,
                bp_systolic, bp_diastolic, sugar_fasting, city, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                patient.patient_id,
                patient.name,
                patient.age,
                patient.gender,
                patient.bmi,
                patient.bp_systolic,
                patient.bp_diastolic,
                patient.sugar_fasting,
                patient.city,
                now,
            ),
        )


def correct_patient_vital(
    conn: sqlite3.Connection,
    patient_id: str,
    field_name: str,
    new_value: Any,
    reason: str,
) -> None:
    """
    Atomically updates the current patient snapshot and appends an entry to the immutable audit log.
    
    Enforces:
      1. Field is editable.
      2. Clinical justification is non-empty.
      3. No-op corrections (new_value == old_value) are rejected.
      4. Proposed change passes Patient domain model invariants.
    """
    if field_name not in ALLOWED_FIELDS:
        raise ValueError(f"Field '{field_name}' is not an editable vital field.")

    if not reason or not reason.strip():
        raise ValueError("A non-empty clinical justification is required for all corrections.")

    now = datetime.now(timezone.utc).isoformat()

    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,))
        row = cursor.fetchone()
        if not row:
            raise KeyError(f"Patient with ID '{patient_id}' not found.")

        old_data = dict(row)
        old_val_raw = old_data[field_name]

        if str(old_val_raw) == str(new_value):
            raise ValueError(
                f"No-op correction rejected: Field '{field_name}' is already '{new_value}'."
            )

        old_data.pop("updated_at", None)
        old_data[field_name] = new_value
        validated_patient = Patient(**old_data)
        persisted_new_val = getattr(validated_patient, field_name)

        cursor.execute(
            f"UPDATE patients SET {field_name} = ?, updated_at = ? WHERE patient_id = ?",
            (persisted_new_val, now, patient_id),
        )

        cursor.execute(
            """
            INSERT INTO patient_corrections (
                patient_id, field_name, old_value, new_value, reason, recorded_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (patient_id, field_name, str(old_val_raw), str(persisted_new_val), reason.strip(), now),
        )


def get_patient(conn: sqlite3.Connection, patient_id: str) -> Optional[Dict[str, Any]]:
    """Returns the current patient record as a dictionary, or None if not found."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,))
    row = cursor.fetchone()
    return dict(row) if row else None


def get_all_patients(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """Returns all active patient records sorted by patient_id."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients ORDER BY patient_id ASC")
    return [dict(row) for row in cursor.fetchall()]


def get_patient_history(conn: sqlite3.Connection, patient_id: str) -> List[Dict[str, Any]]:
    """Returns the immutable audit log for a single patient, newest first."""
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, patient_id, field_name, old_value, new_value, reason, recorded_at
        FROM patient_corrections
        WHERE patient_id = ?
        ORDER BY recorded_at DESC, id DESC
        """,
        (patient_id,),
    )
    return [dict(row) for row in cursor.fetchall()]


def get_all_history(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """Returns the immutable audit log across all patients, newest first."""
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, patient_id, field_name, old_value, new_value, reason, recorded_at
        FROM patient_corrections
        ORDER BY recorded_at DESC, id DESC
        """
    )
    return [dict(row) for row in cursor.fetchall()]