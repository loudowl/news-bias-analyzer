#!/usr/bin/env python3
"""
serve.py — run the web server + scheduler together.

    python serve.py                   # default: port 8080, runs at 8:00 / 12:00 / 17:00
    python serve.py --port 3000
    python serve.py --times 7,13,18   # override schedule hours
"""

import argparse
import subprocess
import sys
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler

from server import app

BASE = Path(__file__).parent


def _run_analysis():
    print("\n⏰  Running scheduled analysis...", flush=True)
    result = subprocess.run([sys.executable, str(BASE / "main.py")])
    if result.returncode != 0:
        print("❌  Scheduled analysis failed.", flush=True)
    else:
        print("✅  Scheduled analysis complete.", flush=True)


def main():
    parser = argparse.ArgumentParser(description="News Bias Analyzer — web server + scheduler")
    parser.add_argument("--port", type=int, default=8080, help="HTTP port (default: 8080)")
    parser.add_argument("--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0)")
    parser.add_argument(
        "--times", default="8,12,17",
        help="Comma-separated hours (24h) to run analysis (default: 8,12,17)",
    )
    args = parser.parse_args()

    hours = [int(h.strip()) for h in args.times.split(",")]

    scheduler = BackgroundScheduler()
    for h in hours:
        scheduler.add_job(_run_analysis, "cron", hour=h, minute=0)
    scheduler.start()

    schedule_str = "  ".join(f"{h:02d}:00" for h in sorted(hours))
    print(f"⏰  Scheduler active — analysis runs at: {schedule_str}")
    print(f"🌐  Web server → http://localhost:{args.port}")
    print("    Ctrl+C to stop.\n")

    try:
        app.run(host=args.host, port=args.port, debug=False)
    finally:
        scheduler.shutdown()


if __name__ == "__main__":
    main()
