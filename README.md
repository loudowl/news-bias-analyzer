# news-bias-analyzer

Fetches the current front pages of major news outlets, runs each through GPT-4o for ideological and sentiment analysis, and produces a self-contained HTML report with interactive charts.

This is an experiment in applied NLP — using LLMs to characterize language patterns and framing from live news data, not to validate presumed outlet reputations.

---

## What it produces

A single `report.html` file with five interactive charts:

| Chart | What it shows |
|---|---|
| **Spectrum Scatter** | Each outlet plotted by ideological lean (x) vs. emotional intensity (y) |
| **Lean Bar** | Outlets ranked from Far Left to Far Right by today's content |
| **Sentiment Bar** | Headline positivity/negativity per outlet |
| **Topic Heatmap** | Which outlets are covering which topics |
| **Intensity Radar** | Emotional charge of language across outlets |

Plus a card for each outlet showing its lean reasoning, topic tags, and key scores.

---

## Outlets analysed (default)

Reuters · AP · BBC · NPR · CNN · MSNBC · Fox News · New York Times · Washington Post · Wall Street Journal · The Guardian · The Hill · Politico · Breitbart

---

## Setup

```bash
git clone https://github.com/loudowl/news-bias-analyzer.git
cd news-bias-analyzer
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your API keys
```

**API keys needed:**
- [NewsAPI](https://newsapi.org) — free tier, 100 requests/day
- [OpenAI](https://platform.openai.com/api-keys) — GPT-4o for analysis

---

## Usage

```bash
# Full run — all 14 outlets
python main.py

# Custom output path
python main.py --output analysis_may2026.html

# Specific outlets only
python main.py --sources cnn,fox-news,bbc-news,the-new-york-times

# Use gpt-4o-mini for faster/cheaper runs
python main.py --model gpt-4o-mini

# Save raw API responses for debugging
python main.py --save-raw
```

Open `report.html` in any browser — no server needed.

---

## How the analysis works

For each outlet, the LLM receives all current headlines and descriptions and is asked to evaluate:

- **Sentiment score** — overall emotional valence of the headlines (-1 to +1)
- **Ideological lean score** — based on language patterns and framing, not presumed reputation (-5 to +5)
- **Emotional intensity** — how charged the language is (0 to 10)
- **Top topics** — subjects covered on today's front page
- **Framing patterns** — rhetorical and linguistic choices observed
- **Distinctive language** — characteristic words/phrases for this outlet today

The model is explicitly instructed *not* to apply prior knowledge of outlet reputation — only what today's actual text shows.

---

## Methodology note

Scores are based on today's headlines only and will vary day to day based on what's in the news. A major crisis will push all outlets toward negative sentiment. A slow news day will compress lean scores toward center. This is a snapshot tool, not a longitudinal study.

---

## Stack

- [NewsAPI](https://newsapi.org) — live headline data
- [OpenAI GPT-4o](https://platform.openai.com) — structured language analysis
- [Plotly](https://plotly.com/python/) — interactive charts
- [pandas](https://pandas.pydata.org) — data shaping

---

## Ideas for extending this

- [ ] Run on a schedule and track lean/sentiment drift over time
- [ ] Add a comparison view: "today vs. 30-day average"
- [ ] Include full article text (NewsAPI paid tier) for deeper analysis
- [ ] Add international outlets (Al Jazeera, RT, DW, etc.)
- [ ] Export findings to a markdown brief (combine with research-crew-agent)
- [ ] Fine-tune a smaller model on labeled media bias datasets to replace GPT-4o

---

## License

MIT
