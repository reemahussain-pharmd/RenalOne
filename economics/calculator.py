"""
Pharmacoeconomic Intelligence — RenalCare AI
Economic burden calculation inspired by published hemodialysis research.
Methodology based on: "Economic burden and quality of life of maintenance
hemodialysis patients in a rural area of South India" (published study).
"""
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dataclasses import dataclass, field
from typing import Optional
from utils.helpers import get_ai_response


@dataclass
class EconomicInput:
    # ---- Direct Medical Costs (monthly in INR) ----
    dialysis_sessions_per_week: int = 3
    cost_per_dialysis_session: float = 1500.0
    medication_cost_monthly: float = 3000.0
    lab_cost_monthly: float = 1500.0
    specialist_visit_cost_monthly: float = 500.0
    hospitalisation_cost_annual: float = 0.0

    # ---- Direct Non-Medical Costs (monthly) ----
    transport_cost_per_session: float = 200.0
    meals_during_dialysis_monthly: float = 500.0
    accommodation_cost_monthly: float = 0.0

    # ---- Indirect Costs (monthly) ----
    patient_wage_loss_monthly: float = 0.0
    caregiver_wage_loss_monthly: float = 5000.0
    caregiver_hours_per_week: float = 20.0
    informal_care_hourly_rate: float = 50.0

    # ---- Patient Context ----
    patient_monthly_income: float = 15000.0
    currency: str = "INR"


@dataclass
class CostBreakdown:
    direct_medical_monthly: float
    direct_medical_annual: float
    direct_non_medical_monthly: float
    direct_non_medical_annual: float
    indirect_monthly: float
    indirect_annual: float
    total_monthly: float
    total_annual: float
    income_burden_pct: float          # % of annual income
    financial_burden_score: float     # 0-100
    financial_risk_category: str      # Low / Moderate / High / Catastrophic
    cost_drivers: list[dict]
    economic_summary: str
    ai_narrative: str


def _financial_risk_category(burden_pct: float) -> str:
    """Classify financial risk based on % income spent on healthcare."""
    if burden_pct < 10:
        return "Low"
    elif burden_pct < 30:
        return "Moderate"
    elif burden_pct < 60:
        return "High"
    else:
        return "Catastrophic"


def _burden_score(burden_pct: float) -> float:
    """Convert income-burden % to 0-100 burden score."""
    return min(round(burden_pct * 1.2, 1), 100.0)


def _ai_economic_narrative(inp: EconomicInput, breakdown: dict) -> str:
    prompt = f"""You are a Health Economist specialising in chronic kidney disease burden analysis.

Patient Economic Profile:
- Monthly Income: ₹{inp.patient_monthly_income:,.0f}
- Dialysis: {inp.dialysis_sessions_per_week} sessions/week at ₹{inp.cost_per_dialysis_session:,.0f}/session
- Total Annual Healthcare Cost: ₹{breakdown['total_annual']:,.0f}
- Income Burden: {breakdown['income_burden_pct']:.1f}% of annual income
- Financial Risk: {breakdown['risk_category']}

Write a 3-4 sentence economic burden summary for this dialysis patient.
Include context about how this compares to rural India healthcare economic burden literature.
Reference the concept of catastrophic health expenditure (>10% of household income) if applicable.
Keep it professional and data-driven."""

    result = get_ai_response(prompt, max_tokens=300)
    if result:
        return result

    # Structured fallback
    cat = breakdown["risk_category"]
    pct = breakdown["income_burden_pct"]
    annual = breakdown["total_annual"]

    if pct >= 40:
        qualifier = "catastrophic"
        who_note = "This exceeds the WHO threshold for catastrophic health expenditure (>40% of non-subsistence spending)."
    elif pct >= 10:
        qualifier = "substantial"
        who_note = "This surpasses the 10% income threshold commonly used to define catastrophic health expenditure."
    else:
        qualifier = "manageable"
        who_note = "This remains below catastrophic expenditure thresholds, though monitoring is advisable."

    return (
        f"The estimated annual healthcare burden of ₹{annual:,.0f} represents {pct:.1f}% of this patient's annual income — "
        f"classified as **{qualifier}** financial risk. {who_note} "
        f"Dialysis dependency creates a sustained economic burden affecting both patients and caregivers, "
        f"consistent with findings in published rural Indian hemodialysis economic burden studies. "
        f"Financial counselling, government scheme enrolment (PMJAY/Aarogyasri), and social support assessment are recommended."
    )


