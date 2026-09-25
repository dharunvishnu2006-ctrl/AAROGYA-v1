import sqlite3, pytest
import clinical_store as cs
from models import Patient

def make_patient(pid="P1", bmi=24.0, sbp=120.0):
    return Patient(pid, "Test", 40, "M", bmi, sbp, 80.0, 90.0, "Delhi")

@pytest.fixture
def db():
    conn = cs.get_connection(":memory:")
    cs.init_db(conn)
    yield conn
    conn.close()

def test_schema_init(db):
    tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"patients", "patient_corrections"}.issubset(tables)

def test_insert_and_duplicate_reject(db):
    p = make_patient()
    cs.insert_patient(db, p)
    assert cs.get_patient(db, "P1")["name"] == "Test"
    with pytest.raises(sqlite3.IntegrityError):
        cs.insert_patient(db, p)

def test_correction_and_audit(db):
    cs.insert_patient(db, make_patient())
    cs.correct_patient_vital(db, "P1", "bmi", 26.5, "Weight increase")
    assert cs.get_patient(db, "P1")["bmi"] == 26.5
    history = cs.get_patient_history(db, "P1")
    assert len(history) == 1
    assert history[0]["old_value"] == "24.0" and history[0]["new_value"] == "26.5"

def test_correction_guards(db):
    cs.insert_patient(db, make_patient())
    with pytest.raises(ValueError, match="already"):
        cs.correct_patient_vital(db, "P1", "bmi", 24.0, "No change")
    with pytest.raises(ValueError, match="justification"):
        cs.correct_patient_vital(db, "P1", "bmi", 25.0, "   ")
    with pytest.raises(ValueError, match="editable"):
        cs.correct_patient_vital(db, "P1", "name", "New", "Valid reason")
    with pytest.raises(KeyError):
        cs.correct_patient_vital(db, "P99", "bmi", 25.0, "Valid reason")

def test_disk_persistence(tmp_path):
    f = str(tmp_path / "test.db")
    c1 = cs.get_connection(f)
    cs.init_db(c1)
    cs.insert_patient(c1, make_patient())
    c1.close()

    c2 = cs.get_connection(f)
    assert cs.get_patient(c2, "P1") is not None
    c2.close()