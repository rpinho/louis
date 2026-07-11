"""
Community signal — the 'listen' layer (bleeding-edge, pre-paper).

Discover and validate tell you what the DATA and the LITERATURE say. This tells
you what the FIELD is saying *right now* — the chatter that isn't in a paper yet:
lab announcements, preprint drops, conference posts, therapy-pipeline news.

It searches X/Twitter for recent posts about a target gene or a disease in a
CD4+ T-cell / immunology context, via the `xurl` CLI running on the user's own
paid X API access (no key handled here — xurl holds the auth). Results are
curated (labs, journals, and news desks surfaced first) and can be filed into
the KB so the pre-paper signal is *remembered* — and ships with the tool even
where live search isn't available (e.g. the Claude Science sandbox has no xurl).

This is the layer Claude Science's paper/database connectors can't see.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from datetime import datetime
from urllib.parse import quote

# macOS GUI apps (Claude Desktop) launch with a minimal PATH that often omits Homebrew,
# so shutil.which("xurl") fails even when it's installed. Check the usual locations too.
_XURL_FALLBACKS = ("/opt/homebrew/bin/xurl", "/usr/local/bin/xurl",
                   os.path.expanduser("~/.local/bin/xurl"))


def _xurl_path() -> str | None:
    return shutil.which("xurl") or next((p for p in _XURL_FALLBACKS if os.path.exists(p)), None)

# Gene queries REQUIRE an immune/inflammation context. Gene symbols collide with other meanings
# (MEN1 = the endocrine-neoplasia syndrome; GLS = a stock ticker; ATM/REL = common words), and the
# immune guard drops those collisions (they carry no immune term) while keeping genuine immunology.
# Niche genes with no immune chatter in the 7-day window come back empty — honest, and better than junk.
_GENE_GUARD = ('(immune OR immunity OR immunolog OR "T cell" OR "T cells" OR CD4 OR CD8 OR Treg '
               'OR FOXP3 OR autoimmune OR autoimmunity OR lymphocyte OR inflammat OR cytokine '
               'OR Th17 OR tolerance)')

# Technical anchor for disease queries — terms the RESEARCH community uses but wellness
# influencers do not (a plain "<disease> immune" query is dominated by gut/detox/EMF noise).
_TECH_BASKET = ('(Treg OR FOXP3 OR Th17 OR "CD4 T" OR "single cell" OR scRNA OR CRISPR '
                'OR preprint OR GWAS OR "transcription factor" OR cytokine OR checkpoint)')

# Name/handle fragments that flag a lab, journal, or news desk — ranked first.
_SIGNAL_HINTS = ("lab", "journal", "news", "immun", "nature", "cell press", "cell ",
                 "science", "biorxiv", "medrxiv", "univ", "institute", "research",
                 "phd", "postdoc", ".edu")

# Research vocabulary — presence in the text marks a genuine science post (used to keep + rank).
_RESEARCH_TERMS = ("preprint", "biorxiv", "medrxiv", "single-cell", "single cell", "scrna",
                   "crispr", "foxp3", "cd4", "cd8", "th17", " th1", " th2", "treg",
                   "t cell", "t-cell", "regulatory t", "t follicular", "tfh", "cytokine",
                   "transcription factor", "gwas", "clinical trial", " ind ", "antibody",
                   "epigenetic", "methyltransferase", "rna-seq", "chip-seq", "immunity",
                   "immunol", "tolerance", "autoreactive", "checkpoint", "knockout",
                   "knockdown", "perturb", "receptor", "signaling", "il-2", "il-17",
                   "il-23", "jak", "stat3", "interferon")

# Wellness/pseudoscience vocabulary — a HARD veto unless the account is a research account.
_NOISE_TERMS = ("leaky gut", "gut lining", "seed oil", "detox", "toxin", "vagus", "emf",
                "cortisol hack", "manifest", "cleanse", "parasite", "supplement", "biohack",
                "root cause protocol", "heavy metals", "vitamin d", "vitamin k", "aluminum",
                "senolytic", "natural anti-inflammator", "micronutrient", "carnivore",
                "steak", "blueprint", "bryan johnson", "fluoride", "chemtrail", "raw milk")

# Accounts that are never research signal (AI bots / generic reply accounts) — vetoed outright.
_JUNK_HANDLES = {"grok", "askperplexity", "perplexity_ai", "chatgptbot", "grokinc"}


def xurl_available() -> bool:
    """True when the `xurl` CLI (the X API access) can be found — the live tier."""
    return _xurl_path() is not None


def _build_query(entity: str, kind: str) -> str:
    e = entity.strip()
    if kind == "disease":
        phrase = f'"{e}"' if " " in e else e
        # Technical anchor filters out the wellness/patient chatter that dominates a bare query.
        return f'{phrase} {_TECH_BASKET} lang:en -is:retweet'
    if kind == "drug":
        # Clinical/pipeline context — drug chatter is trial/FDA/efficacy language, not scRNA/CRISPR.
        return (f'{e} (trial OR phase OR FDA OR approval OR efficacy OR clinical OR inhibitor '
                f'OR autoimmune OR immune OR "T cell" OR Treg OR therapy OR indication) '
                f'lang:en -is:retweet')
    # gene/target: the symbol + a broad bio guard (gene symbols are already highly specific).
    return f'{e} {_GENE_GUARD} lang:en -is:retweet'


def _count(text: str, terms) -> int:
    t = text.lower()
    return sum(1 for k in terms if k in t)


def _is_research(post: dict) -> bool:
    """Keep a post if it comes from a research account OR uses research vocabulary."""
    return post["high_signal"] or _count(post["text"], _RESEARCH_TERMS) > 0


class RateLimited(RuntimeError):
    """X API returned 429 — the caller should back off (recent-search is ~60 req / 15 min on Basic)."""


def _run_search(query: str, max_results: int) -> dict:
    url = ("/2/tweets/search/recent?query=" + quote(query)
           + f"&max_results={max(10, min(max_results, 100))}"
           + "&tweet.fields=note_tweet,created_at,public_metrics,entities"
           + "&expansions=author_id&user.fields=username,name,verified")
    proc = subprocess.run([_xurl_path() or "xurl", url], capture_output=True, text=True, timeout=40)
    out, err = proc.stdout or "", proc.stderr or ""
    # Parse the body first — a valid data response is the common case. NEVER scan the JSON body
    # for "429": tweet/user IDs are ~19 digits and routinely contain that substring by chance,
    # which would misread real data as a rate limit (a bug that stalled the bulk harvest).
    try:
        d = json.loads(out) if out.strip() else None
    except json.JSONDecodeError:
        d = None
    rate_limited = ("Too Many Requests" in err or "rate limit" in err.lower()
                    or (isinstance(d, dict) and (d.get("status") == 429
                                                 or d.get("title") == "Too Many Requests")))
    if rate_limited:
        raise RateLimited("recent-search rate limit (429)")
    if d is None:
        raise RuntimeError(f"xurl: no JSON (exit {proc.returncode}): {(err or out)[:200]}")
    return d


def _signal_name(user: dict) -> bool:
    blob = (user.get("name", "") + " @" + user.get("username", "")).lower()
    return any(h in blob for h in _SIGNAL_HINTS)


def _score(text: str, user: dict, metrics: dict) -> float:
    # Engagement is CAPPED so a viral wellness post can't outrank a real lab's quiet one.
    eng = min(metrics.get("like_count", 0) + 2 * metrics.get("retweet_count", 0), 30)
    research = 12 * _count(text, _RESEARCH_TERMS)
    noise = _count(text, _NOISE_TERMS)
    penalty = 0 if _signal_name(user) else 40 * noise   # noise only forgiven for research accounts
    return research + eng + (35 if _signal_name(user) else 0) + (12 if user.get("verified") else 0) - penalty


def _post_links(t: dict) -> list:
    """Expanded (real) URLs a tweet points to — papers, labs, YouTube, Substack — minus X self-links."""
    urls = []
    for ent in (t.get("entities") or {}), ((t.get("note_tweet") or {}).get("entities") or {}):
        for u in ent.get("urls", []) or []:
            exp = u.get("expanded_url") or u.get("url") or ""
            if exp and not re.search(r"https?://(x\.com|twitter\.com|t\.co)/", exp):
                urls.append(exp.split("?")[0])   # drop tracking query params
    seen, out = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def _extract_posts(d: dict, min_engagement: int = 0) -> tuple[list, int]:
    """Parse a search response into scored post dicts (carrying _score/_research). Returns (posts, n_vetoed)."""
    users = {u["id"]: u for u in d.get("includes", {}).get("users", [])}
    posts, vetoed = [], 0
    for t in d.get("data", []):
        u = users.get(t.get("author_id"), {})
        m = t.get("public_metrics", {})
        if m.get("like_count", 0) + m.get("retweet_count", 0) < min_engagement:
            continue
        txt = ((t.get("note_tweet") or {}).get("text") or t.get("text", "")).replace("\n", " ").strip()
        signal = _signal_name(u)
        # HARD VETO: known-junk accounts (AI bots) never count, regardless of text.
        if u.get("username", "").lower() in _JUNK_HANDLES:
            vetoed += 1
            continue
        # HARD VETO: wellness/pseudoscience terms drop the post outright — unless it's a research account.
        if not signal and _count(txt, _NOISE_TERMS) > 0:
            vetoed += 1
            continue
        posts.append({
            "handle": u.get("username", "?"),
            "author": u.get("name", "?"),
            "date": (t.get("created_at", "") or "")[:10],
            "text": txt,
            "likes": m.get("like_count", 0),
            "retweets": m.get("retweet_count", 0),
            "url": f"https://x.com/{u.get('username', 'i')}/status/{t.get('id', '')}",
            "links": _post_links(t),                                    # expanded URLs to chase
            "high_signal": signal,
            "_score": _score(txt, u, m),
            "_research": signal or _count(txt, _RESEARCH_TERMS) >= 2,   # research account OR >=2 terms
        })
    return posts, vetoed


def _finalize(posts: list, top: int) -> list:
    """Sort by score, dedup near-identical text, keep only research posts, strip internal keys, trim."""
    posts = sorted(posts, key=lambda p: p["_score"], reverse=True)
    seen, deduped = set(), []
    for p in posts:
        key = "".join(p["text"].lower().split())[:90]   # reposts / same thread collapse
        if key in seen:
            continue
        seen.add(key)
        deduped.append(p)
    kept = [dict(p) for p in deduped if p["_research"]]   # research-only; empty is the honest answer
    for p in kept:
        p.pop("_score", None)
        p.pop("_research", None)
    return kept[:top]


def community_signal(entity: str, kind: str = "target", max_results: int = 25,
                     min_engagement: int = 0, top: int = 10) -> dict:
    """
    Recent X/Twitter chatter about a gene (`kind='target'`) or a disease
    (`kind='disease'`) in a T-cell/immunology context — curated, labs/journals first.

    Live tier only: needs the `xurl` CLI + X API auth (present in Claude Code / Desktop,
    absent in the Claude Science sandbox). When unavailable, returns a note pointing to
    the baked signal in the KB (kb_recall). Never raises — always returns a dict.
    """
    if not xurl_available():
        return {"entity": entity, "kind": kind, "available": False, "posts": [],
                "note": ("Live X search needs the `xurl` CLI + X API auth — present in "
                         "Claude Code/Desktop, not in the Claude Science sandbox. Read the "
                         "baked community signal from the KB via kb_recall instead.")}
    query = _build_query(entity, kind)
    try:
        d = _run_search(query, max_results)
    except RateLimited:  # surfaced as a flag so a bulk caller can back off
        return {"entity": entity, "kind": kind, "available": True, "posts": [],
                "query": query, "rate_limited": True, "error": "recent-search rate limit (429)"}
    except Exception as e:  # network / auth — degrade, don't crash
        return {"entity": entity, "kind": kind, "available": True, "posts": [],
                "query": query, "error": str(e)}
    if "data" not in d:
        detail = d.get("detail") or d.get("title") or (d.get("errors") or [{}])[0].get("message", "")
        return {"entity": entity, "kind": kind, "available": True, "posts": [],
                "query": query, "note": f"no results ({detail or 'empty'})"}

    posts, vetoed = _extract_posts(d, min_engagement)
    kept = _finalize(posts, top)
    return {"entity": entity, "kind": kind, "available": True, "query": query,
            "harvested": datetime.now().strftime("%Y-%m-%d"),
            "n_matched": len(posts), "n_vetoed_noise": vetoed, "posts": kept}


def search_batch(genes: list, kind: str = "target", max_results: int = 100,
                 min_engagement: int = 0) -> dict:
    """
    OR-batched search for many gene symbols in ONE call — the rate-limit-friendly path for the
    bulk harvest. Builds `(GENE1 OR GENE2 OR …) <immune guard>` and returns the raw scored posts
    (carrying _score/_research) for the caller to attribute back to individual genes. Never raises.
    """
    if not xurl_available():
        return {"available": False, "posts": [], "note": "xurl unavailable"}
    guard = _GENE_GUARD if kind == "target" else _TECH_BASKET
    query = f"({' OR '.join(g.strip() for g in genes)}) {guard} lang:en -is:retweet"
    try:
        d = _run_search(query, max_results)
    except RateLimited:
        return {"available": True, "posts": [], "query": query, "rate_limited": True}
    except Exception as e:
        return {"available": True, "posts": [], "query": query, "error": str(e)}
    if "data" not in d:
        return {"available": True, "posts": [], "query": query, "note": "empty"}
    posts, vetoed = _extract_posts(d, min_engagement)
    return {"available": True, "query": query, "posts": posts, "n_vetoed_noise": vetoed,
            "harvested": datetime.now().strftime("%Y-%m-%d"),
            "result_count": len(d.get("data", []))}
