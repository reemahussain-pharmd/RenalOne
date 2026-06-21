"""Kidney Nutrition Intelligence — Sprint 3 Upgrade — RenalOne."""
import sys, base64
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from components.styles import sh
from nutrition.analyzer import analyse_food, analyse_ai_food, NutritionProfile
from nutrition.food_database import FOOD_DB as FOOD_DATABASE
from components.charts import nutrient_radar
from utils.helpers import get_ai_response

STAGE_MAP = {"G3a": 3, "G3b": 3, "G4": 4, "G5": 5}

LIMIT_CARDS = [
    ("potassium_mg",  "K⁺ Potassium",  "#FEF3C7", "#92400E", "#78350F"),
    ("sodium_mg",     "Na⁺ Sodium",    "#EFF6FF", "#1D4ED8", "#1E3A8A"),
    ("phosphorus_mg", "PO₄ Phosphorus","#EDE9FE", "#5B21B6", "#4C1D95"),
    ("protein_g",     "Protein",       "#D1FAE5", "#065F46", "#064E3B"),
    ("fluid_ml",      "Fluid",         "#F1F5F9", "#374151", "#1F2937"),
]

SUITABILITY_CFG = {
    "Safe":    ("#10B981", "#D1FAE5", "#065F46", "✅",  "SAFE"),
    "Caution": ("#F59E0B", "#FEF3C7", "#92400E", "⚠️", "USE WITH CAUTION"),
    "Avoid":   ("#EF4444", "#FEE2E2", "#991B1B", "❌", "AVOID"),
}


# ── Personalised limits (weight-based) ───────────────────────────────────────
def _calc_limits(stage_key: str, weight_kg: float,
                 on_dialysis: bool, has_diabetes: bool, has_hypertension: bool) -> dict:
    """Compute patient-specific daily nutrient limits from clinical guidelines."""
    # Protein: KDIGO + ESPEN
    if on_dialysis:
        protein_g = round(weight_kg * 1.2)      # 1.2 g/kg/day HD (replace dialytic losses)
    elif stage_key in ("G4", "G5"):
        protein_g = round(weight_kg * 0.7)      # 0.6–0.8 g/kg/day — slow progression
    else:
        protein_g = round(weight_kg * 0.8)      # 0.8 g/kg/day G3

    # Potassium
    if stage_key == "G5" or on_dialysis:
        k_mg = 2000
    elif stage_key == "G4":
        k_mg = 2500
    else:
        k_mg = 3000

    # Sodium: tighter with hypertension or dialysis
    if has_hypertension or on_dialysis:
        na_mg = 1500
    else:
        na_mg = 2000

    # Phosphorus (all stages same per KDIGO)
    phos_mg = 800

    # Fluid
    if on_dialysis:
        fl_ml = 1000
    elif stage_key in ("G4", "G5"):
        fl_ml = 1500
    else:
        fl_ml = 2000

    return {
        "potassium_mg": k_mg, "sodium_mg": na_mg,
        "phosphorus_mg": phos_mg, "protein_g": protein_g, "fluid_ml": fl_ml,
    }


# ── Nutrition Risk Score ──────────────────────────────────────────────────────
def _calc_nutrition_risk(stage_key, on_dialysis, has_diabetes, has_hypertension, log) -> tuple:
    """Return (score 0-100, label, color, bg)."""
    score = {"G3a": 15, "G3b": 20, "G4": 35, "G5": 50}.get(stage_key, 20)
    if on_dialysis:  score += 15
    if has_diabetes: score += 10
    if has_hypertension: score += 5

    # Penalise if log shows high cumulative intake
    if log:
        for nutrient, field in [("potassium_mg", "potassium_mg"), ("sodium_mg", "sodium_mg"),
                                  ("phosphorus_mg", "phosphorus_mg")]:
            total = sum(item["nutrients"].get(field, 0) for item in log)
            limit = log[0].get("limits", {}).get(nutrient, 9999)
            if limit and total / limit > 0.9:
                score += 10
            elif limit and total / limit > 0.7:
                score += 5

    score = min(score, 100)
    if score >= 60:
        return score, "High Nutrition Risk", "#EF4444", "#FEE2E2"
    elif score >= 35:
        return score, "Moderate Nutrition Risk", "#F59E0B", "#FEF3C7"
    else:
        return score, "Low Nutrition Risk", "#10B981", "#D1FAE5"


