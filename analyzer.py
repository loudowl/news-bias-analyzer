"""
LLM-based analysis of news headlines per outlet.
Uses OpenAI to score each outlet on sentiment, ideological lean,
topic coverage, and framing patterns.
"""

import json
from openai import OpenAI
from typing import Dict, List

SYSTEM_PROMPT = """You are a computational media analysis tool.
Your job is to objectively characterize the LANGUAGE PATTERNS, SENTIMENT, and FRAMING
of news headlines — not to validate or challenge the politics of any outlet.
Focus entirely on what the text shows: word choice, tone, topic selection, and rhetorical framing.
Be rigorous, specific, and neutral in your own language."""

ANALYSIS_PROMPT = """Analyze the following headlines and descriptions from {source_name}.
These are the top stories currently on their front page.

---
{content}
---

Return ONLY a valid JSON object with these fields. No markdown, no explanation — just the JSON.

{{
  "sentiment_score": <float -1.0 to 1.0, where -1 = very negative, 0 = neutral, 1 = very positive>,
  "emotional_intensity": <float 0 to 10, where 0 = dry/factual, 10 = highly charged>,
  "ideological_lean_score": <float -5.0 to 5.0, where -5 = far left, 0 = center, 5 = far right — based solely on language patterns and topic framing, not presumed outlet reputation>,
  "ideological_lean_label": <one of: "Far Left", "Left", "Center-Left", "Center", "Center-Right", "Right", "Far Right">,
  "ideological_lean_reasoning": <1-2 sentences explaining the score based specifically on language evidence from these headlines>,
  "top_topics": <list of 5-7 strings naming the main subjects covered>,
  "framing_patterns": <list of 3-5 strings describing notable rhetorical or framing choices observed>,
  "distinctive_language": <list of 5-10 words or short phrases that stand out as characteristic of this outlet's voice today>,
  "notable_omissions": <string: mention any major ongoing story that appears absent from this front page, or "none apparent">,
  "one_line_summary": <string: one sentence characterizing the overall editorial tone and focus of this front page today>
}}"""


def analyze_source(
    source_name: str,
    content: str,
    client: OpenAI,
    model: str = "gpt-4o",
) -> Dict:
    """Send headlines to the LLM and return structured analysis."""
    prompt = ANALYSIS_PROMPT.format(source_name=source_name, content=content)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,  # low temp for consistent, analytical output
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"    ⚠️  JSON parse error for {source_name}: {e}")
        return _empty_result(source_name)
    except Exception as e:
        print(f"    ⚠️  LLM error for {source_name}: {e}")
        return _empty_result(source_name)


def analyze_all(
    source_data: Dict[str, Dict],  # {source_id: {name, content}}
    client: OpenAI,
    model: str = "gpt-4o",
) -> Dict[str, Dict]:
    """Run analysis for all sources. Returns {source_id: analysis_result}."""
    results = {}
    total = len(source_data)
    for i, (sid, data) in enumerate(source_data.items(), 1):
        name = data["name"]
        content = data["content"]
        print(f"  [{i}/{total}] Analysing {name}...", end=" ")
        if not content or content == "(no articles retrieved)":
            print("skipped (no content)")
            results[sid] = _empty_result(name)
        else:
            result = analyze_source(name, content, client, model)
            result["source_name"] = name
            result["article_count"] = data.get("article_count", 0)
            results[sid] = result
            lean = result.get("ideological_lean_label", "?")
            sentiment = result.get("sentiment_score", 0)
            print(f"lean={lean}, sentiment={sentiment:+.2f}")
    return results


def _empty_result(source_name: str) -> Dict:
    return {
        "source_name": source_name,
        "sentiment_score": 0.0,
        "emotional_intensity": 0.0,
        "ideological_lean_score": 0.0,
        "ideological_lean_label": "Unknown",
        "ideological_lean_reasoning": "No data available.",
        "top_topics": [],
        "framing_patterns": [],
        "distinctive_language": [],
        "notable_omissions": "N/A",
        "one_line_summary": "No data available.",
        "article_count": 0,
        "error": True,
    }
