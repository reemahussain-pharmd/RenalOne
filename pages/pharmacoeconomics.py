"""Pharmacoeconomic Intelligence Page — RenalCare OS."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from economics.calculator import EconomicInput, calculate_economic_burden
from components.charts import cost_donut
import plotly.graph_objects as go


def _cost_metric(label: str, monthly: float, annual: float, color: str = "#2980b9"):
    st.markdown(f"""
    <div style='background:white; border-radius:10px; padding:1rem; box-shadow:0 2px 8px rgba(0,0,0,0.06);
                border-left:4px solid {color};'>
        <div style='font-size:0.78rem; color:#718096; font-weight:600; text-transform:uppercase;'>{label}</div>
        <div style='font-size:1.4rem; font-weight:700; color:{color};'>₹{annual:,.0f}</div>
        <div style='font-size:0.8rem; color:#a0aec0;'>₹{monthly:,.0f}/month</div>
    </div>
    """, unsafe_allow_html=True)


def render():
    st.markdown("""
    <div style='background: linear-gradient(135deg, #5d3a00, #e67e22);
                border-radius: 12px; padding: 1.5rem 2rem; margin-bottom: 1.5rem;'>
        <h2 style='color:white; margin:0; font-size:1.5rem;'>💰 Pharmacoeconomic Intelligence</h2>
        <p style='color:#fde8c8; margin:0.3rem 0 0 0; font-size:0.88rem;'>
            Economic burden analysis · Based on published hemodialysis pharmacoeconomic research
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='info-box'>
        <b>📚 Research Foundation:</b> This module is inspired by published pharmacoeconomic research on
        economic burden and quality of life of maintenance hemodialysis patients. It estimates direct medical,
        direct non-medical, and indirect costs to quantify the total financial burden on patients and caregivers.
    </div>
    """, unsafe_allow_html=True)

    with st.form("econ_form"):

        # ---- Patient income ----
        st.markdown("<div class='section-header'>👤 Patient Financial Context</div>", unsafe_allow_html=True)
        fi1, fi2 = st.columns(2)
        with fi1:
            monthly_income = st.number_input("Patient Monthly Income (₹)", min_value=0.0, max_value=500000.0,
                                              value=12000.0, step=500.0,
                                              help="Used to calculate income burden percentage")
        with fi2:
            currency = st.selectbox("Currency", ["INR (₹)", "USD ($)"], index=0)

        st.markdown("<br>", unsafe_allow_html=True)

        # ---- Dialysis ----
        st.markdown("<div class='section-header'>🏥 Direct Medical Costs (Monthly)</div>", unsafe_allow_html=True)
        dm1, dm2 = st.columns(2)
        with dm1:
            dial_freq = st.selectbox("Dialysis Frequency", ["3 sessions/week (standard)", "2 sessions/week", "4 sessions/week"], index=0)
            dial_sessions = {"3 sessions/week (standard)": 3, "2 sessions/week": 2, "4 sessions/week": 4}[dial_freq]
            cost_per_session = st.number_input("Cost per Dialysis Session (₹)", min_value=0.0, max_value=20000.0,
                                               value=1500.0, step=100.0)
        with dm2:
            med_cost = st.number_input("Monthly Medication Cost (₹)", min_value=0.0, value=3500.0, step=100.0)
            lab_cost = st.number_input("Monthly Laboratory Cost (₹)", min_value=0.0, value=1200.0, step=100.0)

        dm3, dm4 = st.columns(2)
        with dm3:
            specialist_cost = st.number_input("Specialist Visit Cost/month (₹)", min_value=0.0, value=600.0, step=100.0)
        with dm4:
            hospitalisation = st.number_input("Annual Hospitalisation Cost (₹)", min_value=0.0, value=25000.0, step=1000.0)

        st.markdown("<br>", unsafe_allow_html=True)

        # ---- Non-medical ----
        st.markdown("<div class='section-header'>🚗 Direct Non-Medical Costs (Monthly)</div>", unsafe_allow_html=True)
        nm1, nm2, nm3 = st.columns(3)
        with nm1:
            transport_per_session = st.number_input("Transport Cost per Dialysis Session (₹)", min_value=0.0, value=180.0, step=10.0)
        with nm2:
            meals_cost = st.number_input("Meals During Dialysis/month (₹)", min_value=0.0, value=450.0, step=50.0)
        with nm3:
            accommodation = st.number_input("Accommodation/month (₹)", min_value=0.0, value=0.0, step=100.0)

        st.markdown("<br>", unsafe_allow_html=True)

        # ---- Indirect ----
        st.markdown("<div class='section-header'>👨‍👩‍👧 Indirect Costs (Monthly)</div>", unsafe_allow_html=True)
        ic1, ic2, ic3 = st.columns(3)
        with ic1:
            patient_wage_loss = st.number_input("Patient Wage Loss/month (₹)", min_value=0.0, value=8000.0, step=500.0,
                                                 help="Income lost due to inability to work")
        with ic2:
            caregiver_wage_loss = st.number_input("Caregiver Wage Loss/month (₹)", min_value=0.0, value=4500.0, step=500.0)
        with ic3:
            caregiver_hours = st.number_input("Caregiver Hours/week", min_value=0.0, max_value=168.0, value=24.0, step=1.0)

        informal_rate = st.slider("Informal Care Hourly Rate (₹)", min_value=20, max_value=500, value=60, step=10,
                                   help="Estimated cost of informal caregiver time")

        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("📊 Calculate Economic Burden", use_container_width=True)

    if submit:
        with st.spinner("Running pharmacoeconomic analysis..."):
            inp = EconomicInput(
                dialysis_sessions_per_week=dial_sessions,
                cost_per_dialysis_session=cost_per_session,
                medication_cost_monthly=med_cost,
                lab_cost_monthly=lab_cost,
                specialist_visit_cost_monthly=specialist_cost,
                hospitalisation_cost_annual=hospitalisation,
                transport_cost_per_session=transport_per_session,
                meals_during_dialysis_monthly=meals_cost,
                accommodation_cost_monthly=accommodation,
                patient_wage_loss_monthly=patient_wage_loss,
                caregiver_wage_loss_monthly=caregiver_wage_loss,
                caregiver_hours_per_week=caregiver_hours,
                informal_care_hourly_rate=float(informal_rate),
                patient_monthly_income=monthly_income,
            )
            result = calculate_economic_burden(inp)

        st.session_state["economic_result"] = result
        st.session_state["economic_input"] = inp

        st.markdown("---")
        st.markdown("## 📊 Economic Burden Analysis")

        # Risk banner
        risk_configs = {
            "Low": ("#27ae60", "#d5f5e3"),
            "Moderate": ("#e67e22", "#fdf2e9"),
            "High": ("#e74c3c", "#fdedec"),
            "Catastrophic": ("#8e44ad", "#f3e8ff"),
        }
        rc = result.financial_risk_category
        fc, fbg = risk_configs.get(rc, ("#718096", "#f8f9fa"))
        risk_icons = {"Low": "✅", "Moderate": "⚠️", "High": "🔶", "Catastrophic": "🚨"}
        ri = risk_icons.get(rc, "⚠️")

        st.markdown(f"""
        <div style='background:{fbg}; border:2px solid {fc}; border-radius:10px; padding:1.2rem 1.5rem; margin-bottom:1rem;'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <div>
                    <div style='font-size:1.1rem; font-weight:700; color:{fc};'>{ri} Financial Risk: {rc}</div>
                    <div style='font-size:0.85rem; color:#4a5568;'>
                        Income burden: <b>{result.income_burden_pct:.1f}%</b> of annual income spent on healthcare
                    </div>
                </div>
                <div style='text-align:right;'>
                    <div style='font-size:2rem; font-weight:800; color:{fc};'>₹{result.total_annual:,.0f}</div>
                    <div style='font-size:0.8rem; color:#718096;'>Estimated Annual Cost</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # WHO Catastrophic threshold note
        if result.income_burden_pct >= 10:
            threshold_text = "WHO threshold for catastrophic health expenditure (10% of income)" if result.income_burden_pct < 40 else "WHO catastrophic expenditure threshold (40% of non-subsistence spending)"
            st.markdown(f"""
            <div class='danger-box' style='font-size:0.85rem;'>
                🚨 <b>Catastrophic Health Expenditure:</b> Healthcare costs exceed {threshold_text}.
                Financial counselling and government health scheme enrolment are strongly recommended.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Cost metrics
        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1:
            _cost_metric("Direct Medical", result.direct_medical_monthly, result.direct_medical_annual, "#2980b9")
        with mc2:
            _cost_metric("Direct Non-Medical", result.direct_non_medical_monthly, result.direct_non_medical_annual, "#16a085")
        with mc3:
            _cost_metric("Indirect Cost", result.indirect_monthly, result.indirect_annual, "#8e44ad")
        with mc4:
            _cost_metric("Total Annual", result.total_monthly, result.total_annual, "#e74c3c")

        st.markdown("<br>", unsafe_allow_html=True)

        # Charts
        ch1, ch2 = st.columns(2)
        with ch1:
            categories = [d["name"] for d in result.cost_drivers if d["annual"] > 0]
            values = [d["annual"] for d in result.cost_drivers if d["annual"] > 0]
            if categories:
                st.plotly_chart(cost_donut(categories, values, "Annual Cost Breakdown"), use_container_width=True)

        with ch2:
            # Burden gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=result.income_burden_pct,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Income Burden (%)", "font": {"size": 13, "color": "#1e3a5f"}},
                number={"suffix": "%", "font": {"size": 32}},
                gauge={
                    "axis": {"range": [0, 100], "tickfont": {"size": 9}},
                    "bar": {"color": fc, "thickness": 0.25},
                    "steps": [
                        {"range": [0, 10], "color": "#d5f5e3"},
                        {"range": [10, 30], "color": "#fef9e7"},
                        {"range": [30, 60], "color": "#fdf2e9"},
                        {"range": [60, 100], "color": "#fdedec"},
                    ],
                    "threshold": {"line": {"color": fc, "width": 3}, "thickness": 0.75, "value": result.income_burden_pct},
                },
            ))
            fig.update_layout(height=220, margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)

        # Cost drivers table
        st.markdown("### 📋 Cost Drivers Breakdown")
        cost_table_html = """
        <div style='background:white; border-radius:10px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.06);'>
        <table style='width:100%; border-collapse:collapse; font-size:0.88rem;'>
            <tr style='background:#1e3a5f; color:white;'>
                <th style='padding:10px 14px; text-align:left;'>Cost Driver</th>
                <th style='padding:10px 14px; text-align:right;'>Monthly (₹)</th>
                <th style='padding:10px 14px; text-align:right;'>Annual (₹)</th>
                <th style='padding:10px 14px; text-align:right;'>Share</th>
            </tr>
        """
        for i, driver in enumerate(result.cost_drivers):
            row_bg = "#f8fafc" if i % 2 == 0 else "white"
            bar_w = min(driver["pct"], 100)
            cost_table_html += f"""
            <tr style='background:{row_bg};'>
                <td style='padding:8px 14px; font-weight:500; color:#1e3a5f;'>{driver["name"]}</td>
                <td style='padding:8px 14px; text-align:right; color:#4a5568;'>₹{driver["monthly"]:,}</td>
                <td style='padding:8px 14px; text-align:right; font-weight:600; color:#2980b9;'>₹{driver["annual"]:,}</td>
                <td style='padding:8px 14px; text-align:right;'>
                    <div style='display:flex; align-items:center; gap:6px; justify-content:flex-end;'>
                        <div style='background:#e2e8f0; border-radius:4px; width:60px; height:6px;'>
                            <div style='background:#2980b9; width:{bar_w}%; height:6px; border-radius:4px;'></div>
                        </div>
                        <span style='color:#4a5568; font-size:0.8rem;'>{driver["pct"]:.1f}%</span>
                    </div>
                </td>
            </tr>
            """
        cost_table_html += f"""
            <tr style='background:#ebf8ff; font-weight:700;'>
                <td style='padding:10px 14px; color:#1e3a5f;'>TOTAL</td>
                <td style='padding:10px 14px; text-align:right; color:#1e3a5f;'>₹{result.total_monthly:,.0f}</td>
                <td style='padding:10px 14px; text-align:right; color:#e74c3c;'>₹{result.total_annual:,.0f}</td>
                <td style='padding:10px 14px; text-align:right; color:#e74c3c;'>100%</td>
            </tr>
        </table></div>
        """
        st.markdown(cost_table_html, unsafe_allow_html=True)

        # AI narrative
        if result.ai_narrative:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 📝 Economic Burden Assessment")
            st.markdown(f"""
            <div style='background:white; border-radius:10px; padding:1.5rem; box-shadow:0 2px 8px rgba(0,0,0,0.06);
                        border-left:4px solid #e67e22;'>
            """, unsafe_allow_html=True)
            st.markdown(result.ai_narrative)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        if st.button("📋 Add to Clinical Report →", use_container_width=True):
            st.session_state.current_page = "Report"
            st.rerun()
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='background:white; border-radius:12px; padding:3rem; text-align:center;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);'>
            <div style='font-size:3rem; margin-bottom:1rem;'>💰</div>
            <h3 style='color:#1e3a5f;'>Hemodialysis Economic Burden Calculator</h3>
            <p style='color:#718096; font-size:0.9rem;'>
                Enter cost parameters above to estimate the total economic burden
                of hemodialysis treatment on patients and their families.
            </p>
        </div>
        """, unsafe_allow_html=True)
