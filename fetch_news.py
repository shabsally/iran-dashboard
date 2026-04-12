#!/usr/bin/env python3
"""
fetch_news.py
-------------
Calls the Anthropic API with web search enabled, asks Claude to find the
latest Iran conflict news, and writes the results to docs/news.json.

Run locally:   ANTHROPIC_API_KEY=sk-... python fetch_news.py
Run in CI:     triggered by GitHub Actions (see .github/workflows/refresh-news.yml)
"""

import anthropic
import json
import os
import re
import sys
from datetime import datetime, timezone

# ── Config ────────────────────────────────────────────────────────────────────

OUTPUT_FILE = "docs/news.json"
MODEL       = "claude-opus-4-6"   # use Opus for best search + reasoning
MAX_TOKENS  = 2048

TODAY = datetime.now(timezone.utc).strftime("%B %d, %Y")

SYSTEM_PROMPT = f"""You are a geopolitical intelligence analyst specialising in the Middle East.
Today is {TODAY} (UTC). Your job is to search the web for the latest news about the
2026 Iran conflict and return a structured JSON array.

IMPORTANT: Return ONLY a raw JSON array — no preamble, no markdown fences, no explanation.
The array must contain exactly 8 objects, each with these fields:

{{
  "headline":  "string, max 110 chars",
  "summary":   "string, 2–3 factual sentences, regional focus preferred over US-centric framing",
  "source":    "string, publication name",
  "url":       "string, full URL or empty string",
  "date":      "string, e.g. 12 Apr 2026",
  "tag":       "one of: diplomacy | military | economic | humanitarian | nuclear",
  "region":    "one of: iran | lebanon | gulf | international | humanitarian",
  "scenarios": ["1–3 items from: Negotiated peace deal | Frozen conflict | Renewed escalation | Regime collapse | Nuclear breakout risk | Extended ceasefire"],
  "isNew":     true
}}

Prioritise:
- Regional impact (Lebanon, Gulf states, Iran internally, international reactions)
- Humanitarian consequences
- Economic effects (Hormuz, energy, shipping)
- Avoid defaulting to US political framing as the primary lens
"""

USER_PROMPT = (
    f"Search for the 8 most important Iran conflict news stories from today or yesterday "
    f"({TODAY}, UK time). Focus on regional and humanitarian angles — Lebanon, Gulf states, "
    f"Iran internally, and international reactions — rather than US political angles. "
    f"Return only the raw JSON array."
)

# ── Main ──────────────────────────────────────────────────────────────────────

def fetch_news() -> list[dict]:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    print(f"[{datetime.now(timezone.utc).isoformat()}] Calling Claude API with web search…")

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": USER_PROMPT}],
    )

    # Extract all text blocks from the response
    full_text = "\n".join(
        block.text for block in response.content if block.type == "text"
    )

    print(f"[{datetime.now(timezone.utc).isoformat()}] Response received. Parsing JSON…")

    # Strip any accidental markdown fences
    clean = re.sub(r"```(?:json)?", "", full_text).strip()

    # Find the JSON array
    match = re.search(r"\[[\s\S]*\]", clean)
    if not match:
        print("ERROR: No JSON array found in response.", file=sys.stderr)
        print("Raw response:", full_text[:500], file=sys.stderr)
        sys.exit(1)

    articles = json.loads(match.group(0))

    if not isinstance(articles, list) or len(articles) == 0:
        print("ERROR: Parsed result is empty or not a list.", file=sys.stderr)
        sys.exit(1)

    print(f"[{datetime.now(timezone.utc).isoformat()}] Parsed {len(articles)} articles.")
    return articles


def write_output(articles: list[dict]) -> None:
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    payload = {
        "fetchedAt":  datetime.now(timezone.utc).isoformat(),
        "fetchedOn":  datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "articleCount": len(articles),
        "articles": articles,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"[{datetime.now(timezone.utc).isoformat()}] Written to {OUTPUT_FILE}")


if __name__ == "__main__":
    articles = fetch_news()
    write_output(articles)
    print("Done.")
