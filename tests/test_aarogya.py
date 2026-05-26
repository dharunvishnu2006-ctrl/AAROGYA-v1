import pytest
import pandas as pd
from models import Patient, Doctor, Hospital
from analytics import (calc_avg_bmi,
                       score_patient_risk)
from charts import plot_age_distribution

def test_patient_creation():
    p = Patient('P001', 'Arjun', 28,
                'Male', 22.5, 118, 75, 95,
                'Chennai')
    assert p.patient_id == 'P001'
    assert p.name == 'Arjun'

def test_bmi_category():
    p = Patient('P002', 'Priya', 35,
                'Female', 31.0, 125, 80,
                100, 'Mumbai')
    assert p.get_bmi_category() == 'Obese'

def test_calc_avg_bmi():
    df = pd.read_csv('data/patients_sample.csv')
    result = calc_avg_bmi(df)
    assert isinstance(result, dict)
    assert 'mean' in result

def test_plot_returns_figure():
    import matplotlib
    df = pd.read_csv('data/patients_sample.csv')
    fig = plot_age_distribution(df)
    assert isinstance(fig, 
                      matplotlib.figure.Figure)

def test_high_risk_patient():
    p = Patient('P003', 'Ravi', 55,
                'Male', 38.0, 185, 110,
                220, 'Delhi')
    assert score_patient_risk(p) == 'High'               