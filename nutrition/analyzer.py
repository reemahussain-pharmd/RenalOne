"""
Kidney Nutrition Intelligence — RenalCare AI
Analyses food suitability for CKD patients based on stage and clinical status.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nutrition.food_database import FOOD_DB, get_food_data, search_food
from utils.constants import NUTRITION_LIMITS
from utils.helpers import get_ai_response
from dataclasses import dataclass
from typing import Optional


@dataclass
class NutritionProfile:
    ckd_stage: int            # 1-5
    on_dialysis: bool
    has_diabetes: bool
    weight_kg: float
    serving_g: float = 100.0  # portion size in grams


@dataclass
class NutrientValues:
    potassium_mg: float
    sodium_mg: float
    phosphorus_mg: float
    protein_g: float
    calories: float
    fluid_ml: float


@dataclass
class FoodAssessment:
    food_name: str
    serving_g: float
    nutrients: NutrientValues
    suitability: str          # "Safe" / "Caution" / "Avoid"
    suitability_color: str    # green / orange / red
    reasons: list[str]
    tips: list[str]
    ai_insight: str


SUITABILITY_MAP = {
    "Safe": {"color": "#27ae60", "icon": "✅", "label": "Generally Suitable"},
    "Caution": {"color": "#f39c12", "icon": "⚠️", "label": "Use Caution / Portion Control"},
    "Avoid": {"color": "#e74c3c", "icon": "🚫", "label": "Needs Review — Limit/Avoid"},
}


def _scale_nutrients(raw: dict, serving_g: float) -> NutrientValues:
    scale = serving_g / 100.0
    return NutrientValues(
        potassium_mg=round(raw.get("potassium_mg", 0) * scale, 1),
        sodium_mg=round(raw.get("sodium_mg", 0) * scale, 1),
        phosphorus_mg=round(raw.get("phosphorus_mg", 0) * scale, 1),
        protein_g=round(raw.get("protein_g", 0) * scale, 1),
        calories=round(raw.get("calories", 0) * scale, 0),
        fluid_ml=round(raw.get("fluid_ml", 0) * scale * (serving_g / 100), 0),
    )


def _get_limits(profile: NutritionProfile) -> dict:
    stage = profile.ckd_stage
    if profile.on_dialysis:
        # Dialysis patients need more protein, stricter potassium/phosphorus
        return {
            "potassium_mg": 2000,
            "sodium_mg": 2000,
            "phosphorus_mg": 800,
            "protein_g_per_kg": 1.2,
            "fluid_ml_per_day": 1000,
        }
    limits = NUTRITION_LIMITS.get(stage, NUTRITION_LIMITS[3]).copy()
    limits["fluid_ml_per_day"] = 2000 if stage <= 3 else 1500
    return limits


def _assess_suitability(nutrients: NutrientValues, limits: dict, profile: NutritionProfile) -> tuple[str, list[str], list[str]]:
    """Return (suitability, reasons, tips)."""
    concerns = []
    tips = []

    # Per-serving thresholds (based on roughly 30% of daily limit per meal)
    k_limit_meal = limits["potassium_mg"] * 0.3
    na_limit_meal = limits["sodium_mg"] * 0.3
    p_limit_meal = limits["phosphorus_mg"] * 0.3
    protein_daily = limits["protein_g_per_kg"] * profile.weight_kg

    high_count = 0
    moderate_count = 0

    if nutrients.potassium_mg > k_limit_meal:
        high_count += 1
        concerns.append(f"High potassium ({nutrients.potassium_mg:.0f} mg/serving vs recommended ≤{k_limit_meal:.0f} mg/meal)")
        tips.append("Leach high-potassium vegetables by peeling, chopping, and boiling in large water; discard water")
    elif nutrients.potassium_mg > k_limit_meal * 0.7:
        moderate_count += 1
        concerns.append(f"Moderate potassium ({nutrients.potassium_mg:.0f} mg/serving) — portion mindfully")

    if nutrients.sodium_mg > na_limit_meal:
        high_count += 1
        concerns.append(f"High sodium ({nutrients.sodium_mg:.0f} mg/serving)")
        tips.append("Choose low-sodium or unsalted alternatives; avoid adding table salt")
    elif nutrients.sodium_mg > na_limit_meal * 0.7:
        moderate_count += 1

    if nutrients.phosphorus_mg > p_limit_meal:
        high_count += 1
        concerns.append(f"High phosphorus ({nutrients.phosphorus_mg:.0f} mg/serving)")
        tips.append("Take phosphate binders as prescribed with this meal if phosphorus is elevated")

    if profile.has_diabetes and nutrients.calories > 200:
        moderate_count += 1
        concerns.append("High calorie density — monitor carbohydrate intake for glycaemic control")

    if not concerns:
        tips.append("This food is generally well-tolerated for your CKD stage in recommended portion sizes")

    if high_count >= 2:
        return "Avoid", concerns, tips
    elif high_count == 1 or moderate_count >= 2:
        return "Caution", concerns, tips
    else:
        return "Safe", concerns, tips


def _get_ai_nutrition_insight(food_name: str, nutrients: NutrientValues,
                              profile: NutritionProfile, suitability: str) -> str:
    prompt = f"""You are a Renal Dietitian AI assistant.

