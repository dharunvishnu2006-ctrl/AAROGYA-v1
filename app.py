import sqlite3
import pandas as pd
import streamlit as st

import clinical_store as cs
from models import Patient
from analytics import score_patient_risk

DB_PATH = "data/aarogya.db"
SEED_CSV = "data/patients_sample.csv"

st.set_page_config(page_title="AAROGYA Clinical Decision Support", layout="wide")

class Hospital:
    def __init__(self, hospital_id: str, name: str, city: str, total_beds: int):
        self.hospital_id = hospital_id
        self.name = name
        self.city = city
        self.total_beds = total_beds

    def occupancy_rate(self, active_patients: int) -> float:
        if self.total_beds <= 0:
            return 0.0
        return round((active_patients / self.total_beds) * 100, 1)


HOSPITAL_NETWORK = [
    Hospital("H001", "Apollo Hospital", "Chennai", 500),
    Hospital("H002", "Fortis Hospital", "Bangalore", 400),
    Hospital("H003", "Manipal Hospital", "Delhi", 450),
]

@st.cache_resource
def bootstrap_database():
    conn = cs.get_connection(DB_PATH)
    try:
        cs.init_db(conn)
        existing = cs.get_all_patients(conn)
        quarantined = []
        if not existing:
            try:
                seed_df = pd.read_csv(SEED_CSV)
                for idx, row in seed_df.iterrows():
                    try:
                        p = Patient(
                            patient_id=str(row["patient_id"]).strip(),
                            name=str(row["name"]).strip(),
                            age=int(row["age"]),
                            gender=str(row["gender"]).strip(),
                            bmi=float(row["bmi"]),
                            bp_systolic=float(row["bp_systolic"]),
                            bp_diastolic=float(row["bp_diastolic"]),
                            sugar_fasting=float(row["sugar_fasting"]),
                            city=str(row["city"]).strip(),
                        )
                        cs.insert_patient(conn, p)
                    except (ValueError, TypeError, KeyError) as err:
                        quarantined.append(
                            {"row": idx + 1, "id": row.get("patient_id", "N/A"), "reason": str(err)}
                        )
            except FileNotFoundError:
                pass
        return {"quarantined": quarantined}
    finally:
        conn.close()


init_status = bootstrap_database()

conn = cs.get_connection(DB_PATH)

