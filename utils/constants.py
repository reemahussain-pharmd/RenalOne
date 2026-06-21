"""Shared constants for RenalCare AI."""

# CKD Stage definitions by eGFR
CKD_STAGES = {
    1: {"label": "Stage 1", "egfr_range": (90, float("inf")), "description": "Normal or High", "color": "#27ae60"},
    2: {"label": "Stage 2", "egfr_range": (60, 90), "description": "Mildly Decreased", "color": "#2ecc71"},
    3: {"label": "Stage 3a", "egfr_range": (45, 60), "description": "Mildly to Moderately Decreased", "color": "#f39c12"},
    4: {"label": "Stage 3b", "egfr_range": (30, 45), "description": "Moderately to Severely Decreased", "color": "#e67e22"},
    5: {"label": "Stage 4", "egfr_range": (15, 30), "description": "Severely Decreased", "color": "#e74c3c"},
    6: {"label": "Stage 5", "egfr_range": (0, 15), "description": "Kidney Failure (ESRD)", "color": "#8e44ad"},
}

RISK_LEVELS = {
    "Low": {"color": "#27ae60", "bg": "#d5f5e3", "icon": "✅", "score_range": (0, 25)},
    "Moderate": {"color": "#f39c12", "bg": "#fef9e7", "icon": "⚠️", "score_range": (25, 50)},
    "High": {"color": "#e67e22", "bg": "#fdf2e9", "icon": "🔶", "score_range": (50, 75)},
    "Critical": {"color": "#e74c3c", "bg": "#fdedec", "icon": "🚨", "score_range": (75, 100)},
}

# Renal nutrition thresholds by CKD stage
NUTRITION_LIMITS = {
    1: {"potassium_mg": 4700, "sodium_mg": 2300, "phosphorus_mg": 700, "protein_g_per_kg": 0.8},
    2: {"potassium_mg": 4700, "sodium_mg": 2300, "phosphorus_mg": 700, "protein_g_per_kg": 0.8},
    3: {"potassium_mg": 3000, "sodium_mg": 2000, "phosphorus_mg": 800, "protein_g_per_kg": 0.6},
    4: {"potassium_mg": 2000, "sodium_mg": 1500, "phosphorus_mg": 800, "protein_g_per_kg": 0.6},
    5: {"potassium_mg": 2000, "sodium_mg": 1500, "phosphorus_mg": 800, "protein_g_per_kg": 1.2},  # dialysis
}

# Nephrotoxic drug classes
NEPHROTOXIC_DRUGS = {
    "NSAIDs": ["ibuprofen", "naproxen", "diclofenac", "indomethacin", "celecoxib", "aspirin"],
    "Aminoglycosides": ["gentamicin", "tobramycin", "amikacin", "streptomycin"],
    "Contrast Agents": ["iodinated contrast", "gadolinium"],
    "Calcineurin Inhibitors": ["cyclosporine", "tacrolimus"],
    "Chemotherapy": ["cisplatin", "carboplatin", "methotrexate"],
    "Antivirals": ["acyclovir", "tenofovir", "adefovir"],
    "Lithium": ["lithium carbonate", "lithium"],
    "Antifungals": ["amphotericin b"],
}

# Drugs requiring renal dose adjustment
RENAL_DOSE_DRUGS = {
    "metformin": {"concern": "Contraindicated in eGFR <30; use with caution 30-45", "egfr_threshold": 45},
    "gabapentin": {"concern": "Dose reduction required below eGFR 60", "egfr_threshold": 60},
    "pregabalin": {"concern": "Dose reduction required below eGFR 60", "egfr_threshold": 60},
    "metoclopramide": {"concern": "Dose reduction in moderate-severe CKD", "egfr_threshold": 40},
    "allopurinol": {"concern": "Dose reduction required in CKD", "egfr_threshold": 60},
    "digoxin": {"concern": "Reduced clearance in CKD; monitor levels closely", "egfr_threshold": 60},
    "atenolol": {"concern": "Dose adjustment needed in CKD", "egfr_threshold": 35},
    "lisinopril": {"concern": "Start low, titrate; monitor potassium and creatinine", "egfr_threshold": 30},
    "ramipril": {"concern": "Start low, titrate; monitor potassium and creatinine", "egfr_threshold": 30},
    "enoxaparin": {"concern": "Dose reduction in severe CKD (eGFR <30)", "egfr_threshold": 30},
    "rivaroxaban": {"concern": "Use with caution; contraindicated in eGFR <15", "egfr_threshold": 30},
    "apixaban": {"concern": "Dose reduction criteria apply in CKD", "egfr_threshold": 25},
    "dabigatran": {"concern": "Contraindicated in eGFR <30", "egfr_threshold": 30},
    "spironolactone": {"concern": "Risk of hyperkalemia increases in CKD", "egfr_threshold": 45},
    "trimethoprim": {"concern": "Can cause hyperkalemia and raise creatinine in CKD", "egfr_threshold": 30},
}

# App color scheme
COLORS = {
    "primary": "#1e3a5f",
    "secondary": "#2980b9",
    "accent": "#16a085",
    "success": "#27ae60",
    "warning": "#f39c12",
    "danger": "#e74c3c",
    "light": "#ecf0f1",
    "dark": "#2c3e50",
    "white": "#ffffff",
    "card_bg": "#f8fafc",
}

APP_TITLE = "RenalCare AI"
APP_SUBTITLE = "AI-Powered Kidney Disease Intelligence Platform"
APP_VERSION = "1.0.0"
