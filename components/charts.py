"""Premium Plotly chart components — RenalCare AI."""
import plotly.graph_objects as go
import plotly.express as px


# Shared layout defaults
_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#0F172A"),
    margin=dict(l=20, r=20, t=30, b=20),
)

PALETTE = ["#14B8A6", "#6366F1", "#F59E0B", "#EF4444", "#10B981", "#3B82F6", "#8B5CF6"]


def risk_gauge(score: float, risk_level: str) -> go.Figure:
    level_colors = {
        "LOW":       "#10B981",
        "MODERATE":  "#F59E0B",
        "HIGH":      "#EF4444",
        "VERY HIGH": "#7C3AED",
    }
    color = level_colors.get(risk_level.upper(), "#F59E0B")

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        number={"suffix": "/100", "font": {"size": 36, "family": "Inter", "color": color}, "valueformat": ".0f"},
        delta={"reference": 50, "valueformat": ".0f"},
        gauge={
            "axis": {
                "range": [0, 100],
                "tickwidth": 1,
                "tickcolor": "#E2E8F0",
                "tickfont": {"size": 10, "color": "#94A3B8"},
                "nticks": 6,
            },
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  25], "color": "#D1FAE5"},
                {"range": [25, 50], "color": "#FEF3C7"},
                {"range": [50, 75], "color": "#FEE2E2"},
                {"range": [75,100], "color": "#EDE9FE"},
            ],
            "threshold": {
                "line": {"color": color, "width": 3},
                "thickness": 0.85,
                "value": score,
            },
        },
        title={
            "text": f"<b>Risk Score</b><br><span style='font-size:12px;color:#64748B;'>{risk_level} RISK</span>",
            "font": {"size": 14, "color": "#0F172A"},
        },
    ))
    fig.update_layout(**_LAYOUT, height=260)
    return fig


def risk_factor_bar(factors: dict) -> go.Figure:
    if not factors:
        return go.Figure()

    labels = list(factors.keys())[:8]
    values = [factors[k] for k in labels]
    colors = [
        "#EF4444" if v >= 15 else ("#F59E0B" if v >= 8 else "#14B8A6")
        for v in values
    ]

    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker=dict(
            color=colors,
            line=dict(width=0),
        ),
        text=[f"{v:.0f}" for v in values],
        textposition="outside",
        textfont=dict(size=11, color="#374151", family="Inter"),
        hovertemplate="<b>%{y}</b><br>Contribution: %{x:.0f}<extra></extra>",
    ))

    fig.update_layout(
        **_LAYOUT,
        height=280,
        title=dict(text="<b>Risk Factor Contributions</b>", font=dict(size=13, color="#0F172A")),
        xaxis=dict(
            showgrid=True,
            gridcolor="#F1F5F9",
            gridwidth=1,
            zeroline=False,
            showline=False,
            tickfont=dict(size=10, color="#94A3B8"),
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(size=11, color="#374151"),
        ),
        bargap=0.35,
    )
    return fig


def cost_donut(breakdown: dict) -> go.Figure:
    labels = list(breakdown.keys())
    values = list(breakdown.values())
    colors = ["#1E3A5F", "#14B8A6", "#6366F1", "#F59E0B", "#EF4444", "#10B981"][:len(labels)]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(
            colors=colors,
            line=dict(color="white", width=3),
        ),
        textinfo="percent",
        textfont=dict(size=12, color="white", family="Inter"),
        hovertemplate="<b>%{label}</b><br>$%{value:,.0f}/month<br>%{percent}<extra></extra>",
    ))

    total = sum(values)
    fig.add_annotation(
        text=f"<b>${total:,.0f}</b><br><span style='font-size:10px'>Monthly Total</span>",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=14, color="#0F172A", family="Inter"),
        align="center",
    )

    fig.update_layout(
        **_LAYOUT,
        height=300,
        title=dict(text="<b>Cost Distribution</b>", font=dict(size=13, color="#0F172A")),
        legend=dict(
            orientation="v",
            x=1.02, y=0.5,
            font=dict(size=11, color="#374151"),
        ),
        showlegend=True,
    )
    return fig


