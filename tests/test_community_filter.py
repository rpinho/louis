#!/usr/bin/env python3
"""Regression test for the community-signal keep-gate (X + Bluesky harvests).

The bug this guards against: a post from an account whose *name* contained a generic substring
("…Labs", "…News", "…Wire", "…Research") was kept as research signal even when the post itself
was crypto/finance/off-topic — because `_signal_name` alone satisfied the keep gate. That injected
$ticker spam, crypto shills, and off-topic feeds into the KB (had to be scrubbed by hand).

The fix: both live paths now require `_on_topic()` — the post must READ as immunology/disease/method
AND not be finance chatter — the same gate the baked fallback already used. A lab-sounding handle is
no longer sufficient. This test feeds the exact junk shapes that got through before (from lab-*named*
accounts, so they'd pass the old filter) and asserts they're dropped, while real lab posts survive.

Run:  .venv/bin/python tests/test_community_filter.py       (or: python -m pytest tests/)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from louis import community, harvest  # noqa: E402


def _x_response(cases):
    """Build a minimal X recent-search response from (handle, name, text) tuples."""
    users, data = [], []
    for i, (handle, name, text) in enumerate(cases):
        uid = str(1000 + i)
        users.append({"id": uid, "username": handle, "name": name, "verified": False})
        data.append({"author_id": uid, "id": str(9000 + i), "created_at": "2026-07-12T00:00:00Z",
                     "text": text, "public_metrics": {"like_count": 20, "retweet_count": 3}})
    return {"data": data, "includes": {"users": users}}


# (handle, name, text, should_keep) — junk cases use lab/news/wire NAMES so they passed the OLD gate.
CASES = [
    # --- real research signal (KEEP) ---
    ("MarsonLab", "Marson Lab",
     "New preprint: DOT1L restrains Treg identity via H3K79 methylation in CD4 T cells. bioRxiv →", True),
    ("jdoe_phd", "Jane Doe, PhD",
     "Our CRISPRi screen nominates HDAC7 as a colitis Treg regulator — single-cell data in the thread", True),
    # --- the bug: off-topic posts from LAB/NEWS/WIRE-named accounts (KEEP under old gate, DROP now) ---
    ("539Labs", "539 Labs",
     "$SOL call wall at 200, expected move is massive this week 🚀", False),           # crypto + cashtag
    ("DailyBioNews", "Daily Bio News",
     "Premarket: $NVDA intraday analysis, short interest rising", False),             # finance desk-speak
    ("CryptoLabsHQ", "Crypto Labs",
     "our token pumps immunity to dips lol, $DOGE to the moon", False),               # cashtag beats stray "immunity"
    ("AILabsWire", "AI Labs Wire",
     "Our new LLM benchmark crushes GPT-5 on reasoning evals", False),                # pure off-topic, lab-named
    # --- wellness junk (already vetoed; keep it dropped) ---
    ("WelloraHealth", "Wellora Health",
     "Take our detox quiz! Boost immunity naturally with our gut cleanse protocol", False),
    ("FarmersTrend", "Farmers Trend",
     "GLS fertilizer boosts crop yield this planting season", False),                 # gene symbol, wrong domain
]


def test_x_harvest_gate():
    d = _x_response([(h, n, t) for h, n, t, _ in CASES])
    posts, _ = community._extract_posts(d)
    kept = {p["handle"] for p in community._finalize(posts, top=20)}
    _assert_gate(kept, "X")


def test_bluesky_harvest_gate():
    posts = [{"handle": h, "author": n, "text": t, "likes": 20} for h, n, t, _ in CASES]
    kept = {p["handle"] for p in harvest._bsky_filter(posts, per_top=20)}
    _assert_gate(kept, "Bluesky")


def _assert_gate(kept, label):
    want = {h for h, _, _, keep in CASES if keep}
    junk = {h for h, _, _, keep in CASES if not keep}
    leaked = kept & junk
    dropped_good = want - kept
    assert not leaked, f"[{label}] junk leaked through the gate: {sorted(leaked)}"
    assert not dropped_good, f"[{label}] real research posts were dropped: {sorted(dropped_good)}"
    print(f"  [{label}] OK — kept {sorted(kept)}; vetoed all {len(junk)} junk cases")


def test_on_topic_unit():
    assert community._on_topic("DOT1L in CD4 Treg cells, new preprint")
    assert not community._on_topic("$SOL call wall, expected move huge")   # finance
    assert not community._on_topic("our new LLM benchmark on reasoning")   # off-topic
    print("  [unit] _on_topic OK")


if __name__ == "__main__":
    test_on_topic_unit()
    test_x_harvest_gate()
    test_bluesky_harvest_gate()
    print("\n✓ all community-filter regression tests passed")
