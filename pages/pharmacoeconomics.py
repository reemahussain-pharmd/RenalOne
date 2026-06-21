"""Pharmacoeconomic Intelligence Page — RenalCare AI."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from economics.calculator import EconomicInput, calculate_economic_burden
from components.charts import cost_donut


def render():
    st.markdown("""
    <div class="page-header">
        <div style="display:flex;align-items:flex-start;justify-content:space-between;">
            <div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.5rem;">
                    <span style="font-size:1.5rem;">\U0001f4ca</span>
                    <span style="background:rgba(255,255,255,0.15);color:rgba(255,255,255,0.9);
                                 font-size:0.7rem;font-weight:700;padding:3px 10px;border-radius:20px;
                                 letter-spacing:0.06em;">PUBLISHED RESEARCH MODEL</span>
                </div>
                <h1 style="color:white !important;font-size:1.7rem !important;font-weight:800 !important;
                           margin:0 0 0.3rem 0 !important;">Pharmacoeconomic Intelligence</h1>
                <p style="color:rgba(255,255,255,0.72) !important;font-size:0.88rem !important;margin:0 !important;">
                    Cost-of-illness modeling &bull; WHO catastrophic expenditure analysis &bull; Treatment burden
                </p>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.7rem;color:rgba(255,255,255,0.5);text-transform:uppercase;letter-spacing:0.07em;">Based on</div>
                <div style="font-size:0.82rem;color:rgba(255,255,255,0.85);font-weight:600;">Hemodialysis Burden</div>
                <div style="font-size:0.82rem;color:rgba(255,255,255,0.85);font-weight:600;">Rural India Study</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    left_col, right_col = st.columns([1.1, 1.5])

    with left_col:
        with st.form("econ_form"):
            st.markdown('<div class="section-title-accent"><span>\U0001f3e5</span> Dialysis Costs</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                sessions_per_week = st.number_input("Sessions/week", 1, 7, 3)
                cost_per_session  = st.number_input("Cost/session ($)", 0, 1000, 185)
            with c2:
                dialysis_type = st.selectbox("Dialysis Type",
                    ["Hemodialysis", "Peritoneal Dialysis", "Pre-Dialysis CKD"])

            st.markdown('<div class="section-title-accent" style="margin-top:0.8rem;"><span>\U0001f48a</span> Medication Costs</div>', unsafe_allow_html=True)
            c3, c4 = st.columns(2)
            with c3:
                monthly_meds = st.number_input("Medications/month ($)", 0, 2000, 320)
            with c4:
                epo_cost = st.number_input("EPO agents/month ($)", 0, 2000, 0)

            st.markdown('<div class="section-title-accent" style="margin-top:0.8rem;"><span>\U0001f9ea</span> Laboratory & Monitoring</div>', unsafe_allow_html=True)
            c5, c6 = st.columns(2)
            with c5:
                monthly_labs = st.number_input("Lab tests/month ($)", 0, 500, 120)
            with c6:
                consults = st.number_input("Specialist visits/month ($)", 0, 500, 80)

            st.markdown('<div class="section-title-accent" style="margin-top:0.8rem;"><span>\U0001f697</span> Indirect Costs</div>', unsafe_allow_html=True)
            c7, c8 = st.columns(2)
            with c7:
                transport_per_session = st.number_input("Transport/session ($)", 0, 200, 18)
                caregiver_monthly = st.number_input("Caregiver wages/month ($)", 0, 2000, 400)
            with c8:
                lost_wages = st.number_input("Lost wages/month ($)", 0, 5000, 600)
                hospitalization = st.number_input("Hospitalization/year ($)", 0, 20000, 0)

            st.markdown('<div class="section-title-accent" style="margin-top:0.8rem;"><span>\U0001f4b0</span> Household Income</div>', unsafe_allow_html=True)
            monthly_income = st.number_input("Household income/month ($)", 100, 20000, 1800)

            submitted = st.form_submit_button(
                "\U0001f4ca  Calculate Economic Burden",
                use_container_width=True,
                type="primary",
            )

    with right_col:
        if submitted:
            inp = EconomicInput(
                dialysis_sessions_per_week=sessions_per_week,
                cost_per_dialysis_session=float(cost_per_session),
                medication_cost_monthly=float(monthly_meds + epo_cost),
                lab_cost_monthly=float(monthly_labs),
                specialist_visit_cost_monthly=float(consults),
                transport_cost_per_session=float(transport_per_session),
                caregiver_wage_loss_monthly=float(caregiver_monthly),
                patient_wage_loss_monthly=float(lost_wages),
                hospitalisation_cost_annual=float(hospitalization),
                patient_monthly_income=float(monthly_income),
                currency="USD",
            )
            result = calculate_economic_burden(inp)
            st.session_state.econ_result = result
            _render_results(result)
        elif st.session_state.get("econ_result"):
            _render_results(st.session_state.econ_result)
        else:
            _render_placeholder()


def _render_results(result):
    total = result.total_monthly
    pct   = result.income_burden_pct
    is_catastrophic = pct >= 40 or result.financial_risk_category == "Catastrophic"

    cat_color = "#EF4444" if is_catastrophic else "#10B981"
    cat_bg    = "#FEE2E2" if is_catastrophic else "#D1FAE5"
    cat_icon  = "❌" if is_catastrophic else "✅"
    cat_label = "CATASTROPHIC EXPENDITURE" if is_catastrophic else "MANAGEABLE BURDEN"

    # ── KPI row ────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    metrics = [
        ("Total Monthly",  f"${total:,.0f}",         "#1E3A5F"),
        ("Annual Cost",    f"${total * 12:,.0f}",    "#6366F1"),
        ("Income %",       f"{pct:.0f}%",            cat_color),
        ("Direct Costs",   f"${result.direct_medical_monthly + result.direct_non_medical_monthly:,.0f}", "#F59E0B"),
    ]
    for col, (label, val, color) in zip([k1, k2, k3, k4], metrics):
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value" style="color:{color};font-size:1.5rem;">{val}</div>
                <div class="kpi-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:0.8rem;'></div>", unsafe_allow_html=True)

    # ── Catastrophic expenditure banner ────────────────────────────────────
    st.markdown(f"""
    <div style="background:{cat_bg};border:2px solid {cat_color};border-radius:12px;
                padding:1rem 1.4rem;margin-bottom:1rem;">
        <div style="display:flex;align-items:center;justify-content:space-between;">
            <div>
                <div style="font-size:0.72rem;font-weight:700;color:{cat_color};
                            letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.2rem;">
                    WHO Threshold Assessment
                </div>
                <div style="font-size:1.1rem;font-weight:800;color:{cat_color};">
                    {cat_icon} {cat_label}
                </div>
                <div style="font-size:0.82rem;color:#334155;margin-top:0.2rem;">
                    {pct:.1f}% of monthly household income &bull; WHO threshold: &gt;40% = catastrophic
                </div>
            </div>
            <div style="font-size:2.5rem;font-weight:900;color:{cat_color};">{pct:.0f}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Chart + breakdown table ────────────────────────────────────────────
    chart_col, table_col = st.columns([1, 1.1])

    with chart_col:
        try:
            breakdown = {
                "Direct Medical":     result.direct_medical_monthly,
                "Direct Non-Medical": result.direct_non_medical_monthly,
                "Indirect Costs":     result.indirect_monthly,
            }
            fig = cost_donut(breakdown)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        except Exception:
            pass

    with table_col:
        st.markdown('<div class="section-title"><span>\U0001f4cb</span> Cost Breakdown</div>', unsafe_allow_html=True)

        # Build rows from cost_drivers if available, else fallback to top-level fields
        drivers = getattr(result, "cost_drivers", []) or []
        table_colors = ["#EF4444","#8B5CF6","#3B82F6","#F59E0B","#10B981","#6366F1","#F97316"]

        table_html = '<table class="rc-table"><thead><tr><th>Category</th><th>Monthly</th><th>Share</th></tr></thead><tbody>'
        for i, d in enumerate(drivers[:7]):
            val = d.get("monthly", 0)
            pct_d = d.get("pct", 0)
            color = table_colors[i % len(table_colors)]
            table_html += f"""
            <tr>
                <td>
                    <div style="display:flex;align-items:center;gap:6px;">
                        <div style="width:8px;height:8px;border-radius:50%;background:{color};flex-shrink:0;"></div>
                        {d.get('name','—')}
                    </div>
                </td>
                <td style="font-weight:700;color:#0F172A;">${val:,}</td>
                <td>
                    <div style="background:#F1F5F9;border-radius:999px;height:6px;margin-bottom:2px;">
                        <div style="background:{color};width:{min(pct_d,100):.0f}%;height:6px;border-radius:999px;"></div>
                    </div>
                    <span style="font-size:0.73rem;color:#64748B;">{pct_d:.0f}%</span>
                </td>
            </tr>
            """
        table_html += f"""
        <tr style="background:#F8FAFC;">
            <td style="font-weight:800;color:#0F172A;">TOTAL</td>
            <td style="font-weight:900;color:#1E3A5F;font-size:1rem;">${total:,.0f}</td>
            <td style="font-weight:700;color:#1E3A5F;">100%</td>
        </tr></tbody></table>
        """
        st.markdown(table_html, unsafe_allow_html=True)

    # ── AI narrative ───────────────────────────────────────────────────────
    if getattr(result, "ai_narrative", ""):
        st.markdown("<div style='margin-top:0.8rem;'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#EEF2FF,#F0FDF4);border-radius:12px;
                    padding:1.2rem;border:1px solid #C7D2FE;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.7rem;">
                <span style="font-size:1rem;">\U0001f916</span>
                <span style="font-size:0.85rem;font-weight:700;color:#3730A3;">AI Economic Narrative</span>
                <span style="background:#EEF2FF;color:#6366F1;font-size:0.65rem;font-weight:700;
                             padding:2px 8px;border-radius:20px;letter-spacing:0.05em;">GPT-4o</span>
            </div>
            <div style="font-size:0.85rem;color:#1E293B;line-height:1.65;">
                {result.ai_narrative.replace(chr(10), '<br>')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Policy insights ────────────────────────────────────────────────────
    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="rc-card">
        <div class="section-title"><span>\U0001f4a1</span> Policy & Clinical Implications</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.7rem;">
            <div style="background:#EFF6FF;border-radius:8px;padding:0.8rem;border-left:3px solid #3B82F6;">
                <div style="font-size:0.8rem;font-weight:700;color:#1D4ED8;margin-bottom:0.3rem;">Financial Assistance</div>
                <div style="font-size:0.79rem;color:#334155;line-height:1.5;">
                    Explore ESRD Medicare coverage, state Medicaid programs, pharmaceutical patient assistance programs.
                </div>
            </div>
            <div style="background:#F0FDF4;border-radius:8px;padding:0.8rem;border-left:3px solid #10B981;">
                <div style="font-size:0.8rem;font-weight:700;color:#065F46;margin-bottom:0.3rem;">Cost Optimization</div>
                <div style="font-size:0.79rem;color:#334155;line-height:1.5;">
                    Generic substitution, home dialysis transition, telehealth monitoring, transport subsidy programs.
                </div>
            </div>
            <div style="background:#FEF3C7;border-radius:8px;padding:0.8rem;border-left:3px solid #F59E0B;">
                <div style="font-size:0.8rem;font-weight:700;color:#92400E;margin-bottom:0.3rem;">Indirect Burden</div>
                <div style="font-size:0.79rem;color:#334155;line-height:1.5;">
                    Lost productivity and caregiver costs often exceed direct medical costs. Social worker referral recommended.
                </div>
            </div>
            <div style="background:#EEF2FF;border-radius:8px;padding:0.8rem;border-left:3px solid #6366F1;">
                <div style="font-size:0.8rem;font-weight:700;color:#3730A3;margin-bottom:0.3rem;">Preventive Economics</div>
                <div style="font-size:0.79rem;color:#334155;line-height:1.5;">
                    Early CKD management reduces progression to dialysis. Annual savings: $70,000+ per patient-year.
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_placeholder():
    st.markdown("""
    <div style="background:white;border:2px dashed #E2E8F0;border-radius:16px;
                padding:3rem;text-align:center;">
        <div style="font-size:3rem;margin-bottom:1rem;">\U0001f4ca</div>
        <div style="font-size:1rem;font-weight:700;color:#0F172A;margin-bottom:0.5rem;">
            Economic Burden Calculator
        </div>
        <div style="font-size:0.84rem;color:#64748B;max-width:400px;margin:0 auto;line-height:1.6;">
            Complete the cost profile form to generate a comprehensive pharmacoeconomic analysis
            including WHO catastrophic expenditure assessment and annual burden modeling.
        </div>
        <div style="margin-top:1.5rem;display:flex;gap:8px;justify-content:center;flex-wrap:wrap;">
            <span style="background:#FEE2E2;color:#991B1B;font-size:0.78rem;font-weight:600;padding:5px 12px;border-radius:8px;">Direct Costs</span>
            <span style="background:#EFF6FF;color:#1E40AF;font-size:0.78rem;font-weight:600;padding:5px 12px;border-radius:8px;">Indirect Burden</span>
            <span style="background:#FEF3C7;color:#92400E;font-size:0.78rem;font-weight:600;padding:5px 12px;border-radius:8px;">WHO Threshold</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