def nutrient_radar(nutrients: dict, limits: dict) -> go.Figure:
    categories = {
        "potassium_mg":  "Potassium",
        "sodium_mg":     "Sodium",
        "phosphorus_mg": "Phosphorus",
        "protein_g":     "Protein",
    }

    labels = []
    values = []
    for key, label in categories.items():
        if key in nutrients and key in limits and limits[key] > 0:
            pct = min(nutrients[key] / limits[key] * 100, 150)
            labels.append(label)
            values.append(pct)

    if not labels:
        return go.Figure()

    labels_closed = labels + [labels[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()

    # Safe zone fill (0-80%)
    fig.add_trace(go.Scatterpolar(
        r=[80] * (len(labels) + 1),
        theta=labels_closed,
        fill="toself",
        fillcolor="rgba(16,185,129,0.08)",
        line=dict(color="rgba(16,185,129,0.3)", width=1, dash="dash"),
        name="Safe Zone (80%)",
        hoverinfo="skip",
    ))

    # Actual values
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=labels_closed,
        fill="toself",
        fillcolor="rgba(99,102,241,0.15)",
        line=dict(color="#6366F1", width=2.5),
        marker=dict(size=7, color="#6366F1"),
        name="% of Daily Limit",
        hovertemplate="<b>%{theta}</b><br>%{r:.0f}% of daily limit<extra></extra>",
    ))

    fig.update_layout(
        **_LAYOUT,
        height=280,
        title=dict(text="<b>Nutrient Profile (% of daily limit)</b>", font=dict(size=13, color="#0F172A")),
        polar=dict(
            bgcolor="rgba(248,250,252,0.8)",
            radialaxis=dict(
                visible=True,
                range=[0, 120],
                ticksuffix="%",
                tickfont=dict(size=9, color="#94A3B8"),
                gridcolor="#E2E8F0",
                linecolor="#E2E8F0",
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color="#374151", family="Inter"),
                gridcolor="#E2E8F0",
                linecolor="#E2E8F0",
            ),
        ),
        legend=dict(
            x=0.5, y=-0.15,
            xanchor="center",
            orientation="h",
            font=dict(size=10, color="#64748B"),
        ),
        showlegend=True,
    )
    return fig


def egfr_trend_placeholder() -> go.Figure:
    import numpy as np
    months = list(range(1, 13))
    egfr_values = [52, 51, 49, 48, 50, 47, 45, 44, 46, 43, 42, 41]

    fig = go.Figure()

    # Danger zone fill
    fig.add_hrect(y0=0, y1=30, fillcolor="rgba(239,68,68,0.06)", line_width=0)
    fig.add_hrect(y0=30, y1=45, fillcolor="rgba(245,158,11,0.06)", line_width=0)
    fig.add_hrect(y0=45, y1=60, fillcolor="rgba(20,184,166,0.06)", line_width=0)

    # Area fill
    fig.add_trace(go.Scatter(
        x=months, y=egfr_values,
        fill="tozeroy",
        fillcolor="rgba(20,184,166,0.08)",
        line=dict(color="#14B8A6", width=0),
        showlegend=False,
        hoverinfo="skip",
    ))

    # Line
    fig.add_trace(go.Scatter(
        x=months,
        y=egfr_values,
        mode="lines+markers",
        line=dict(color="#14B8A6", width=2.5, shape="spline"),
        marker=dict(size=6, color="#14B8A6", line=dict(color="white", width=2)),
        name="eGFR",
        hovertemplate="Month %{x}<br>eGFR: <b>%{y} mL/min</b><extra></extra>",
    ))

    # Stage lines
    for y, label, color in [(60, "G3a threshold", "#F59E0B"), (30, "G4 threshold", "#EF4444")]:
        fig.add_hline(y=y, line_dash="dot", line_color=color, line_width=1.2,
                      annotation_text=label, annotation_position="right",
                      annotation_font_size=9, annotation_font_color=color)

    fig.update_layout(
        **_LAYOUT,
        height=260,
        title=dict(text="<b>eGFR Trend (12 months)</b><br><span style='font-size:10px;color:#94A3B8'>Sample data — connect EHR for live data</span>",
                   font=dict(size=13, color="#0F172A")),
        xaxis=dict(
            title="Month",
            showgrid=False,
            tickfont=dict(size=10, color="#94A3B8"),
        ),
        yaxis=dict(
            title="eGFR (mL/min/1.73m²)",
            showgrid=True,
            gridcolor="#F1F5F9",
            tickfont=dict(size=10, color="#94A3B8"),
            range=[0, 70],
        ),
        showlegend=False,
    )
    return fig
