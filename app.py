import streamlit as st
import pandas as pd
from models import Patient, Doctor, Hospital
from analytics import (calc_avg_bmi,
                       calc_median_bp,
                       calc_std_sugar,
                       score_patient_risk)
from charts import (plot_age_distribution,
                    plot_bmi_vs_age,
                    plot_city_patient_count,
                    plot_dashboard)

st.set_page_config(
    page_title='AAROGYA v1',
    layout='wide'
)

st.title('AAROGYA v1 = India Health Analytics')
st.caption('Inspired by ABDM - Ayushman Bharat Digital Mission')

uploaded = st.sidebar.file_uploader(
    'Upload Patient CSV', type='csv')

if uploaded:
    df = pd.read_csv(uploaded)
else:
    df = pd.read_csv('data/patients_sample.csv')

st.sidebar.success(f'{len(df)} patients loaded!')

tab1, tab2, tab3 = st.tabs([
    'Dashboard',
    'Patients',
    'Hospitals'
])

with tab1:
    st.subheader('Health Analytics Dashboard')

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric('Total Patients', len(df))
    with col2:
        st.metric('Avg BMI',
                  round(df['bmi'].mean(),1))    
    with col3:
        high_bp = len(df[df['bp_systolic'] > 140])
        st.metric('High BP Patients', high_bp)   

    st.pyplot(plot_dashboard(df))     
                  

with tab2:
    st.subheader('Patient Records')

    col1, col2 = st.columns(2)
    with col1:
        city_filter = st.selectbox(
            'Filter by City',
            ['All'] + list(df['city'].unique()))
        
    with col2:
        gender_filter = st.radio(
            'Filter by Gender',
            ['All', 'Male', 'Female'])


    filtered_df = df.copy()
    if city_filter !='All':
        filtered_df = filtered_df[
            filtered_df['city'] == city_filter]
    if gender_filter != 'All':        
        filtered_df = filtered_df[
            filtered_df['gender'] == gender_filter]
        
    st.dataframe(filtered_df,
                 use_container_width=True)
    st.caption(f'{len(filtered_df)} patients found!')    

with tab3:
    st.subheader('Hospital Occupancy')

    hospitals = [
        Hospital('H001', 'Apollo Chennai',
                 'Chennai', 500),
        Hospital('H002', 'AIIMS Delhi',
                 'Delhi', 1000),
        Hospital('H003','Fortis Mumbai',
                 'Mumbai',300)
    ]   
    for h in hospitals:
        current = len(df[df['city'] == h.city])
        rate = h.occupancy_rate(current)
        st.subheader(h.name)
        st.progress(min(rate/100, 1.0))
        st.caption(f'{rate}% occupied - '
                   f'{current} patients')
        
st.divider()
st.subheader('Patient Risk Lookup')

pid = st.selectbox(
    'Select Patient ID',
    df['patient_id'].tolist())

row = df[df['patient_id']== pid].iloc[0]
patient = Patient(
    row['patient_id'], row['name'],
    row['age'], row['gender'], row['bmi'],
    row['bp_systolic'], row['bp_diastolic'],
    row['sugar_fasting'], row['city'])

risk = score_patient_risk(patient)

if risk == 'Low':
    st.success(f'{row["name"]} - Low Risk')
elif risk == 'Medium':
    st.warning(f'{["name"]} - Medium Risk')
else:
    st.error(f'{row["name"]} - High Risk')        