try:
    if init_status.get("quarantined"):
        with st.expander("⚠️ Seed Ingestion Quarantine Alert", expanded=False):
            st.warning(f"Quarantined {len(init_status['quarantined'])} malformed rows during seed.")
            st.dataframe(pd.DataFrame(init_status["quarantined"]))

    st.sidebar.header("Clinical Actions")

    uploaded_file = st.sidebar.file_uploader("Batch Ingest Patients (CSV)", type=["csv"])
    if uploaded_file is not None:
        if st.sidebar.button("Run Ingestion"):
            upload_df = pd.read_csv(uploaded_file)
            inserted, skipped, upload_quarantine = 0, 0, []

            for idx, row in upload_df.iterrows():
                try:
                    patient = Patient(
                        patient_id=str(row["patient_id"]).strip(),
                        name=str(row["name"]).strip(),
                        age=int(row["age"]),
                        gender=str(row["gender"]).strip(),
                        bmi=float(row["bmi"]),
                        bp_systolic=float(row["bp_systolic"]),
                        bp_diastolic=float(row["bp_diastolic"]),
                        sugar_fasting=float(row["sugar_fasting"]),
                        city=str(row["city"]).strip(),
                    )
                    try:
                        cs.insert_patient(conn, patient)
                        inserted += 1
                    except sqlite3.IntegrityError:
                        skipped += 1
                except (ValueError, TypeError, KeyError) as err:
                    upload_quarantine.append(
                        {"row": idx + 1, "id": row.get("patient_id", "N/A"), "reason": str(err)}
                    )

            st.sidebar.success(f"Ingested {inserted} new patients.")
            if skipped > 0:
                st.sidebar.info(f"Skipped {skipped} existing patients (duplicate IDs).")
            if upload_quarantine:
                st.sidebar.error(f"Quarantined {len(upload_quarantine)} invalid rows.")
            st.rerun()

    st.sidebar.divider()

    st.sidebar.subheader("Record Correction")
    all_records = cs.get_all_patients(conn)
    patient_id_options = [p["patient_id"] for p in all_records]

    if patient_id_options:
        target_pid = st.sidebar.selectbox("Patient ID", options=patient_id_options)
        field = st.sidebar.selectbox(
            "Vital Field",
            options=["bmi", "bp_systolic", "bp_diastolic", "sugar_fasting", "age", "city"],
        )
        new_val_str = st.sidebar.text_input("New Value")
        reason_str = st.sidebar.text_input("Clinical Justification")

        if st.sidebar.button("Commit Correction"):
            if not new_val_str or not reason_str:
                st.sidebar.error("Value and clinical justification are both required.")
            else:
                try:
                    typed_val = (
                        int(new_val_str)
                        if field == "age"
                        else float(new_val_str)
                        if field in {"bmi", "bp_systolic", "bp_diastolic", "sugar_fasting"}
                        else new_val_str.strip()
                    )
                    cs.correct_patient_vital(conn, target_pid, field, typed_val, reason_str.strip())
                    st.sidebar.success(f"Updated {field} for {target_pid}.")
                    st.rerun()
                except (ValueError, TypeError, KeyError) as err:
                    st.sidebar.error(f"Correction rejected: {err}")

    st.title("AAROGYA Clinical Decision Support System")

    tab_dashboard, tab_directory, tab_lookup, tab_hospitals, tab_audit = st.tabs(
        ["Dashboard Metrics", "Patient Directory", "Risk Lookup", "Hospital Network", "Audit Log"]
    )

    df_current = pd.DataFrame(all_records) if all_records else pd.DataFrame()

    with tab_dashboard:
        if not df_current.empty:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Active Cohort Size", len(df_current))
            c2.metric("Mean Systolic BP", f"{df_current['bp_systolic'].mean():.1f} mmHg")
            c3.metric("Mean Fasting Sugar", f"{df_current['sugar_fasting'].mean():.1f} mg/dL")
            c4.metric("Mean BMI", f"{df_current['bmi'].mean():.1f}")

            st.subheader("Cohort Vitals Overview")
            st.dataframe(
                df_current[[
                    "patient_id", "name", "age", "gender", "bmi",
                    "bp_systolic", "bp_diastolic", "sugar_fasting", "city", "updated_at"
                ]],
                use_container_width=True,
            )
        else:
            st.info("No clinical records found in the database.")

    with tab_directory:
        st.subheader("Patient Clinical Profile Directory")
        if not df_current.empty:
            st.dataframe(df_current, use_container_width=True)
        else:
            st.info("No records to display.")

    with tab_lookup:
        st.subheader("Patient Clinical Risk Lookup")
        search_id = st.selectbox("Select Patient to Inspect", options=[""] + patient_id_options)
        if search_id:
            patient_row = cs.get_patient(conn, search_id)
            if patient_row:
                p_data = dict(patient_row)
                p_data.pop("updated_at", None)
                patient_obj = Patient(**p_data)
                risk_tier = score_patient_risk(patient_obj)

                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**Name:** {patient_obj.name}")
                    st.write(f"**Demographics:** {patient_obj.age} yrs | {patient_obj.gender} | {patient_obj.city}")
                    st.write(f"**Last Sync:** {patient_row['updated_at']}")
                    st.write(f"**Calculated BMI Category:** `{patient_obj.get_bmi_category()}`")

                with c2:
                    tier_color = "🔴" if risk_tier == "High" else "🟡" if risk_tier == "Medium" else "🟢"
                    st.metric("Clinical Risk Tier", f"{tier_color} {risk_tier}")
                    st.write(f"**Hypertension Check:** {'Positive' if patient_obj.is_hypertensive() else 'Negative'}")
                    st.write(f"**Diabetic Check:** {'Positive' if patient_obj.is_diabetic() else 'Negative'}")

                st.json(p_data)

    with tab_hospitals:
        st.subheader("Regional Hospital Network Occupancy")
        if not df_current.empty:
            norm_counts = df_current["city"].astype(str).str.strip().str.lower().value_counts().to_dict()
            h_data = []
            for h in HOSPITAL_NETWORK:
                admissions = norm_counts.get(h.city.strip().lower(), 0)
                rate = h.occupancy_rate(admissions)
                h_data.append({
                    "Hospital ID": h.hospital_id,
                    "Hospital Name": h.name,
                    "City": h.city,
                    "Total Capacity": h.total_beds,
                    "Active Cohort Admissions": admissions,
                    "Occupancy Rate (%)": f"{rate:.1f}%",
                    "Status": "⚠️ High Load" if rate >= 80.0 else "Normal"
                })
            st.dataframe(pd.DataFrame(h_data), use_container_width=True)
        else:
            st.info("No cohort data available to compute hospital occupancies.")

    with tab_audit:
        st.subheader("Immutable Correction History")
        audit_target = st.selectbox("Filter Audit Trail", options=["All Patients"] + patient_id_options)
        audit_records = cs.get_all_history(conn) if audit_target == "All Patients" else cs.get_patient_history(conn, audit_target)
        if audit_records:
            st.dataframe(pd.DataFrame(audit_records), use_container_width=True)
        else:
            st.info("No clinical adjustments recorded in audit ledger.")

finally:
    conn.close()