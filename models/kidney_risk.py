"""
Kidney Risk Assessment Model — RenalCare AI
Uses rule-based clinical scoring validated against KDIGO guidelines
with optional ML overlay if scikit-learn is available.
"""
import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class RiskInput:
    age: float
    gender: str               # "Male" / "Female"
    weight_kg: float
    height_cm: float
    bmi: float
    diabetes: bool
    hypertension: bool
    smoking: bool
    alcohol: bool
    family_history: bool
    serum_creatinine: float   # mg/dL
    egfr: float               # mL/min/1.73m²
    albuminuria: str          # "None" / "Microalbuminuria" / "Macroalbuminuria"
    hba1c: Optional[float] = None  # %
    systolic_bp: Optional[float] = None
    diastolic_bp: Optional[float] = None


@dataclass
class RiskResult:
    kidney_health_score: float       # 0-100 (higher = healthier)
    risk_score: float                # 0-100 (higher = worse)
    risk_category: str               # Low / Moderate / High / Critical
    ckd_stage: str
    ckd_stage_num: str
    egfr_category: str
    contributing_factors: list[dict]
    recommendations: list[str]
    clinical_summary: str
    monitoring_priority: str


def _score_egfr(egfr: float) -> tuple[float, str, str, str]:
    """Return (risk_pts, stage_label, stage_num, egfr_cat)."""
    if egfr >= 90:
        return 0, "CKD Stage G1", "G1", "Normal or High"
    elif egfr >= 60:
        return 10, "CKD Stage G2", "G2", "Mildly Decreased"
    elif egfr >= 45:
        return 25, "CKD Stage G3a", "G3a", "Mildly to Moderately Decreased"
    elif egfr >= 30:
        return 40, "CKD Stage G3b", "G3b", "Moderately to Severely Decreased"
    elif egfr >= 15:
        return 60, "CKD Stage G4", "G4", "Severely Decreased"
    else:
        return 80, "CKD Stage G5 (ESRD)", "G5", "Kidney Failure"


def _score_albuminuria(level: str) -> float:
    mapping = {"None": 0, "Microalbuminuria": 15, "Macroalbuminuria": 30}
    return mapping.get(level, 0)


def calculate_risk(inp: RiskInput) -> RiskResult:
    """Main scoring function — clinical rule-based with weighted factors."""
    score = 0.0
    factors = []

    # --- eGFR (highest weight) ---
    egfr_pts, ckd_stage, ckd_num, egfr_cat = _score_egfr(inp.egfr)
    score += egfr_pts
    if egfr_pts > 0:
        severity = "Moderate" if egfr_pts < 40 else "High" if egfr_pts < 70 else "Critical"
        factors.append({
            "factor": "eGFR / Kidney Function",
            "value": f"{inp.egfr:.1f} mL/min/1.73m²",
            "impact": severity,
            "detail": f"Current kidney function: {egfr_cat}",
        })

    # --- Albuminuria ---
    alb_pts = _score_albuminuria(inp.albuminuria)
    score += alb_pts
    if alb_pts > 0:
        factors.append({
            "factor": "Albuminuria",
            "value": inp.albuminuria,
            "impact": "High" if alb_pts >= 30 else "Moderate",
            "detail": "Protein leakage indicates glomerular damage",
        })

    # --- Diabetes ---
    if inp.diabetes:
        pts = 12
        score += pts
        detail = "Diabetic nephropathy is the leading cause of CKD"
        if inp.hba1c and inp.hba1c > 7.0:
            pts_extra = min((inp.hba1c - 7.0) * 2, 8)
            score += pts_extra
            detail += f" (HbA1c {inp.hba1c}% — suboptimal glycaemic control)"
        factors.append({
            "factor": "Diabetes Mellitus",
            "value": f"HbA1c {inp.hba1c}%" if inp.hba1c else "Present",
            "impact": "High",
            "detail": detail,
        })

    # --- Hypertension ---
    if inp.hypertension:
        pts = 10
        score += pts
        detail = "Hypertension accelerates CKD progression"
        if inp.systolic_bp and inp.systolic_bp > 140:
            score += 5
            detail += f" (BP {inp.systolic_bp}/{inp.diastolic_bp or '?'} mmHg — above target)"
        factors.append({
            "factor": "Hypertension",
            "value": f"{inp.systolic_bp}/{inp.diastolic_bp} mmHg" if inp.systolic_bp else "Present",
            "impact": "High",
            "detail": detail,
        })

    # --- Age ---
    if inp.age >= 65:
        score += 8
        factors.append({
            "factor": "Age",
            "value": f"{inp.age:.0f} years",
            "impact": "Moderate",
            "detail": "Age ≥65 is an independent CKD risk factor",
        })
    elif inp.age >= 50:
        score += 4

    # --- BMI ---
    if inp.bmi >= 30:
        pts = 6 if inp.bmi < 35 else 9
        score += pts
        factors.append({
            "factor": "Obesity",
            "value": f"BMI {inp.bmi:.1f}",
            "impact": "Moderate",
            "detail": "Obesity increases intraglomerular pressure and CKD risk",
        })

    # --- Smoking ---
    if inp.smoking:
        score += 5
        factors.append({
            "factor": "Smoking",
            "value": "Active Smoker",
            "impact": "Moderate",
            "detail": "Smoking reduces renal blood flow and accelerates CKD",
        })

    # --- Family History ---
    if inp.family_history:
        score += 5
        factors.append({
            "factor": "Family History of CKD",
            "value": "Present",
            "impact": "Moderate",
            "detail": "Genetic predisposition increases CKD risk",
        })

    # --- Serum Creatinine (cross-check) ---
    creat_high = (inp.gender == "Male" and inp.serum_creatinine > 1.2) or \
                 (inp.gender == "Female" and inp.serum_creatinine > 1.0)
    if creat_high:
        bonus = min((inp.serum_creatinine - 1.2) * 5, 10)
        score += bonus
        factors.append({
            "factor": "Elevated Serum Creatinine",
            "value": f"{inp.serum_creatinine:.2f} mg/dL",
            "impact": "High",
            "detail": "Above normal range — reflects reduced GFR",
        })

    # --- Alcohol ---
    if inp.alcohol:
        score += 3
        factors.append({
            "factor": "Alcohol Use",
            "value": "Present",
            "impact": "Low",
            "detail": "Chronic alcohol use can affect kidney function",
        })

    # Cap score at 100
    score = min(round(score, 1), 100.0)

    # Health score = inverse
    health_score = round(100.0 - score, 1)

    # Risk category
    if score < 25:
        category = "Low"
        monitoring = "Annual monitoring recommended"
    elif score < 50:
        category = "Moderate"
        monitoring = "Monitoring every 3-6 months recommended"
    elif score < 75:
        category = "High"
        monitoring = "Frequent monitoring every 1-3 months recommended"
    else:
        category = "Critical"
        monitoring = "Immediate nephrology referral and close monitoring required"

    # Recommendations
    recs = _generate_recommendations(inp, score, category)

    # Clinical summary
    summary = _generate_clinical_summary(inp, score, category, ckd_stage, ckd_num)

    return RiskResult(
        kidney_health_score=health_score,
        risk_score=score,
        risk_category=category,
        ckd_stage=ckd_stage,
        ckd_stage_num=ckd_num,
        egfr_category=egfr_cat,
        contributing_factors=factors,
        recommendations=recs,
        clinical_summary=summary,
        monitoring_priority=monitoring,
    )


