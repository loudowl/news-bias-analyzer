"""
Fetches top headlines from NewsAPI for each configured source.
Docs: https://newsapi.org/docs/endpoints/top-headlines
"""

import time
import requests
from typing import Dict, List


NEWSAPI_URL = "https://newsapi.org/v2/top-headlines"


def fetch_source(source_id: str, api_key: str, page_size: int = 20) -> List[Dict]:
    """Fetch top headlines for a single source. Returns list of article dicts."""
    params = {
        "sources": source_id,
        "apiKey": api_key,
        "pageSize": page_size,
    }
    try:
        resp = requests.get(NEWSAPI_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != "ok":
            print(f"    ⚠️  API error for {source_id}: {data.get('message', 'unknown')}")
            return []
        return data.get("articles", [])
    except requests.RequestException as e:
        print(f"    ⚠️  Request failed for {source_id}: {e}")
        return []


def fetch_all(sources: List[Dict], api_key: str, delay: float = 0.3) -> Dict[str, List[Dict]]:
    """
    Fetch headlines for all sources.
    Returns dict of {source_id: [articles]}.
    Adds a small delay between requests to be polite to the API.
    """
    results = {}
    total = len(sources)
    for i, source in enumerate(sources, 1):
        sid = source["id"]
        name = source["name"]
        print(f"  [{i}/{total}] Fetching {name}...", end=" ")
        articles = fetch_source(sid, api_key)
        results[sid] = articles
        print(f"{len(articles)} articles")
        if i < total:
            time.sleep(delay)
    return results


def format_for_analysis(articles: List[Dict]) -> str:
    """Format articles into a plain-text block suitable for LLM analysis."""
    lines = []
    for i, a in enumerate(articles, 1):
        title = a.get("title") or ""
        description = a.get("description") or ""
        if title:
            lines.append(f"{i}. HEADLINE: {title}")
        if description:
            lines.append(f"   DESC: {description}")
    return "\n".join(lines) if lines else "(no articles retrieved)"
