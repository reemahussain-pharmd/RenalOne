# 🫀 RenalCare OS

## AI-Powered Kidney Disease Intelligence Platform

> *Transform kidney disease management from reactive treatment to predictive, preventive, and personalised care through AI — supporting clinicians, not replacing them.*

---

## 🎯 What Is RenalCare OS?

RenalCare OS is a portfolio-grade, production-ready healthcare AI platform built for nephrologists, clinical pharmacists, researchers, and patients. It provides six integrated intelligence modules covering kidney risk assessment, clinical evidence retrieval, medication safety, renal nutrition, pharmacoeconomic analysis, and professional clinical report generation.

**Built on:** Published pharmacoeconomic research on hemodialysis economic burden in rural India · KDIGO 2024 Clinical Guidelines · Clinical Pharmacy expertise

---

## 🏥 Platform Modules — Version 1

| Module | Description | Key Output |
|--------|-------------|------------|
| 🫀 **Kidney Risk Assessment** | AI-powered CKD risk scoring from clinical biomarkers | Risk Score (0–100), CKD Stage, Recommendations |
| 🔬 **Clinical Evidence Intelligence** | RAG-powered KDIGO knowledge base + PDF upload | Evidence summaries, guideline insights |
| 💊 **Medication Intelligence** | PharmD AI — drug safety for CKD patients | Nephrotoxicity alerts, dose adjustment flags, interaction screening |
| 🥗 **Kidney Nutrition Intelligence** | Stage-specific renal food analysis | Safe/Caution/Avoid with nutrient breakdowns |
| 💰 **Pharmacoeconomic Intelligence** | Economic burden calculator (hemodialysis research methodology) | Annual cost, catastrophic expenditure analysis |
| 📋 **AI Report Generator** | Professional PDF clinical report | Downloadable clinical-grade PDF |

---

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# 1. Clone / navigate to project directory
cd "hemo version 2"

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment (optional — works without API keys)
copy .env.example .env
# Edit .env and add your OpenAI/Gemini API key

# 5. Run
streamlit run app.py
```

The app opens at **http://localhost:8501**

### With Docker

```bash
# Build and run
cd deployment
docker-compose up --build

# Access at http://localhost:8501
```

---

## 🔑 API Keys (Optional)

The platform works **without any API keys** using rule-based fallbacks for all analysis.

For enhanced AI capabilities:
- **OpenAI** (GPT-4o-mini): Best quality — add `OPENAI_API_KEY` to `.env`
- **Google Gemini**: Free tier available — add `GOOGLE_API_KEY` to `.env`

```env
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AI...
```

---

## 🗂️ Project Structure

```
renalcare-os/
├── app.py                      ← Main Streamlit application
├── requirements.txt
├── .env.example                ← Environment variable template
│
├── pages/                      ← Streamlit page modules
│   ├── home.py                 ← Dashboard homepage
│   ├── kidney_risk.py          ← Risk Assessment
│   ├── clinical_evidence.py    ← RAG Evidence Intelligence
│   ├── medication_intelligence.py  ← PharmD AI Module
│   ├── nutrition_intelligence.py   ← Renal Nutrition
│   ├── pharmacoeconomics.py    ← Economic Burden
│   └── report_generator.py     ← PDF Report
│
├── models/
│   └── kidney_risk.py          ← CKD risk scoring model
│
├── medication/
│   └── checker.py              ← Drug safety engine
│
├── nutrition/
│   ├── food_database.py        ← Renal food nutrient database
│   └── analyzer.py             ← Food suitability analyser
│
├── economics/
│   └── calculator.py           ← Pharmacoeconomic calculator
│
├── rag/
│   └── engine.py               ← Clinical RAG engine (FAISS + KDIGO KB)
│
├── reports/
│   └── generator.py            ← ReportLab PDF generator
│
├── components/
│   └── charts.py               ← Plotly chart components
│
├── utils/
│   ├── constants.py            ← Clinical constants & thresholds
│   └── helpers.py              ← Shared utilities + AI client
│
├── data/
│   └── sample_patients.csv     ← Sample patient data
│
├── deployment/
│   ├── Dockerfile
│   └── docker-compose.yml
│
└── .streamlit/
    └── config.toml             ← Streamlit theme
```

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Streamlit 1.32+ |
| **Backend** | Python 3.11, FastAPI (API mode) |
| **AI Engine** | OpenAI GPT-4o-mini / Google Gemini 1.5 Flash |
| **RAG / Vector** | FAISS, sentence-transformers |
| **ML Models** | scikit-learn, XGBoost |
| **PDF** | ReportLab |
| **Charts** | Plotly |
| **Document Parse** | PyPDF2 / pypdf |
| **Database** | PostgreSQL (optional) |
| **Deployment** | Docker, Streamlit Cloud |

---

## 🗺️ Version Roadmap

### ✅ Version 1 — Current
- Kidney Risk Assessment
- Clinical Evidence Intelligence (RAG)
- Medication Intelligence Engine
- Kidney Nutrition Intelligence
- Pharmacoeconomic Intelligence
- AI Renal Report Generator

### 🔮 Version 2 — Planned
- CKD Progression Prediction (1/3/5-year ESRD risk)
- Patient Adherence Intelligence
- Dialysis Intelligence Module
- Research-grade ML models

### 🚀 Version 3 — Future
- Kidney Digital Twin (virtual patient simulation)
- Population Health Intelligence
- Hospital EHR Integration
- FHIR Connectivity
- Mobile Application

---

## ⚕️ Clinical Disclaimer

RenalCare OS is designed for **clinical decision support only**. It does not constitute medical advice and does not replace the clinical judgment of qualified physicians, pharmacists, or other licensed healthcare professionals. All clinical decisions must be made by authorised healthcare providers.

---

## 📚 Clinical References

- KDIGO 2024 CKD Clinical Practice Guidelines
- KDIGO 2022 Diabetes Management in CKD
- KDIGO 2021 Blood Pressure Guideline
- KDIGO 2020 Nutrition in CKD
- ADA Standards of Medical Care 2024
- CREDENCE, DAPA-CKD, EMPA-KIDNEY Trials
- Published: "Economic burden and quality of life of maintenance hemodialysis patients in a rural area of South India — a pharmacoeconomic study"

---

## 🏗️ Built With

**Clinical Pharmacy Intelligence** · **AI/ML Engineering** · **Healthcare Informatics** · **Pharmacoeconomics Research**

*RenalCare OS v1.0 — Portfolio & Clinical Preview*
