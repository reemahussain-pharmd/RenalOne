"""Kidney Nutrition Intelligence Page — RenalCare AI."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from nutrition.analyzer import analyse_food, analyse_ai_food, NutritionProfile
from nutrition.food_database import FOOD_DB as FOOD_DATABASE
from components.charts import nutrient_radar

STAGE_MAP = {"G3a": 3, "G3b": 3, "G4": 4, "G5": 5}

DISPLAY_LIMITS = {
    "G3a": {"potassium_mg": 3000, "sodium_mg": 2000, "phosphorus_mg": 800, "protein_g": 50,  "fluid_ml": 2000},
    "G3b": {"potassium_mg": 3000, "sodium_mg": 2000, "phosphorus_mg": 800, "protein_g": 45,  "fluid_ml": 1800},
    "G4":  {"potassium_mg": 2000, "sodium_mg": 1500, "phosphorus_mg": 800, "protein_g": 40,  "fluid_ml": 1500},
    "G5":  {"potassium_mg": 2000, "sodium_mg": 1000, "phosphorus_mg": 800, "protein_g": 60,  "fluid_ml": 1000},
}

LIMIT_CARDS = [
    ("potassium_mg",  "mg Potassium",  "#FEF3C7", "#92400E", "#78350F"),
    ("sodium_mg",     "mg Sodium",     "#EFF6FF", "#1D4ED8", "#1E3A8A"),
    ("phosphorus_mg", "mg Phosphorus", "#EDE9FE", "#5B21B6", "#4C1D95"),
    ("protein_g",     "g Protein",     "#D1FAE5", "#065F46", "#064E3B"),
    ("fluid_ml",      "mL Fluid",      "#F1F5F9", "#374151", "#1F2937"),
]


def render():
    st.markdown("""