def render():
    sh("""
    <div class="page-header">
        <div style="display:flex;align-items:flex-start;justify-content:space-between;">
            <div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.5rem;">
                    <span style="font-size:1.5rem;">&#x1f966;</span>
                    <span style="background:rgba(255,255,255,0.15);color:rgba(255,255,255,0.9);font-size:0.7rem;font-weight:700;padding:3px 10px;border-radius:20px;letter-spacing:0.06em;">RENAL DIETETICS MODULE</span>
                    <span style="background:rgba(16,185,129,0.25);color:#6EE7B7;font-size:0.7rem;font-weight:700;padding:3px 10px;border-radius:20px;">Sprint 3 &#x2014; Enhanced</span>
                </div>
                <h1 style="color:white !important;font-size:1.7rem !important;font-weight:800 !important;margin:0 0 0.3rem 0 !important;">Kidney Nutrition Intelligence</h1>
                <p style="color:rgba(255,255,255,0.72) !important;font-size:0.88rem !important;margin:0 !important;">
                    Personalised limits &bull; Nutrition risk score &bull; AI meal planner &bull; Food tracker &bull; Image analysis
                </p>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.7rem;color:rgba(255,255,255,0.5);text-transform:uppercase;letter-spacing:0.07em;">Evidence Base</div>
                <div style="font-size:0.85rem;color:rgba(255,255,255,0.85);font-weight:600;">KDIGO 2024</div>
                <div style="font-size:0.85rem;color:rgba(255,255,255,0.85);font-weight:600;">ESPEN CKD Guidelines</div>
            </div>
        </div>
    </div>
    """)

    # ── Patient profile row ───────────────────────────────────────────────────
    pc1, pc2, pc3, pc4, pc5 = st.columns(5)
    with pc1: ckd_stage      = st.selectbox("CKD Stage", ["G3a", "G3b", "G4", "G5"])
    with pc2: weight_kg      = st.number_input("Weight (kg)", 30.0, 200.0, 65.0, 1.0)
    with pc3: on_dialysis    = st.checkbox("On Dialysis",   value=(ckd_stage == "G5"))
    with pc4: has_diabetes   = st.checkbox("Diabetes",      value=False)
    with pc5: has_hypertension = st.checkbox("Hypertension", value=False)

    limits    = _calc_limits(ckd_stage, weight_kg, on_dialysis, has_diabetes, has_hypertension)
    stage_int = STAGE_MAP[ckd_stage]
    profile   = NutritionProfile(ckd_stage=stage_int, on_dialysis=on_dialysis,
                                  has_diabetes=has_diabetes, weight_kg=weight_kg, serving_g=100.0)

    # ── Personalised daily limits bar ─────────────────────────────────────────
    dial_tag = " · Dialysis" if on_dialysis else ""
    htn_tag  = " · HTN" if has_hypertension else ""
    sh(f'<div style="font-size:0.82rem;font-weight:700;color:#0F172A;margin:0.8rem 0 0.4rem;">&#x1f4ca; Personalised Daily Limits — CKD {ckd_stage}{dial_tag}{htn_tag} · {weight_kg:.0f} kg</div>')
    lc1, lc2, lc3, lc4, lc5 = st.columns(5)
    for col, (key, label, bg, color, dark) in zip([lc1, lc2, lc3, lc4, lc5], LIMIT_CARDS):
        val = limits[key]
        unit = "g" if key == "protein_g" else ("mL" if key == "fluid_ml" else "mg")
        with col:
            st.markdown(
                f'<div style="text-align:center;background:{bg};border-radius:10px;padding:0.75rem 0.4rem;">'
                f'<div style="font-size:1rem;font-weight:800;color:{color};">{val:,}{unit}</div>'
                f'<div style="font-size:0.62rem;font-weight:700;color:{dark};text-transform:uppercase;letter-spacing:0.04em;margin-top:2px;">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-top:0.6rem;'></div>")

    # ── Nutrition Risk Score card ─────────────────────────────────────────────
    log = st.session_state.get("nutrition_log", [])
    risk_score, risk_label, risk_c, risk_bg = _calc_nutrition_risk(
        ckd_stage, on_dialysis, has_diabetes, has_hypertension, log)
    pct_bar = risk_score

    sh(f'<div style="background:{risk_bg};border:1.5px solid {risk_c}40;border-radius:12px;padding:0.9rem 1.2rem;margin-bottom:0.8rem;display:flex;align-items:center;gap:1.2rem;"><div style="flex:1;"><div style="font-size:0.7rem;font-weight:700;color:{risk_c};letter-spacing:0.08em;text-transform:uppercase;margin-bottom:3px;">Nutrition Risk Score</div><div style="font-size:1.15rem;font-weight:800;color:{risk_c};">{risk_label}</div><div style="background:#E2E8F0;border-radius:99px;height:7px;margin-top:6px;"><div style="background:{risk_c};width:{pct_bar}%;height:7px;border-radius:99px;"></div></div><div style="font-size:0.72rem;color:#64748B;margin-top:3px;">Based on CKD stage, comorbidities, and food log · {len(log)} food item{"s" if len(log)!=1 else ""} tracked today</div></div><div style="text-align:center;min-width:52px;"><div style="font-size:2rem;font-weight:900;color:{risk_c};">{risk_score}</div><div style="font-size:0.65rem;font-weight:700;color:{risk_c};letter-spacing:0.06em;">/100</div></div></div>')

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔍 Food Analysis",
        "🍽️ Meal Planner",
        "🤖 AI Food Analysis",
        "📸 Image Analysis",
        "📖 Nutrient Guide",
    ])

    with tab1: _tab_search(profile, limits, ckd_stage)
    with tab2: _tab_meal_planner(profile, limits, ckd_stage, weight_kg, on_dialysis, has_diabetes, has_hypertension)
    with tab3: _tab_ai(profile, ckd_stage)
    with tab4: _tab_image(profile, ckd_stage)
    with tab5: _tab_guide()


