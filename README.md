# news-bias-analyzer

Fetches the current front pages of major news outlets, runs each through GPT-4o for ideological and sentiment analysis, and produces a self-contained HTML report with interactive charts.

This is an experiment in applied NLP — using LLMs to characterize language patterns and framing from live news data, not to validate presumed outlet reputations.

---

## What it produces

A timestamped HTML report saved to `archive/` with five interactive charts:

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

## Prerequisites

- **Python 3.10+** — check with `python3 --version`
- **NewsAPI key** — free tier at [newsapi.org](https://newsapi.org) (100 requests/day)
- **OpenAI API key** — [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

> **macOS note:** macOS ships without a `python` command — only `python3`. Either use `python3` in all commands below, or add `alias python="python3"` to your `~/.zshrc` and restart your terminal.

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/loudowl/news-bias-analyzer.git
cd news-bias-analyzer
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows
```

You should see `(.venv)` in your prompt. **All subsequent commands assume the venv is active.**

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your API keys

```bash
cp .env.example .env
```

Open `.env` and fill in both keys:

```
NEWS_API_KEY=your-newsapi-key-here
OPENAI_API_KEY=sk-...
```

---

## Running the project

### Web server + scheduler (recommended)

```bash
python3 serve.py
```

This starts two things at once:

- A web server at **http://localhost:8080** — always shows the latest report
- A background scheduler that auto-generates a new report at **08:00, 12:00, and 17:00** daily

Each run saves a timestamped file to `archive/`. The home page shows the most recent report with a paginated archive nav at the bottom linking to every previous run.

```bash
# Custom port
python3 serve.py --port 3000

# Custom schedule (24h hours, comma-separated)
python3 serve.py --times 7,13,18

# Both
python3 serve.py --port 3000 --times 7,13,18
```

Press **Ctrl+C** to stop the server and scheduler.

---

### Generate a single report (no server)

```bash
python3 main.py
```

Saves to `archive/YYYY-MM-DD_HH-MM.html`. Open the file directly in any browser.

```bash
# Save to a custom path instead
python3 main.py --output my_report.html

# Analyse specific outlets only
python3 main.py --sources cnn,fox-news,bbc-news,the-new-york-times

# Use gpt-4o-mini for faster, cheaper runs (~80% less cost)
python3 main.py --model gpt-4o-mini

# Save raw API responses for debugging
python3 main.py --save-raw
```

Available source IDs: `reuters`, `associated-press`, `bbc-news`, `npr`, `cnn`, `msnbc`, `fox-news`, `the-new-york-times`, `the-washington-post`, `the-wall-street-journal`, `the-guardian-us`, `the-hill`, `politico`, `breitbart-news`

---

## Troubleshooting

**`command not found: python`**
Use `python3` instead, or add `alias python="python3"` to `~/.zshrc` and run `source ~/.zshrc`.

**`ModuleNotFoundError`**
Your venv isn't active. Run `source .venv/bin/activate` first.

**`Missing environment variables`**
The `.env` file is missing or incomplete. Make sure both `NEWS_API_KEY` and `OPENAI_API_KEY` are set.

**`429` from NewsAPI**
The free tier allows 100 requests/day. Three scheduled runs × 14 sources = 42 requests/day — well within the limit. If you hit the cap, it resets at midnight UTC.

**Port 8080 already in use**
Run `python3 serve.py --port 3001` (or any free port).

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
- [Flask](https://flask.palletsprojects.com) — web server
- [APScheduler](https://apscheduler.readthedocs.io) — scheduled runs

---

## Ideas for extending this

- [x] Run on a schedule and track lean/sentiment drift over time
- [ ] Add a comparison view: "today vs. 30-day average"
- [ ] Include full article text (NewsAPI paid tier) for deeper analysis
- [ ] Add international outlets (Al Jazeera, RT, DW, etc.)
- [ ] Export findings to a markdown brief (combine with research-crew-agent)
- [ ] Fine-tune a smaller model on labeled media bias datasets to replace GPT-4o

---

## License

MIT
