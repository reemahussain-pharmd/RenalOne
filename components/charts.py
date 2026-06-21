"""Shared Plotly chart components for RenalCare OS."""
import plotly.graph_objects as go
import plotly.express as px


def risk_gauge(score: float, title: str = "Risk Score") -> go.Figure:
    """Circular gauge chart for risk score 0-100."""
    if score < 25:
        color = "#27ae60"
    elif score < 50:
        color = "#f39c12"
    elif score < 75:
        color = "#e67e22"
    else:
        color = "#e74c3c"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": title, "font": {"size": 14, "color": "#1e3a5f"}},
        number={"font": {"size": 36, "color": color}, "suffix": "/100"},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#ccc", "tickfont": {"size": 9}},
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": "white",
            "borderwidth": 1,
            "bordercolor": "#eee",
            "steps": [
                {"range": [0, 25], "color": "#d5f5e3"},
                {"range": [25, 50], "color": "#fef9e7"},
                {"range": [50, 75], "color": "#fdf2e9"},
                {"range": [75, 100], "color": "#fdedec"},
            ],
            "threshold": {
                "line": {"color": color, "width": 3},
                "thickness": 0.75,
                "value": score,
            },
        },
    ))
    fig.update_layout(
        height=220, margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="white", font={"family": "Inter, sans-serif"},
    )
    return fig


def health_score_gauge(score: float) -> go.Figure:
    """Green-to-red gauge for kidney health score (higher = better)."""
    return risk_gauge(100 - score, "Risk Score")


def risk_factor_bar(factors: list[dict]) -> go.Figure:
    """Horizontal bar chart of contributing risk factors."""
    impact_map = {"High": 3, "Moderate": 2, "Low": 1, "Critical": 4}
    color_map = {"High": "#e74c3c", "Moderate": "#f39c12", "Low": "#3498db", "Critical": "#8e44ad"}

    names = [f["factor"] for f in factors]
    values = [impact_map.get(f.get("impact", "Low"), 1) for f in factors]
    colors = [color_map.get(f.get("impact", "Low"), "#95a5a6") for f in factors]

    fig = go.Figure(go.Bar(
        x=values, y=names,
        orientation="h",
        marker_color=colors,
        text=[f.get("impact", "") for f in factors],
        textposition="inside",
        textfont={"color": "white", "size": 10},
    ))
    fig.update_layout(
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(tickfont={"size": 10}),
        margin=dict(l=10, r=10, t=10, b=10),
        height=max(150, len(factors) * 35),
        paper_bgcolor="white", plot_bgcolor="white",
        font={"family": "Inter, sans-serif"},
    )
    return fig


def cost_donut(categories: list[str], values: list[float], title: str = "Cost Breakdown") -> go.Figure:
    """Donut chart for cost breakdown."""
    COLORS = ["#2980b9", "#16a085", "#8e44ad", "#e67e22", "#e74c3c", "#f39c12"]
    fig = go.Figure(go.Pie(
        labels=categories, values=values,
        hole=0.5,
        marker=dict(colors=COLORS[:len(categories)], line=dict(color="white", width=2)),
        textinfo="label+percent",
        textfont={"size": 10},
        hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color="#1e3a5f")),
        height=300, margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="white", font={"family": "Inter, sans-serif"},
        showlegend=True,
        legend=dict(font=dict(size=9)),
    )
    return fig


def nutrient_radar(nutrients: dict, daily_limits: dict, food_name: str) -> go.Figure:
    """Radar chart comparing food nutrients against daily limits."""
    keys = ["potassium_mg", "sodium_mg", "phosphorus_mg", "protein_g", "calories"]
    labels = ["Potassium", "Sodium", "Phosphorus", "Protein", "Calories"]

    serving_pct = []
    for k, lim_key in zip(keys, ["potassium_mg", "sodium_mg", "phosphorus_mg", None, None]):
        val = getattr(nutrients, k, 0)
        if lim_key and lim_key in daily_limits and daily_limits[lim_key] > 0:
            pct = (val / daily_limits[lim_key]) * 100
        else:
            if k == "protein_g":
                pct = (val / 60) * 100  # rough daily reference
            elif k == "calories":
                pct = (val / 2000) * 100
            else:
                pct = 0
        serving_pct.append(min(round(pct, 1), 150))

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=serving_pct + [serving_pct[0]],
        theta=labels + [labels[0]],
        fill="toself",
        fillcolor="rgba(41,128,185,0.2)",
        line=dict(color="#2980b9"),
        name="Serving (% of daily limit)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=[100] * (len(labels) + 1),
        theta=labels + [labels[0]],
        line=dict(color="#e74c3c", dash="dash"),
        name="Daily Limit",
        fill=None,
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 150], tickfont=dict(size=8))),
        title=dict(text=f"Nutrient Profile: {food_name}", font=dict(size=12, color="#1e3a5f")),
        height=280, margin=dict(l=40, r=40, t=50, b=20),
        paper_bgcolor="white", font={"family": "Inter, sans-serif"},
        legend=dict(font=dict(size=9)),
        showlegend=True,
    )
    return fig


def egfr_trend_placeholder() -> go.Figure:
    """Demo eGFR trend chart with sample data."""
    import numpy as np
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    egfr = [58, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months, y=egfr,
        mode="lines+markers",
        line=dict(color="#2980b9", width=2.5),
        marker=dict(size=7, color="#2980b9"),
        name="eGFR",
        fill="tozeroy",
        fillcolor="rgba(41,128,185,0.1)",
    ))
    fig.add_hline(y=60, line_dash="dash", line_color="#27ae60", annotation_text="Stage 2/3 Threshold (60)", annotation_font_size=9)
    fig.add_hline(y=45, line_dash="dash", line_color="#f39c12", annotation_text="Stage 3a/3b Threshold (45)", annotation_font_size=9)
    fig.add_hline(y=30, line_dash="dash", line_color="#e74c3c", annotation_text="Stage 3b/4 Threshold (30)", annotation_font_size=9)

    fig.update_layout(
        title=dict(text="eGFR Trend (Sample)", font=dict(size=12, color="#1e3a5f")),
        xaxis_title="Month", yaxis_title="eGFR (mL/min/1.73m²)",
        height=250, margin=dict(l=40, r=20, t=45, b=40),
        paper_bgcolor="white", plot_bgcolor="white",
        font={"family": "Inter, sans-serif"},
        yaxis=dict(range=[0, 90], gridcolor="#f0f0f0"),
        xaxis=dict(gridcolor="#f0f0f0"),
    )
    return fig