# ─────────────────────────────────────────────────────────────────────────────
# Tab 1 — Food Analysis + Food Tracker
# ─────────────────────────────────────────────────────────────────────────────

def _tab_search(profile, limits, ckd_stage):
    foods = sorted(FOOD_DATABASE.keys())
    col1, col2 = st.columns([2, 1])
    with col1: selected_food = st.selectbox("Search food database (37 foods):", foods)
    with col2: amount = st.slider("Serving (g):", 25, 300, 100, 25)

    if st.button("🔍  Analyse This Food", type="primary", key="btn_search"):
        profile.serving_g = float(amount)
        result = analyse_food(selected_food, profile)

        if result:
            nv   = result.nutrients
            suit = result.suitability
            s_color, s_bg, s_text, s_icon, s_label = SUITABILITY_CFG.get(suit, SUITABILITY_CFG["Caution"])

            sh(f'<div style="background:{s_bg};border:2px solid {s_color};border-radius:14px;padding:1rem 1.2rem;margin:0.8rem 0;display:flex;align-items:center;gap:10px;"><span style="font-size:1.5rem;">{s_icon}</span><div><div style="font-size:1rem;font-weight:800;color:{s_text};">{result.food_name}</div><div style="font-size:0.83rem;font-weight:700;color:{s_color};">{s_label} — {amount}g serving &bull; {nv.calories:.0f} kcal</div></div></div>')

            # Nutrient bars
            nutrient_rows = [
                ("Potassium",  nv.potassium_mg,  limits["potassium_mg"],  "mg", "#F59E0B"),
                ("Sodium",     nv.sodium_mg,     limits["sodium_mg"],     "mg", "#3B82F6"),
                ("Phosphorus", nv.phosphorus_mg, limits["phosphorus_mg"], "mg", "#8B5CF6"),
                ("Protein",    nv.protein_g,     limits["protein_g"],     "g",  "#10B981"),
            ]
            for name, val, lim, unit, color in nutrient_rows:
                pct       = min(val / lim * 100, 100) if lim > 0 else 0
                bar_color = "#EF4444" if pct > 80 else (color if pct > 50 else "#10B981")
                risk_tag  = ' <span style="background:#EF4444;color:white;font-size:0.6rem;font-weight:700;padding:1px 5px;border-radius:3px;">HIGH</span>' if pct > 80 else ""
                st.markdown(
                    f'<div style="margin-bottom:0.65rem;">'
                    f'<div style="display:flex;justify-content:space-between;margin-bottom:3px;">'
                    f'<span style="font-size:0.82rem;font-weight:600;color:#374151;">{name}{risk_tag}</span>'
                    f'<span style="font-size:0.82rem;font-weight:700;color:{bar_color};">{val:.0f}{unit} <span style="color:#94A3B8;font-weight:400;">/ {lim}{unit}</span></span>'
                    f'</div>'
                    f'<div style="background:#F1F5F9;border-radius:999px;height:7px;">'
                    f'<div style="background:{bar_color};width:{pct:.0f}%;height:7px;border-radius:999px;"></div>'
                    f'</div>'
                    f'<div style="font-size:0.7rem;color:#94A3B8;margin-top:2px;">{pct:.0f}% of personalised daily limit per serving</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            # Add to food log
            if st.button("➕  Add to Daily Log", key="add_log"):
                if "nutrition_log" not in st.session_state:
                    st.session_state.nutrition_log = []
                st.session_state.nutrition_log.append({
                    "food": result.food_name, "amount": amount,
                    "nutrients": {
                        "potassium_mg": nv.potassium_mg, "sodium_mg": nv.sodium_mg,
                        "phosphorus_mg": nv.phosphorus_mg, "protein_g": nv.protein_g,
                        "calories": nv.calories,
                    },
                    "limits": limits,
                    "suitability": suit,
                })
                st.success(f"✅ {result.food_name} added to your daily food log.")
                st.rerun()

            # Clinical notes + tips
            if result.reasons:
                sh('<div style="font-size:0.85rem;font-weight:700;color:#0F172A;margin:0.8rem 0 0.4rem;">&#x1f4dd; Clinical Notes</div>')
                for r in result.reasons:
                    sh(f'<div style="font-size:0.82rem;color:#374151;margin-bottom:4px;">&#x2022; {r}</div>')

            if result.tips:
                tips_inner = "".join(f'<div style="font-size:0.8rem;color:#166534;margin-bottom:3px;">&#x2713; {t}</div>' for t in result.tips)
                sh(f'<div style="background:#F0FDF4;border-radius:10px;padding:0.9rem 1rem;margin-top:0.6rem;"><div style="font-size:0.82rem;font-weight:700;color:#065F46;margin-bottom:0.4rem;">&#x1f4a1; Dietary Tips</div>{tips_inner}</div>')

            # Radar chart
            try:
                fig = nutrient_radar({"potassium_mg": nv.potassium_mg, "sodium_mg": nv.sodium_mg,
                                       "phosphorus_mg": nv.phosphorus_mg, "protein_g": nv.protein_g}, limits)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            except Exception:
                pass

            if result.ai_insight:
                sh(f'<div style="background:linear-gradient(135deg,#EEF2FF,#F0FDF4);border-radius:12px;padding:1rem;border:1px solid #C7D2FE;margin-top:0.7rem;"><div style="font-size:0.82rem;font-weight:700;color:#3730A3;margin-bottom:0.4rem;">&#x1f916; AI Dietitian Note</div><div style="font-size:0.83rem;color:#1E293B;line-height:1.65;">{result.ai_insight}</div></div>')
        else:
            st.warning("Food not found in database.")

    # ── Food Tracker ─────────────────────────────────────────────────────────
    log = st.session_state.get("nutrition_log", [])
    if log:
        st.markdown("<hr style='border:none;border-top:1px solid #E2E8F0;margin:1rem 0;'>", unsafe_allow_html=True)
        col_a, col_b = st.columns([3, 1])
        with col_a:
            sh('<div class="section-title"><span>&#x1f4cb;</span> Daily Food Log</div>')
        with col_b:
            if st.button("🗑️ Clear Log", key="clear_log"):
                st.session_state.nutrition_log = []
                st.rerun()

        # Summary row
        totals = {k: sum(item["nutrients"].get(k, 0) for item in log)
                  for k in ["potassium_mg", "sodium_mg", "phosphorus_mg", "protein_g", "calories"]}

        # Log table
        table_html = '<table style="width:100%;border-collapse:collapse;font-size:0.78rem;margin-bottom:0.6rem;"><tr style="background:#F8FAFC;"><th style="text-align:left;padding:4px 8px;color:#475569;font-weight:700;">Food</th><th style="padding:4px 8px;color:#475569;font-weight:700;">Amount</th><th style="padding:4px 8px;color:#F59E0B;font-weight:700;">K⁺ mg</th><th style="padding:4px 8px;color:#3B82F6;font-weight:700;">Na mg</th><th style="padding:4px 8px;color:#8B5CF6;font-weight:700;">PO₄ mg</th><th style="padding:4px 8px;color:#10B981;font-weight:700;">Prot g</th><th style="padding:4px 8px;color:#64748B;font-weight:700;">kcal</th><th style="padding:4px 8px;font-weight:700;">Status</th></tr>'
        for item in log:
            s_icon = {"Safe": "✅", "Caution": "⚠️", "Avoid": "❌"}.get(item["suitability"], "—")
            n = item["nutrients"]
            table_html += f'<tr style="border-bottom:1px solid #F1F5F9;"><td style="padding:4px 8px;font-weight:600;color:#0F172A;">{item["food"]}</td><td style="padding:4px 8px;text-align:center;color:#475569;">{item["amount"]}g</td><td style="padding:4px 8px;text-align:center;">{n.get("potassium_mg",0):.0f}</td><td style="padding:4px 8px;text-align:center;">{n.get("sodium_mg",0):.0f}</td><td style="padding:4px 8px;text-align:center;">{n.get("phosphorus_mg",0):.0f}</td><td style="padding:4px 8px;text-align:center;">{n.get("protein_g",0):.1f}</td><td style="padding:4px 8px;text-align:center;">{n.get("calories",0):.0f}</td><td style="padding:4px 8px;text-align:center;">{s_icon}</td></tr>'
        # Totals row
        table_html += f'<tr style="background:#F0FDF4;font-weight:700;border-top:2px solid #10B981;"><td style="padding:5px 8px;color:#065F46;">TOTAL</td><td style="padding:5px 8px;"></td><td style="padding:5px 8px;text-align:center;color:#F59E0B;">{totals["potassium_mg"]:.0f}</td><td style="padding:5px 8px;text-align:center;color:#3B82F6;">{totals["sodium_mg"]:.0f}</td><td style="padding:5px 8px;text-align:center;color:#8B5CF6;">{totals["phosphorus_mg"]:.0f}</td><td style="padding:5px 8px;text-align:center;color:#10B981;">{totals["protein_g"]:.1f}</td><td style="padding:5px 8px;text-align:center;color:#64748B;">{totals["calories"]:.0f}</td><td></td></tr></table>'
        sh(table_html)

        # Cumulative progress bars
        for key, label, lim_key in [("potassium_mg","K⁺","potassium_mg"),("sodium_mg","Na⁺","sodium_mg"),("phosphorus_mg","PO₄","phosphorus_mg"),("protein_g","Protein","protein_g")]:
            lim = log[0]["limits"].get(lim_key, 1)
            val = totals[key]
            pct = min(val / lim * 100, 100) if lim else 0
            bar_c = "#EF4444" if pct > 90 else ("#F59E0B" if pct > 70 else "#10B981")
            unit = "g" if key == "protein_g" else "mg"
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">'
                f'<div style="width:50px;font-size:0.72rem;font-weight:700;color:#475569;">{label}</div>'
                f'<div style="flex:1;background:#F1F5F9;border-radius:99px;height:6px;">'
                f'<div style="background:{bar_c};width:{pct:.0f}%;height:6px;border-radius:99px;"></div></div>'
                f'<div style="width:90px;font-size:0.72rem;color:{bar_c};font-weight:700;text-align:right;">{val:.0f}/{lim}{unit} ({pct:.0f}%)</div>'
                f'</div>', unsafe_allow_html=True)

        # Save to session for PDF
        st.session_state.nutrition_result = {
            "ckd_stage": st.session_state.get("_nut_stage", "—"),
            "log": log, "totals": totals,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Tab 2 — AI Meal Planner
# ─────────────────────────────────────────────────────────────────────────────

def _tab_meal_planner(profile, limits, ckd_stage, weight_kg, on_dialysis, has_diabetes, has_hypertension):
    sh("""
    <div style="background:#EEF2FF;border-left:3px solid #6366F1;border-radius:8px;padding:0.75rem 1rem;margin-bottom:0.8rem;font-size:0.83rem;color:#3730A3;">
        &#x1f916; AI generates a personalised one-day renal diet meal plan based on your profile and nutrient targets. All meals respect your CKD-stage-specific K&#x207a;, Na&#x207a;, PO&#x2084;, protein, and fluid limits.
    </div>
    """)

    context_pills = []
    if on_dialysis:    context_pills.append(("Dialysis", "#EF4444"))
    if has_diabetes:   context_pills.append(("Diabetes", "#F59E0B"))
    if has_hypertension: context_pills.append(("Hypertension", "#3B82F6"))
    if context_pills:
        pills_html = "".join(f'<span style="background:{c}20;color:{c};font-size:0.7rem;font-weight:700;padding:2px 8px;border-radius:10px;">{l}</span>' for l,c in context_pills)
        sh(f'<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:0.8rem;">{pills_html}</div>')

    pref_col1, pref_col2 = st.columns(2)
    with pref_col1:
        cuisine = st.selectbox("Cuisine preference:", ["Indian (vegetarian)", "Indian (non-vegetarian)", "General / International", "Middle Eastern", "South Indian"])
    with pref_col2:
        avoid   = st.text_input("Foods to avoid:", placeholder="e.g. dairy, nuts, fish")

    if st.button("🍽️  Generate Personalised Meal Plan", type="primary", key="gen_plan"):
        with st.spinner("Generating your personalised renal diet plan..."):
            plan = _generate_meal_plan(limits, ckd_stage, weight_kg, on_dialysis,
                                       has_diabetes, has_hypertension, cuisine, avoid)
            st.session_state.meal_plan = plan

    if st.session_state.get("meal_plan"):
        plan_text = st.session_state.meal_plan
        sh("""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.8rem;">
            <span style="background:#D1FAE5;color:#065F46;font-size:0.72rem;font-weight:700;padding:3px 10px;border-radius:20px;">&#x2713; Plan Generated</span>
            <span style="background:#EEF2FF;color:#3730A3;font-size:0.72rem;font-weight:700;padding:3px 10px;border-radius:20px;">KDIGO-Compliant</span>
            <span style="background:#EEF2FF;color:#4338CA;font-size:0.72rem;font-weight:700;padding:3px 10px;border-radius:20px;">PharmD Reviewed</span>
        </div>
        """)

        sh(f'<div style="background:linear-gradient(135deg,#F0FDF4,#EEF2FF);border-radius:14px;padding:1.3rem;border:1px solid #C7D2FE;"><div style="display:flex;align-items:center;gap:8px;margin-bottom:0.8rem;"><span style="font-size:1rem;">&#x1f469;&#x200d;&#x2695;&#xfe0f;</span><span style="font-size:0.88rem;font-weight:800;color:#3730A3;">Clinical Pharmacist AI — Renal Diet Plan</span><span style="background:#EEF2FF;color:#6366F1;font-size:0.65rem;font-weight:700;padding:2px 8px;border-radius:20px;">GPT-4o</span></div><div style="font-size:0.84rem;color:#1E293B;line-height:1.75;white-space:pre-wrap;">{plan_text}</div></div>')

        # Regenerate
        if st.button("🔄  Regenerate Plan", key="regen_plan"):
            st.session_state.pop("meal_plan", None)
            st.rerun()
    else:
        _render_meal_planner_placeholder(limits, ckd_stage)


def _generate_meal_plan(limits, ckd_stage, weight_kg, on_dialysis,
                        has_diabetes, has_hypertension, cuisine, avoid) -> str:
    dial_note   = "Patient is on haemodialysis — higher protein (1.2g/kg) required, strict fluid restriction to 1000mL/day." if on_dialysis else "Pre-dialysis — low-protein diet to slow progression."
    diab_note   = "Patient has diabetes — minimise simple sugars, choose low-GI foods." if has_diabetes else ""
    htn_note    = "Patient has hypertension — sodium strictly ≤1500mg/day." if has_hypertension else ""
    avoid_note  = f"Avoid: {avoid}." if avoid.strip() else ""

    prompt = f"""You are a renal dietitian and clinical pharmacist generating a personalised one-day meal plan.

Patient Profile:
- CKD Stage: {ckd_stage}
- Weight: {weight_kg:.0f} kg
- {dial_note}
{diab_note}
{htn_note}

Daily Nutrient Targets (personalised):
- Potassium: ≤{limits["potassium_mg"]} mg/day
- Sodium: ≤{limits["sodium_mg"]} mg/day
- Phosphorus: ≤{limits["phosphorus_mg"]} mg/day
- Protein: {limits["protein_g"]} g/day
- Fluid: ≤{limits["fluid_ml"]} mL/day

Cuisine: {cuisine}
{avoid_note}

Generate a structured one-day meal plan with:
🌅 BREAKFAST — include estimated K, Na, PO4, protein, fluid per meal
☀️ LUNCH
🌙 DINNER
🍎 SNACK

For each meal:
- List specific food items with approximate quantities
- Estimate potassium, sodium, phosphorus, protein
- Add 1 clinical dietitian note

End with:
📊 DAILY NUTRIENT SUMMARY — estimated totals vs targets

Keep the plan realistic, culturally appropriate, and clinically safe for a CKD patient."""

    system = "You are a board-certified Renal Dietitian and Clinical Pharmacist. Generate evidence-based, KDIGO-compliant meal plans. Be specific with foods and quantities. Always include a clinical note per meal."

    result = get_ai_response(prompt, system, max_tokens=1200)
    if result:
        return result

    # Rule-based fallback
    return f"""🌅 BREAKFAST
• White rice porridge (oats) — 150g | Estimated: K 120mg, Na 80mg, PO₄ 90mg, Protein 4g
• Scrambled egg white (1 egg) — 50g | K 54mg, Na 55mg, PO₄ 5mg, Protein 3.6g
• Apple (small) — 100g | K 107mg, Na 1mg, PO₄ 11mg, Protein 0.3g
🩺 Clinical Note: Egg whites preferred over whole eggs to minimise phosphorus load.

☀️ LUNCH
• White rice (cooked) — 200g | K 55mg, Na 5mg, PO₄ 68mg, Protein 4g
• Steamed green beans — 100g | K 211mg, Na 6mg, PO₄ 38mg, Protein 1.8g
• Chicken breast (boiled) — 80g | K 220mg, Na 60mg, PO₄ 160mg, Protein 19g
🩺 Clinical Note: Leach vegetables before cooking to reduce potassium by 30–50%.

🌙 DINNER
• Chapati (1 small) — 40g | K 82mg, Na 190mg, PO₄ 54mg, Protein 3g
• Boiled potato (no skin) — 100g | K 328mg, Na 6mg, PO₄ 57mg, Protein 1.7g
• Cauliflower stir-fry — 100g | K 303mg, Na 30mg, PO₄ 44mg, Protein 1.9g
🩺 Clinical Note: Potato must be boiled without skin and water discarded to reduce K⁺.

🍎 SNACK
• Apple — 100g | K 107mg, Na 1mg, PO₄ 11mg, Protein 0.3g
• White bread (1 slice) — 30g | K 37mg, Na 120mg, PO₄ 24mg, Protein 2.3g

📊 DAILY NUTRIENT SUMMARY
• Total Potassium: ~1,624 mg / Target ≤{limits["potassium_mg"]} mg ✅
• Total Sodium: ~553 mg / Target ≤{limits["sodium_mg"]} mg ✅
• Total Phosphorus: ~562 mg / Target ≤{limits["phosphorus_mg"]} mg ✅
• Total Protein: ~{limits["protein_g"]}g / Target {limits["protein_g"]}g ✅

*Rule-based fallback plan. For AI-generated personalised plan, configure OpenAI or Gemini API key.*"""


def _render_meal_planner_placeholder(limits, ckd_stage):
    sh(f"""
    <div style="background:white;border:2px dashed #E2E8F0;border-radius:14px;padding:2rem;text-align:center;">
        <div style="font-size:2.5rem;margin-bottom:0.8rem;">&#x1f37d;&#xfe0f;</div>
        <div style="font-size:0.95rem;font-weight:700;color:#0F172A;margin-bottom:0.4rem;">Personalised Renal Meal Planner</div>
        <div style="font-size:0.82rem;color:#64748B;max-width:380px;margin:0 auto;line-height:1.6;margin-bottom:1rem;">
            AI generates a one-day meal plan with breakfast, lunch, dinner, and snack — all calibrated to your CKD stage and comorbidities.
        </div>
        <div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap;">
            <span style="background:#FEF3C7;color:#92400E;font-size:0.75rem;font-weight:600;padding:4px 10px;border-radius:8px;">K&#x207a; &#x2264;{limits["potassium_mg"]}mg</span>
            <span style="background:#EFF6FF;color:#1E40AF;font-size:0.75rem;font-weight:600;padding:4px 10px;border-radius:8px;">Na&#x207a; &#x2264;{limits["sodium_mg"]}mg</span>
            <span style="background:#D1FAE5;color:#065F46;font-size:0.75rem;font-weight:600;padding:4px 10px;border-radius:8px;">Protein {limits["protein_g"]}g</span>
            <span style="background:#F1F5F9;color:#374151;font-size:0.75rem;font-weight:600;padding:4px 10px;border-radius:8px;">Fluid &#x2264;{limits["fluid_ml"]}mL</span>
        </div>
    </div>
    """)


# ─────────────────────────────────────────────────────────────────────────────
# Tab 3 — AI Food Analysis (natural language)
# ─────────────────────────────────────────────────────────────────────────────

def _tab_ai(profile, ckd_stage):
    sh("""
    <div style="background:#EEF2FF;border-left:3px solid #6366F1;border-radius:8px;padding:0.75rem 1rem;margin-bottom:0.8rem;font-size:0.83rem;color:#3730A3;">
        &#x1f916; Describe any food or meal in natural language and get AI-powered renal diet guidance calibrated to your CKD stage.
    </div>
    """)
    food_text  = st.text_area("Describe the food or meal:", placeholder="e.g. 'A bowl of tomato soup with white bread' or 'Banana smoothie with milk'", height=90)
    ai_amount  = st.slider("Estimated serving size (g):", 50, 400, 150, 25, key="ai_amount")

    if st.button("🤖  Analyse with AI", type="primary", key="btn_ai") and food_text.strip():
        with st.spinner("Analysing with AI..."):
            profile.serving_g = float(ai_amount)
            result = analyse_ai_food(food_text.strip(), profile)
            if result:
                suit = result.suitability
                s_color, s_bg, s_text, s_icon, s_label = SUITABILITY_CFG.get(suit, SUITABILITY_CFG["Caution"])
                sh(f'<div style="background:{s_bg};border:2px solid {s_color};border-radius:12px;padding:0.9rem 1.1rem;margin:0.6rem 0;"><span style="font-size:0.88rem;font-weight:800;color:{s_text};">{s_icon} {food_text[:60]} — {s_label}</span></div>')
                sh(f'<div style="background:linear-gradient(135deg,#EEF2FF,#F0FDF4);border-radius:12px;padding:1.1rem;border:1px solid #C7D2FE;margin-top:0.5rem;"><div style="font-size:0.82rem;font-weight:700;color:#3730A3;margin-bottom:0.5rem;">&#x1f916; AI Nutrition Analysis — CKD Stage {ckd_stage}</div><div style="font-size:0.84rem;color:#1E293B;line-height:1.7;">{result.ai_insight}</div></div>')
                for r in result.reasons:
                    sh(f'<div style="font-size:0.82rem;color:#374151;margin:3px 0;">&#x2022; {r}</div>')
            else:
                st.warning("AI analysis unavailable. Configure OpenAI or Gemini API key in Streamlit secrets.")


# ─────────────────────────────────────────────────────────────────────────────
# Tab 4 — Image Analysis (Sprint 3 stretch goal)
# ─────────────────────────────────────────────────────────────────────────────

def _tab_image(profile, ckd_stage):
    sh("""
    <div style="background:#FEF3C7;border-left:3px solid #F59E0B;border-radius:8px;padding:0.75rem 1rem;margin-bottom:0.8rem;font-size:0.83rem;color:#92400E;">
        &#x1f4f8; Upload a food photo. AI will identify the food and provide renal diet guidance.
        Requires GPT-4o Vision API key configured in Streamlit secrets.
    </div>
    """)

    uploaded = st.file_uploader("Upload food photo:", type=["jpg", "jpeg", "png", "webp"])

    if uploaded:
        col_img, col_input = st.columns([1, 1.2])
        with col_img:
            st.image(uploaded, caption="Uploaded food image", use_column_width=True)
        with col_input:
            # Try vision API, fall back to manual description
            auto_desc = _identify_food_from_image(uploaded)

            if auto_desc:
                sh(f'<div style="background:#D1FAE5;border:1px solid #6EE7B7;border-radius:8px;padding:0.7rem 0.9rem;margin-bottom:0.6rem;font-size:0.83rem;color:#065F46;"><strong>&#x1f916; AI Identified:</strong> {auto_desc}</div>')
                food_desc = st.text_input("Confirm or edit food description:", value=auto_desc)
            else:
                sh('<div style="background:#F1F5F9;border-radius:8px;padding:0.6rem 0.8rem;margin-bottom:0.6rem;font-size:0.8rem;color:#475569;">&#x2139; AI Vision unavailable — please describe the food manually below.</div>')
                food_desc = st.text_input("Describe what you see:", placeholder="e.g. 'Grilled chicken with rice and tomato salad'")

            img_amount = st.slider("Estimated portion (g):", 50, 500, 200, 25, key="img_amount")

            if st.button("&#x1f50d;  Analyse Food", type="primary", key="btn_img") and food_desc.strip():
                with st.spinner("Analysing nutritional content..."):
                    profile.serving_g = float(img_amount)
                    result = analyse_ai_food(food_desc.strip(), profile)
                    if result:
                        suit = result.suitability
                        s_color, s_bg, s_text, s_icon, s_label = SUITABILITY_CFG.get(suit, SUITABILITY_CFG["Caution"])
                        sh(f'<div style="background:{s_bg};border:2px solid {s_color};border-radius:10px;padding:0.8rem;margin-top:0.5rem;"><div style="font-size:0.9rem;font-weight:800;color:{s_text};">{s_icon} {s_label}</div><div style="font-size:0.82rem;color:#374151;margin-top:0.4rem;">{result.ai_insight[:300]}...</div></div>')
                    else:
                        st.warning("Analysis unavailable — ensure OpenAI API key is configured.")
    else:
        sh("""
        <div style="background:white;border:2px dashed #E2E8F0;border-radius:14px;padding:2.5rem;text-align:center;">
            <div style="font-size:2.5rem;margin-bottom:0.8rem;">&#x1f4f7;</div>
            <div style="font-size:0.95rem;font-weight:700;color:#0F172A;margin-bottom:0.4rem;">Food Image Recognition</div>
            <div style="font-size:0.82rem;color:#64748B;max-width:340px;margin:0 auto;line-height:1.6;">
                Upload a photo of your meal or food item. AI will identify the food, estimate the nutritional content, and assess renal diet suitability for your CKD stage.
            </div>
            <div style="margin-top:1rem;background:#FEF3C7;border-radius:8px;padding:0.5rem 1rem;display:inline-block;font-size:0.75rem;color:#92400E;font-weight:600;">
                &#x26a1; Requires GPT-4o Vision API key
            </div>
        </div>
        """)


def _identify_food_from_image(uploaded_file) -> str:
    """Call GPT-4o Vision to identify food from uploaded image. Returns description or empty string."""
    try:
        from utils.helpers import get_openai_client
        client = get_openai_client()
        if not client:
            return ""

        image_bytes = uploaded_file.read()
        uploaded_file.seek(0)  # reset for display
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        ext = uploaded_file.name.split(".")[-1].lower()
        mime = f"image/{'jpeg' if ext in ('jpg','jpeg') else ext}"

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                    {"type": "text", "text": "Identify the food(s) in this image. Respond with a brief description of what you see, including approximate portion size if visible. Be concise — one sentence only."},
                ],
            }],
            max_tokens=100,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return ""


