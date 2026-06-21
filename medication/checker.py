"""
Medication Intelligence Engine — RenalCare AI
Clinical Pharmacist AI module for drug safety in CKD patients.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.constants import NEPHROTOXIC_DRUGS, RENAL_DOSE_DRUGS
from utils.helpers import get_ai_response
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MedicationInput:
    medications: list[str]
    diagnoses: list[str]
    egfr: Optional[float] = None
    serum_creatinine: Optional[float] = None
    potassium: Optional[float] = None
    sodium: Optional[float] = None
    hemoglobin: Optional[float] = None
    ckd_stage: Optional[str] = None


@dataclass
class DrugFlag:
    drug: str
    flag_type: str       # "Nephrotoxicity" / "Dose Adjustment" / "Interaction" / "ADR" / "Monitoring"
    severity: str        # "High" / "Moderate" / "Low"
    detail: str
    action: str


@dataclass
class MedicationReviewResult:
    flags: list[DrugFlag]
    monitoring_requirements: list[str]
    clinical_considerations: list[str]
    overall_risk: str           # Low / Moderate / High / Critical
    ai_narrative: str
    disclaimer: str = (
        "This AI-generated medication review is for clinical decision support only. "
        "It does not replace the judgment of a licensed pharmacist or physician. "
        "All medication decisions must be made by qualified healthcare professionals."
    )


def _normalise_drug(drug: str) -> str:
    return drug.strip().lower()


def _check_nephrotoxicity(drugs: list[str]) -> list[DrugFlag]:
    flags = []
    for drug in drugs:
        drug_lower = _normalise_drug(drug)
        for drug_class, members in NEPHROTOXIC_DRUGS.items():
            if any(m in drug_lower or drug_lower in m for m in members):
                flags.append(DrugFlag(
                    drug=drug,
                    flag_type="Nephrotoxicity",
                    severity="High",
                    detail=f"'{drug}' belongs to the {drug_class} class, known to be potentially nephrotoxic.",
                    action=f"Review necessity; consider alternative if renal function is compromised. Avoid or use with extreme caution in CKD.",
                ))
                break
    return flags


def _check_renal_dosing(drugs: list[str], egfr: Optional[float]) -> list[DrugFlag]:
    flags = []
    for drug in drugs:
        drug_lower = _normalise_drug(drug)
        for key, info in RENAL_DOSE_DRUGS.items():
            if key in drug_lower or drug_lower in key:
                if egfr is None or egfr <= info["egfr_threshold"]:
                    severity = "High" if (egfr or 100) < info["egfr_threshold"] * 0.5 else "Moderate"
                    flags.append(DrugFlag(
                        drug=drug,
                        flag_type="Dose Adjustment",
                        severity=severity,
                        detail=info["concern"],
                        action=f"Review dosing per current eGFR ({egfr:.1f} mL/min)" if egfr else "Verify eGFR before prescribing",
                    ))
                break
    return flags


def _check_interactions(drugs: list[str], labs: dict) -> list[DrugFlag]:
    """Rule-based interaction checks for common CKD-relevant combinations."""
    flags = []
    drug_lower_list = [_normalise_drug(d) for d in drugs]

    def has(keyword: str) -> bool:
        return any(keyword in d for d in drug_lower_list)

    # ACEi/ARB + potassium-sparing diuretic → hyperkalemia risk
    raas = has("lisinopril") or has("ramipril") or has("enalapril") or has("valsartan") or has("losartan") or has("telmisartan")
    k_sparing = has("spironolactone") or has("eplerenone") or has("amiloride")
    if raas and k_sparing:
        flags.append(DrugFlag(
            drug="ACEi/ARB + Potassium-Sparing Diuretic",
            flag_type="Interaction",
            severity="High",
            detail="Concurrent use significantly increases risk of hyperkalaemia, particularly in CKD.",
            action="Monitor serum potassium closely; consider dose reduction or alternative.",
        ))

    # Metformin + contrast / low eGFR
    if has("metformin") and labs.get("egfr", 100) < 30:
        flags.append(DrugFlag(
            drug="Metformin",
            flag_type="Nephrotoxicity",
            severity="High",
            detail="Metformin is contraindicated in eGFR <30 due to lactic acidosis risk.",
            action="Discontinue or switch to eGFR-appropriate antidiabetic therapy.",
        ))
    elif has("metformin") and labs.get("egfr", 100) < 45:
        flags.append(DrugFlag(
            drug="Metformin",
            flag_type="Dose Adjustment",
            severity="Moderate",
            detail="Use with caution in eGFR 30-45; increased risk of lactic acidosis.",
            action="Reduce dose and monitor closely; consider alternatives.",
        ))

    # NSAID in CKD
    nsaids = ["ibuprofen", "naproxen", "diclofenac", "indomethacin"]
    for nsaid in nsaids:
        if has(nsaid) and labs.get("egfr", 100) < 60:
            flags.append(DrugFlag(
                drug=nsaid.capitalize(),
                flag_type="Nephrotoxicity",
                severity="High",
                detail=f"NSAIDs (incl. {nsaid}) should be avoided in CKD; reduce prostaglandin-mediated renal perfusion.",
                action="Switch to paracetamol (acetaminophen) for analgesia; avoid NSAIDs.",
            ))
            break

    # Digoxin + loop diuretic (hypokalemia potentiates toxicity)
    if has("digoxin") and (has("furosemide") or has("torsemide") or has("bumetanide")):
        flags.append(DrugFlag(
            drug="Digoxin + Loop Diuretic",
            flag_type="Interaction",
            severity="Moderate",
            detail="Loop diuretics can cause hypokalaemia, increasing risk of digoxin toxicity.",
            action="Monitor serum potassium and digoxin levels; electrolyte supplementation may be needed.",
        ))

    # Dual RAAS blockade
    acei = has("lisinopril") or has("ramipril") or has("enalapril") or has("perindopril")
    arb = has("losartan") or has("valsartan") or has("telmisartan") or has("candesartan")
    if acei and arb:
        flags.append(DrugFlag(
            drug="ACEi + ARB (Dual RAAS Blockade)",
            flag_type="Interaction",
            severity="High",
            detail="Dual RAAS blockade is generally not recommended; increased risk of hyperkalaemia, hypotension, and AKI.",
            action="Re-evaluate; ONTARGET trial data suggests no additional benefit with increased harm.",
        ))

    return flags


def _generate_monitoring_requirements(drugs: list[str], egfr: Optional[float]) -> list[str]:
    reqs = []
    drug_lower_list = [_normalise_drug(d) for d in drugs]

    def has(k):
        return any(k in d for d in drug_lower_list)

    if has("lisinopril") or has("ramipril") or has("losartan") or has("valsartan"):
        reqs.append("Monitor serum creatinine, eGFR, and potassium 1-2 weeks after initiation/dose change of RAAS inhibitor")
    if has("digoxin"):
        reqs.append("Monitor digoxin serum levels, renal function, and electrolytes regularly")
    if has("spironolactone") or has("eplerenone"):
        reqs.append("Monitor serum potassium frequently (risk of hyperkalaemia, particularly in CKD)")
    if has("metformin"):
        reqs.append("Monitor eGFR at least annually (every 3-6 months if eGFR <60); withhold if eGFR <30")
    if has("warfarin") or has("acenocoumarol"):
        reqs.append("INR monitoring required; renal impairment can affect anticoagulant pharmacokinetics")
    if has("lithium"):
        reqs.append("Monitor lithium levels and renal function every 3-6 months; lithium is nephrotoxic with chronic use")
    if egfr and egfr < 45:
        reqs.append("General: eGFR-based dose review required for all renally cleared medications")
    if not reqs:
        reqs.append("Routine monitoring per standard clinical guidelines")
    return reqs


def _ai_medication_analysis(inp: MedicationInput, flags: list[DrugFlag]) -> str:
    """Use AI to generate a comprehensive medication narrative."""
    flag_summary = "\n".join(
        f"- {f.drug}: [{f.flag_type}] {f.detail}" for f in flags
    ) if flags else "No major AI-identified concerns beyond rule-based flags."

    prompt = f"""You are a Clinical Pharmacist AI assistant specialising in nephrology pharmacy.

