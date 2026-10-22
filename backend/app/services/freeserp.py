"""FreeSerp client: a few real, live websites in the user's niche, as inspiration.

Docs: https://freeserp.ai/docs.php. Free, no key. Rules here:
- we ask for a pool of candidates and keep the first 6 that pass the filters
  (real business site, readable title, no adult/gambling/cannabis, no directories);
- 5 s timeout; any error, timeout or bad response -> empty list (logged), never an exception;
- in-memory cache per query: 1 hour for results, 1 minute after a failure
  (so a FreeSerp outage doesn't make every page view wait for the timeout).
The cache lives in each uvicorn worker process, so with 2 workers FreeSerp sees
at most 2 requests per query per hour.
"""

import logging
import os
import re
import time

import httpx

log = logging.getLogger("launchwise.freeserp")

API_URL = os.environ.get("FREESERP_URL", "https://freeserp.ai/api.php")
# FreeSerp needs no API key. Set FREESERP_ENABLED=false to skip it (e.g. offline): examples are then empty.
ENABLED = os.environ.get("FREESERP_ENABLED", "true").strip().lower() not in ("0", "false", "no", "off")
TIMEOUT_S = 5.0
CACHE_TTL_S = 3600
FAILURE_TTL_S = 60
RESULT_SIZE = 6       # how many examples we return
CANDIDATES = 20       # how many we ask FreeSerp for, before filtering
SUMMARY_MAX = 160

# Specific multi-word queries: single words like "restaurant" match exact domains
# (restaurant.com, a deals platform) instead of real businesses.
QUERY_BY_BUSINESS = {
    "coffee_shop": "coffee shop cafe",
    "restaurant": "restaurant menu reservations",
    "beauty_salon": "beauty salon hair nails",
    "online_store": "online shop handmade gifts",
    "local_services": "local handyman home repair services",
    "freelancer": "freelance web designer portfolio",
    "consulting": "business consulting firm",
}

# Never show these as "inspiration" (whole words in domain, title or summary).
BLOCKED_WORDS = re.compile(r"\b(adult|sex|porn|escort|casino|betting|gambling|cannabis|cbd|thc|vape)\b", re.I)
# Summaries that mean the crawler didn't see the real site, or the site is a directory, not a business.
JUNK_SUMMARY = re.compile(r"verif|parked|blocking access|basic html structure|cloudflare|for sale|directory", re.I)

# query -> (expires_at, items)
_cache: dict[str, tuple[float, list[dict]]] = {}


def _shorten(text: str, limit: int = SUMMARY_MAX) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(",.;:") + "…"


def _mostly_latin(text: str) -> bool:
    letters = [ch for ch in text if ch.isalpha()]
    return not letters or sum(ord(ch) <= 0x24F for ch in letters) / len(letters) >= 0.7


def _clean(raw: dict) -> dict | None:
    """Keep only the fields we show; None = drop this result."""
    title = (raw.get("title") or "").strip()
    if not title:
        return None
    if "http_status" in raw and str(raw["http_status"]) != "200":
        return None
    domain = raw.get("domain") or ""
    summary = raw.get("ai_summary") or ""
    if raw.get("category") == "betting/casino" or BLOCKED_WORDS.search(f"{domain} {title} {summary}"):
        return None
    if JUNK_SUMMARY.search(summary) or not _mostly_latin(title):
        return None
    dr = raw.get("dr")
    return {
        "domain": domain,
        "url": raw.get("url") or f"https://{domain}",
        "title": _shorten(title, 100),
        "summary": _shorten(summary),
        "dr": int(dr) if dr not in (None, "", "None") else None,
    }


def _fetch(query: str) -> list[dict] | None:
    """Call FreeSerp. Returns None on any failure."""
    params = {"q": query, "size": CANDIDATES, "sort": "relevance",
              "agent": "LaunchWise/1.0", "project": "LaunchWise"}
    try:
        response = httpx.get(API_URL, params=params, timeout=TIMEOUT_S)
        response.raise_for_status()
        data = response.json()
        if not data.get("ok"):
            raise ValueError(f"FreeSerp returned ok=false: {data.get('error')}")
        return [item for item in map(_clean, data.get("results") or []) if item][:RESULT_SIZE]
    except Exception as exc:  # network, timeout, HTTP error, bad JSON: all mean "no examples"
        log.warning("FreeSerp request failed for %r: %s", query, exc)
        return None


def get_examples(business_type: str) -> tuple[list[dict], bool]:
    """Return (items, cached). Never raises."""
    if not ENABLED:
        return [], False
    query = QUERY_BY_BUSINESS[business_type]
    now = time.monotonic()
    hit = _cache.get(query)
    if hit and hit[0] > now:
        return hit[1], True

    items = _fetch(query)
    if items is None:
        _cache[query] = (now + FAILURE_TTL_S, [])
        return [], False
    _cache[query] = (now + CACHE_TTL_S, items)
    return items, False
