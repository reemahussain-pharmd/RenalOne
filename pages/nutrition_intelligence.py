"""Kidney Nutrition Intelligence Page — RenalCare AI."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from nutrition.analyzer import analyse_food, analyse_ai_food
from nutrition.food_database import FOOD_DATABASE
from components.charts import nutrient_radar


NUTRIENT_LIMITS = {
    "G3a": {"potassium_mg": 3000, "sodium_mg": 2300, "phosphorus_mg": 700, "protein_g": 50, "fluid_ml": 2000},
    "G3b": {"potassium_mg": 2500, "sodium_mg": 2000, "phosphorus_mg": 600, "protein_g": 45, "fluid_ml": 1800},
    "G4":  {"potassium_mg": 2000, "sodium_mg": 1500, "phosphorus_mg": 500, "protein_g": 40, "fluid_ml": 1500},
    "G5":  {"potassium_mg": 2000, "sodium_mg": 1000, "phosphorus_mg": 400, "protein_g": 50, "fluid_ml": 1000},
}

NUTRIENT_COLORS = {
    "potassium_mg":  ("#F59E0B", "#FEF3C7"),
    "sodium_mg":     ("#3B82F6", "#EFF6FF"),
    "phosphorus_mg": ("#8B5CF6", "#EDE9FE"),
    "protein_g":     ("#10B981", "#D1FAE5"),
}


def render():
    st.markdown("""
    <div class="page-header">
        <div style="display:flex;align-items:flex-start;justify-content:space-between;">
            <div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.5rem;">
                    <span style="font-size:1.5rem;">\U0001f966</span>
                    <span style="background:rgba(255,255,255,0.15);color:rgba(255,255,255,0.9);
                                 font-size:0.7rem;font-weight:700;padding:3px 10px;border-radius:20px;
                                 letter-spacing:0.06em;">RENAL DIETETICS MODULE</span>
                </div>
                <h1 style="color:white !important;font-size:1.7rem !important;font-weight:800 !important;
                           margin:0 0 0.3rem 0 !important;">Kidney Nutrition Intelligence</h1>
                <p style="color:rgba(255,255,255,0.72) !important;font-size:0.88rem !important;margin:0 !important;">
                    Potassium &bull; Phosphorus &bull; Sodium &bull; Protein analysis per CKD stage
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── CKD Stage selector ─────────────────────────────────────────────────
    stage_col, _ = st.columns([1, 2])
    with stage_col:
        ckd_stage = st.selectbox(
            "Patient CKD Stage",
            ["G3a", "G3b", "G4", "G5"],
            help="Stage determines daily nutrient limits"
        )

    limits = NUTRIENT_LIMITS.get(ckd_stage, NUTRIENT_LIMITS["G3b"])

    # ── Nutrient limits bar ────────────────────────────────────────────────
    st.markdown(f"""
    <div class="rc-card" style="margin-bottom:1rem;">
        <div class="section-title"><span>\U0001f4ca</span> Daily Limits — CKD Stage {ckd_stage}</div>
        <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:0.8rem;">
            <div style="text-align:center;background:#FEF3C7;border-radius:10px;padding:0.8rem;">
                <div style="font-size:1.2rem;font-weight:800;color:#92400E;">{limits['potassium_mg']:,}</div>
                <div style="font-size:0.72rem;font-weight:600;color:#78350F;text-transform:uppercase;letter-spacing:0.05em;">mg Potassium</div>
            </div>
            <div style="text-align:center;background:#EFF6FF;border-radius:10px;padding:0.8rem;">
                <div style="font-size:1.2rem;font-weight:800;color:#1D4ED8;">{limits['sodium_mg']:,}</div>
                <div style="font-size:0.72rem;font-weight:600;color:#1E3A8A;text-transform:uppercase;letter-spacing:0.05em;">mg Sodium</div>
            </div>
            <div style="text-align:center;background:#EDE9FE;border-radius:10px;padding:0.8rem;">
                <div style="font-size:1.2rem;font-weight:800;color:#5B21B6;">{limits['phosphorus_mg']:,}</div>
                <div style="font-size:0.72rem;font-weight:600;color:#4C1D95;text-transform:uppercase;letter-spacing:0.05em;">mg Phosphorus</div>
            </div>
            <div style="text-align:center;background:#D1FAE5;border-radius:10px;padding:0.8rem;">
                <div style="font-size:1.2rem;font-weight:800;color:#065F46;">{limits['protein_g']:,}</div>
                <div style="font-size:0.72rem;font-weight:600;color:#064E3B;text-transform:uppercase;letter-spacing:0.05em;">g Protein</div>
            </div>
            <div style="text-align:center;background:#F1F5F9;border-radius:10px;padding:0.8rem;">
                <div style="font-size:1.2rem;font-weight:800;color:#374151;">{limits['fluid_ml']:,}</div>
                <div style="font-size:0.72rem;font-weight:600;color:#1F2937;text-transform:uppercase;letter-spacing:0.05em;">mL Fluid</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs ───────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["  \U0001f50d  Search Food Database  ", "  \U0001f916  AI Food Analysis  ", "  \U0001f4d6  Nutrient Guide  "])

    with tab1:
        _tab_search(ckd_stage, limits)

    with tab2:
        _tab_ai(ckd_stage)

    with tab3:
        _tab_guide()


def _tab_search(ckd_stage, limits):
    foods = sorted(FOOD_DATABASE.keys())
    selected_food = st.selectbox("Search food database (37 foods):", foods)
    amount = st.slider("Serving size (grams):", 25, 300, 100, 25)

    if st.button("\U0001f50d  Analyze This Food", type="primary"):
        result = analyse_food(selected_food, amount, ckd_stage)
        if result:
            suit = result.get("suitability", "caution").lower()
            suit_cfg = {
                "safe":    ("#10B981", "#D1FAE5", "#065F46", "✅", "SAFE"),
                "caution": ("#F59E0B", "#FEF3C7", "#92400E", "⚠️",   "USE WITH CAUTION"),
                "avoid":   ("#EF4444", "#FEE2E2", "#991B1B", "❌", "AVOID"),
            }
            s_color, s_bg, s_text, s_icon, s_label = suit_cfg.get(suit, suit_cfg["caution"])

            st.markdown(f"""
            <div style="background:{s_bg};border:2px solid {s_color};border-radius:14px;
                        padding:1.2rem 1.5rem;margin:0.8rem 0;">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:0.5rem;">
                    <span style="font-size:1.5rem;">{s_icon}</span>
                    <div>
                        <div style="font-size:1rem;font-weight:800;color:{s_text};">{selected_food}</div>
                        <div style="font-size:0.85rem;font-weight:700;color:{s_color};">
                            {s_label} — {amount}g serving
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Nutrient bars
            nutrients = result.get("nutrients", {})
            label_map = {
                "potassium_mg": ("Potassium", "mg", "#F59E0B"),
                "sodium_mg":    ("Sodium",    "mg", "#3B82F6"),
                "phosphorus_mg":("Phosphorus","mg", "#8B5CF6"),
                "protein_g":    ("Protein",   "g",  "#10B981"),
            }
            st.markdown('<div style="margin-top:0.8rem;"></div>', unsafe_allow_html=True)
            for key, (name, unit, color) in label_map.items():
                val  = nutrients.get(key, 0)
                lim  = limits.get(key, 1)
                pct  = min(val / lim * 100, 100) if lim > 0 else 0
                bar_color = "#EF4444" if pct > 80 else (color if pct > 50 else "#10B981")
                st.markdown(f"""
                <div style="margin-bottom:0.7rem;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
                        <span style="font-size:0.82rem;font-weight:600;color:#374151;">{name}</span>
                        <span style="font-size:0.82rem;font-weight:700;color:{bar_color};">
                            {val:.0f}{unit} <span style="color:#94A3B8;font-weight:400;">/ {lim}{unit} daily limit</span>
                        </span>
                    </div>
                    <div style="background:#F1F5F9;border-radius:999px;height:8px;">
                        <div style="background:{bar_color};width:{pct:.0f}%;height:8px;border-radius:999px;
                                    transition:width 0.4s ease;"></div>
                    </div>
                    <div style="font-size:0.72rem;color:#94A3B8;margin-top:2px;">{pct:.0f}% of daily limit per serving</div>
                </div>
                """, unsafe_allow_html=True)

            # Reasons
            if result.get("reasons"):
                st.markdown('<div class="section-title" style="margin-top:0.8rem;"><span>\U0001f4dd</span> Clinical Notes</div>', unsafe_allow_html=True)
                for r in result["reasons"]:
                    st.markdown(f'<div style="font-size:0.83rem;color:#374151;margin-bottom:4px;">&#x2022; {r}</div>', unsafe_allow_html=True)

            # Tips
            if result.get("tips"):
                st.markdown("""
                <div style="background:#F0FDF4;border-radius:10px;padding:0.9rem 1.1rem;margin-top:0.7rem;">
                    <div style="font-size:0.82rem;font-weight:700;color:#065F46;margin-bottom:0.4rem;">\U0001f4a1 Dietary Tips</div>
                """, unsafe_allow_html=True)
                for tip in result["tips"]:
                    st.markdown(f'<div style="font-size:0.82rem;color:#166534;margin-bottom:3px;">&#x2713; {tip}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Radar chart
            try:
                fig = nutrient_radar(nutrients, limits)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            except Exception:
                pass


def _tab_ai(ckd_stage):
    st.markdown("""
    <div class="alert alert-purple" style="margin-bottom:0.8rem;">
        \U0001f916 Describe any food or meal in natural language and get AI-powered renal diet guidance.
    </div>
    """, unsafe_allow_html=True)
    food_text = st.text_area(
        "Describe the food or meal:",
        placeholder="e.g. 'A bowl of tomato soup with white bread' or 'Banana smoothie with milk'",
        height=100,
    )
    if st.button("\U0001f916  Analyze with AI", type="primary") and food_text:
        with st.spinner("Analyzing with AI..."):
            result = analyse_ai_food(food_text, ckd_stage)
            if result:
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#EEF2FF,#F0FDF4);border-radius:12px;
                            padding:1.2rem;border:1px solid #C7D2FE;margin-top:0.5rem;">
                    <div style="font-size:0.85rem;font-weight:700;color:#3730A3;margin-bottom:0.6rem;">
                        \U0001f916 AI Nutrition Analysis — CKD Stage {ckd_stage}
                    </div>
                    <div style="font-size:0.85rem;color:#1E293B;line-height:1.7;">
                        {result.replace(chr(10), '<br>')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("AI analysis unavailable. Please configure an API key.")


def _tab_guide():
    st.markdown("""
    <div class="rc-card">
        <div class="section-title"><span>\U0001f4d6</span> CKD Nutrition Principles</div>
    """, unsafe_allow_html=True)

    guides = [
        ("\U0001f34c", "Potassium", "#F59E0B", "#FEF3C7",
         "Limit high-potassium foods: bananas, oranges, tomatoes, potatoes. "
         "Leaching vegetables (peel, cut small, soak in water, boil in fresh water) reduces potassium by 30-50%."),
        ("\U0001f9C0", "Phosphorus", "#8B5CF6", "#EDE9FE",
         "Avoid phosphate additives in processed foods (highest bioavailability). "
         "Animal protein phosphorus: 40-60% absorbed. Plant phosphorus: 20-40% absorbed."),
        ("\U0001f9c2", "Sodium", "#3B82F6", "#EFF6FF",
         "Reduce processed, canned, and fast foods. Avoid adding table salt. "
         "Check labels: aim <140mg sodium per serving. Controls blood pressure and fluid retention."),
        ("\U0001f969", "Protein", "#10B981", "#D1FAE5",
         "Pre-dialysis CKD: low-protein diet (0.6-0.8g/kg/day) slows progression. "
         "On dialysis: higher protein needed (1.0-1.2g/kg/day) due to dialytic losses."),
        ("\U0001f4a7", "Fluid", "#6366F1", "#EEF2FF",
         "Dialysis patients: restrict based on residual urine output. "
         "Fluid = urine output + 500ml/day. Includes soups, ice cream, gelatin."),
    ]

    for icon, name, color, bg, desc in guides:
        st.markdown(f"""
        <div style="background:{bg};border-radius:10px;padding:1rem 1.1rem;margin-bottom:0.7rem;
                    border-left:4px solid {color};">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.4rem;">
                <span style="font-size:1.1rem;">{icon}</span>
                <span style="font-size:0.9rem;font-weight:700;color:#0F172A;">{name} Management</span>
                <span style="background:{color};color:white;font-size:0.65rem;font-weight:700;
                             padding:2px 8px;border-radius:20px;letter-spacing:0.05em;">
                    KDIGO
                </span>
            </div>
            <div style="font-size:0.83rem;color:#374151;line-height:1.6;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
