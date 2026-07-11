"""
Follow the links — turn a tweet pointer into the thing it points to.

Community posts carry expanded URLs (papers, labs, preprints, articles, videos).
This module chases them: resolves shorteners, classifies the target, and pulls the
content — a paper's title+abstract via Europe PMC (which indexes published papers AND
bioRxiv/medRxiv PREPRINTS, so it reaches pre-paper work), or a page's title+description
otherwise. The result is filed back so the KB holds not just "a lab tweeted about DNMT3A"
but the actual finding behind it. Mirrors the bookmark-ingest chase-the-pointer pipeline.

Pure stdlib (urllib) — no extra deps, works in the skill sandbox where network is allowed.
"""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from urllib.error import URLError

_UA = {"User-Agent": "tcell-target-explorer/0.3 (research; contact via github.com/rpinho)"}
_EUROPEPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


def _get(url: str, timeout: int = 12) -> tuple[str, str]:
    """GET a URL following redirects. Returns (final_url, body_text). Empty body on failure."""
    try:
        req = urllib.request.Request(url, headers=_UA)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            final = r.geturl()
            body = r.read(400_000).decode("utf-8", "ignore")
            return final, body
    except (URLError, ValueError, OSError, Exception):
        return url, ""


def resolve(url: str, timeout: int = 8) -> str:
    """Follow shortener redirects (bit.ly, t.co, doi.org) to the final URL."""
    if not re.search(r"(bit\.ly|t\.co|ow\.ly|buff\.ly|tinyurl|doi\.org|dlvr\.it|hubs\.)", url):
        return url
    final, _ = _get(url, timeout=timeout)
    return final or url


def classify(url: str) -> str:
    u = url.lower()
    if re.search(r"(doi\.org|pubmed|ncbi\.nlm|biorxiv|medrxiv|nature\.com/articles|"
                 r"sciencedirect|cell\.com|/articles/|link\.springer|wiley|/abstract|/full/10\.)", u):
        return "paper"
    if re.search(r"(youtube\.com|youtu\.be)", u):
        return "video"
    if re.search(r"(substack\.com|medium\.com|/blog/|\.blog)", u):
        return "article"
    if re.search(r"(\.edu|lab\.|/lab/|/labs/|institute|university)", u):
        return "lab"
    return "page"


def _doi_from(url: str) -> str | None:
    """Best-effort DOI extraction from a URL, incl. publisher-specific patterns."""
    m = re.search(r"doi\.org/(10\.\d{4,}/\S+)", url) or re.search(r"(10\.\d{4,}/[^\s?&#]+)", url)
    if m:
        return m.group(1).rstrip(".)")
    m = re.search(r"nature\.com/articles/([a-z0-9\-]+)", url, re.I)
    if m:
        return f"10.1038/{m.group(1)}"
    m = re.search(r"(biorxiv|medrxiv)\.org/content/(10\.1101/[0-9.]+)", url, re.I)
    if m:
        return m.group(2)
    return None


def _europepmc(query: str) -> dict | None:
    final, body = _get(f"{_EUROPEPMC}?query={urllib.parse.quote(query)}"
                       f"&format=json&resultType=core&pageSize=1")
    if not body:
        return None
    try:
        res = json.loads(body).get("resultList", {}).get("result", [])
    except json.JSONDecodeError:
        return None
    if not res:
        return None
    r = res[0]
    return {
        "title": r.get("title", "").strip(),
        "abstract": (r.get("abstractText") or "").replace("\n", " ").strip(),
        "authors": r.get("authorString", ""),
        "journal": (r.get("journalInfo", {}) or {}).get("journal", {}).get("title", "")
                   or r.get("bookOrReportDetails", {}).get("publisher", ""),
        "year": r.get("pubYear", ""),
        "is_preprint": r.get("source") == "PPR" or "preprint" in (r.get("pubType", "") or "").lower(),
        "doi": r.get("doi", ""),
    }


def fetch_paper(url: str) -> dict | None:
    """Title + abstract for a paper/preprint URL, via Europe PMC (published + bioRxiv/medRxiv)."""
    doi = _doi_from(url)
    meta = _europepmc(f'DOI:"{doi}"') if doi else None
    if not meta or not meta.get("abstract"):
        # fall back to the page <title> so we at least know what it is
        title = _page_title(url)
        if title:
            meta = (meta or {}) | {"title": meta.get("title") if meta else title or title,
                                   "title_fallback": title}
    return meta


def _page_title(url: str) -> str:
    _, body = _get(url)
    if not body:
        return ""
    t = re.search(r"<title[^>]*>(.*?)</title>", body, re.I | re.S)
    d = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', body, re.I)
    title = re.sub(r"\s+", " ", (t.group(1) if t else "")).strip()[:200]
    desc = re.sub(r"\s+", " ", (d.group(1) if d else "")).strip()[:280]
    return (title + (" — " + desc if desc else "")).strip(" —")


def follow_link(url: str) -> dict:
    """Chase one link. Returns {url, final_url, type, title, abstract?, authors?, is_preprint?}."""
    final = resolve(url)
    kind = classify(final)
    out = {"url": url, "final_url": final, "type": kind}
    if kind == "paper":
        p = fetch_paper(final)
        if p:
            out.update({k: v for k, v in p.items() if v})
    else:
        title = _page_title(final)
        if title:
            out["title"] = title
    return out
