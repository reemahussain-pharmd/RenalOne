"""Kidney Nutrition Intelligence Page â€” RenalCare AI."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from nutrition.analyzer import analyse_food, analyse_ai_food, NutritionProfile, SUITABILITY_MAP
from nutrition.food_database import get_all_food_names
from components.charts import nutrient_radar
from utils.constants import NUTRITION_LIMITS


def _nutrient_bar(label: str, value: float, unit: str, daily_limit: float, color: str = "#2980b9"):
    pct = min((value / daily_limit * 100) if daily_limit > 0 else 0, 100)
    bar_color = "#27ae60" if pct < 33 else "#f39c12" if pct < 66 else "#e74c3c"
    st.markdown(f"""
    <div style='margin-bottom:0.6rem;'>
        <div style='display:flex; justify-content:space-between; font-size:0.82rem;'>
            <span style='font-weight:600; color:#4a5568;'>{label}</span>
            <span style='color:#1e3a5f;'>{value:.1f} {unit} <span style='color:#a0aec0; font-size:0.75rem;'>/ {daily_limit:.0f} {unit} daily</span></span>
        </div>
        <div style='background:#f0f0f0; border-radius:4px; height:8px; margin-top:3px;'>
            <div style='background:{bar_color}; width:{pct:.0f}%; height:8px; border-radius:4px;'></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render():
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1a4731, #27ae60);
                border-radius: 12px; padding: 1.5rem 2rem; margin-bottom: 1.5rem;'>
        <h2 style='color:white; margin:0; font-size:1.5rem;'>ðŸ¥— Kidney Nutrition Intelligence</h2>
        <p style='color:#a9f7c4; margin:0.3rem 0 0 0; font-size:0.88rem;'>
            Personalised renal nutrition assistant Â· CKD stage-specific food analysis
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Patient profile sidebar
    with st.expander("âš™ï¸ Patient Nutrition Profile", expanded=True):
        pc1, pc2, pc3, pc4 = st.columns(4)
        with pc1:
            ckd_stage = st.selectbox("CKD Stage", [1, 2, 3, 4, 5], index=2, key="nut_stage")
        with pc2:
            on_dialysis = st.checkbox("On Dialysis", value=False, key="nut_dial")
        with pc3:
            has_diabetes = st.checkbox("Diabetes", value=True, key="nut_dm")
        with pc4:
            weight_kg = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=68.0, step=0.5, key="nut_wt")
        serving_g = st.slider("Serving Size (grams)", min_value=50, max_value=400, value=150, step=25,
                              help="Adjust the serving size for the analysis")

    profile = NutritionProfile(
        ckd_stage=ckd_stage,
        on_dialysis=on_dialysis,
        has_diabetes=has_diabetes,
        weight_kg=weight_kg,
        serving_g=float(serving_g),
    )

    # Daily limits for current profile
    if on_dialysis:
        limits = {"potassium_mg": 2000, "sodium_mg": 2000, "phosphorus_mg": 800, "protein_g_per_kg": 1.2}
    else:
        limits = NUTRITION_LIMITS.get(ckd_stage, NUTRITION_LIMITS[3])

    st.markdown(f"""
    <div class='info-box' style='font-size:0.85rem;'>
        <b>ðŸ“Š Daily limits for CKD Stage {ckd_stage}{'  (Dialysis)' if on_dialysis else ''}:</b>
        Potassium â‰¤{limits['potassium_mg']:,} mg Â· Sodium â‰¤{limits['sodium_mg']:,} mg Â·
        Phosphorus â‰¤{limits['phosphorus_mg']:,} mg Â· Protein {limits['protein_g_per_kg']} g/kg/day
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["ðŸ” Search Food", "ðŸ“· Describe Food (AI)", "ðŸ“Š Nutrient Guide"])

    # ---- Tab 1: Search ----
    with tab1:
        st.markdown("### Search Food Database")
        all_foods = get_all_food_names()

        search_col, btn_col = st.columns([3, 1])
        with search_col:
            selected_food = st.selectbox(
                "Select or type a food name",
                options=all_foods,
                index=all_foods.index("white rice (cooked)") if "white rice (cooked)" in all_foods else 0,
                format_func=lambda x: x.title(),
            )
        with btn_col:
            st.markdown("<br>", unsafe_allow_html=True)
            analyse_btn = st.button("ðŸ” Analyse", key="analyse_search", use_container_width=True)

        if analyse_btn and selected_food:
            with st.spinner(f"Analysing {selected_food.title()}..."):
                assessment = analyse_food(selected_food, profile)

            if assessment:
                _display_assessment(assessment, limits, profile)
            else:
                st.error("Could not analyse this food. Please try another.")

    # ---- Tab 2: AI Description ----
    with tab2:
        st.markdown("### Describe a Food Item (AI Analysis)")
        st.markdown("""
        <div class='info-box'>
            Enter any food item not in the database. The AI will estimate its nutrient content
            and provide renal-specific guidance. Accuracy is best for common, single-ingredient foods.
        </div>
        """, unsafe_allow_html=True)

        food_desc = st.text_input(
            "Describe the food",
            placeholder="e.g. Grilled salmon fillet, Idli (South Indian rice cake), Masala dosa, Palak paneer",
        )
        if st.button("ðŸ¤– AI Nutritional Analysis", key="ai_analyse", use_container_width=False):
            if food_desc.strip():
                with st.spinner("Running AI nutritional analysis..."):
                    assessment = analyse_ai_food(food_desc.strip(), profile)
                if assessment:
                    _display_assessment(assessment, limits, profile)
                else:
                    st.warning("AI analysis unavailable. Please configure an OpenAI or Gemini API key in .env file.")
            else:
                st.warning("Please enter a food description.")

    # ---- Tab 3: Nutrient Guide ----
    with tab3:
        st.markdown("### ðŸ“Š Renal Nutrition Quick Reference")
        _show_nutrition_guide(ckd_stage, on_dialysis)


def _display_assessment(assessment, limits: dict, profile: NutritionProfile):
    smap = SUITABILITY_MAP[assessment.suitability]
    suit_icon = smap["icon"]
    suit_label = smap["label"]
    suit_color = smap["color"]

    css_class = {"Safe": "food-safe", "Caution": "food-caution", "Avoid": "food-avoid"}[assessment.suitability]

    st.markdown(f"""
    <div class='{css_class}' style='margin:1rem 0;'>
        <div style='font-size:1.1rem; font-weight:700; color:#1e3a5f; margin-bottom:0.3rem;'>
            {assessment.food_name} ({assessment.serving_g:.0f}g serving)
        </div>
        <div style='font-size:1.3rem; font-weight:700; color:{suit_color};'>
            {suit_icon} {suit_label}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Nutrient details
    n = assessment.nutrients
    col_left, col_right = st.columns([1.2, 1])
    with col_left:
        st.markdown("#### ðŸ§ª Nutrient Content (per serving)")
        _nutrient_bar("Potassium", n.potassium_mg, "mg", limits["potassium_mg"] * 0.3)
        _nutrient_bar("Sodium", n.sodium_mg, "mg", limits["sodium_mg"] * 0.3)
        _nutrient_bar("Phosphorus", n.phosphorus_mg, "mg", limits["phosphorus_mg"] * 0.3)
        _nutrient_bar("Protein", n.protein_g, "g", limits["protein_g_per_kg"] * profile.weight_kg * 0.25)
        _nutrient_bar("Calories", n.calories, "kcal", 600)

        # Nutrient cards
        st.markdown("<br>", unsafe_allow_html=True)
        ncols = st.columns(5)
        metrics = [
            ("Kâº", f"{n.potassium_mg:.0f}", "mg", "#e74c3c"),
            ("Na", f"{n.sodium_mg:.0f}", "mg", "#e67e22"),
            ("POâ‚„", f"{n.phosphorus_mg:.0f}", "mg", "#8e44ad"),
            ("Protein", f"{n.protein_g:.1f}", "g", "#2980b9"),
            ("Cal", f"{n.calories:.0f}", "kcal", "#27ae60"),
        ]
        for col, (name, val, unit, color) in zip(ncols, metrics):
            with col:
                st.markdown(f"""
                <div style='background:white; border-radius:8px; padding:0.5rem; text-align:center;
                            box-shadow:0 1px 4px rgba(0,0,0,0.08); border-top:3px solid {color};'>
                    <div style='font-size:0.7rem; color:#718096; font-weight:600;'>{name}</div>
                    <div style='font-size:1.2rem; font-weight:700; color:{color};'>{val}</div>
                    <div style='font-size:0.65rem; color:#a0aec0;'>{unit}</div>
                </div>
                """, unsafe_allow_html=True)

    with col_right:
        try:
            fig = nutrient_radar(n, limits, assessment.food_name)
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            pass

    # Concerns and tips
    if assessment.reasons:
        st.markdown("#### âš ï¸ Dietary Considerations")
        for reason in assessment.reasons:
            st.markdown(f"""
            <div class='warning-box' style='font-size:0.85rem; margin:0.3rem 0;'>âš ï¸ {reason}</div>
            """, unsafe_allow_html=True)

    if assessment.tips:
        st.markdown("#### ðŸ’¡ Dietary Tips")
        for tip in assessment.tips:
            st.markdown(f"""
            <div class='info-box' style='font-size:0.85rem; margin:0.3rem 0;'>ðŸ’¡ {tip}</div>
            """, unsafe_allow_html=True)

    # AI insight
    if assessment.ai_insight:
        st.markdown("#### ðŸ¤– Renal Dietitian AI Insight")
        st.markdown(f"""
        <div style='background:white; border-radius:10px; padding:1.2rem; box-shadow:0 2px 8px rgba(0,0,0,0.06);
                    border-left:4px solid #27ae60; font-size:0.88rem; color:#4a5568; line-height:1.6;'>
            {assessment.ai_insight}
        </div>
        """, unsafe_allow_html=True)


def _show_nutrition_guide(stage: int, on_dialysis: bool):
    limits = NUTRITION_LIMITS.get(stage, NUTRITION_LIMITS[3])

    st.markdown(f"""
    <div style='background:white; border-radius:10px; padding:1.5rem; box-shadow:0 2px 8px rgba(0,0,0,0.06);'>
        <h4 style='color:#1e3a5f; margin-top:0;'>Daily Limits â€” CKD Stage {stage}{'  (Dialysis)' if on_dialysis else ''}</h4>
        <table style='width:100%; border-collapse:collapse; font-size:0.88rem;'>
            <tr style='background:#ebf8ff;'>
                <th style='padding:8px 12px; text-align:left; color:#2980b9;'>Nutrient</th>
                <th style='padding:8px 12px; text-align:right; color:#2980b9;'>Daily Target</th>
                <th style='padding:8px 12px; text-align:right; color:#2980b9;'>Per Meal (~30%)</th>
            </tr>
            <tr><td style='padding:7px 12px;'>ðŸŸ  Potassium</td><td style='text-align:right; padding:7px 12px;'>â‰¤{limits['potassium_mg']:,} mg</td><td style='text-align:right; padding:7px 12px;'>â‰¤{limits['potassium_mg']*0.3:.0f} mg</td></tr>
            <tr style='background:#f8f9fa;'><td style='padding:7px 12px;'>ðŸ”µ Sodium</td><td style='text-align:right; padding:7px 12px;'>â‰¤{limits['sodium_mg']:,} mg</td><td style='text-align:right; padding:7px 12px;'>â‰¤{limits['sodium_mg']*0.3:.0f} mg</td></tr>
            <tr><td style='padding:7px 12px;'>ðŸŸ£ Phosphorus</td><td style='text-align:right; padding:7px 12px;'>â‰¤{limits['phosphorus_mg']:,} mg</td><td style='text-align:right; padding:7px 12px;'>â‰¤{limits['phosphorus_mg']*0.3:.0f} mg</td></tr>
            <tr style='background:#f8f9fa;'><td style='padding:7px 12px;'>ðŸŸ¢ Protein</td><td style='text-align:right; padding:7px 12px;'>{limits['protein_g_per_kg']} g/kg/day</td><td style='text-align:right; padding:7px 12px;'>â€”</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style='background:#f0fff4; border:2px solid #27ae60; border-radius:10px; padding:1rem;'>
            <div style='font-weight:700; color:#1e8449; margin-bottom:0.5rem;'>âœ… Generally Safe</div>
            <div style='font-size:0.83rem; color:#4a5568; line-height:1.8;'>
                White rice Â· Cabbage Â· Cauliflower Â· Apple Â· Grapes<br>
                Egg white Â· White bread Â· Pasta Â· Green beans<br>
                Watermelon Â· Capsicum Â· Onion
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style='background:#fff5f5; border:2px solid #e74c3c; border-radius:10px; padding:1rem;'>
            <div style='font-weight:700; color:#c0392b; margin-bottom:0.5rem;'>ðŸš« Use Caution / Limit</div>
            <div style='font-size:0.83rem; color:#4a5568; line-height:1.8;'>
                Banana (high Kâº) Â· Potato chips (high Kâº, Na) Â· Spinach (high Kâº)<br>
                Coconut water Â· Dark chocolate Â· Legumes<br>
                Processed foods (high phosphorus additives)
            </div>
        </div>
        """, unsafe_allow_html=True)