Patient Profile:
- Diagnoses: {', '.join(inp.diagnoses)}
- eGFR: {inp.egfr or 'Not provided'} mL/min/1.73m²
- CKD Stage: {inp.ckd_stage or 'Not specified'}
- Serum Creatinine: {inp.serum_creatinine or 'Not provided'} mg/dL
- Potassium: {inp.potassium or 'Not provided'} mEq/L
- Current Medications: {', '.join(inp.medications)}

Rule-based flags identified:
{flag_summary}

Please provide:
1. A brief clinical medication review summary (2-3 sentences)
2. The most clinically significant concerns for this CKD patient
3. Key pharmaceutical care points the prescriber should consider

Keep your response concise, clinically focused, and structured. Use bullet points where appropriate.
Do NOT make prescribing decisions. Present considerations only."""

    system = (
        "You are a board-certified Clinical Pharmacist with specialisation in nephrology. "
        "Provide evidence-based medication review. Always include appropriate clinical disclaimers."
    )

    result = get_ai_response(prompt, system, max_tokens=800)
    if result:
        return result

    # Fallback structured response
    if flags:
        high = [f for f in flags if f.severity == "High"]
        mod = [f for f in flags if f.severity == "Moderate"]
        return (
            f"**Medication Review Summary**\n\n"
            f"{'⚠️ ' + str(len(high)) + ' high-severity concern(s) identified.' if high else ''}\n"
            f"{'ℹ️ ' + str(len(mod)) + ' moderate concern(s) identified.' if mod else ''}\n\n"
            f"**Key Concerns:**\n" +
            "\n".join(f"• **{f.drug}**: {f.detail}" for f in flags[:5]) +
            "\n\n*Please review flagged items with a qualified clinical pharmacist or nephrologist.*"
        )
    return "No significant medication concerns identified based on rule-based analysis. Clinical pharmacist review recommended for comprehensive assessment."


def run_medication_review(inp: MedicationInput) -> MedicationReviewResult:
    """Full medication review pipeline."""
    labs = {
        "egfr": inp.egfr or 100,
        "potassium": inp.potassium or 4.0,
    }

    nephro_flags = _check_nephrotoxicity(inp.medications)
    dose_flags = _check_renal_dosing(inp.medications, inp.egfr)
    interaction_flags = _check_interactions(inp.medications, labs)

    all_flags = nephro_flags + dose_flags + interaction_flags

    monitoring = _generate_monitoring_requirements(inp.medications, inp.egfr)

    # Severity scoring
    high_count = sum(1 for f in all_flags if f.severity == "High")
    mod_count = sum(1 for f in all_flags if f.severity == "Moderate")

    if high_count >= 2:
        overall = "Critical"
    elif high_count == 1:
        overall = "High"
    elif mod_count >= 2:
        overall = "Moderate"
    elif mod_count >= 1 or all_flags:
        overall = "Moderate"
    else:
        overall = "Low"

    ai_narrative = _ai_medication_analysis(inp, all_flags)

    considerations = [
        "All medications should be reviewed by a clinical pharmacist for comprehensive assessment",
        "Renal dose adjustments should be made based on current eGFR per product monograph",
        "Patient counselling on medication adherence and fluid management is essential",
    ]
    if inp.egfr and inp.egfr < 30:
        considerations.insert(0, "eGFR <30: Nephrology specialist review of complete medication list is strongly recommended")

    return MedicationReviewResult(
        flags=all_flags,
        monitoring_requirements=monitoring,
        clinical_considerations=considerations,
        overall_risk=overall,
        ai_narrative=ai_narrative,
    )
