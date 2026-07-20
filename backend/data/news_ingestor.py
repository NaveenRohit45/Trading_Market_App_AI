"""
Automated News Ingestion

Replaces "manually type in headlines" with real, automatic ingestion
from free financial RSS feeds (no paid news API key required). Runs
on a slow cadence (same as predictions/options -- these are not
cheap or fast-changing enough to poll every 3 seconds).

Sentiment scoring here is intentionally simple: keyword-based, not a
trained model. This is a reasonable starting point, not a claim of
accuracy -- like every other brain in this system, its real value
will be judged by the Adaptive Confidence Engine's tracked accuracy
once enough news-influenced predictions have resolved, not by how
sophisticated the scoring sounds.

HONEST LIMITATION: RSS feeds can go down, change format, or get
rate-limited without warning. This fails safe -- a feed failure is
logged and skipped, never crashes the caller.
"""

from __future__ import annotations

import feedparser

FEEDS = [
    "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "https://www.moneycontrol.com/rss/marketreports.xml",
    "https://www.livemint.com/rss/markets",
]

# Simple keyword-based sentiment -- deliberately transparent/inspectable
# rather than a black box. Tune this list based on what you observe.
POSITIVE_WORDS = [
    "rally", "surge", "gain", "gains", "jump", "jumps", "soar", "soars",
    "record high", "bullish", "upbeat", "rebound", "recovery", "boost",
    "outperform", "upgrade", "beat estimates", "strong growth",
]

NEGATIVE_WORDS = [
    "fall", "falls", "plunge", "plunges", "crash", "slump", "slumps",
    "decline", "declines", "bearish", "sell-off", "selloff", "drop",
    "drops", "downgrade", "recession", "weak", "loss", "losses", "correction",
]


def _score_sentiment(headline: str) -> str:
    text = headline.lower()

    pos_hits = sum(1 for w in POSITIVE_WORDS if w in text)
    neg_hits = sum(1 for w in NEGATIVE_WORDS if w in text)

    if pos_hits > neg_hits:
        return "positive"
    if neg_hits > pos_hits:
        return "negative"
    return "neutral"


class AutoNewsIngestor:

    def __init__(self):
        self._seen_headlines = set()

    def fetch_new_items(self, max_per_feed: int = 5) -> list[dict]:
        """
        Returns a list of {"headline", "sentiment", "impact", "source"}
        dicts for headlines not seen before. Safe to call repeatedly --
        dedupes automatically, never raises.
        """

        new_items = []

        for feed_url in FEEDS:
            try:
                parsed = feedparser.parse(feed_url)
            except Exception as error:
                print(f"⚠️ Failed to fetch news feed {feed_url}: {error}")
                continue

            if not getattr(parsed, "entries", None):
                continue

            source_name = feed_url.split("//")[1].split("/")[0]

            for entry in parsed.entries[:max_per_feed]:
                headline = getattr(entry, "title", "").strip()

                if not headline or headline in self._seen_headlines:
                    continue

                self._seen_headlines.add(headline)

                new_items.append({
                    "headline": headline,
                    "sentiment": _score_sentiment(headline),
                    "impact": 0.6,  # moderate default -- auto-ingested, not manually curated
                    "source": f"auto:{source_name}",
                })

        # Keep the seen-set from growing unbounded over a long-running process.
        if len(self._seen_headlines) > 2000:
            self._seen_headlines = set(list(self._seen_headlines)[-1000:])

        return new_items
