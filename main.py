#!/usr/bin/env python3
"""
news-bias-analyzer
------------------
Fetches the current front pages of major news outlets via NewsAPI,
runs each through GPT-4o for ideological and sentiment analysis,
and produces a self-contained HTML report with interactive charts.

Usage:
    python main.py
    python main.py --output my_report.html
    python main.py --sources cnn,fox-news,bbc-news
    python main.py --model gpt-4o-mini   # cheaper, faster
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from sources import SOURCES, SOURCE_MAP
from fetcher import fetch_all, format_for_analysis
from analyzer import analyze_all
from reporter import build_report


def parse_args():
    parser = argparse.ArgumentParser(
        description="Analyse ideological bias across major news outlets.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--output", "-o", default=None,
        help="Output file path (default: archive/YYYY-MM-DD_HH-MM.html)",
    )
    parser.add_argument(
        "--sources", "-s", default=None,
        help="Comma-separated list of NewsAPI source IDs to include "
             "(default: all configured sources)",
    )
    parser.add_argument(
        "--model", "-m", default="gpt-4o",
        help="OpenAI model to use for analysis (default: gpt-4o)",
    )
    parser.add_argument(
        "--save-raw", action="store_true",
        help="Save raw API responses to raw_data.json for debugging",
    )
    return parser.parse_args()


def check_env():
    missing = []
    if not os.getenv("OPENAI_API_KEY"):
        missing.append("OPENAI_API_KEY")
    if not os.getenv("NEWS_API_KEY"):
        missing.append("NEWS_API_KEY")
    if missing:
        print(f"❌  Missing environment variables: {', '.join(missing)}")
        print("    Copy .env.example to .env and fill in your keys.")
        sys.exit(1)


def main():
    args = parse_args()
    check_env()

    Path("archive").mkdir(exist_ok=True)
    output = args.output or f"archive/{datetime.now().strftime('%Y-%m-%d_%H-%M')}.html"

    # Resolve source list
    if args.sources:
        ids = [s.strip() for s in args.sources.split(",")]
        sources = [SOURCE_MAP[sid] for sid in ids if sid in SOURCE_MAP]
        unknown = [sid for sid in ids if sid not in SOURCE_MAP]
        if unknown:
            print(f"⚠️  Unknown source IDs (ignored): {', '.join(unknown)}")
    else:
        sources = SOURCES

    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    news_api_key  = os.getenv("NEWS_API_KEY")

    print(f"\n📰 News Bias Analyzer")
    print(f"   Sources : {len(sources)}")
    print(f"   Model   : {args.model}")
    print(f"   Output  : {output}")
    print("=" * 50)

    # ── Step 1: Fetch headlines ───────────────────────────────────────────────
    print("\n🌐 Fetching front pages...")
    raw_articles = fetch_all(sources, news_api_key)

    # ── Step 2: Prepare content for analysis ─────────────────────────────────
    source_data = {}
    for source in sources:
        sid = source["id"]
        articles = raw_articles.get(sid, [])
        source_data[sid] = {
            "name":          source["name"],
            "content":       format_for_analysis(articles),
            "article_count": len(articles),
        }

    if args.save_raw:
        with open("raw_data.json", "w") as f:
            json.dump(source_data, f, indent=2)
        print("💾 Raw data saved to raw_data.json")

    # ── Step 3: LLM analysis ─────────────────────────────────────────────────
    print(f"\n🤖 Analysing with {args.model}...")
    analysis_results = analyze_all(source_data, openai_client, model=args.model)

    # ── Step 4: Build HTML report ─────────────────────────────────────────────
    print("\n📄 Building report...")
    output_path = build_report(analysis_results, output_path=output)

    print("\n" + "=" * 50)
    print(f"✅  Report saved to: {Path(output_path).resolve()}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
