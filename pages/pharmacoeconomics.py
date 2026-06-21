"""Pharmacoeconomic Intelligence — Sprint 4 Upgrade — RenalCare AI."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from components.styles import sh
from economics.calculator import EconomicInput, calculate_economic_burden
from components.charts import cost_donut

# ── Country configuration ─────────────────────────────────────────────────────
COUNTRY_CONFIG = {
    "🇮🇳  India (₹ INR)": {
        "code": "IN", "symbol": "₹", "currency": "INR",
        "catastrophic_threshold": 40,
        "defaults": {
            "sessions": 3, "cps": 1500, "meds": 3000, "epo": 0,
            "labs": 1500, "consults": 500, "transport": 200,
            "caregiver": 5000, "lost_wages": 8000,
            "hospitalization": 0, "income": 15000,
        },
    },
    "🇺🇸  USA ($ USD)": {
        "code": "US", "symbol": "$", "currency": "USD",
        "catastrophic_threshold": 40,
        "defaults": {
            "sessions": 3, "cps": 500, "meds": 800, "epo": 200,
            "labs": 300, "consults": 200, "transport": 50,
            "caregiver": 1500, "lost_wages": 2000,
            "hospitalization": 5000, "income": 5000,
        },
    },
    "🇦🇪  UAE (AED)": {
        "code": "AE", "symbol": "AED ", "currency": "AED",
        "catastrophic_threshold": 40,
        "defaults": {
            "sessions": 3, "cps": 900, "meds": 1200, "epo": 400,
            "labs": 600, "consults": 400, "transport": 80,
            "caregiver": 2000, "lost_wages": 3000,
            "hospitalization": 8000, "income": 10000,
        },
    },
    "🇬🇧  UK (£ GBP)": {
        "code": "GB", "symbol": "£", "currency": "GBP",
        "catastrophic_threshold": 40,
        "defaults": {
            "sessions": 3, "cps": 50, "meds": 30, "epo": 0,
            "labs": 20, "consults": 0, "transport": 30,
            "caregiver": 500, "lost_wages": 1200,
            "hospitalization": 0, "income": 2500,
        },
    },
}

# ── Government Assistance Programs ────────────────────────────────────────────
SCHEMES = {
    "IN": [
        {"name": "PMJAY — Ayushman Bharat", "type": "Government Insurance",
         "coverage": "₹5 lakh/year hospitalisation", "eligibility": "Bottom 40% of population (SECC database)",
         "dialysis": "Inpatient HD sessions covered; limited outpatient", "savings_pct": 30,
         "enroll": "Nearest Ayushman Bharat empanelled hospital or CSC centre", "color": "#10B981"},
        {"name": "NKM Free Dialysis Programme", "type": "Central Govt Scheme",
         "coverage": "Free HD at government hospitals", "eligibility": "BPL / PMJAY beneficiaries; physician referral",
         "dialysis": "3 sessions/week free of cost", "savings_pct": 60,
         "enroll": "District hospital nephrology department", "color": "#3B82F6"},
        {"name": "Employees' State Insurance (ESI)", "type": "Social Insurance",
         "coverage": "Full medical coverage", "eligibility": "Employees earning ≤₹21,000/month",
         "dialysis": "Full dialysis at ESI hospitals", "savings_pct": 80,
         "enroll": "ESI dispensary with employer registration", "color": "#6366F1"},
        {"name": "CGHS (Central Govt Health Scheme)", "type": "Govt Employee Scheme",
         "coverage": "Comprehensive for central govt employees & pensioners", "eligibility": "Central govt employees / pensioners",
         "dialysis": "Approved dialysis centres; empanelled hospitals", "savings_pct": 75,
         "enroll": "CGHS wellness centre with employment proof", "color": "#F59E0B"},
        {"name": "State CM Health Schemes", "type": "State Government",
         "coverage": "₹2–5 lakh/year (state-specific)", "eligibility": "Varies; mostly BPL families",
         "dialysis": "Dialysis covered in most states under state schemes", "savings_pct": 40,
         "enroll": "State health portal or nearest PHC", "color": "#EF4444"},
    ],
    "US": [
        {"name": "Medicare ESRD Entitlement", "type": "Federal Medicare",
         "coverage": "80% of approved dialysis costs", "eligibility": "US citizens/PRs with ESRD; age-independent",
         "dialysis": "HD and PD; in-centre and home", "savings_pct": 80,
         "enroll": "Social Security Administration; nephrologist referral", "color": "#10B981"},
        {"name": "Medicaid (Dual Eligible)", "type": "Federal + State Insurance",
         "coverage": "Covers Medicare cost-sharing", "eligibility": "Low-income; state-specific income thresholds",
         "dialysis": "Full coverage for dual Medicare-Medicaid patients", "savings_pct": 95,
         "enroll": "State Medicaid agency; Healthcare.gov", "color": "#3B82F6"},
        {"name": "American Kidney Fund (AKF) HIPP", "type": "Non-profit",
         "coverage": "Up to $3,000/yr for insurance premiums", "eligibility": "Dialysis patients with income ≤350% FPL",
         "dialysis": "Maintains private insurance alongside Medicare", "savings_pct": 20,
         "enroll": "kidneyfund.org or dialysis centre social worker", "color": "#6366F1"},
        {"name": "Pharmaceutical Assistance Programs (PAPs)", "type": "Industry",
         "coverage": "Free/reduced-cost medications", "eligibility": "Income-based; no Part D coverage for specific drug",
         "dialysis": "ESA agents (Epogen/Aranesp), phosphate binders, EPO", "savings_pct": 25,
         "enroll": "NeedyMeds.org · RxAssist.org", "color": "#F59E0B"},
    ],
    "AE": [
        {"name": "Thiqa (UAE Nationals)", "type": "National Health Insurance",
         "coverage": "Comprehensive — 100% dialysis coverage", "eligibility": "UAE citizens (Emirati nationals only)",
         "dialysis": "Full HD and PD at SEHA/approved centres", "savings_pct": 100,
         "enroll": "SEHA facilities; Abu Dhabi Health Authority", "color": "#10B981"},
        {"name": "Daman Enhanced / Essential", "type": "Mandatory Insurance (Expatriates)",
         "coverage": "AED 25,000–150,000/year; employer provided", "eligibility": "All Abu Dhabi residents — mandatory",
         "dialysis": "Inpatient dialysis covered; outpatient varies by plan tier", "savings_pct": 50,
         "enroll": "Employer HR department; damanhealth.ae", "color": "#3B82F6"},
        {"name": "DHA Smile Program", "type": "Low-income Insurance (Dubai)",
         "coverage": "Basic coverage for low-income Dubai residents", "eligibility": "Monthly income below AED 4,000",
         "dialysis": "Limited dialysis; referral to DHA facility required", "savings_pct": 40,
         "enroll": "DHA eServices portal (dha.gov.ae)", "color": "#F59E0B"},
    ],
    "GB": [
        {"name": "NHS Renal Services", "type": "NHS (Free at point of care)",
         "coverage": "Full dialysis — no cost to patient", "eligibility": "All UK residents — no income requirement",
         "dialysis": "HD + PD; home and in-centre; all medications included", "savings_pct": 100,
         "enroll": "GP referral to NHS nephrologist — automatic", "color": "#10B981"},
        {"name": "NHS Healthcare Travel Costs Scheme", "type": "NHS Transport Support",
         "coverage": "Transport costs to dialysis reimbursed", "eligibility": "Receiving Universal Credit, ESA, PIP, or pension credit",
         "dialysis": "Covers mileage or public transport to dialysis unit", "savings_pct": 15,
         "enroll": "HC1 form; dialysis unit admin desk", "color": "#3B82F6"},
        {"name": "Personal Independence Payment (PIP)", "type": "Disability Benefit",
         "coverage": "£28–£184/week for care + mobility", "eligibility": "CKD/dialysis patients with daily living difficulty",
         "dialysis": "Indirect — offsets caregiver and living costs", "savings_pct": 12,
         "enroll": "gov.uk/pip — online or telephone claim", "color": "#6366F1"},
        {"name": "Kidney Care UK Patient Grants", "type": "Charity Grant",
         "coverage": "One-off grants £250–£2,000 for specific needs", "eligibility": "Kidney patients in financial hardship (UK)",
         "dialysis": "Grants for transport, equipment, home adaptation", "savings_pct": 5,
         "enroll": "kidneycareuk.org — online application", "color": "#F59E0B"},
    ],
}

# ── Cost reduction scenarios ──────────────────────────────────────────────────
def _calc_scenarios(inp: EconomicInput, result, sym: str) -> list:
    base = result.total_monthly
    sessions_mo = inp.dialysis_sessions_per_week * 4.33
    scenarios = []

    # 1 — HD → Peritoneal Dialysis
    pd_session_cost = inp.cost_per_dialysis_session * 0.6   # PD ~40% cheaper
    pd_monthly = (sessions_mo * pd_session_cost) + inp.medication_cost_monthly + \
                 inp.lab_cost_monthly + inp.specialist_visit_cost_monthly + \
                 inp.hospitalisation_cost_annual / 12 + \
                 (inp.transport_cost_per_session * sessions_mo * 0.3) + \
                 inp.caregiver_wage_loss_monthly * 0.5 + inp.patient_wage_loss_monthly
    scenarios.append({"label": "HD → Peritoneal Dialysis", "monthly": round(pd_monthly),
                       "saving": round(base - pd_monthly),
                       "note": "PD performed at home — eliminates in-centre transport; reduces caregiver burden by ~50%; dialysis costs ~40% lower.",
                       "icon": "🔄", "feasibility": "Clinician decision"})

    # 2 — Generic medication substitution
    generic_monthly = result.total_monthly - (inp.medication_cost_monthly * 0.30)
    scenarios.append({"label": "Generic Medication Switch", "monthly": round(generic_monthly),
                       "saving": round(base - generic_monthly),
                       "note": "Substituting branded medications with generic equivalents (where bioequivalent). Typical savings: 25–35% on medication costs.",
                       "icon": "💊", "feasibility": "Pharmacist review required"})

    # 3 — Reduce HD frequency 3x → 2x/week (if clinically feasible)
    if inp.dialysis_sessions_per_week >= 3:
        reduced_sessions_mo = 2 * 4.33
        reduced_monthly = result.total_monthly - (sessions_mo - reduced_sessions_mo) * (
            inp.cost_per_dialysis_session + inp.transport_cost_per_session)
        scenarios.append({"label": "Reduce HD: 3×/wk → 2×/wk", "monthly": round(reduced_monthly),
                           "saving": round(base - reduced_monthly),
                           "note": "Twice-weekly HD may be appropriate in patients with residual renal function. Requires nephrologist assessment.",
                           "icon": "📅", "feasibility": "Nephrologist approval required"})

    # 4 — Home HD
    home_hd_monthly = result.total_monthly * 0.75  # ~25% saving from eliminating transport + some direct costs
    scenarios.append({"label": "Home Haemodialysis", "monthly": round(home_hd_monthly),
                       "saving": round(base - home_hd_monthly),
                       "note": "Home HD eliminates transport costs and reduces caregiver burden. Initial setup cost; long-term savings significant.",
                       "icon": "🏠", "feasibility": "Patient training + infrastructure"})

    return [s for s in scenarios if s["saving"] > 0]


def render():
    sh("""
    <div class="page-header">
        <div style="display:flex;align-items:flex-start;justify-content:space-between;">
            <div>
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.5rem;">
                    <span style="font-size:1.5rem;">&#x1f4ca;</span>
                    <span style="background:rgba(255,255,255,0.15);color:rgba(255,255,255,0.9);font-size:0.7rem;font-weight:700;padding:3px 10px;border-radius:20px;letter-spacing:0.06em;">PUBLISHED RESEARCH MODEL</span>
                    <span style="background:rgba(245,158,11,0.25);color:#FCD34D;font-size:0.7rem;font-weight:700;padding:3px 10px;border-radius:20px;">Sprint 4 &#x2014; Enhanced</span>
                </div>
                <h1 style="color:white !important;font-size:1.7rem !important;font-weight:800 !important;margin:0 0 0.3rem 0 !important;">Pharmacoeconomic Intelligence</h1>
                <p style="color:rgba(255,255,255,0.72) !important;font-size:0.88rem !important;margin:0 !important;">
                    Multi-country &bull; Government schemes &bull; Cost reduction simulator &bull; WHO catastrophic expenditure
                </p>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.7rem;color:rgba(255,255,255,0.5);text-transform:uppercase;letter-spacing:0.07em;">Based on</div>
                <div style="font-size:0.82rem;color:rgba(255,255,255,0.85);font-weight:600;">Hemodialysis Burden</div>
                <div style="font-size:0.82rem;color:rgba(255,255,255,0.85);font-weight:600;">Peer-Reviewed Study</div>
            </div>
        </div>
    </div>
    """)

    # ── Country selector (outside form so it updates instantly) ───────────────
    country_c, load_c = st.columns([2, 1])
    with country_c:
        country = st.selectbox("&#x1f30d; Country / Region", list(COUNTRY_CONFIG.keys()), key="econ_country")
    with load_c:
        st.markdown("<div style='margin-top:1.8rem;'></div>", unsafe_allow_html=True)
        if st.button("&#x1f4e5; Load Country Defaults", use_container_width=True):
            d = COUNTRY_CONFIG[country]["defaults"]
            for k, v in d.items():
                st.session_state[f"ec_{k}"] = v
            st.rerun()

    cfg = COUNTRY_CONFIG[country]
    sym = cfg["symbol"]
    defs = cfg["defaults"]

    def _d(key):
        return st.session_state.get(f"ec_{key}", defs[key])

    left_col, right_col = st.columns([1.1, 1.5])

    with left_col:
        with st.form("econ_form"):
            sh('<div class="section-title-accent"><span>&#x1f3e5;</span> Dialysis Costs</div>')
            c1, c2 = st.columns(2)
            with c1:
                sessions_per_week = st.number_input("Sessions/week", 1, 7, _d("sessions"))
                cost_per_session  = st.number_input(f"Cost/session ({sym})", 0, 10000, _d("cps"))
            with c2:
                dialysis_type = st.selectbox("Dialysis Type",
                    ["Hemodialysis", "Peritoneal Dialysis", "Pre-Dialysis CKD"])

            sh('<div class="section-title-accent" style="margin-top:0.8rem;"><span>&#x1f48a;</span> Medication Costs</div>')
            c3, c4 = st.columns(2)
            with c3: monthly_meds = st.number_input(f"Medications/month ({sym})", 0, 50000, _d("meds"))
            with c4: epo_cost     = st.number_input(f"EPO agents/month ({sym})", 0, 20000, _d("epo"))

            sh('<div class="section-title-accent" style="margin-top:0.8rem;"><span>&#x1f9ea;</span> Laboratory & Monitoring</div>')
            c5, c6 = st.columns(2)
            with c5: monthly_labs = st.number_input(f"Lab tests/month ({sym})", 0, 10000, _d("labs"))
            with c6: consults     = st.number_input(f"Specialist visits/month ({sym})", 0, 10000, _d("consults"))

            sh('<div class="section-title-accent" style="margin-top:0.8rem;"><span>&#x1f697;</span> Indirect Costs</div>')
            c7, c8 = st.columns(2)
            with c7:
                transport_per_session = st.number_input(f"Transport/session ({sym})", 0, 5000, _d("transport"))
                caregiver_monthly     = st.number_input(f"Caregiver wages/month ({sym})", 0, 50000, _d("caregiver"))
            with c8:
                lost_wages      = st.number_input(f"Lost wages/month ({sym})", 0, 100000, _d("lost_wages"))
                hospitalization = st.number_input(f"Hospitalization/year ({sym})", 0, 500000, _d("hospitalization"))

            sh('<div class="section-title-accent" style="margin-top:0.8rem;"><span>&#x1f4b0;</span> Household Income</div>')
            monthly_income = st.number_input(f"Monthly household income ({sym})", 100, 500000, _d("income"))

            submitted = st.form_submit_button("&#x1f4ca;  Calculate Economic Burden",
                                              use_container_width=True, type="primary")

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
                currency=cfg["currency"],
            )
            result = calculate_economic_burden(inp)
            st.session_state.econ_result = result
            st.session_state.econ_inp    = inp
            st.session_state.econ_cfg    = cfg

        if st.session_state.get("econ_result"):
            result = st.session_state.econ_result
            inp    = st.session_state.get("econ_inp")
            r_cfg  = st.session_state.get("econ_cfg", cfg)
            _render_results(result, inp, r_cfg)
        elif not submitted:
            _render_placeholder()


# ─────────────────────────────────────────────────────────────────────────────
# Results — 4 tabs
# ─────────────────────────────────────────────────────────────────────────────

def _render_results(result, inp, cfg):
    sym   = cfg["symbol"]
    total = result.total_monthly
    pct   = result.income_burden_pct
    is_cat = pct >= cfg["catastrophic_threshold"] or result.financial_risk_category == "Catastrophic"

    cat_color = "#EF4444" if is_cat else "#10B981"
    cat_bg    = "#FEE2E2" if is_cat else "#D1FAE5"
    cat_icon  = "❌" if is_cat else "✅"
    cat_label = "CATASTROPHIC EXPENDITURE" if is_cat else "MANAGEABLE BURDEN"

    # ── KPI row ───────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    for col, (label, val, color) in zip([k1, k2, k3, k4], [
        ("Monthly Cost",  f"{sym}{total:,.0f}",          "#1E3A5F"),
        ("Annual Cost",   f"{sym}{total*12:,.0f}",        "#6366F1"),
        ("Income Burden", f"{pct:.0f}%",                  cat_color),
        ("Direct Medical",f"{sym}{result.direct_medical_monthly:,.0f}","#F59E0B"),
    ]):
        with col:
            sh(f'<div class="kpi-card"><div class="kpi-value" style="color:{color};font-size:1.4rem;">{val}</div><div class="kpi-label">{label}</div></div>')

    sh("<div style='margin-top:0.8rem;'></div>")

    # ── Catastrophic banner ───────────────────────────────────────────────────
    sh(f'<div style="background:{cat_bg};border:2px solid {cat_color};border-radius:12px;padding:0.9rem 1.2rem;margin-bottom:0.8rem;display:flex;align-items:center;justify-content:space-between;"><div><div style="font-size:0.7rem;font-weight:700;color:{cat_color};letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.2rem;">WHO Threshold Assessment</div><div style="font-size:1rem;font-weight:800;color:{cat_color};">{cat_icon} {cat_label}</div><div style="font-size:0.8rem;color:#334155;margin-top:0.2rem;">{pct:.1f}% of monthly income &bull; WHO threshold: &gt;{cfg["catastrophic_threshold"]}% = catastrophic</div></div><div style="font-size:2.2rem;font-weight:900;color:{cat_color};">{pct:.0f}%</div></div>')

    # ── 4 Tabs ────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Cost Analysis",
        "🏛️ Government Schemes",
        "💡 Cost Reduction Simulator",
        "📚 Research Transparency",
    ])

    with tab1: _tab_cost_analysis(result, sym)
    with tab2: _tab_schemes(cfg)
    with tab3: _tab_simulator(inp, result, sym, cfg) if inp else sh('<div style="color:#64748B;padding:1rem;">Re-run the calculation to use the simulator.</div>')
    with tab4: _tab_research(cfg)


# ─────────────────────────────────────────────────────────────────────────────
# Tab 1 — Cost Analysis
# ─────────────────────────────────────────────────────────────────────────────

def _tab_cost_analysis(result, sym):
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

        # Annual summary cards
        sh(f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin-top:0.3rem;"><div style="background:#EFF6FF;border-radius:8px;padding:0.6rem;text-align:center;"><div style="font-size:0.8rem;font-weight:800;color:#1D4ED8;">{sym}{result.direct_medical_annual:,.0f}</div><div style="font-size:0.62rem;color:#1E40AF;font-weight:600;text-transform:uppercase;">Direct Medical</div></div><div style="background:#FEF3C7;border-radius:8px;padding:0.6rem;text-align:center;"><div style="font-size:0.8rem;font-weight:800;color:#92400E;">{sym}{result.direct_non_medical_annual:,.0f}</div><div style="font-size:0.62rem;color:#78350F;font-weight:600;text-transform:uppercase;">Non-Medical</div></div><div style="background:#F3F4F6;border-radius:8px;padding:0.6rem;text-align:center;"><div style="font-size:0.8rem;font-weight:800;color:#1F2937;">{sym}{result.indirect_annual:,.0f}</div><div style="font-size:0.62rem;color:#374151;font-weight:600;text-transform:uppercase;">Indirect</div></div></div>')

    with table_col:
        sh('<div class="section-title"><span>&#x1f4cb;</span> Cost Breakdown</div>')
        drivers = getattr(result, "cost_drivers", []) or []
        COLORS  = ["#EF4444","#8B5CF6","#3B82F6","#F59E0B","#10B981","#6366F1","#F97316"]

        table_html = '<table class="rc-table"><thead><tr><th>Category</th><th>Monthly</th><th>Annual</th><th>Share</th></tr></thead><tbody>'
        for i, d in enumerate(drivers[:7]):
            val   = d.get("monthly", 0)
            ann   = d.get("annual", val * 12)
            pct_d = d.get("pct", 0)
            color = COLORS[i % len(COLORS)]
            table_html += f'<tr><td><div style="display:flex;align-items:center;gap:6px;"><div style="width:8px;height:8px;border-radius:50%;background:{color};flex-shrink:0;"></div>{d.get("name","—")}</div></td><td style="font-weight:700;color:#0F172A;">{sym}{val:,}</td><td style="color:#64748B;">{sym}{ann:,}</td><td><div style="background:#F1F5F9;border-radius:999px;height:5px;margin-bottom:2px;"><div style="background:{color};width:{min(pct_d,100):.0f}%;height:5px;border-radius:999px;"></div></div><span style="font-size:0.72rem;color:#64748B;">{pct_d:.0f}%</span></td></tr>'
        table_html += f'<tr style="background:#F8FAFC;"><td style="font-weight:800;color:#0F172A;">TOTAL</td><td style="font-weight:900;color:#1E3A5F;font-size:1rem;">{sym}{result.total_monthly:,.0f}</td><td style="font-weight:700;color:#1E3A5F;">{sym}{result.total_annual:,.0f}</td><td style="font-weight:700;color:#1E3A5F;">100%</td></tr></tbody></table>'
        sh(table_html)

    # AI narrative
    if getattr(result, "ai_narrative", ""):
        sh(f'<div style="background:linear-gradient(135deg,#EEF2FF,#F0FDF4);border-radius:12px;padding:1.1rem;border:1px solid #C7D2FE;margin-top:0.8rem;"><div style="display:flex;align-items:center;gap:8px;margin-bottom:0.6rem;"><span style="font-size:1rem;">&#x1f4bc;</span><span style="font-size:0.85rem;font-weight:800;color:#3730A3;">AI Economic Burden Assessment</span><span style="background:#EEF2FF;color:#6366F1;font-size:0.65rem;font-weight:700;padding:2px 8px;border-radius:20px;">GPT-4o</span></div><div style="font-size:0.84rem;color:#1E293B;line-height:1.65;">{result.ai_narrative.replace(chr(10), "<br>")}</div></div>')


# ─────────────────────────────────────────────────────────────────────────────
# Tab 2 — Government Schemes
# ─────────────────────────────────────────────────────────────────────────────

def _tab_schemes(cfg):
    code    = cfg["code"]
    sym     = cfg["symbol"]
    schemes = SCHEMES.get(code, [])

    if not schemes:
        sh('<div style="color:#64748B;padding:1rem;font-size:0.84rem;">No scheme data available for selected country.</div>')
        return

    country_label = {"IN": "India", "US": "United States", "AE": "UAE", "GB": "United Kingdom"}.get(code, "")
    sh(f'<div style="font-size:0.82rem;font-weight:700;color:#0F172A;margin-bottom:0.4rem;">&#x1f3db;&#xfe0f; Financial Assistance Programmes — {country_label}</div>')
    sh(f'<div style="font-size:0.78rem;color:#64748B;margin-bottom:0.8rem;">Available government insurance, social schemes, and patient assistance programmes for dialysis patients in {country_label}.</div>')

    total_possible_saving_pct = max(s["savings_pct"] for s in schemes)
    sh(f'<div style="background:linear-gradient(135deg,#D1FAE5,#EFF6FF);border:1px solid #6EE7B7;border-radius:10px;padding:0.8rem 1rem;margin-bottom:0.9rem;display:flex;align-items:center;gap:10px;"><span style="font-size:1.3rem;">&#x1f4b0;</span><div><div style="font-size:0.85rem;font-weight:800;color:#065F46;">Up to {total_possible_saving_pct}% cost reduction possible</div><div style="font-size:0.76rem;color:#047857;margin-top:2px;">with the most comprehensive scheme for eligible patients in {country_label}</div></div></div>')

    for s in schemes:
        c = s["color"]
        sh(f'<div style="background:white;border:1px solid #E2E8F0;border-left:4px solid {c};border-radius:0 10px 10px 0;padding:0.85rem 1rem;margin-bottom:0.55rem;"><div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:0.4rem;"><div><div style="font-size:0.87rem;font-weight:800;color:#0F172A;">{s["name"]}</div><div style="font-size:0.72rem;font-weight:600;color:{c};text-transform:uppercase;letter-spacing:0.05em;margin-top:2px;">{s["type"]}</div></div><div style="background:{c}15;border:1px solid {c}40;border-radius:8px;padding:4px 10px;text-align:center;min-width:60px;"><div style="font-size:1rem;font-weight:800;color:{c};">~{s["savings_pct"]}%</div><div style="font-size:0.6rem;font-weight:700;color:{c};">saving</div></div></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:0.4rem;"><div style="font-size:0.76rem;color:#374151;"><span style="color:#64748B;font-weight:600;">Coverage: </span>{s["coverage"]}</div><div style="font-size:0.76rem;color:#374151;"><span style="color:#64748B;font-weight:600;">Dialysis: </span>{s["dialysis"]}</div><div style="font-size:0.76rem;color:#374151;"><span style="color:#64748B;font-weight:600;">Eligibility: </span>{s["eligibility"]}</div><div style="font-size:0.76rem;color:#374151;"><span style="color:#64748B;font-weight:600;">Enrol: </span>{s["enroll"]}</div></div></div>')

    sh("""
    <div style="background:#FFF7ED;border:1px solid #FED7AA;border-radius:8px;padding:0.75rem 1rem;margin-top:0.5rem;font-size:0.78rem;color:#92400E;">
        &#x26a0;&#xfe0f; <strong>Disclaimer:</strong> Eligibility criteria, coverage limits, and programme availability change frequently.
        Always verify current details directly with the scheme administrator or a social worker before advising patients.
    </div>
    """)


# ─────────────────────────────────────────────────────────────────────────────
# Tab 3 — Cost Reduction Simulator
# ─────────────────────────────────────────────────────────────────────────────

def _tab_simulator(inp: EconomicInput, result, sym: str, cfg: dict):
    sh("""
    <div style="background:#EEF2FF;border-left:3px solid #6366F1;border-radius:8px;padding:0.75rem 1rem;margin-bottom:0.8rem;font-size:0.83rem;color:#3730A3;">
        &#x1f4a1; <strong>What-If Scenarios</strong> — explore how clinical and economic interventions could reduce the dialysis cost burden.
        All projections are estimates based on published cost-reduction data.
    </div>
    """)

    scenarios = _calc_scenarios(inp, result, sym)
    base = result.total_monthly

    if not scenarios:
        sh('<div style="color:#64748B;padding:1rem;">No cost-reduction scenarios applicable for current inputs.</div>')
        return

    # Plotly grouped bar chart
    try:
        import plotly.graph_objects as go

        labels = ["Current Cost"] + [s["label"] for s in scenarios]
        values = [base]            + [s["monthly"] for s in scenarios]
        colors = ["#1E3A5F"] + ["#10B981" if s["saving"] > 0 else "#EF4444" for s in scenarios]

        fig = go.Figure(go.Bar(
            x=labels, y=values,
            marker_color=colors,
            text=[f"{sym}{v:,.0f}" for v in values],
            textposition="outside",
            textfont=dict(size=11, color="#1E293B"),
        ))
        fig.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=30, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(248,250,252,1)",
            yaxis=dict(title=f"Monthly Cost ({sym})", gridcolor="#F1F5F9"),
            xaxis=dict(tickfont=dict(size=10)),
            showlegend=False,
            title=dict(text="Monthly Cost Comparison by Scenario", font=dict(size=11, color="#1E3A5F"), x=0.5),
        )
        fig.add_hline(y=base, line_dash="dot", line_color="#EF4444",
                      annotation_text="Current", annotation_position="top right",
                      annotation_font=dict(color="#EF4444", size=10))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    except Exception:
        pass

    # Scenario cards
    sh('<div class="section-title"><span>&#x1f4ca;</span> Scenario Details</div>')
    for s in scenarios:
        saving_pct = round(s["saving"] / base * 100) if base > 0 else 0
        annual_saving = s["saving"] * 12
        sh(f'<div style="background:white;border:1px solid #E2E8F0;border-radius:10px;padding:0.85rem 1rem;margin-bottom:0.5rem;"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.4rem;"><div style="display:flex;align-items:center;gap:8px;"><span style="font-size:1.1rem;">{s["icon"]}</span><span style="font-size:0.87rem;font-weight:800;color:#0F172A;">{s["label"]}</span><span style="background:#EEF2FF;color:#3730A3;font-size:0.65rem;font-weight:700;padding:2px 7px;border-radius:4px;">{s["feasibility"]}</span></div><div style="text-align:right;"><div style="font-size:0.9rem;font-weight:800;color:#10B981;">&#x2212;{sym}{s["saving"]:,.0f}/mo</div><div style="font-size:0.72rem;color:#065F46;">{saving_pct}% reduction &bull; {sym}{annual_saving:,.0f}/yr</div></div></div><div style="font-size:0.78rem;color:#475569;line-height:1.5;">{s["note"]}</div><div style="display:flex;align-items:center;gap:8px;margin-top:0.4rem;"><div style="flex:1;background:#F1F5F9;border-radius:99px;height:5px;"><div style="background:#10B981;width:{min(saving_pct,100)}%;height:5px;border-radius:99px;"></div></div><div style="font-size:0.72rem;font-weight:700;color:#10B981;min-width:40px;text-align:right;">{sym}{s["monthly"]:,.0f}/mo</div></div></div>')

    sh('<div style="background:#F8FAFC;border-radius:8px;padding:0.75rem 1rem;margin-top:0.5rem;font-size:0.77rem;color:#64748B;">&#x26a0;&#xfe0f; All scenario projections are estimates. Clinical feasibility must be assessed by the treating nephrologist and multidisciplinary team before implementation.</div>')


# ─────────────────────────────────────────────────────────────────────────────
# Tab 4 — Research Transparency
# ─────────────────────────────────────────────────────────────────────────────

def _tab_research(cfg):
    sh("""
    <div style="background:linear-gradient(135deg,#1E3A5F,#1E40AF);border-radius:12px;padding:1.2rem 1.4rem;margin-bottom:1rem;">
        <div style="font-size:0.7rem;font-weight:700;color:rgba(255,255,255,0.6);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.4rem;">Primary Research Source</div>
        <div style="font-size:1rem;font-weight:800;color:white;margin-bottom:0.3rem;">Economic Burden and Quality of Life of Maintenance Hemodialysis Patients in a Rural Area of South India</div>
        <div style="font-size:0.8rem;color:rgba(255,255,255,0.75);margin-bottom:0.5rem;">Peer-reviewed pharmacoeconomic evaluation &mdash; published in Indian Journal of Nephrology</div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
            <span style="background:rgba(255,255,255,0.15);color:rgba(255,255,255,0.9);font-size:0.7rem;font-weight:600;padding:3px 9px;border-radius:6px;">PharmD Research</span>
            <span style="background:rgba(255,255,255,0.15);color:rgba(255,255,255,0.9);font-size:0.7rem;font-weight:600;padding:3px 9px;border-radius:6px;">South India Rural Cohort</span>
            <span style="background:rgba(255,255,255,0.15);color:rgba(255,255,255,0.9);font-size:0.7rem;font-weight:600;padding:3px 9px;border-radius:6px;">Cost-of-Illness Design</span>
            <span style="background:rgba(255,255,255,0.15);color:rgba(255,255,255,0.9);font-size:0.7rem;font-weight:600;padding:3px 9px;border-radius:6px;">WHO Catastrophic Expenditure Framework</span>
        </div>
    </div>
    """)

    sh('<div class="section-title"><span>&#x1f4d0;</span> Methodology Summary</div>')

    methodology = [
        ("Study Design", "Cost-of-illness analysis using bottom-up approach from the patient/household perspective"),
        ("Population", "Maintenance haemodialysis patients at a rural tertiary care hospital in South India"),
        ("Cost Categories", "Direct medical, direct non-medical, and indirect costs collected via structured interview"),
        ("Catastrophic Threshold", "WHO definition: out-of-pocket health expenditure >40% of household non-subsistence income"),
        ("Currency", "Original study in Indian Rupees (₹); model adapted for multi-country use with country-specific defaults"),
        ("Burden Scoring", "Financial burden score derived from income-burden percentage (capped at 100)"),
        ("Income Classification", "Low (<10%), Moderate (10-29%), High (30-59%), Catastrophic (≥40% WHO threshold)"),
    ]
    for label, desc in methodology:
        sh(f'<div style="display:grid;grid-template-columns:1.8fr 3fr;gap:8px;padding:6px 0;border-bottom:1px solid #F1F5F9;"><div style="font-size:0.78rem;font-weight:700;color:#1E3A5F;">{label}</div><div style="font-size:0.78rem;color:#374151;line-height:1.5;">{desc}</div></div>')

    sh('<div style="margin-top:1rem;"></div>')
    sh('<div class="section-title"><span>&#x1f4da;</span> Supporting References</div>')

    refs = [
        ("Primary Study", "Guideline", "Hemodialysis economic burden study — South India (adapted)", "Indian Journal of Nephrology"),
        ("WHO Framework", "Guideline", "WHO — Catastrophic Health Expenditure Definition & Measurement", "World Health Organization, 2017"),
        ("KDIGO 2024", "Guideline", "KDIGO Clinical Practice Guideline for CKD Evaluation and Management", "Kidney International, 2024"),
        ("ESRD Economics", "Systematic Review", "Global burden and cost of ESRD — systematic review and meta-analysis", "Lancet, 2020"),
        ("India PMJAY", "Policy", "Pradhan Mantri Jan Arogya Yojana — National Health Authority Guidelines", "Government of India, 2023"),
        ("Medicare ESRD", "Policy", "End Stage Renal Disease (ESRD) Medicare Benefit — Coverage Guidelines", "CMS, USA, 2024"),
    ]
    for ref_type, badge_type, title, journal in refs:
        badge_cfg = {"Guideline": ("#EFF6FF","#1D4ED8"), "Systematic Review": ("#F0FDF4","#065F46"), "Policy": ("#FEF3C7","#92400E")}
        bg, c = badge_cfg.get(badge_type, ("#F1F5F9","#475569"))
        sh(f'<div style="display:flex;align-items:flex-start;gap:8px;padding:5px 0;border-bottom:1px solid #F8FAFC;"><span style="background:{bg};color:{c};font-size:0.62rem;font-weight:700;padding:2px 7px;border-radius:4px;white-space:nowrap;margin-top:2px;">{badge_type}</span><div><div style="font-size:0.78rem;font-weight:600;color:#1E293B;">{title}</div><div style="font-size:0.72rem;color:#64748B;">{journal}</div></div></div>')

    sh("""
    <div style="background:#F8FAFC;border-radius:8px;padding:0.8rem 1rem;margin-top:1rem;font-size:0.77rem;color:#64748B;line-height:1.55;">
        &#x1f4cb; <strong>Adaptation Note:</strong> The core economic model (cost categories, burden scoring, WHO catastrophic threshold) is adapted from
        the primary South India hemodialysis burden study. Country-specific cost defaults are based on published healthcare cost benchmarks
        and professional clinical estimates. This model is intended for educational and clinical decision-support use only.
    </div>
    """)


def _render_placeholder():
    sh("""
    <div style="background:white;border:2px dashed #E2E8F0;border-radius:16px;padding:3rem;text-align:center;">
        <div style="font-size:3rem;margin-bottom:1rem;">&#x1f4ca;</div>
        <div style="font-size:1rem;font-weight:700;color:#0F172A;margin-bottom:0.5rem;">Pharmacoeconomic Intelligence</div>
        <div style="font-size:0.84rem;color:#64748B;max-width:400px;margin:0 auto;line-height:1.6;">
            Select a country, load defaults, and enter cost inputs to generate a comprehensive economic burden analysis
            with government scheme eligibility, cost reduction scenarios, and WHO catastrophic expenditure assessment.
        </div>
        <div style="margin-top:1.5rem;display:flex;gap:8px;justify-content:center;flex-wrap:wrap;">
            <span style="background:#FEE2E2;color:#991B1B;font-size:0.78rem;font-weight:600;padding:5px 12px;border-radius:8px;">WHO Catastrophic Threshold</span>
            <span style="background:#EFF6FF;color:#1E40AF;font-size:0.78rem;font-weight:600;padding:5px 12px;border-radius:8px;">Government Schemes</span>
            <span style="background:#D1FAE5;color:#065F46;font-size:0.78rem;font-weight:600;padding:5px 12px;border-radius:8px;">Cost Reduction Simulator</span>
            <span style="background:#EEF2FF;color:#3730A3;font-size:0.78rem;font-weight:600;padding:5px 12px;border-radius:8px;">Research Transparency</span>
        </div>
    </div>
    """)