<div class="page-header">
<div style="display:flex;align-items:flex-start;justify-content:space-between;">
<div>
<div style="display:flex;align-items:center;gap:8px;margin-bottom:0.5rem;">
<span style="font-size:1.5rem;">\U0001f966</span>
<span style="background:rgba(255,255,255,0.15);color:rgba(255,255,255,0.9);font-size:0.7rem;font-weight:700;padding:3px 10px;border-radius:20px;letter-spacing:0.06em;">RENAL DIETETICS MODULE</span>
</div>
<h1 style="color:white !important;font-size:1.7rem !important;font-weight:800 !important;margin:0 0 0.3rem 0 !important;">Kidney Nutrition Intelligence</h1>
<p style="color:rgba(255,255,255,0.72) !important;font-size:0.88rem !important;margin:0 !important;">Potassium &bull; Phosphorus &bull; Sodium &bull; Protein analysis per CKD stage</p>
</div>
</div>
</div>
""", unsafe_allow_html=True)

    pc1, pc2, pc3, pc4 = st.columns(4)
    with pc1:
        ckd_stage = st.selectbox("CKD Stage", ["G3a", "G3b", "G4", "G5"],
                                  help="Determines daily nutrient limits")
    with pc2:
        weight_kg = st.number_input("Weight (kg)", 30.0, 200.0, 65.0, 1.0)
    with pc3:
        on_dialysis = st.checkbox("On Dialysis", value=(ckd_stage == "G5"))
    with pc4:
        has_diabetes = st.checkbox("Diabetes", value=False)

    limits = DISPLAY_LIMITS[ckd_stage]
    stage_int = STAGE_MAP[ckd_stage]
    dialysis_tag = " (Dialysis)" if on_dialysis else ""

    # ── Daily limits — using st.columns so no HTML grid needed ────────────
    st.markdown(
        f'<div style="font-size:0.85rem;font-weight:700;color:#0F172A;margin:0.8rem 0 0.5rem;">'
        f'\U0001f4ca Daily Limits — CKD Stage {ckd_stage}{dialysis_tag}</div>',
        unsafe_allow_html=True,
    )
    lc1, lc2, lc3, lc4, lc5 = st.columns(5)
    for col, (key, label, bg, color, dark) in zip([lc1, lc2, lc3, lc4, lc5], LIMIT_CARDS):
        val = limits[key]
        with col:
            st.markdown(
                f'<div style="text-align:center;background:{bg};border-radius:10px;padding:0.75rem 0.5rem;">'
                f'<div style="font-size:1.1rem;font-weight:800;color:{color};">{val:,}</div>'
                f'<div style="font-size:0.65rem;font-weight:700;color:{dark};text-transform:uppercase;letter-spacing:0.04em;">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-top:0.8rem;'></div>", unsafe_allow_html=True)

    profile = NutritionProfile(
        ckd_stage=stage_int,
        on_dialysis=on_dialysis,
        has_diabetes=has_diabetes,
        weight_kg=weight_kg,
    )

    tab1, tab2, tab3 = st.tabs([
        "  \U0001f50d  Search Food Database  ",
        "  \U0001f916  AI Food Analysis  ",
        "  \U0001f4d6  Nutrient Guide  ",
    ])

    with tab1:
        _tab_search(profile, limits)
    with tab2:
        _tab_ai(profile, ckd_stage)
    with tab3:
        _tab_guide()


def _tab_search(profile, limits):
    foods = sorted(FOOD_DATABASE.keys())
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_food = st.selectbox("Search food database:", foods)
    with col2:
        amount = st.slider("Serving (g):", 25, 300, 100, 25)

    if st.button("\U0001f50d  Analyze This Food", type="primary"):
        profile.serving_g = float(amount)
        result = analyse_food(selected_food, profile)

        if result:
            suit = result.suitability
            suit_cfg = {
                "Safe":    ("#10B981", "#D1FAE5", "#065F46", "✅",  "SAFE"),
                "Caution": ("#F59E0B", "#FEF3C7", "#92400E", "⚠️", "USE WITH CAUTION"),
                "Avoid":   ("#EF4444", "#FEE2E2", "#991B1B", "❌", "AVOID"),
            }
            s_color, s_bg, s_text, s_icon, s_label = suit_cfg.get(suit, suit_cfg["Caution"])

            st.markdown(
                f'<div style="background:{s_bg};border:2px solid {s_color};border-radius:14px;padding:1.2rem 1.5rem;margin:0.8rem 0;">'
                f'<div style="display:flex;align-items:center;gap:10px;">'
                f'<span style="font-size:1.5rem;">{s_icon}</span>'
                f'<div>'
                f'<div style="font-size:1rem;font-weight:800;color:{s_text};">{result.food_name}</div>'
                f'<div style="font-size:0.85rem;font-weight:700;color:{s_color};">{s_label} — {amount}g serving</div>'
                f'</div></div></div>',
                unsafe_allow_html=True,
            )

            nv = result.nutrients
            nutrient_rows = [
                ("Potassium",  nv.potassium_mg,  limits["potassium_mg"],  "mg", "#F59E0B"),
                ("Sodium",     nv.sodium_mg,     limits["sodium_mg"],     "mg", "#3B82F6"),
                ("Phosphorus", nv.phosphorus_mg, limits["phosphorus_mg"], "mg", "#8B5CF6"),
                ("Protein",    nv.protein_g,     limits["protein_g"],     "g",  "#10B981"),
            ]
            for name, val, lim, unit, color in nutrient_rows:
                pct = min(val / lim * 100, 100) if lim > 0 else 0
                bar_color = "#EF4444" if pct > 80 else (color if pct > 50 else "#10B981")
                st.markdown(
                    f'<div style="margin-bottom:0.7rem;">'
                    f'<div style="display:flex;justify-content:space-between;margin-bottom:3px;">'
                    f'<span style="font-size:0.82rem;font-weight:600;color:#374151;">{name}</span>'
                    f'<span style="font-size:0.82rem;font-weight:700;color:{bar_color};">{val:.0f}{unit} <span style="color:#94A3B8;font-weight:400;">/ {lim}{unit} daily</span></span>'
                    f'</div>'
                    f'<div style="background:#F1F5F9;border-radius:999px;height:8px;">'
                    f'<div style="background:{bar_color};width:{pct:.0f}%;height:8px;border-radius:999px;"></div>'
                    f'</div>'
                    f'<div style="font-size:0.72rem;color:#94A3B8;margin-top:2px;">{pct:.0f}% of daily limit per serving</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            if result.reasons:
                st.markdown('<div style="font-size:0.88rem;font-weight:700;color:#0F172A;margin:0.8rem 0 0.4rem;">\U0001f4dd Clinical Notes</div>', unsafe_allow_html=True)
                for r in result.reasons:
                    st.markdown(f'<div style="font-size:0.83rem;color:#374151;margin-bottom:4px;">&#x2022; {r}</div>', unsafe_allow_html=True)

            if result.tips:
                tips_inner = "".join(f'<div style="font-size:0.82rem;color:#166534;margin-bottom:3px;">&#x2713; {t}</div>' for t in result.tips)
                st.markdown(
                    f'<div style="background:#F0FDF4;border-radius:10px;padding:0.9rem 1.1rem;margin-top:0.7rem;">'
                    f'<div style="font-size:0.82rem;font-weight:700;color:#065F46;margin-bottom:0.4rem;">\U0001f4a1 Dietary Tips</div>'
                    f'{tips_inner}</div>',
                    unsafe_allow_html=True,
                )

            try:
                nutrients_dict = {
                    "potassium_mg": nv.potassium_mg,
                    "sodium_mg":    nv.sodium_mg,
                    "phosphorus_mg": nv.phosphorus_mg,
                    "protein_g":    nv.protein_g,
                }
                fig = nutrient_radar(nutrients_dict, limits)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            except Exception:
                pass

            if result.ai_insight:
                st.markdown(
                    f'<div style="background:linear-gradient(135deg,#EEF2FF,#F0FDF4);border-radius:12px;padding:1rem;border:1px solid #C7D2FE;margin-top:0.8rem;">'
                    f'<div style="font-size:0.82rem;font-weight:700;color:#3730A3;margin-bottom:0.4rem;">\U0001f916 AI Dietitian Note</div>'
                    f'<div style="font-size:0.83rem;color:#1E293B;line-height:1.65;">{result.ai_insight}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.warning("Food not found in database.")


def _tab_ai(profile, ckd_stage):
    st.markdown(
        '<div style="background:#EEF2FF;border-left:3px solid #6366F1;border-radius:8px;padding:0.75rem 1rem;margin-bottom:0.8rem;font-size:0.84rem;color:#3730A3;">'
        '\U0001f916 Describe any food or meal in natural language and get AI-powered renal diet guidance.'
        '</div>',
        unsafe_allow_html=True,
    )
    food_text = st.text_area(
        "Describe the food or meal:",
        placeholder="e.g. 'A bowl of tomato soup with white bread' or 'Banana smoothie with milk'",
        height=100,
    )
    ai_amount = st.slider("Estimated serving size (g):", 50, 400, 150, 25, key="ai_amount")

    if st.button("\U0001f916  Analyze with AI", type="primary") and food_text.strip():
        with st.spinner("Analyzing with AI..."):
            profile.serving_g = float(ai_amount)
            result = analyse_ai_food(food_text.strip(), profile)
            if result:
                suit_cfg = {
                    "Safe":    ("#10B981", "#D1FAE5", "#065F46", "✅",  "GENERALLY SAFE"),
                    "Caution": ("#F59E0B", "#FEF3C7", "#92400E", "⚠️", "USE WITH CAUTION"),
                    "Avoid":   ("#EF4444", "#FEE2E2", "#991B1B", "❌", "AVOID / LIMIT"),
                }
                suit = result.suitability
                s_color, s_bg, s_text, s_icon, s_label = suit_cfg.get(suit, suit_cfg["Caution"])

                st.markdown(
                    f'<div style="background:{s_bg};border:2px solid {s_color};border-radius:14px;padding:1rem 1.2rem;margin:0.8rem 0;">'
                    f'<span style="font-size:0.9rem;font-weight:800;color:{s_text};">{s_icon} {food_text[:60]} — {s_label}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div style="background:linear-gradient(135deg,#EEF2FF,#F0FDF4);border-radius:12px;padding:1.2rem;border:1px solid #C7D2FE;margin-top:0.5rem;">'
                    f'<div style="font-size:0.82rem;font-weight:700;color:#3730A3;margin-bottom:0.6rem;">\U0001f916 AI Nutrition Analysis — CKD Stage {ckd_stage}</div>'
                    f'<div style="font-size:0.85rem;color:#1E293B;line-height:1.7;">{result.ai_insight}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                for r in result.reasons:
                    st.markdown(f'<div style="font-size:0.83rem;color:#374151;margin:3px 0;">&#x2022; {r}</div>', unsafe_allow_html=True)
            else:
                st.warning("AI analysis unavailable. Please configure an API key in Streamlit secrets.")


def _tab_guide():
    guides = [
        ("\U0001f34c", "Potassium", "#F59E0B", "#FEF3C7",
         "Limit high-potassium foods: bananas, oranges, tomatoes, potatoes. "
         "Leaching vegetables (peel, cut small, soak in water, boil in fresh water) reduces potassium by 30-50%."),
        ("\U0001f9c0", "Phosphorus", "#8B5CF6", "#EDE9FE",
         "Avoid phosphate additives in processed foods (highest bioavailability). "
         "Animal protein phosphorus: 40-60% absorbed. Plant phosphorus: 20-40% absorbed."),
        ("\U0001f9c2", "Sodium", "#3B82F6", "#EFF6FF",
         "Reduce processed, canned, and fast foods. Avoid adding table salt. "
         "Check labels: aim less than 140 mg sodium per serving."),
        ("\U0001f969", "Protein", "#10B981", "#D1FAE5",
         "Pre-dialysis CKD: low-protein diet (0.6-0.8 g/kg/day) slows progression. "
         "On dialysis: higher protein needed (1.0-1.2 g/kg/day) due to dialytic losses."),
        ("\U0001f4a7", "Fluid", "#6366F1", "#EEF2FF",
         "Dialysis patients: restrict based on residual urine output. "
         "Fluid = urine output + 500 mL/day. Includes soups, ice cream, gelatin."),
    ]
    for icon, name, color, bg, desc in guides:
        st.markdown(
            f'<div style="background:{bg};border-radius:10px;padding:1rem 1.1rem;margin-bottom:0.7rem;border-left:4px solid {color};">'
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:0.4rem;">'
            f'<span style="font-size:1.1rem;">{icon}</span>'
            f'<span style="font-size:0.9rem;font-weight:700;color:#0F172A;">{name} Management</span>'
            f'<span style="background:{color};color:white;font-size:0.65rem;font-weight:700;padding:2px 8px;border-radius:20px;letter-spacing:0.05em;">KDIGO</span>'
            f'</div>'
            f'<div style="font-size:0.83rem;color:#374151;line-height:1.6;">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
