"""
Generates Plotly charts from analysis results.
All charts are returned as HTML div strings for embedding in the report.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List


# ── Colour palette ────────────────────────────────────────────────────────────

LEAN_COLORS = {
    "Far Left":     "#1a3a8f",
    "Left":         "#2e6bbf",
    "Center-Left":  "#6aaed6",
    "Center":       "#888888",
    "Center-Right": "#f4a460",
    "Right":        "#d2522b",
    "Far Right":    "#8b0000",
    "Unknown":      "#cccccc",
}

CHART_CONFIG = {"displayModeBar": False, "responsive": True}
CHART_HEIGHT = 480


def _to_div(fig) -> str:
    return fig.to_html(full_html=False, include_plotlyjs=False, config=CHART_CONFIG)


# ── Chart 1: Ideological Spectrum Scatter ─────────────────────────────────────

def ideological_spectrum_chart(results: Dict[str, Dict]) -> str:
    """
    Scatter plot: x = ideological lean score, y = emotional intensity.
    Bubble size = article count. Colour = lean label.
    """
    rows = []
    for sid, r in results.items():
        if r.get("error"):
            continue
        rows.append({
            "Source":      r["source_name"],
            "Lean Score":  r.get("ideological_lean_score", 0),
            "Lean Label":  r.get("ideological_lean_label", "Unknown"),
            "Intensity":   r.get("emotional_intensity", 0),
            "Sentiment":   r.get("sentiment_score", 0),
            "Articles":    r.get("article_count", 10),
            "Summary":     r.get("one_line_summary", ""),
        })
    if not rows:
        return "<p>No data available.</p>"

    df = pd.DataFrame(rows)
    colors = [LEAN_COLORS.get(lbl, "#aaa") for lbl in df["Lean Label"]]

    fig = go.Figure()
    for _, row in df.iterrows():
        fig.add_trace(go.Scatter(
            x=[row["Lean Score"]],
            y=[row["Intensity"]],
            mode="markers+text",
            marker=dict(
                size=max(row["Articles"] * 2, 20),
                color=LEAN_COLORS.get(row["Lean Label"], "#aaa"),
                opacity=0.85,
                line=dict(width=1, color="white"),
            ),
            text=row["Source"],
            textposition="top center",
            textfont=dict(size=11),
            name=row["Source"],
            hovertemplate=(
                f"<b>{row['Source']}</b><br>"
                f"Lean: {row['Lean Label']} ({row['Lean Score']:+.1f})<br>"
                f"Intensity: {row['Intensity']:.1f}/10<br>"
                f"Sentiment: {row['Sentiment']:+.2f}<br>"
                f"<i>{row['Summary']}</i><extra></extra>"
            ),
            showlegend=False,
        ))

    fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.4)
    fig.add_annotation(x=-4.5, y=9.5, text="← Left", showarrow=False,
                       font=dict(color="#2e6bbf", size=12))
    fig.add_annotation(x=4.5, y=9.5, text="Right →", showarrow=False,
                       font=dict(color="#d2522b", size=12))

    fig.update_layout(
        title="Ideological Lean vs. Emotional Intensity",
        xaxis=dict(title="Ideological Lean Score (-5 = Far Left → +5 = Far Right)",
                   range=[-5.5, 5.5], zeroline=False),
        yaxis=dict(title="Emotional Intensity (0 = Dry, 10 = Highly Charged)",
                   range=[-0.5, 10.5]),
        height=CHART_HEIGHT,
        plot_bgcolor="#1a1a2e",
        paper_bgcolor="#1a1a2e",
        font=dict(color="white"),
        margin=dict(t=60, b=60, l=60, r=40),
    )
    return _to_div(fig)


# ── Chart 2: Sentiment Bar Chart ──────────────────────────────────────────────

def sentiment_bar_chart(results: Dict[str, Dict]) -> str:
    """Horizontal bar chart of sentiment score per outlet, sorted left to right."""
    rows = [
        {
            "Source":    r["source_name"],
            "Sentiment": r.get("sentiment_score", 0),
            "Lean":      r.get("ideological_lean_label", "Unknown"),
        }
        for r in results.values() if not r.get("error")
    ]
    if not rows:
        return "<p>No data available.</p>"

    df = pd.DataFrame(rows).sort_values("Sentiment")
    colors = [LEAN_COLORS.get(lbl, "#aaa") for lbl in df["Lean"]]

    fig = go.Figure(go.Bar(
        x=df["Sentiment"],
        y=df["Source"],
        orientation="h",
        marker_color=colors,
        text=[f"{v:+.2f}" for v in df["Sentiment"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Sentiment: %{x:+.2f}<extra></extra>",
    ))

    fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.update_layout(
        title="Headline Sentiment by Outlet (−1 = Very Negative → +1 = Very Positive)",
        xaxis=dict(title="Sentiment Score", range=[-1.2, 1.2]),
        yaxis=dict(title=""),
        height=max(CHART_HEIGHT, len(rows) * 38),
        plot_bgcolor="#1a1a2e",
        paper_bgcolor="#1a1a2e",
        font=dict(color="white"),
        margin=dict(t=60, b=40, l=160, r=80),
    )
    return _to_div(fig)


# ── Chart 3: Topic Coverage Heatmap ───────────────────────────────────────────

def topic_heatmap(results: Dict[str, Dict]) -> str:
    """
    Heatmap: rows = sources, columns = top topics across all outlets.
    Cell value = 1 if outlet covers that topic, 0 if not.
    """
    # Gather all topics
    topic_counts: Dict[str, int] = {}
    for r in results.values():
        if r.get("error"):
            continue
        for t in r.get("top_topics", []):
            topic_counts[t] = topic_counts.get(t, 0) + 1

    if not topic_counts:
        return "<p>No topic data available.</p>"

    # Keep top 12 topics by frequency
    top_topics = [t for t, _ in sorted(topic_counts.items(),
                                        key=lambda x: -x[1])][:12]

    sources = [r["source_name"] for r in results.values() if not r.get("error")]
    matrix = []
    for r in results.values():
        if r.get("error"):
            continue
        outlet_topics = [t.lower() for t in r.get("top_topics", [])]
        row = []
        for topic in top_topics:
            # fuzzy match: topic word appears in any of the outlet's topics
            match = any(
                topic.lower() in ot or ot in topic.lower()
                for ot in outlet_topics
            )
            row.append(1 if match else 0)
        matrix.append(row)

    fig = go.Figure(go.Heatmap(
        z=matrix,
        x=top_topics,
        y=sources,
        colorscale=[[0, "#1a1a2e"], [1, "#6aaed6"]],
        showscale=False,
        hovertemplate="<b>%{y}</b><br>Topic: %{x}<br>Covered: %{z}<extra></extra>",
    ))
    fig.update_layout(
        title="Topic Coverage Across Outlets",
        xaxis=dict(tickangle=-35, title=""),
        yaxis=dict(title=""),
        height=max(CHART_HEIGHT, len(sources) * 38),
        plot_bgcolor="#1a1a2e",
        paper_bgcolor="#1a1a2e",
        font=dict(color="white"),
        margin=dict(t=60, b=120, l=160, r=40),
    )
    return _to_div(fig)


# ── Chart 4: Emotional Intensity Radar ────────────────────────────────────────

def intensity_radar(results: Dict[str, Dict]) -> str:
    """
    Radar / polar bar chart comparing emotional intensity across outlets.
    """
    rows = [
        {"Source": r["source_name"], "Intensity": r.get("emotional_intensity", 0)}
        for r in results.values() if not r.get("error")
    ]
    if not rows:
        return "<p>No data available.</p>"

    df = pd.DataFrame(rows).sort_values("Intensity", ascending=False)

    fig = go.Figure(go.Barpolar(
        r=df["Intensity"],
        theta=df["Source"],
        marker_color=[
            LEAN_COLORS.get(
                results.get(
                    next((sid for sid, rv in results.items()
                           if rv.get("source_name") == row["Source"]), None),
                    {}
                ).get("ideological_lean_label", "Unknown"),
                "#888"
            )
            for _, row in df.iterrows()
        ],
        marker_line_color="white",
        marker_line_width=1,
        opacity=0.85,
        hovertemplate="<b>%{theta}</b><br>Intensity: %{r:.1f}/10<extra></extra>",
    ))
    fig.update_layout(
        title="Emotional Intensity by Outlet (0 = Dry, 10 = Highly Charged)",
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10],
                            tickfont=dict(color="white")),
            bgcolor="#1a1a2e",
        ),
        height=CHART_HEIGHT,
        plot_bgcolor="#1a1a2e",
        paper_bgcolor="#1a1a2e",
        font=dict(color="white"),
        margin=dict(t=60, b=40, l=40, r=40),
    )
    return _to_div(fig)


# ── Chart 5: Lean Score Summary Bar ───────────────────────────────────────────

def lean_bar_chart(results: Dict[str, Dict]) -> str:
    """Horizontal bar showing each outlet's ideological lean score."""
    rows = [
        {
            "Source": r["source_name"],
            "Score":  r.get("ideological_lean_score", 0),
            "Lean":   r.get("ideological_lean_label", "Unknown"),
        }
        for r in results.values() if not r.get("error")
    ]
    if not rows:
        return "<p>No data available.</p>"

    df = pd.DataFrame(rows).sort_values("Score")
    colors = [LEAN_COLORS.get(lbl, "#aaa") for lbl in df["Lean"]]

    fig = go.Figure(go.Bar(
        x=df["Score"],
        y=df["Source"],
        orientation="h",
        marker_color=colors,
        text=df["Lean"],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Score: %{x:+.1f}<br>%{text}<extra></extra>",
    ))

    fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_annotation(x=-4, y=-0.8, text="← Far Left", showarrow=False,
                       font=dict(color="#2e6bbf", size=11))
    fig.add_annotation(x=4, y=-0.8, text="Far Right →", showarrow=False,
                       font=dict(color="#d2522b", size=11))

    fig.update_layout(
        title="Ideological Lean Score by Outlet",
        xaxis=dict(title="Score (−5 = Far Left → +5 = Far Right)", range=[-5.5, 5.5]),
        yaxis=dict(title=""),
        height=max(CHART_HEIGHT, len(rows) * 38),
        plot_bgcolor="#1a1a2e",
        paper_bgcolor="#1a1a2e",
        font=dict(color="white"),
        margin=dict(t=60, b=60, l=160, r=120),
    )
    return _to_div(fig)