Patient: CKD Stage {profile.ckd_stage}, {'on dialysis' if profile.on_dialysis else 'not on dialysis'}, {'diabetic' if profile.has_diabetes else 'non-diabetic'}

Food analysed: {food_name} ({profile.serving_g}g serving)
Nutrients: Potassium {nutrients.potassium_mg}mg | Sodium {nutrients.sodium_mg}mg | Phosphorus {nutrients.phosphorus_mg}mg | Protein {nutrients.protein_g}g | Calories {nutrients.calories}kcal
Overall suitability: {suitability}

Provide a 2-3 sentence clinical nutrition note about this food for this patient.
Include practical advice specific to their CKD stage. Keep it simple and patient-friendly."""

    result = get_ai_response(prompt, max_tokens=200)
    if result:
        return result

    # Fallback
    stage_note = {
        1: "CKD Stage 1 patients generally have fewer dietary restrictions.",
        2: "In CKD Stage 2, a balanced renal diet with reduced sodium is recommended.",
        3: "CKD Stage 3 requires careful monitoring of potassium, phosphorus, and sodium.",
        4: "CKD Stage 4 demands strict dietary management of all electrolytes.",
        5: "ESRD/Stage 5 patients on dialysis have specific high-protein requirements with strict potassium/phosphorus limits.",
    }
    return stage_note.get(profile.ckd_stage, "Follow your renal dietitian's guidance for dietary choices.")


def analyse_food(food_name: str, profile: NutritionProfile) -> Optional[FoodAssessment]:
    """Main nutrition analysis function."""
    raw_data = get_food_data(food_name)
    if not raw_data:
        # Try fuzzy match
        matches = search_food(food_name)
        if matches:
            food_name, raw_data = matches[0]
        else:
            return None

    nutrients = _scale_nutrients(raw_data, profile.serving_g)
    limits = _get_limits(profile)
    suitability, reasons, tips = _assess_suitability(nutrients, limits, profile)
    ai_insight = _get_ai_nutrition_insight(food_name, nutrients, profile, suitability)

    note = raw_data.get("note")
    if note:
        tips.insert(0, f"📝 {note}")

    return FoodAssessment(
        food_name=food_name.title(),
        serving_g=profile.serving_g,
        nutrients=nutrients,
        suitability=suitability,
        suitability_color=SUITABILITY_MAP[suitability]["color"],
        reasons=reasons,
        tips=tips,
        ai_insight=ai_insight,
    )


def analyse_ai_food(food_description: str, profile: NutritionProfile) -> Optional[FoodAssessment]:
    """For foods not in database — use AI to estimate nutrients."""
    prompt = f"""You are a renal dietitian AI. Estimate the nutritional content per 100g of: "{food_description}"

Provide ONLY a JSON object with these exact keys (numbers only, no units):
{{
  "potassium_mg": <number>,
  "sodium_mg": <number>,
  "phosphorus_mg": <number>,
  "protein_g": <number>,
  "calories": <number>,
  "fluid_ml": <number>
}}"""

    result = get_ai_response(prompt, max_tokens=200)
    if not result:
        return None

    try:
        import json
        import re
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            nutrients = _scale_nutrients(data, profile.serving_g)
            limits = _get_limits(profile)
            suitability, reasons, tips = _assess_suitability(nutrients, limits, profile)
            ai_insight = _get_ai_nutrition_insight(food_description, nutrients, profile, suitability)
            return FoodAssessment(
                food_name=food_description.title(),
                serving_g=profile.serving_g,
                nutrients=nutrients,
                suitability=suitability,
                suitability_color=SUITABILITY_MAP[suitability]["color"],
                reasons=reasons,
                tips=tips,
                ai_insight=ai_insight + "\n\n*Nutrient values estimated by AI — consult a renal dietitian for precise assessment.*",
            )
    except Exception:
        pass
    return None