def calculate_economic_burden(inp: EconomicInput) -> CostBreakdown:
    """Main pharmacoeconomic calculation."""
    sessions_per_month = inp.dialysis_sessions_per_week * 4.33

    # ---- Direct Medical ----
    dialysis_monthly = sessions_per_month * inp.cost_per_dialysis_session
    direct_medical_monthly = (
        dialysis_monthly
        + inp.medication_cost_monthly
        + inp.lab_cost_monthly
        + inp.specialist_visit_cost_monthly
        + inp.hospitalisation_cost_annual / 12
    )
    direct_medical_annual = direct_medical_monthly * 12

    # ---- Direct Non-Medical ----
    transport_monthly = sessions_per_month * inp.transport_cost_per_session
    direct_non_medical_monthly = (
        transport_monthly
        + inp.meals_during_dialysis_monthly
        + inp.accommodation_cost_monthly
    )
    direct_non_medical_annual = direct_non_medical_monthly * 12

    # ---- Indirect ----
    informal_care_monthly = inp.caregiver_hours_per_week * 4.33 * inp.informal_care_hourly_rate
    indirect_monthly = (
        inp.patient_wage_loss_monthly
        + inp.caregiver_wage_loss_monthly
        + informal_care_monthly
    )
    indirect_annual = indirect_monthly * 12

    total_monthly = direct_medical_monthly + direct_non_medical_monthly + indirect_monthly
    total_annual = total_monthly * 12

    annual_income = inp.patient_monthly_income * 12
    income_burden_pct = (total_annual / annual_income * 100) if annual_income > 0 else 0
    risk_category = _financial_risk_category(income_burden_pct)
    burden_score = _burden_score(income_burden_pct)

    # Cost drivers
    cost_drivers = sorted([
        {"name": "Dialysis Treatment", "monthly": round(dialysis_monthly), "annual": round(dialysis_monthly * 12), "pct": round(dialysis_monthly / total_monthly * 100, 1)},
        {"name": "Medications", "monthly": round(inp.medication_cost_monthly), "annual": round(inp.medication_cost_monthly * 12), "pct": round(inp.medication_cost_monthly / total_monthly * 100, 1)},
        {"name": "Laboratory Tests", "monthly": round(inp.lab_cost_monthly), "annual": round(inp.lab_cost_monthly * 12), "pct": round(inp.lab_cost_monthly / total_monthly * 100, 1)},
        {"name": "Transportation", "monthly": round(transport_monthly), "annual": round(transport_monthly * 12), "pct": round(transport_monthly / total_monthly * 100, 1)},
        {"name": "Caregiver Burden", "monthly": round(inp.caregiver_wage_loss_monthly + informal_care_monthly), "annual": round((inp.caregiver_wage_loss_monthly + informal_care_monthly) * 12), "pct": round((inp.caregiver_wage_loss_monthly + informal_care_monthly) / total_monthly * 100, 1)},
        {"name": "Specialist Visits", "monthly": round(inp.specialist_visit_cost_monthly), "annual": round(inp.specialist_visit_cost_monthly * 12), "pct": round(inp.specialist_visit_cost_monthly / total_monthly * 100, 1)},
    ], key=lambda x: x["monthly"], reverse=True)

    econ_summary = (
        f"Estimated total annual cost: ₹{total_annual:,.0f} | "
        f"Direct medical: ₹{direct_medical_annual:,.0f} | "
        f"Non-medical: ₹{direct_non_medical_annual:,.0f} | "
        f"Indirect: ₹{indirect_annual:,.0f} | "
        f"Income burden: {income_burden_pct:.1f}%"
    )

    bd = {
        "total_annual": total_annual,
        "income_burden_pct": income_burden_pct,
        "risk_category": risk_category,
    }
    ai_narrative = _ai_economic_narrative(inp, bd)

    return CostBreakdown(
        direct_medical_monthly=round(direct_medical_monthly, 2),
        direct_medical_annual=round(direct_medical_annual, 2),
        direct_non_medical_monthly=round(direct_non_medical_monthly, 2),
        direct_non_medical_annual=round(direct_non_medical_annual, 2),
        indirect_monthly=round(indirect_monthly, 2),
        indirect_annual=round(indirect_annual, 2),
        total_monthly=round(total_monthly, 2),
        total_annual=round(total_annual, 2),
        income_burden_pct=round(income_burden_pct, 1),
        financial_burden_score=burden_score,
        financial_risk_category=risk_category,
        cost_drivers=cost_drivers,
        economic_summary=econ_summary,
        ai_narrative=ai_narrative,
    )