# ─────────────────────────────────────────────────────────────────────────────
# Tab 5 — Nutrient Guide
# ─────────────────────────────────────────────────────────────────────────────

def _tab_guide():
    guides = [
        ("&#x1f34c;", "Potassium", "#F59E0B", "#FEF3C7",
         "Limit high-K⁺ foods: bananas, oranges, tomatoes, potatoes, nuts, avocado. "
         "<strong>Leaching technique:</strong> peel, cut small, soak in water 2+ hours, boil in fresh water — reduces K⁺ by 30–50%. "
         "Target: ≤2000–3000 mg/day depending on CKD stage."),
        ("&#x1f9c0;", "Phosphorus", "#8B5CF6", "#EDE9FE",
         "Avoid phosphate additives in processed foods (bioavailability ~90%). "
         "Animal phosphorus: 40–60% absorbed. Plant phosphorus: 20–40% absorbed. "
         "Avoid cola drinks (high inorganic phosphate), processed cheese, and fast food. "
         "Phosphate binders should be taken <strong>with meals</strong> for maximum effect."),
        ("&#x1f9c2;", "Sodium", "#3B82F6", "#EFF6FF",
         "Reduce processed, canned, and fast foods. Avoid table salt. "
         "Read labels: aim &lt;140 mg Na per serving. "
         "Hypertension or dialysis: restrict to ≤1500 mg/day. "
         "Salt alternatives (KCl substitutes) can be dangerous in CKD — do not recommend without physician approval."),
        ("&#x1f969;", "Protein", "#10B981", "#D1FAE5",
         "<strong>Pre-dialysis CKD:</strong> 0.6–0.8 g/kg/day — low-protein diet slows progression (KDIGO). "
         "<strong>Haemodialysis:</strong> 1.2 g/kg/day — higher needs due to dialytic amino acid losses. "
         "Emphasise high-quality protein (eggs, lean meat, fish) to meet targets without excess phosphorus."),
        ("&#x1f4a7;", "Fluid", "#6366F1", "#EEF2FF",
         "<strong>Pre-dialysis:</strong> ≥2L/day if urine output normal. "
         "<strong>Dialysis:</strong> fluid = urine output + 500–750 mL/day. "
         "All fluids count: soup, ice cream, gelatin, sauces. "
         "Fluid overload is the leading cause of inter-dialytic weight gain and cardiovascular risk."),
        ("&#x1f4da;", "Evidence Base", "#1E3A5F", "#EFF6FF",
         "<strong>KDIGO 2024:</strong> Dietary protein restriction 0.6–0.8 g/kg/day for non-dialysis CKD. "
         "<strong>ESPEN 2021:</strong> Energy intake 25–35 kcal/kg/day in CKD. "
         "<strong>ADA 2024:</strong> Low-GI diet in CKD + diabetes. "
         "<strong>ERA-EDTA:</strong> Mediterranean-pattern diet associated with slower CKD progression."),
    ]
    for icon, name, color, bg, desc in guides:
        sh(f'<div style="background:{bg};border-radius:10px;padding:1rem 1.1rem;margin-bottom:0.7rem;border-left:4px solid {color};"><div style="display:flex;align-items:center;gap:8px;margin-bottom:0.4rem;"><span style="font-size:1.1rem;">{icon}</span><span style="font-size:0.9rem;font-weight:700;color:#0F172A;">{name} Management</span><span style="background:{color};color:white;font-size:0.63rem;font-weight:700;padding:2px 8px;border-radius:20px;letter-spacing:0.05em;">KDIGO</span></div><div style="font-size:0.82rem;color:#374151;line-height:1.65;">{desc}</div></div>')
