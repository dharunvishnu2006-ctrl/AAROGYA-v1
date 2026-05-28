<div align="center">

```
█████╗  █████╗ ██████╗  ██████╗  ██████╗██╗   ██╗ █████╗
██╔══██╗██╔══██╗██╔══██╗██╔═══██╗██╔════╝╚██╗ ██╔╝██╔══██╗
███████║███████║██████╔╝██║   ██║██║  ███╗╚████╔╝ ███████║
██╔══██║██╔══██║██╔══██╗██║   ██║██║   ██║ ╚██╔╝  ██╔══██║
██║  ██║██║  ██║██║  ██║╚██████╔╝╚██████╔╝  ██║   ██║  ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝   ╚═╝   ╚═╝  ╚═╝
```

### **v1 — India Health Analytics Platform**
#### *Inspired by ABDM — Ayushman Bharat Digital Mission 🇮🇳*

<br/>

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.37-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Tests](https://img.shields.io/badge/pytest-5_Passing-2CA5E0?style=for-the-badge&logo=pytest&logoColor=white)
![Status](https://img.shields.io/badge/Status-Live-00D26A?style=for-the-badge)
![Open Source](https://img.shields.io/badge/Open_Source-❤️-FF6B6B?style=for-the-badge)

<br/>

> *"Code can heal millions when data meets humanity."*

---

</div>

## 🚀 Live Demo

> 🌐 **[Click Here → Launch AAROGYA v1](https://your-demo-link.streamlit.app)**

---

## 🎯 What is AAROGYA?

**AAROGYA** (आरोग्य — meaning *Health* in Sanskrit) is a real-time public health analytics platform built for Bharat. Designed around the vision of ABDM, it gives healthcare workers and administrators a single dashboard to monitor patient vitals, hospital capacity, and AI-powered risk classification — all in one place.

This is not just a project. It is **digital infrastructure for a healthier India.**

---

## ✨ Features

| Module | Description |
|--------|-------------|
| 📊 **Vitals Dashboard** | Live BMI, Blood Pressure, and Sugar level monitoring per patient |
| 🗂️ **Patient Records** | Filterable and searchable patient registry with full health history |
| 🏥 **Hospital Occupancy** | Real-time bed availability tracker across hospital departments |
| 🔴 **Risk Classifier** | AI-powered Low / Medium / High patient risk scoring engine |

---

## 🧠 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     AAROGYA v1 — Data Flow                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Patient Input                                             │
│       │                                                     │
│       ▼                                                     │
│   OOP Model Layer ──── Patient | Doctor | Hospital          │
│       │                        (Python Classes)             │
│       ▼                                                     │
│   Pandas Analytics Engine ──── Aggregation + Filtering      │
│       │                                                     │
│       ▼                                                     │
│   Risk Prediction Module ──── Rule-Based Classifier         │
│       │                        Low / Medium / High          │
│       ▼                                                     │
│   Streamlit Dashboard ──── Interactive UI + Visualizations  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

```
Python 3.11  ·  Streamlit  ·  Pandas  ·  Matplotlib  ·  pytest
```

---

## ⚡ Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/your-username/AAROGYA-v1.git
cd AAROGYA-v1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the dashboard
streamlit run app.py
```

> ✅ **Requirements:** Python 3.11+ · pip · Git

---

## 🧪 Tests

```bash
pytest tests/ -v
```

```
PASSED  test_patient_bmi_calculation
PASSED  test_risk_classifier_low
PASSED  test_risk_classifier_high
PASSED  test_hospital_occupancy_update
PASSED  test_patient_record_filter

5 passed in 0.42s ✅
```

---

## 📂 Project Structure

```
AAROGYA-v1/
│
├── app.py                  # Main Streamlit entry point
├── requirements.txt        # Python dependencies
│
├── models/
│   ├── patient.py          # Patient OOP class
│   ├── doctor.py           # Doctor OOP class
│   └── hospital.py         # Hospital OOP class
│
├── analytics/
│   ├── vitals.py           # BMI / BP / Sugar processing
│   ├── risk.py             # Risk classification engine
│   └── occupancy.py        # Hospital bed tracker
│
├── tests/
│   └── test_core.py        # 5 pytest test cases
│
└── data/
    └── sample_patients.csv # Demo dataset
```

---

## 💡 What I Learned

Building AAROGYA v1 was a deep dive into production-grade Python development:

- **OOP Mastery** — Designed modular `Patient`, `Doctor`, and `Hospital` classes with clean inheritance and encapsulation
- **Data Engineering** — Used Pandas for real-world health data aggregation, filtering, and analytics pipelines
- **Deployment** — Shipped a live Streamlit app from local dev to public URL
- **Testing** — Wrote 5 pytest unit tests covering the core logic of the platform
- **Healthcare Domain** — Understood ABDM's mission and translated real-world health metrics into code

---

## 🗺️ Roadmap

This project is **P1** in a 20-project AI/ML Engineering roadmap:

| Project | Name | Domain |
|---------|------|--------|
| **P1 ✅** | **AAROGYA v1** | Health Analytics |
| P2 | AAROGYA v2 | AI Health Assistant |
| P3 | SURAKSHA v1 | Network Security |
| P9 | KAVACH v1 | Fraud Detection |
| P17 | SentinelAI India | Unified AI Command |

> Full roadmap: 8 Courses · 20 Projects · 3 AWS Certifications · 261 Days

---

## 👨‍💻 Author

<div align="center">

**J. Dharun Vishnu**
*Future AI/ML Engineer · India*

[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github)](https://github.com/your-username)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/your-profile)

<br/>

*"Dedication and love are stronger than any degree."*

</div>

---

<div align="center">

**Built with ❤️ for Bharat** · AAROGYA v1 · 2025

*Inspired by the Ayushman Bharat Digital Mission — because every Indian deserves data-driven healthcare.*

</div>
