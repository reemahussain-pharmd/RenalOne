"""Medication Intelligence Engine — Sprint 2 Upgrade — RenalOne."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import math
import streamlit as st
from components.styles import sh
from medication.checker import MedicationInput, run_medication_review
from utils.constants import COMMON_DIAGNOSES, COMMON_MEDICATIONS, RENAL_DOSE_DRUGS


# ── Design tokens ────────────────────────────────────────────────────────────
SEVERITY_CONFIG = {
    "HIGH":     ("#EF4444", "#FEE2E2", "#991B1B", "🔴"),
    "MODERATE": ("#F59E0B", "#FEF3C7", "#92400E", "🟡"),
    "LOW":      ("#3B82F6", "#EFF6FF", "#1E40AF", "🔵"),
    "INFO":     ("#6366F1", "#EEF2FF", "#3730A3", "🟣"),
}

# ── ADR Intelligence Database ─────────────────────────────────────────────────
# Keyed by lowercase keyword found in drug name
ADR_DB = {
    "lisinopril": {
        "class": "ACE Inhibitor", "systems": ["Renal", "Electrolytes", "Cardiovascular"],
        "adrs": [
            {"name": "Hyperkalemia",          "sev": "MODERATE", "likelihood": "Common",   "monitoring": "K⁺ every 1–3 months"},
            {"name": "Acute Kidney Injury",   "sev": "HIGH",     "likelihood": "Uncommon", "monitoring": "SCr/eGFR 1–2 wk post-initiation"},
            {"name": "First-dose Hypotension","sev": "MODERATE", "likelihood": "Common",   "monitoring": "BP check post-first dose"},
            {"name": "Dry Cough",             "sev": "LOW",      "likelihood": "Very Common","monitoring": "Patient-reported; switch to ARB if intolerable"},
        ],
    },
    "ramipril": {
        "class": "ACE Inhibitor", "systems": ["Renal", "Electrolytes", "Cardiovascular"],
        "adrs": [
            {"name": "Hyperkalemia",        "sev": "MODERATE", "likelihood": "Common",   "monitoring": "K⁺ every 1–3 months"},
            {"name": "Acute Kidney Injury", "sev": "HIGH",     "likelihood": "Uncommon", "monitoring": "SCr/eGFR 1–2 wk post-initiation"},
            {"name": "Dry Cough",           "sev": "LOW",      "likelihood": "Very Common","monitoring": "Patient-reported"},
        ],
    },
    "losartan": {
        "class": "ARB", "systems": ["Renal", "Electrolytes", "Cardiovascular"],
        "adrs": [
            {"name": "Hyperkalemia",        "sev": "MODERATE", "likelihood": "Common",   "monitoring": "K⁺ every 1–3 months"},
            {"name": "Acute Kidney Injury", "sev": "HIGH",     "likelihood": "Uncommon", "monitoring": "SCr/eGFR post-initiation"},
            {"name": "Dizziness",           "sev": "LOW",      "likelihood": "Common",   "monitoring": "BP monitoring"},
        ],
    },
    "valsartan": {
        "class": "ARB", "systems": ["Renal", "Electrolytes", "Cardiovascular"],
        "adrs": [
            {"name": "Hyperkalemia",        "sev": "MODERATE", "likelihood": "Common",   "monitoring": "K⁺ every 1–3 months"},
            {"name": "Acute Kidney Injury", "sev": "HIGH",     "likelihood": "Uncommon", "monitoring": "SCr/eGFR post-initiation"},
        ],
    },
    "metformin": {
        "class": "Biguanide (Antidiabetic)", "systems": ["Metabolic", "GI", "Renal"],
        "adrs": [
            {"name": "Lactic Acidosis",      "sev": "HIGH",  "likelihood": "Rare (↑ risk if eGFR<30)", "monitoring": "eGFR q3–6mo; withhold if eGFR<30"},
            {"name": "GI Intolerance",       "sev": "LOW",   "likelihood": "Very Common",               "monitoring": "Patient-reported; start low, titrate slowly"},
            {"name": "Vitamin B12 Deficiency","sev": "LOW",  "likelihood": "Uncommon",                  "monitoring": "B12 levels annually with long-term use"},
        ],
    },
    "ibuprofen": {
        "class": "NSAID (Non-selective COX inhibitor)", "systems": ["Renal", "GI", "Cardiovascular"],
        "adrs": [
            {"name": "Acute Kidney Injury",   "sev": "HIGH",     "likelihood": "Common in CKD",  "monitoring": "SCr/eGFR, urine output"},
            {"name": "Fluid Retention/Edema", "sev": "MODERATE", "likelihood": "Common",          "monitoring": "Weight, fluid balance"},
            {"name": "GI Bleeding",           "sev": "MODERATE", "likelihood": "Uncommon",        "monitoring": "Stool occult blood, Hb"},
            {"name": "Hyperkalemia",          "sev": "MODERATE", "likelihood": "Common in CKD",  "monitoring": "K⁺ monitoring"},
        ],
    },
    "naproxen": {
        "class": "NSAID", "systems": ["Renal", "GI", "Cardiovascular"],
        "adrs": [
            {"name": "Acute Kidney Injury",   "sev": "HIGH",     "likelihood": "Common in CKD", "monitoring": "SCr/eGFR"},
            {"name": "GI Bleeding",           "sev": "MODERATE", "likelihood": "Uncommon",       "monitoring": "Hb, GI symptoms"},
        ],
    },
    "diclofenac": {
        "class": "NSAID", "systems": ["Renal", "GI", "Hepatic"],
        "adrs": [
            {"name": "Acute Kidney Injury",   "sev": "HIGH",     "likelihood": "Common in CKD", "monitoring": "SCr/eGFR"},
            {"name": "Hepatotoxicity",        "sev": "MODERATE", "likelihood": "Uncommon",       "monitoring": "LFTs"},
        ],
    },
    "spironolactone": {
        "class": "Potassium-Sparing Diuretic / MRA", "systems": ["Electrolytes", "Renal", "Endocrine"],
        "adrs": [
            {"name": "Hyperkalemia",      "sev": "HIGH",     "likelihood": "Common in CKD",  "monitoring": "K⁺ within 1 wk of initiation, then monthly"},
            {"name": "Hyponatremia",      "sev": "MODERATE", "likelihood": "Uncommon",        "monitoring": "Na⁺, fluid balance"},
            {"name": "Gynecomastia",      "sev": "LOW",      "likelihood": "Common",           "monitoring": "Patient-reported"},
            {"name": "AKI (high dose)",   "sev": "HIGH",     "likelihood": "Uncommon",         "monitoring": "SCr/eGFR monitoring"},
        ],
    },
    "furosemide": {
        "class": "Loop Diuretic", "systems": ["Renal", "Electrolytes", "Auditory"],
        "adrs": [
            {"name": "Hypokalemia",     "sev": "HIGH",     "likelihood": "Common",          "monitoring": "K⁺ every 1–2 months"},
            {"name": "Hyponatremia",    "sev": "MODERATE", "likelihood": "Uncommon",         "monitoring": "Na⁺, osmolality"},
            {"name": "Ototoxicity",     "sev": "HIGH",     "likelihood": "Rare (high dose)", "monitoring": "Auditory function with high IV doses"},
            {"name": "Dehydration/AKI", "sev": "HIGH",     "likelihood": "Uncommon",         "monitoring": "SCr/eGFR, urine output, weight"},
        ],
    },
    "digoxin": {
        "class": "Cardiac Glycoside", "systems": ["Cardiovascular", "Neurological", "GI"],
        "adrs": [
            {"name": "Digoxin Toxicity",  "sev": "HIGH",     "likelihood": "Common in CKD",   "monitoring": "Digoxin levels, ECG, K⁺"},
            {"name": "Bradycardia/Heart Block","sev": "HIGH", "likelihood": "Uncommon",         "monitoring": "ECG, heart rate"},
            {"name": "Nausea/Vomiting",   "sev": "LOW",      "likelihood": "Common (toxicity)", "monitoring": "Patient-reported"},
        ],
    },
    "atorvastatin": {
        "class": "Statin (HMG-CoA Reductase Inhibitor)", "systems": ["Musculoskeletal", "Hepatic"],
        "adrs": [
            {"name": "Myopathy/Rhabdomyolysis", "sev": "HIGH",     "likelihood": "Rare (↑ in CKD)", "monitoring": "CK if muscle pain; LFTs at baseline"},
            {"name": "Hepatotoxicity",           "sev": "MODERATE", "likelihood": "Rare",             "monitoring": "LFTs at baseline and if symptomatic"},
        ],
    },
    "warfarin": {
        "class": "Vitamin K Antagonist (Anticoagulant)", "systems": ["Haematological", "Renal"],
        "adrs": [
            {"name": "Major Bleeding",      "sev": "HIGH",     "likelihood": "Uncommon",      "monitoring": "INR every 1–4 weeks"},
            {"name": "Over-anticoagulation","sev": "HIGH",     "likelihood": "Common in CKD", "monitoring": "INR; CKD alters pharmacokinetics"},
        ],
    },
    "gabapentin": {
        "class": "Anticonvulsant/Neuropathic Pain Agent", "systems": ["Neurological", "Renal"],
        "adrs": [
            {"name": "Excessive Sedation",      "sev": "HIGH",     "likelihood": "Common in CKD",  "monitoring": "Sedation score; dose reduce per eGFR"},
            {"name": "Dizziness/Ataxia",        "sev": "MODERATE", "likelihood": "Common",          "monitoring": "Patient-reported; fall risk assessment"},
            {"name": "Drug Accumulation (CKD)", "sev": "HIGH",     "likelihood": "Common if eGFR<60","monitoring": "eGFR-based dose reduction essential"},
        ],
    },
    "allopurinol": {
        "class": "Xanthine Oxidase Inhibitor", "systems": ["Renal", "Dermatological", "Haematological"],
        "adrs": [
            {"name": "SJS/TEN (rare but severe)", "sev": "HIGH",     "likelihood": "Rare (↑ with HLA-B*5801)", "monitoring": "Skin rash — stop immediately if rash appears"},
            {"name": "Allopurinol Hypersensitivity Syndrome","sev":"HIGH","likelihood":"Rare","monitoring":"Rash, fever, eosinophilia"},
            {"name": "Drug Accumulation (CKD)", "sev": "MODERATE", "likelihood": "Common in CKD", "monitoring": "Dose reduce: 100 mg/day per eGFR 30–60"},
        ],
    },
}


# ── Renal Dose Adjustment Reference ──────────────────────────────────────────
DOSE_MATRIX_DATA = {
    "Metformin":        {"threshold": 45, "safe": "eGFR≥45",  "caution": "eGFR 30–44 (reduce dose)", "contraindicated": "eGFR<30",  "monitoring": "eGFR q3–6mo"},
    "Gabapentin":       {"threshold": 60, "safe": "eGFR≥60",  "caution": "eGFR 30–59 (reduce dose)", "contraindicated": "—",         "monitoring": "Sedation score, renal function"},
    "Pregabalin":       {"threshold": 60, "safe": "eGFR≥60",  "caution": "eGFR 30–59 (reduce dose)", "contraindicated": "—",         "monitoring": "Sedation score"},
    "Digoxin":          {"threshold": 60, "safe": "eGFR≥60",  "caution": "eGFR <60 (reduce, monitor levels)", "contraindicated": "—", "monitoring": "Digoxin level, K⁺, ECG"},
    "Lisinopril":       {"threshold": 30, "safe": "eGFR≥30",  "caution": "eGFR 15–29 (start low, titrate)", "contraindicated": "eGFR<15", "monitoring": "SCr, K⁺ q1–2wk post-initiation"},
    "Atenolol":         {"threshold": 35, "safe": "eGFR≥35",  "caution": "eGFR 15–35 (reduce frequency)", "contraindicated": "—",   "monitoring": "HR, BP"},
    "Allopurinol":      {"threshold": 60, "safe": "eGFR≥60",  "caution": "eGFR 30–59: max 100 mg/day",    "contraindicated": "—",   "monitoring": "Skin rash, uric acid, LFTs"},
    "Metoclopramide":   {"threshold": 40, "safe": "eGFR≥40",  "caution": "eGFR <40 (reduce by 50%)",       "contraindicated": "—",   "monitoring": "EPS symptoms, sedation"},
    "Spironolactone":   {"threshold": 30, "safe": "eGFR≥30",  "caution": "eGFR 15–30 (use with caution)", "contraindicated": "eGFR<15", "monitoring": "K⁺ within 1 week, then monthly"},
    "Furosemide":       {"threshold": 30, "safe": "All stages (higher doses in CKD)", "caution": "Higher doses needed in CKD", "contraindicated": "Anuria", "monitoring": "K⁺, Na⁺, SCr, urine output"},
}


def render():
    sh("""
    <div class="page-header">
        <div style="display:flex;align-items:flex-start;justify-content:space-between;">
            <div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.5rem;">
                    <span style="font-size:1.6rem;">&#x1f48a;</span>
                    <span style="background:rgba(255,255,255,0.15);color:rgba(255,255,255,0.9);font-size:0.7rem;font-weight:700;padding:3px 10px;border-radius:20px;letter-spacing:0.06em;">PHARMD SIGNATURE MODULE</span>
                    <span style="background:rgba(99,102,241,0.25);color:#A5B4FC;font-size:0.7rem;font-weight:700;padding:3px 10px;border-radius:20px;letter-spacing:0.05em;">Sprint 2 &#x2014; Enhanced</span>
                </div>
                <h1 style="color:white !important;font-size:1.7rem !important;font-weight:800 !important;margin:0 0 0.3rem 0 !important;letter-spacing:-0.02em;">Medication Intelligence Engine</h1>
                <p style="color:rgba(255,255,255,0.72) !important;font-size:0.88rem !important;margin:0 !important;">
                    ADR profiling &bull; Renal dose matrix &bull; Interaction network &bull; Clinical Pharmacist AI Review
                </p>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.7rem;color:rgba(255,255,255,0.5);text-transform:uppercase;letter-spacing:0.07em;">Evidence Base</div>
                <div style="font-size:0.85rem;color:rgba(255,255,255,0.85);font-weight:600;">KDIGO 2024</div>
                <div style="font-size:0.85rem;color:rgba(255,255,255,0.85);font-weight:600;">Micromedex / BNF</div>
            </div>
        </div>
    </div>
    """)

    left_col, right_col = st.columns([1.1, 1.5])

    with left_col:
        with st.form("med_form"):
            sh('<div class="section-title-accent"><span>&#x1f9fe;</span> Patient Profile</div>')
            egfr       = st.number_input("eGFR (mL/min/1.73m²)", min_value=1, max_value=150, value=45)
            creatinine = st.number_input("Serum Creatinine (mg/dL)", 0.4, 15.0, 1.8, 0.1)

            sh('<div style="font-size:0.83rem;font-weight:600;color:#374151;margin:0.8rem 0 0.3rem;">Active Diagnoses</div>')
            diagnoses = st.multiselect("Diagnoses", options=COMMON_DIAGNOSES,
                                       default=["Chronic Kidney Disease", "Hypertension"],
                                       label_visibility="collapsed")

            sh('<div style="font-size:0.83rem;font-weight:600;color:#374151;margin:0.8rem 0 0.3rem;">Current Medications</div>')
            medications = st.multiselect("Medications", options=COMMON_MEDICATIONS,
                                         default=["Metformin", "Ibuprofen", "Lisinopril"],
                                         label_visibility="collapsed")

            sh('<div style="font-size:0.83rem;font-weight:600;color:#374151;margin:0.8rem 0 0.3rem;">Laboratory Values</div>')
            c1, c2    = st.columns(2)
            with c1:  potassium  = st.number_input("Potassium (mEq/L)",  2.5, 7.0,  4.2, 0.1)
            with c2:  sodium     = st.number_input("Sodium (mEq/L)",     120, 160,  138)
            hemoglobin = st.number_input("Hemoglobin (g/dL)", 5.0, 18.0, 10.5, 0.1)

            submitted = st.form_submit_button("&#x1f50d;  Run Medication Review",
                                              use_container_width=True, type="primary")

    with right_col:
        if submitted and medications:
            with st.spinner("Running PharmD medication review..."):
                inp = MedicationInput(
                    egfr=float(egfr), serum_creatinine=float(creatinine),
                    diagnoses=diagnoses, medications=medications,
                    potassium=potassium, sodium=sodium, hemoglobin=hemoglobin,
                )
                result = run_medication_review(inp)
                st.session_state.med_result      = result
                st.session_state.med_input       = inp
                st.session_state.med_input_count = len(medications)

        if st.session_state.get("med_result"):
            result    = st.session_state.med_result
            inp       = st.session_state.get("med_input")
            med_count = st.session_state.get("med_input_count", 0)
            medications_used = getattr(inp, "medications", medications) if inp else medications
            egfr_used        = getattr(inp, "egfr", egfr)              if inp else egfr
            _render_results(result, med_count, medications_used, egfr_used)
        elif submitted and not medications:
            sh('<div class="alert alert-warning">&#x26a0;&#xfe0f; Please select at least one medication to review.</div>')
        else:
            _render_placeholder()


# ─────────────────────────────────────────────────────────────────────────────
# Results
# ─────────────────────────────────────────────────────────────────────────────

def _render_results(result, med_count, medications, egfr):
    flags = result.flags

    # Deduplicate: group by primary drug name
    drug_groups = {}
    for flag in flags:
        primary = flag.drug.split("+")[0].strip() if "+" in flag.drug else flag.drug
        drug_groups.setdefault(primary, []).append(flag)

    high_ct  = sum(1 for f in flags if f.severity.upper() == "HIGH")
    mod_ct   = sum(1 for f in flags if f.severity.upper() == "MODERATE")
    low_ct   = sum(1 for f in flags if f.severity.upper() not in ("HIGH", "MODERATE"))

    risk_color = "#EF4444" if high_ct else ("#F59E0B" if mod_ct else "#10B981")
    risk_label = "HIGH RISK"     if high_ct else ("MODERATE RISK" if mod_ct else "LOW RISK")
    risk_bg    = "#FEE2E2"       if high_ct else ("#FEF3C7"       if mod_ct else "#D1FAE5")

    # ── Summary banner ──────────────────────────────────────────────────────
    sh(f'<div style="background:{risk_bg};border:2px solid {risk_color};border-radius:14px;padding:1.2rem 1.5rem;margin-bottom:1rem;display:flex;align-items:center;justify-content:space-between;"><div><div style="font-size:0.72rem;font-weight:700;color:{risk_color};letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.2rem;">Medication Review Complete</div><div style="font-size:1.4rem;font-weight:800;color:{risk_color};">{risk_label}</div><div style="font-size:0.82rem;color:#334155;margin-top:0.2rem;">{len(flags)} flags identified &bull; {med_count} medications reviewed &bull; {len(drug_groups)} drugs with concerns</div></div><div style="text-align:right;"><div style="font-size:2rem;font-weight:900;color:{risk_color};">{high_ct}</div><div style="font-size:0.72rem;font-weight:700;color:{risk_color};letter-spacing:0.06em;text-transform:uppercase;">Critical Alerts</div></div></div>')

    # ── Severity pills ───────────────────────────────────────────────────────
    sh(f'<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:1rem;"><span style="background:#FEE2E2;color:#991B1B;padding:4px 12px;border-radius:20px;font-size:0.77rem;font-weight:700;">&#x1f534; {high_ct} High</span><span style="background:#FEF3C7;color:#92400E;padding:4px 12px;border-radius:20px;font-size:0.77rem;font-weight:700;">&#x1f7e1; {mod_ct} Moderate</span><span style="background:#EFF6FF;color:#1E40AF;padding:4px 12px;border-radius:20px;font-size:0.77rem;font-weight:700;">&#x1f535; {low_ct} Informational</span><span style="background:#EEF2FF;color:#4338CA;padding:4px 12px;border-radius:20px;font-size:0.77rem;font-weight:700;">&#x1f4bc; PharmD Analysis</span></div>')

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "🚨 Drug Alerts",
        "💊 Dose Matrix",
        "⚡ Interactions",
        "🩺 Clinical Review",
    ])

    with tab1:
        _render_drug_alerts(drug_groups, flags, medications, egfr)

    with tab2:
        _render_dose_matrix(medications, egfr)

    with tab3:
        _render_interaction_network(flags, medications)

    with tab4:
        _render_clinical_review(result)


# ─────────────────────────────────────────────────────────────────────────────
# Tab 1 — Drug Alerts (deduplicated) + ADR Intelligence
# ─────────────────────────────────────────────────────────────────────────────

def _render_drug_alerts(drug_groups: dict, flags: list, medications: list, egfr: float):
    if not drug_groups:
        sh('<div class="alert alert-success">&#x2705; <strong>No drug alerts identified.</strong> All selected medications appear appropriate for the entered eGFR and clinical context.</div>')
        return

    sh('<div class="section-title"><span>&#x1f6a8;</span> Drug Safety Alerts <span style="font-size:0.72rem;font-weight:500;color:#64748B;">(deduplicated by drug)</span></div>')

    for drug, drug_flags in drug_groups.items():
        worst_sev = "HIGH" if any(f.severity.upper() == "HIGH" for f in drug_flags) else \
                    ("MODERATE" if any(f.severity.upper() == "MODERATE" for f in drug_flags) else "LOW")
        color, bg, text_c, dot = SEVERITY_CONFIG.get(worst_sev, SEVERITY_CONFIG["LOW"])

        # Flag type badges
        flag_badges = "".join(
            f'<span style="background:{color}20;color:{text_c};font-size:0.65rem;font-weight:700;padding:2px 7px;border-radius:4px;border:1px solid {color}40;white-space:nowrap;">{f.flag_type.replace("_"," ")}</span>'
            for f in drug_flags
        )
        # Action items
        actions_html = "".join(
            f'<div style="background:rgba(255,255,255,0.7);border-radius:5px;padding:4px 8px;font-size:0.78rem;color:#1E3A5F;margin-top:3px;"><strong>&#x1f4a1; {f.flag_type.replace("_"," ")}:</strong> {f.action}</div>'
            for f in drug_flags
        )
        details_html = "".join(
            f'<div style="font-size:0.82rem;color:#374151;line-height:1.5;margin-bottom:4px;">{f.detail}</div>'
            for f in drug_flags
        )

        sh(f'<div style="background:{bg}30;border:1px solid {color}50;border-left:4px solid {color};border-radius:8px;padding:0.9rem 1rem;margin-bottom:0.6rem;"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;"><div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;"><span style="font-size:1rem;">{dot}</span><span style="font-size:0.92rem;font-weight:800;color:#0F172A;">{drug}</span>{flag_badges}</div><span style="background:{color};color:white;border-radius:5px;padding:3px 8px;font-size:0.68rem;font-weight:700;white-space:nowrap;">{worst_sev}</span></div>{details_html}{actions_html}</div>')

    # ── ADR Intelligence ─────────────────────────────────────────────────────
    sh('<div style="margin-top:1rem;"></div>')
    sh('<div class="section-title"><span>&#x1f9ec;</span> ADR Intelligence <span style="background:#EEF2FF;color:#4338CA;font-size:0.65rem;font-weight:700;padding:2px 8px;border-radius:10px;margin-left:6px;">PharmD Clinical Logic</span></div>')

    adr_found = False
    for med in medications:
        med_lower = med.lower()
        matched_key = next((k for k in ADR_DB if k in med_lower or med_lower in k), None)
        if not matched_key:
            continue
        adr_found = True
        adr_info = ADR_DB[matched_key]
        systems_html = "".join(
            f'<span style="background:#F1F5F9;color:#475569;font-size:0.65rem;font-weight:600;padding:2px 7px;border-radius:4px;">{s}</span>'
            for s in adr_info["systems"]
        )
        sh(f'<div style="background:white;border:1px solid #E2E8F0;border-radius:10px;padding:0.85rem 1rem;margin-bottom:0.6rem;"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.6rem;"><div><span style="font-size:0.88rem;font-weight:800;color:#0F172A;">{med}</span><span style="font-size:0.72rem;color:#64748B;margin-left:8px;">{adr_info["class"]}</span></div><div style="display:flex;gap:4px;flex-wrap:wrap;">{systems_html}</div></div>')

        for adr in adr_info["adrs"]:
            ac, abg, at, _ = SEVERITY_CONFIG.get(adr["sev"], SEVERITY_CONFIG["LOW"])
            sh(f'<div style="display:grid;grid-template-columns:2fr 1fr 1.5fr 2fr;gap:4px;align-items:center;background:{abg}40;border-radius:5px;padding:4px 8px;margin-bottom:3px;"><span style="font-size:0.78rem;font-weight:600;color:#1E293B;">{adr["name"]}</span><span style="background:{ac};color:white;font-size:0.62rem;font-weight:700;padding:1px 6px;border-radius:4px;text-align:center;">{adr["sev"]}</span><span style="font-size:0.72rem;color:#475569;">{adr["likelihood"]}</span><span style="font-size:0.72rem;color:#374151;">&#x1f50d; {adr["monitoring"]}</span></div>')

        sh('</div>')

    if not adr_found:
        sh('<div style="font-size:0.83rem;color:#64748B;padding:0.8rem;">No ADR profiles available for selected medications in current database.</div>')


# ─────────────────────────────────────────────────────────────────────────────
# Tab 2 — Renal Dose Adjustment Matrix
# ─────────────────────────────────────────────────────────────────────────────

def _render_dose_matrix(medications: list, egfr: float):
    sh('<div class="section-title"><span>&#x1f4ca;</span> Renal Dose Adjustment Matrix <span style="background:#EEF2FF;color:#4338CA;font-size:0.65rem;font-weight:700;padding:2px 8px;border-radius:10px;margin-left:6px;">PharmD Clinical Logic</span></div>')
    sh(f'<div style="font-size:0.8rem;color:#64748B;margin-bottom:0.8rem;">Patient eGFR: <strong style="color:#1E3A5F;">{egfr:.0f} mL/min/1.73m²</strong> &mdash; Color coding reflects action urgency at current eGFR</div>')

    # Header
    sh('<div style="display:grid;grid-template-columns:1.4fr 1fr 1.5fr 1.5fr 1.5fr;gap:3px;margin-bottom:4px;"><div style="font-size:0.68rem;font-weight:700;color:#64748B;text-transform:uppercase;padding:4px 6px;">Drug</div><div style="font-size:0.68rem;font-weight:700;color:#64748B;text-transform:uppercase;padding:4px 6px;">eGFR Threshold</div><div style="font-size:0.68rem;font-weight:700;color:#64748B;text-transform:uppercase;padding:4px 6px;">Safe Range</div><div style="font-size:0.68rem;font-weight:700;color:#64748B;text-transform:uppercase;padding:4px 6px;">Caution</div><div style="font-size:0.68rem;font-weight:700;color:#64748B;text-transform:uppercase;padding:4px 6px;">Monitoring</div></div>')

    med_lower_list = [m.lower() for m in medications]
    rows_shown = 0

    for drug_name, data in DOSE_MATRIX_DATA.items():
        if not any(drug_name.lower() in ml or ml in drug_name.lower() for ml in med_lower_list):
            continue
        rows_shown += 1
        threshold = data["threshold"]
        if egfr < threshold * 0.5:
            row_bg = "#FEE2E2"; status_c = "#EF4444"; status = "DOSE REDUCE"
        elif egfr < threshold:
            row_bg = "#FEF3C7"; status_c = "#F59E0B"; status = "CAUTION"
        else:
            row_bg = "#F0FDF4"; status_c = "#10B981"; status = "SAFE"

        ci = data.get("contraindicated", "—")
        ci_html = f'<span style="color:#EF4444;font-weight:600;">{ci}</span>' if ci != "—" else "—"

        sh(f'<div style="display:grid;grid-template-columns:1.4fr 1fr 1.5fr 1.5fr 1.5fr;gap:3px;background:{row_bg};border-radius:6px;padding:6px;margin-bottom:3px;align-items:center;"><div style="font-size:0.8rem;font-weight:700;color:#0F172A;">{drug_name}<br><span style="background:{status_c};color:white;font-size:0.58rem;font-weight:700;padding:1px 5px;border-radius:3px;">{status}</span></div><div style="font-size:0.78rem;color:#374151;">eGFR &lt; {threshold}</div><div style="font-size:0.75rem;color:#374151;">{data["safe"]}</div><div style="font-size:0.75rem;color:#374151;">{data["caution"]}</div><div style="font-size:0.72rem;color:#475569;">&#x1f4dd; {data["monitoring"]}</div></div>')

    if rows_shown == 0:
        sh('<div style="text-align:center;padding:1.5rem;color:#64748B;font-size:0.84rem;">No renal dose adjustment data found for currently selected medications.</div>')

    # Full reference table toggle
    sh('<div style="margin-top:1rem;"></div>')
    with st.expander("📋 Full Renal Dose Reference (All CKD Medications)"):
        sh('<div style="font-size:0.78rem;color:#64748B;margin-bottom:0.6rem;">Complete reference regardless of current selection — for clinical reference use.</div>')
        sh('<div style="display:grid;grid-template-columns:1.4fr 1fr 1.5fr 1.5fr 1.5fr;gap:3px;margin-bottom:4px;"><div style="font-size:0.65rem;font-weight:700;color:#64748B;text-transform:uppercase;padding:3px 6px;">Drug</div><div style="font-size:0.65rem;font-weight:700;color:#64748B;text-transform:uppercase;padding:3px 6px;">Threshold</div><div style="font-size:0.65rem;font-weight:700;color:#64748B;text-transform:uppercase;padding:3px 6px;">Safe</div><div style="font-size:0.65rem;font-weight:700;color:#64748B;text-transform:uppercase;padding:3px 6px;">Caution</div><div style="font-size:0.65rem;font-weight:700;color:#64748B;text-transform:uppercase;padding:3px 6px;">Monitoring</div></div>')
        for drug_name, data in DOSE_MATRIX_DATA.items():
            sh(f'<div style="display:grid;grid-template-columns:1.4fr 1fr 1.5fr 1.5fr 1.5fr;gap:3px;background:#F8FAFC;border-radius:4px;padding:5px 6px;margin-bottom:2px;"><div style="font-size:0.76rem;font-weight:600;color:#0F172A;">{drug_name}</div><div style="font-size:0.73rem;color:#374151;">eGFR &lt; {data["threshold"]}</div><div style="font-size:0.72rem;color:#374151;">{data["safe"]}</div><div style="font-size:0.72rem;color:#374151;">{data["caution"]}</div><div style="font-size:0.7rem;color:#475569;">{data["monitoring"]}</div></div>')


# ─────────────────────────────────────────────────────────────────────────────
# Tab 3 — Drug Interaction Network
# ─────────────────────────────────────────────────────────────────────────────

def _render_interaction_network(flags: list, medications: list):
    interaction_flags = [f for f in flags if f.flag_type == "Interaction"]

    sh('<div class="section-title"><span>&#x26a1;</span> Drug Interaction Network</div>')

    if not medications or len(medications) < 2:
        sh('<div style="text-align:center;padding:1.5rem;color:#64748B;">Add at least 2 medications to visualize interactions.</div>')
        return

    # Build network with Plotly
    try:
        import plotly.graph_objects as go

        n = len(medications)
        # Place nodes in a circle
        angles = [2 * math.pi * i / n for i in range(n)]
        x_nodes = [math.cos(a) for a in angles]
        y_nodes = [math.sin(a) for a in angles]

        # Parse interaction flags to find which pairs interact
        SEV_EDGE = {"High": ("#EF4444", "Major", 3), "Moderate": ("#F59E0B", "Moderate", 2), "Low": ("#3B82F6", "Minor", 1)}
        med_lower = [m.lower() for m in medications]

        edge_traces = []
        for flag in interaction_flags:
            involved = [i for i, ml in enumerate(med_lower)
                        if any(part.strip().lower() in ml or ml in part.strip().lower()
                               for part in flag.drug.replace("+","/").replace("(","").replace(")","").split("/"))]
            if len(involved) >= 2:
                i1, i2 = involved[0], involved[1]
            elif len(involved) == 1:
                # Connect to next med as fallback
                i1 = involved[0]
                i2 = (i1 + 1) % n
            else:
                i1, i2 = 0, min(1, n - 1)

            c, lbl, width = SEV_EDGE.get(flag.severity, SEV_EDGE["Low"])
            edge_traces.append(go.Scatter(
                x=[x_nodes[i1], x_nodes[i2], None],
                y=[y_nodes[i1], y_nodes[i2], None],
                mode="lines",
                line=dict(color=c, width=width + 1),
                name=f"{lbl}: {flag.drug}",
                hoverinfo="name",
                showlegend=True,
            ))

        # Node trace
        node_colors = []
        for i, med in enumerate(medications):
            ml = med.lower()
            is_involved = any(
                any(part.strip().lower() in ml or ml in part.strip().lower()
                    for part in f.drug.replace("+","/").replace("(","").replace(")","").split("/"))
                for f in interaction_flags
            )
            node_colors.append("#EF4444" if is_involved else "#10B981")

        node_trace = go.Scatter(
            x=x_nodes, y=y_nodes,
            mode="markers+text",
            marker=dict(size=22, color=node_colors, line=dict(color="white", width=2)),
            text=[m[:12] + ("…" if len(m) > 12 else "") for m in medications],
            textposition="top center",
            textfont=dict(size=9, color="#1E293B"),
            hovertext=medications,
            hoverinfo="text",
            showlegend=False,
        )

        fig = go.Figure(data=[*edge_traces, node_trace])
        fig.update_layout(
            height=320,
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(248,250,252,1)",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(size=9)),
            title=dict(text="Medication Interaction Map", font=dict(size=11, color="#1E3A5F"), x=0.5),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    except Exception as e:
        sh(f'<div style="color:#64748B;font-size:0.82rem;padding:0.8rem;">Network visualization unavailable: {e}</div>')

    # ── Interaction list ─────────────────────────────────────────────────────
    if interaction_flags:
        sh('<div class="section-title" style="margin-top:0.5rem;"><span>&#x1f4cb;</span> Interaction Details</div>')
        for flag in interaction_flags:
            c, bg, tc, dot = SEVERITY_CONFIG.get(flag.severity.upper(), SEVERITY_CONFIG["MODERATE"])
            sh(f'<div style="background:{bg}40;border-left:3px solid {c};border-radius:0 8px 8px 0;padding:0.7rem 0.9rem;margin-bottom:0.4rem;"><div style="display:flex;align-items:center;gap:8px;margin-bottom:0.3rem;"><span>{dot}</span><span style="font-size:0.85rem;font-weight:700;color:#0F172A;">{flag.drug}</span><span style="background:{c};color:white;font-size:0.62rem;font-weight:700;padding:1px 7px;border-radius:4px;">{flag.severity.upper()}</span></div><div style="font-size:0.8rem;color:#374151;margin-bottom:0.3rem;">{flag.detail}</div><div style="font-size:0.78rem;color:#1E3A5F;font-weight:500;">&#x1f4a1; {flag.action}</div></div>')
    else:
        sh('<div style="background:#F0FDF4;border:1px solid #86EFAC;border-radius:8px;padding:0.8rem 1rem;margin-top:0.5rem;font-size:0.83rem;color:#065F46;">&#x2705; No significant drug-drug interactions detected among selected medications.</div>')

    # ── Interaction legend ───────────────────────────────────────────────────
    sh('<div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:0.6rem;"><span style="font-size:0.72rem;color:#64748B;">Network legend:</span><span style="font-size:0.72rem;color:#EF4444;font-weight:600;">&#x25cf; Major</span><span style="font-size:0.72rem;color:#F59E0B;font-weight:600;">&#x25cf; Moderate</span><span style="font-size:0.72rem;color:#3B82F6;font-weight:600;">&#x25cf; Minor</span><span style="font-size:0.72rem;color:#10B981;font-weight:600;">&#x25cf; No interaction</span></div>')


# ─────────────────────────────────────────────────────────────────────────────
# Tab 4 — Clinical Pharmacist AI Review
# ─────────────────────────────────────────────────────────────────────────────

def _render_clinical_review(result):
    # ── Clinical Pharmacist AI Review (renamed from AI Clinical Narrative) ───
    sh("""
    <div style="background:linear-gradient(135deg,#EEF2FF,#F0FDF4);border-radius:12px;padding:1.2rem;border:1px solid #C7D2FE;margin-bottom:0.8rem;">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.6rem;">
            <span style="font-size:1.1rem;">&#x1f469;&#x200d;&#x2695;&#xfe0f;</span>
            <span style="font-size:0.88rem;font-weight:800;color:#3730A3;">Clinical Pharmacist AI Review</span>
            <span style="background:#EEF2FF;color:#6366F1;font-size:0.65rem;font-weight:700;padding:2px 8px;border-radius:20px;letter-spacing:0.05em;">GPT-4o</span>
            <span style="background:#EEF2FF;color:#4338CA;font-size:0.65rem;font-weight:700;padding:2px 8px;border-radius:20px;">PharmD Logic</span>
        </div>
    """)

    if result.ai_narrative:
        # Parse the narrative into labelled sections for display
        narrative = result.ai_narrative
        sh(f'<div style="font-size:0.85rem;color:#1E293B;line-height:1.7;">{narrative.replace(chr(10), "<br>")}</div>')
    else:
        sh('<div style="font-size:0.83rem;color:#64748B;">AI narrative unavailable — see rule-based findings in Drug Alerts tab.</div>')

    sh('</div>')

    # ── Drug Related Problems ─────────────────────────────────────────────────
    high_flags = [f for f in result.flags if f.severity.upper() == "HIGH"]
    if high_flags:
        sh('<div class="section-title"><span>&#x26a0;&#xfe0f;</span> Drug Related Problems (DRPs)</div>')
        for f in high_flags:
            sh(f'<div style="background:#FEF2F2;border:1px solid #FCA5A5;border-radius:8px;padding:0.65rem 0.9rem;margin-bottom:0.4rem;"><span style="font-size:0.8rem;font-weight:700;color:#991B1B;">&#x1f534; {f.drug}</span> &mdash; <span style="font-size:0.8rem;color:#374151;">{f.detail}</span></div>')

    # ── Monitoring Plan ───────────────────────────────────────────────────────
    monitoring = getattr(result, "monitoring_requirements", [])
    if monitoring:
        sh('<div class="section-title" style="margin-top:0.8rem;"><span>&#x1f9ea;</span> Monitoring Plan</div>')
        mon_html = '<div style="display:flex;flex-wrap:wrap;gap:6px;">' + \
                   "".join(f'<span style="background:#EEF2FF;color:#3730A3;font-size:0.78rem;font-weight:600;padding:5px 12px;border-radius:8px;">&#x1f4dd; {m}</span>' for m in monitoring) + \
                   '</div>'
        sh(mon_html)

    # ── Clinical Considerations ───────────────────────────────────────────────
    considerations = getattr(result, "clinical_considerations", [])
    if considerations:
        sh('<div style="margin-top:0.8rem;"></div>')
        sh('<div class="section-title"><span>&#x1f4da;</span> Clinical Considerations</div>')
        for c in considerations:
            sh(f'<div style="font-size:0.82rem;color:#374151;padding:4px 0;border-bottom:1px solid #F1F5F9;">&#x2022; {c}</div>')

    # ── Evidence Sources ──────────────────────────────────────────────────────
    sh("""
    <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:10px;padding:0.8rem 1rem;margin-top:1rem;">
        <div style="font-size:0.72rem;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.5rem;">&#x1f4da; Evidence Sources</div>
        <div style="display:flex;flex-direction:column;gap:4px;">
            <div style="font-size:0.77rem;color:#374151;"><span style="background:#EFF6FF;color:#1D4ED8;font-size:0.63rem;font-weight:700;padding:1px 6px;border-radius:4px;margin-right:5px;">Guideline</span>KDIGO 2024 &mdash; Pharmacological Treatment in CKD</div>
            <div style="font-size:0.77rem;color:#374151;"><span style="background:#F0FDF4;color:#065F46;font-size:0.63rem;font-weight:700;padding:1px 6px;border-radius:4px;margin-right:5px;">Drug DB</span>Micromedex Drug Interactions &amp; Renal Dosing Reference</div>
            <div style="font-size:0.77rem;color:#374151;"><span style="background:#FEF3C7;color:#92400E;font-size:0.63rem;font-weight:700;padding:1px 6px;border-radius:4px;margin-right:5px;">Reference</span>BNF / eMC &mdash; Renal Impairment Dose Adjustments</div>
            <div style="font-size:0.77rem;color:#374151;"><span style="background:#EEF2FF;color:#3730A3;font-size:0.63rem;font-weight:700;padding:1px 6px;border-radius:4px;margin-right:5px;">Guideline</span>ADA 2024 &mdash; CKD &amp; Antidiabetic Agent Selection</div>
        </div>
        <div style="margin-top:0.5rem;font-size:0.72rem;color:#94A3B8;font-style:italic;">This review is for clinical decision support only and does not replace pharmacist or physician judgment.</div>
    </div>
    """)


def _render_placeholder():
    sh("""
    <div style="background:white;border:2px dashed #E2E8F0;border-radius:16px;padding:3rem;text-align:center;">
        <div style="font-size:3rem;margin-bottom:1rem;">&#x1f48a;</div>
        <div style="font-size:1rem;font-weight:700;color:#0F172A;margin-bottom:0.5rem;">Medication Intelligence Engine</div>
        <div style="font-size:0.84rem;color:#64748B;max-width:380px;margin:0 auto;line-height:1.6;">Complete the patient profile to run a PharmD-grade medication review: ADR profiling, renal dose adjustment matrix, drug interaction network, and clinical pharmacist AI synthesis.</div>
        <div style="margin-top:1.5rem;display:flex;gap:8px;justify-content:center;flex-wrap:wrap;">
            <span style="background:#FEE2E2;color:#991B1B;font-size:0.78rem;font-weight:600;padding:5px 12px;border-radius:8px;">ADR Intelligence</span>
            <span style="background:#FEF3C7;color:#92400E;font-size:0.78rem;font-weight:600;padding:5px 12px;border-radius:8px;">Dose Adjustment Matrix</span>
            <span style="background:#EEF2FF;color:#3730A3;font-size:0.78rem;font-weight:600;padding:5px 12px;border-radius:8px;">Interaction Network</span>
            <span style="background:#F0FDF4;color:#065F46;font-size:0.78rem;font-weight:600;padding:5px 12px;border-radius:8px;">Clinical Pharmacist Review</span>
        </div>
    </div>
    """)
