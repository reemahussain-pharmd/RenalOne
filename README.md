# ðŸ«€ RenalCare AI

## AI-Powered Kidney Disease Intelligence Platform

> *Transform kidney disease management from reactive treatment to predictive, preventive, and personalised care through AI â€” supporting clinicians, not replacing them.*

---

## ðŸŽ¯ What Is RenalCare AI?

RenalCare AI is a portfolio-grade, production-ready healthcare AI platform built for nephrologists, clinical pharmacists, researchers, and patients. It provides six integrated intelligence modules covering kidney risk assessment, clinical evidence retrieval, medication safety, renal nutrition, pharmacoeconomic analysis, and professional clinical report generation.

**Built on:** Published pharmacoeconomic research on hemodialysis economic burden in rural India Â· KDIGO 2024 Clinical Guidelines Â· Clinical Pharmacy expertise

---

## ðŸ¥ Platform Modules â€” Version 1

| Module | Description | Key Output |
|--------|-------------|------------|
| ðŸ«€ **Kidney Risk Assessment** | AI-powered CKD risk scoring from clinical biomarkers | Risk Score (0â€“100), CKD Stage, Recommendations |
| ðŸ”¬ **Clinical Evidence Intelligence** | RAG-powered KDIGO knowledge base + PDF upload | Evidence summaries, guideline insights |
| ðŸ’Š **Medication Intelligence** | PharmD AI â€” drug safety for CKD patients | Nephrotoxicity alerts, dose adjustment flags, interaction screening |
| ðŸ¥— **Kidney Nutrition Intelligence** | Stage-specific renal food analysis | Safe/Caution/Avoid with nutrient breakdowns |
| ðŸ’° **Pharmacoeconomic Intelligence** | Economic burden calculator (hemodialysis research methodology) | Annual cost, catastrophic expenditure analysis |
| ðŸ“‹ **AI Report Generator** | Professional PDF clinical report | Downloadable clinical-grade PDF |

---

## âš¡ Quick Start

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

# 4. Configure environment (optional â€” works without API keys)
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

## ðŸ”‘ API Keys (Optional)

The platform works **without any API keys** using rule-based fallbacks for all analysis.

For enhanced AI capabilities:
- **OpenAI** (GPT-4o-mini): Best quality â€” add `OPENAI_API_KEY` to `.env`
- **Google Gemini**: Free tier available â€” add `GOOGLE_API_KEY` to `.env`

```env
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AI...
```

---

## ðŸ—‚ï¸ Project Structure

```
renalcare-os/
â”œâ”€â”€ app.py                      â† Main Streamlit application
â”œâ”€â”€ requirements.txt
â”œâ”€â”€ .env.example                â† Environment variable template
â”‚
â”œâ”€â”€ pages/                      â† Streamlit page modules
â”‚   â”œâ”€â”€ home.py                 â† Dashboard homepage
â”‚   â”œâ”€â”€ kidney_risk.py          â† Risk Assessment
â”‚   â”œâ”€â”€ clinical_evidence.py    â† RAG Evidence Intelligence
â”‚   â”œâ”€â”€ medication_intelligence.py  â† PharmD AI Module
â”‚   â”œâ”€â”€ nutrition_intelligence.py   â† Renal Nutrition
â”‚   â”œâ”€â”€ pharmacoeconomics.py    â† Economic Burden
â”‚   â””â”€â”€ report_generator.py     â† PDF Report
â”‚
â”œâ”€â”€ models/
â”‚   â””â”€â”€ kidney_risk.py          â† CKD risk scoring model
â”‚
â”œâ”€â”€ medication/
â”‚   â””â”€â”€ checker.py              â† Drug safety engine
â”‚
â”œâ”€â”€ nutrition/
â”‚   â”œâ”€â”€ food_database.py        â† Renal food nutrient database
â”‚   â””â”€â”€ analyzer.py             â† Food suitability analyser
â”‚
â”œâ”€â”€ economics/
â”‚   â””â”€â”€ calculator.py           â† Pharmacoeconomic calculator
â”‚
â”œâ”€â”€ rag/
â”‚   â””â”€â”€ engine.py               â† Clinical RAG engine (FAISS + KDIGO KB)
â”‚
â”œâ”€â”€ reports/
â”‚   â””â”€â”€ generator.py            â† ReportLab PDF generator
â”‚
â”œâ”€â”€ components/
â”‚   â””â”€â”€ charts.py               â† Plotly chart components
â”‚
â”œâ”€â”€ utils/
â”‚   â”œâ”€â”€ constants.py            â† Clinical constants & thresholds
â”‚   â””â”€â”€ helpers.py              â† Shared utilities + AI client
â”‚
â”œâ”€â”€ data/
â”‚   â””â”€â”€ sample_patients.csv     â† Sample patient data
â”‚
â”œâ”€â”€ deployment/
â”‚   â”œâ”€â”€ Dockerfile
â”‚   â””â”€â”€ docker-compose.yml
â”‚
â””â”€â”€ .streamlit/
    â””â”€â”€ config.toml             â† Streamlit theme
```

---

## ðŸ› ï¸ Technology Stack

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

## ðŸ—ºï¸ Version Roadmap

### âœ… Version 1 â€” Current
- Kidney Risk Assessment
- Clinical Evidence Intelligence (RAG)
- Medication Intelligence Engine
- Kidney Nutrition Intelligence
- Pharmacoeconomic Intelligence
- AI Renal Report Generator

### ðŸ”® Version 2 â€” Planned
- CKD Progression Prediction (1/3/5-year ESRD risk)
- Patient Adherence Intelligence
- Dialysis Intelligence Module
- Research-grade ML models

### ðŸš€ Version 3 â€” Future
- Kidney Digital Twin (virtual patient simulation)
- Population Health Intelligence
- Hospital EHR Integration
- FHIR Connectivity
- Mobile Application

---

## âš•ï¸ Clinical Disclaimer

RenalCare AI is designed for **clinical decision support only**. It does not constitute medical advice and does not replace the clinical judgment of qualified physicians, pharmacists, or other licensed healthcare professionals. All clinical decisions must be made by authorised healthcare providers.

---

## ðŸ“š Clinical References

- KDIGO 2024 CKD Clinical Practice Guidelines
- KDIGO 2022 Diabetes Management in CKD
- KDIGO 2021 Blood Pressure Guideline
- KDIGO 2020 Nutrition in CKD
- ADA Standards of Medical Care 2024
- CREDENCE, DAPA-CKD, EMPA-KIDNEY Trials
- Published: "Economic burden and quality of life of maintenance hemodialysis patients in a rural area of South India â€” a pharmacoeconomic study"

---

## ðŸ—ï¸ Built With

**Clinical Pharmacy Intelligence** Â· **AI/ML Engineering** Â· **Healthcare Informatics** Â· **Pharmacoeconomics Research**

*RenalCare AI v1.0 â€” Portfolio & Clinical Preview*
