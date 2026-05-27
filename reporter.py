"""
Assembles analysis results and Plotly charts into a self-contained HTML report.
"""

import json
from datetime import datetime
from typing import Dict
from visualizer import (
    ideological_spectrum_chart,
    sentiment_bar_chart,
    topic_heatmap,
    intensity_radar,
    lean_bar_chart,
)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>News Bias Analysis — {date}</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<style>
  :root {{
    --bg: #0f0f1a;
    --surface: #1a1a2e;
    --surface2: #16213e;
    --accent: #6aaed6;
    --left: #2e6bbf;
    --right: #d2522b;
    --text: #e0e0e0;
    --muted: #888;
    --border: #2a2a4a;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    line-height: 1.6;
  }}
  header {{
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 2rem;
    text-align: center;
  }}
  header h1 {{ font-size: 1.8rem; color: var(--accent); margin-bottom: 0.3rem; }}
  header p  {{ color: var(--muted); font-size: 0.9rem; }}
  .methodology {{
    background: var(--surface2);
    border-left: 3px solid var(--accent);
    margin: 1.5rem auto;
    max-width: 900px;
    padding: 1rem 1.5rem;
    font-size: 0.85rem;
    color: var(--muted);
    border-radius: 4px;
  }}
  .container {{ max-width: 1100px; margin: 0 auto; padding: 1.5rem; }}
  .section {{ margin-bottom: 3rem; }}
  .section h2 {{
    font-size: 1.2rem;
    color: var(--accent);
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.5rem;
    margin-bottom: 1.2rem;
  }}
  .chart-wrap {{
    background: var(--surface);
    border-radius: 8px;
    padding: 1rem;
    border: 1px solid var(--border);
  }}
  .cards {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
  }}
  .card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.2rem;
  }}
  .card h3 {{
    font-size: 1rem;
    margin-bottom: 0.3rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }}
  .lean-badge {{
    font-size: 0.7rem;
    padding: 2px 8px;
    border-radius: 12px;
    font-weight: 600;
    color: white;
  }}
  .card .summary {{ font-size: 0.85rem; color: var(--muted); margin: 0.5rem 0; font-style: italic; }}
  .card .topics {{ font-size: 0.8rem; margin-top: 0.6rem; }}
  .card .topics span {{
    display: inline-block;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1px 8px;
    margin: 2px 2px;
    font-size: 0.75rem;
    color: var(--accent);
  }}
  .card .reasoning {{
    font-size: 0.8rem;
    color: var(--muted);
    margin-top: 0.6rem;
    padding-top: 0.6rem;
    border-top: 1px solid var(--border);
  }}
  .scores {{
    display: flex;
    gap: 1rem;
    margin-top: 0.6rem;
    font-size: 0.8rem;
  }}
  .score-pill {{
    background: var(--surface2);
    border-radius: 4px;
    padding: 2px 8px;
  }}
  .spectrum-bar {{
    width: 100%;
    height: 8px;
    border-radius: 4px;
    background: linear-gradient(to right, #1a3a8f, #6aaed6, #888, #f4a460, #8b0000);
    margin: 0.8rem 0 0.3rem;
    position: relative;
  }}
  .spectrum-marker {{
    position: absolute;
    top: -3px;
    width: 14px;
    height: 14px;
    background: white;
    border-radius: 50%;
    transform: translateX(-50%);
    border: 2px solid #333;
  }}
  footer {{
    text-align: center;
    padding: 2rem;
    color: var(--muted);
    font-size: 0.8rem;
    border-top: 1px solid var(--border);
    margin-top: 3rem;
  }}
</style>
</head>
<body>

<header>
  <h1>📰 News Front Page Bias Analysis</h1>
  <p>Generated {datetime} · {source_count} outlets · {total_articles} headlines analysed</p>
  <p style="margin-top:0.3rem; color:#6aaed6; font-size:0.85rem">
    Analysis powered by GPT-4o + NewsAPI
  </p>
</header>

<div class="container">
  <div class="methodology">
    <strong>Methodology:</strong> Headlines and descriptions from each outlet's current front page were
    retrieved via NewsAPI and analysed by GPT-4o. The model was instructed to evaluate
    <em>language patterns, word choice, and framing only</em> — not to apply presumed outlet reputations.
    Ideological lean scores are derived from today's actual content and may differ from historical classifications.
    This is an experimental tool; treat scores as directional, not definitive.
  </div>

  <div class="section">
    <h2>Ideological Spectrum &amp; Emotional Intensity</h2>
    <div class="chart-wrap">{chart_spectrum}</div>
  </div>

  <div class="section">
    <h2>Ideological Lean by Outlet</h2>
    <div class="chart-wrap">{chart_lean_bar}</div>
  </div>

  <div class="section">
    <h2>Headline Sentiment by Outlet</h2>
    <div class="chart-wrap">{chart_sentiment}</div>
  </div>

  <div class="section">
    <h2>Topic Coverage Heatmap</h2>
    <div class="chart-wrap">{chart_heatmap}</div>
  </div>

  <div class="section">
    <h2>Emotional Intensity by Outlet</h2>
    <div class="chart-wrap">{chart_radar}</div>
  </div>

  <div class="section">
    <h2>Outlet-by-Outlet Breakdown</h2>
    <div class="cards">{cards}</div>
  </div>
</div>

<footer>
  Built with <a href="https://github.com/loudowl/news-bias-analyzer" style="color:var(--accent)">news-bias-analyzer</a>
  · Data from <a href="https://newsapi.org" style="color:var(--accent)">NewsAPI</a>
  · Analysis by GPT-4o
</footer>

</body>
</html>"""

LEAN_COLORS_CSS = {
    "Far Left":     "#1a3a8f",
    "Left":         "#2e6bbf",
    "Center-Left":  "#6aaed6",
    "Center":       "#888888",
    "Center-Right": "#f4a460",
    "Right":        "#d2522b",
    "Far Right":    "#8b0000",
    "Unknown":      "#555",
}


def _lean_position(score: float) -> float:
    """Convert lean score (-5 to 5) to a 0–100% position for the spectrum bar."""
    return max(0, min(100, (score + 5) / 10 * 100))


def _make_card(r: Dict) -> str:
    if r.get("error"):
        return f"""
        <div class="card">
          <h3>{r['source_name']}</h3>
          <p class="summary">No data retrieved.</p>
        </div>"""

    lean_label = r.get("ideological_lean_label", "Unknown")
    lean_score = r.get("ideological_lean_score", 0)
    sentiment  = r.get("sentiment_score", 0)
    intensity  = r.get("emotional_intensity", 0)
    lean_color = LEAN_COLORS_CSS.get(lean_label, "#555")
    topics_html = "".join(f"<span>{t}</span>" for t in r.get("top_topics", []))
    pos = _lean_position(lean_score)

    return f"""
    <div class="card">
      <h3>
        {r['source_name']}
        <span class="lean-badge" style="background:{lean_color}">{lean_label}</span>
      </h3>
      <div class="spectrum-bar">
        <div class="spectrum-marker" style="left:{pos:.1f}%"></div>
      </div>
      <p class="summary">"{r.get('one_line_summary', '')}"</p>
      <div class="scores">
        <span class="score-pill">Lean: {lean_score:+.1f}</span>
        <span class="score-pill">Sentiment: {sentiment:+.2f}</span>
        <span class="score-pill">Intensity: {intensity:.1f}/10</span>
      </div>
      <div class="topics">{topics_html}</div>
      <p class="reasoning">{r.get('ideological_lean_reasoning', '')}</p>
    </div>"""


def build_report(results: Dict[str, Dict], output_path: str = "report.html") -> str:
    now = datetime.now()
    total_articles = sum(r.get("article_count", 0) for r in results.values())
    valid = [r for r in results.values() if not r.get("error")]

    print("\n📊 Generating charts...")
    chart_spectrum  = ideological_spectrum_chart(results)
    chart_lean_bar  = lean_bar_chart(results)
    chart_sentiment = sentiment_bar_chart(results)
    chart_heatmap   = topic_heatmap(results)
    chart_radar     = intensity_radar(results)

    print("🃏 Building outlet cards...")
    cards = "\n".join(_make_card(r) for r in results.values())

    html = HTML_TEMPLATE.format(
        date=now.strftime("%B %d, %Y"),
        datetime=now.strftime("%B %d, %Y at %H:%M"),
        source_count=len(valid),
        total_articles=total_articles,
        chart_spectrum=chart_spectrum,
        chart_lean_bar=chart_lean_bar,
        chart_sentiment=chart_sentiment,
        chart_heatmap=chart_heatmap,
        chart_radar=chart_radar,
        cards=cards,
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path