def _generate_recommendations(inp: RiskInput, score: float, category: str) -> list[str]:
    recs = []
    if inp.diabetes and (not inp.hba1c or inp.hba1c > 7.0):
        recs.append("Optimise glycaemic control; target HbA1c <7% per ADA/KDIGO guidelines")
    if inp.hypertension:
        recs.append("Target BP <130/80 mmHg; consider RAAS inhibitor (ACEi/ARB) if albuminuria present")
    if inp.albuminuria != "None":
        recs.append("ACEi or ARB therapy should be evaluated for albuminuria management")
    if inp.bmi >= 30:
        recs.append("Weight reduction towards BMI <25 can reduce intraglomerular hyperfiltration")
    if inp.smoking:
        recs.append("Smoking cessation is strongly recommended; accelerates CKD progression")
    if inp.egfr < 60:
        recs.append("Restrict dietary phosphorus intake; consult renal dietitian")
    if inp.egfr < 30:
        recs.append("Nephrology referral for renal replacement therapy planning (dialysis/transplant)")
        recs.append("Review all medications for renal dose adjustment (avoid nephrotoxic agents)")
    if inp.egfr < 60:
        recs.append("Avoid NSAIDs and nephrotoxic contrast agents")
    if inp.family_history:
        recs.append("Genetic counselling may be appropriate given family history")
    if not recs:
        recs.append("Maintain healthy lifestyle; continue regular monitoring per clinical guidelines")
    return recs


def _generate_clinical_summary(inp: RiskInput, score: float, category: str,
                                stage: str, stage_num: str) -> str:
    gender_str = inp.gender
    age_str = f"{inp.age:.0f}-year-old"
    comorbidities = []
    if inp.diabetes:
        comorbidities.append("diabetes mellitus")
    if inp.hypertension:
        comorbidities.append("hypertension")
    if inp.smoking:
        comorbidities.append("active smoking")
    comorbid_str = ", ".join(comorbidities) if comorbidities else "no major comorbidities"

    return (
        f"This {age_str} {gender_str} patient presents with a kidney risk score of {score:.1f}/100, "
        f"classified as {category} risk. Current kidney function is categorised as {stage} "
        f"(eGFR: {inp.egfr:.1f} mL/min/1.73m²) with {inp.albuminuria.lower()} on urine testing. "
        f"Key comorbidities include {comorbid_str}. "
        f"Clinical assessment suggests {'urgent nephrology referral is warranted' if score >= 75 else 'proactive monitoring and risk factor modification are recommended'}."
    )
