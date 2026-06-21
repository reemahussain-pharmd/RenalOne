# 🫀 RenalOne

## Unified Kidney Intelligence Platform

> *One Platform. One Patient Journey. One Kidney Intelligence Ecosystem.*

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://renalone.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Modules](https://img.shields.io/badge/Modules-7_Active-14B8A6)
![KDIGO](https://img.shields.io/badge/Evidence-KDIGO_2024-6366F1)

---

## 🚀 Live Demo

| | |
|---|---|
| **🌐 Live App** | **[https://renalone.streamlit.app](https://renalone.streamlit.app)** |
| **📁 Repository** | [github.com/reemahussain-pharmd/RenalOne](https://github.com/reemahussain-pharmd/RenalOne) |
| **🛠 Stack** | Python · Streamlit · GPT-4o · ReportLab · Plotly · FAISS |

> **To deploy your own instance:** Fork this repo → Go to [share.streamlit.io](https://share.streamlit.io) → Connect repo → Set main file to `app.py` → Deploy

---

## 🎯 What Is RenalOne?

**RenalOne** is an AI-powered kidney intelligence platform that integrates kidney risk assessment, medication intelligence, clinical evidence retrieval, renal nutrition guidance, pharmacoeconomic analysis, dialysis intelligence, and patient adherence scoring into one unified ecosystem.

Built for nephrologists, clinical pharmacists, researchers, and patients — RenalOne delivers seven integrated intelligence modules covering the complete kidney disease management journey.

**Built on:** Published pharmacoeconomic research on hemodialysis economic burden in rural India · KDIGO 2024 Clinical Guidelines · Clinical Pharmacy expertise (PharmD)

---

## 🏥 Platform Modules — Version 1

| Module | Description | Key Output |
|--------|-------------|------------|
| 🫀 **Kidney Risk Assessment** | AI-powered CKD risk scoring from clinical biomarkers with KDIGO heatmap | Risk Score (0–100), CKD Stage, Explainable factors |
| 🔬 **Clinical Evidence Intelligence** | RAG-powered KDIGO knowledge base + PDF upload | Evidence summaries, guideline insights |
| 💊 **Medication Intelligence** | PharmD AI — drug safety for CKD patients | Nephrotoxicity alerts, dose adjustment flags, interaction network |
| 🥗 **Kidney Nutrition Intelligence** | Stage-specific renal food analysis with AI meal planner | Safe/Caution/Avoid ratings, AI-generated meal plans |
| 💰 **Pharmacoeconomic Intelligence** | Multi-country cost-of-illness model (India/USA/UAE/UK) | Annual cost, WHO catastrophic expenditure assessment, govt schemes |
| 🎯 **Patient Adherence Intelligence** | 5-domain adherence scoring with radar chart | Adherence score (0–100), evidence-based interventions |
| 📋 **AI Report Generator** | Professional PDF clinical report with executive summary | Downloadable clinical-grade PDF |

---

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/reemahussain-pharmd/Renalcare-AI.git
cd Renalcare-AI

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment (optional — works without API keys)
copy .env.example .env
# Edit .env and add your OpenAI API key for AI features

# 5. Run
streamlit run app.py
```

The app opens at **http://localhost:8501**

### With Docker

```bash
cd deployment
docker-compose up --build
# Access at http://localhost:8501
```

---

## 🔑 API Keys (Optional)

RenalOne works **without any API keys** using rule-based fallbacks for all analysis.

For enhanced AI capabilities:
- **OpenAI** (GPT-4o): Best quality — add `OPENAI_API_KEY` to `.env`
- **Google Gemini**: Free tier available — add `GOOGLE_API_KEY` to `.env`

```env
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AI...
```

---

## 🗂️ Project Structure

```
renalone/
├── app.py                          ← Main Streamlit application + sidebar
├── requirements.txt
├── .env.example
│
├── pages/                          ← Intelligence module pages
│   ├── home.py                     ← Dashboard homepage
│   ├── kidney_risk.py              ← Risk Assessment + KDIGO heatmap
│   ├── clinical_evidence.py        ← RAG Evidence Intelligence
│   ├── medication_intelligence.py  ← PharmD AI Module
│   ├── nutrition_intelligence.py   ← Renal Nutrition + Meal Planner
│   ├── pharmacoeconomics.py        ← Multi-country Economic Burden
│   ├── adherence_intelligence.py   ← Patient Adherence Scoring
│   └── report_generator.py         ← PDF Report Generator
│
├── models/
│   └── kidney_risk.py              ← CKD risk scoring model
│
├── medication/
│   └── checker.py                  ← Drug safety engine
│
├── nutrition/
│   ├── food_database.py            ← Renal food nutrient database
│   └── analyzer.py                 ← Food suitability analyser
│
├── economics/
│   └── calculator.py               ← Pharmacoeconomic calculator
│
├── rag/
│   └── engine.py                   ← Clinical RAG engine (FAISS + KDIGO KB)
│
├── reports/
│   └── generator.py                ← ReportLab PDF generator
│
├── components/
│   ├── styles.py                   ← Global CSS design system
│   └── charts.py                   ← Plotly chart components
│
├── utils/
│   ├── constants.py                ← Clinical constants & thresholds
│   └── helpers.py                  ← Shared utilities + AI client
│
└── .streamlit/
    └── config.toml                 ← Streamlit theme
```

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Streamlit 1.32+ |
| **AI Engine** | OpenAI GPT-4o / Google Gemini 1.5 Flash |
| **RAG / Vector** | FAISS, sentence-transformers |
| **ML Models** | scikit-learn, XGBoost |
| **PDF** | ReportLab |
| **Charts** | Plotly |
| **Document Parse** | PyPDF2 / pypdf |
| **Deployment** | Streamlit Cloud, Docker |

---

## 🗺️ Version Roadmap

### ✅ Version 1 — Current (7 Modules)
- Kidney Risk Assessment + KDIGO Heatmap + Explainability
- Clinical Evidence Intelligence (RAG)
- Medication Intelligence Engine (Drug interactions, dose matrix, ADR)
- Kidney Nutrition Intelligence (AI meal planner, food image analysis)
- Pharmacoeconomic Intelligence (Multi-country, govt schemes, cost simulator)
- Patient Adherence Intelligence (5-domain scoring, radar chart)
- AI Clinical Report Generator (Executive summary PDF)

### 🔮 Version 2 — Planned
- CKD Progression Prediction (1/3/5-year ESRD risk ML model)
- Dialysis Adequacy Intelligence (Kt/V, URR monitoring)
- Transplant Eligibility Module
- Fluid Management Intelligence
- Anemia Protocol AI
- EHR Integration Layer

### 🚀 Version 3 — Future
- Kidney Digital Twin (virtual patient simulation)
- Population Health Intelligence
- FHIR Connectivity
- Mobile Application
- Multi-site deployment

---

## 🌍 Multi-Country Pharmacoeconomic Support

RenalOne's Pharmacoeconomic Intelligence module supports four countries:

| Country | Currency | Govt Schemes |
|---------|----------|-------------|
| 🇮🇳 India | ₹ INR | PMJAY, NKM Free Dialysis, CGHS, ESI |
| 🇺🇸 USA | $ USD | Medicare ESRD, Medicaid, AKF HIPP |
| 🇦🇪 UAE | AED | Thiqa, Daman, DHA Smile |
| 🇬🇧 UK | £ GBP | NHS (free), PIP, Kidney Care UK |

---

## 📋 Patient Adherence — 5 Domain Scoring

| Domain | Weight | Assessment |
|--------|--------|------------|
| 💊 Medication Adherence | 30% | Dose frequency, self-discontinuation, side effects |
| 🥦 Dietary Adherence | 25% | Renal diet compliance + auto-score from food log |
| 💧 Fluid Management | 20% | Daily intake vs. prescribed limit |
| 📅 Appointment Adherence | 15% | Dialysis sessions + clinic visits |
| 🏃 Lifestyle Modification | 10% | Smoking, exercise, alcohol, stress management |

---

## ⚕️ Clinical Disclaimer

RenalOne is designed for **clinical decision support only**. It does not constitute medical advice and does not replace the clinical judgment of qualified physicians, pharmacists, or other licensed healthcare professionals. All clinical decisions must be made by authorised healthcare providers.

---

## 📚 Clinical References

- KDIGO 2024 CKD Clinical Practice Guidelines
- KDIGO 2022 Diabetes Management in CKD
- KDIGO 2021 Blood Pressure Guideline
- KDIGO 2020 Nutrition in CKD
- ADA Standards of Medical Care 2024
- CREDENCE, DAPA-CKD, EMPA-KIDNEY Trials
- Morisky MMAS-8 Medication Adherence Scale
- Published: *"Economic burden and quality of life of maintenance hemodialysis patients in a rural area of South India — a pharmacoeconomic study"*

---

## 🏗️ Built With

**Clinical Pharmacy Intelligence** · **AI/ML Engineering** · **Healthcare Informatics** · **Pharmacoeconomics Research** · **PharmD Expertise**

---

*RenalOne v1.0 — Unified Kidney Intelligence Platform*
*One Platform. One Patient Journey. One Kidney Intelligence Ecosystem.*
