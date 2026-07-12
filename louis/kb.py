"""
Knowledge base — the tool's memory, in the personal-wiki shape.

Design mirrors a mature PKM: `raw/` (immutable evidence by source) + `wiki/`
(synthesized profiles by domain: diseases/ targets/ modules/) + index.md / log.md /
state.md. Principles carried over verbatim: FULL ROUTING (every finding goes to its
own specific profile, never a catch-all), PROVENANCE (cite the source + date),
RECALL BEFORE DERIVE (read the KB before re-computing), filename hygiene (ASCII only).

Everything is git-tracked markdown — so the KB is shareable: hand it to a student or a
lab, and it keeps what's known, what's novel, and the scientist's verdicts. This is how
the agent stops re-deriving the same thing every session.
"""
from __future__ import annotations
import json
import os
import re
from datetime import date
from pathlib import Path

# Default: the repo's kb/. Override with LOUIS_KB_DIR so a packaged bundle can write
# to a user-writable dir (an installed .mcpb dir may be read-only).
KB_DIR = Path(os.environ.get("LOUIS_KB_DIR") or (Path(__file__).resolve().parent.parent / "kb"))


def _today() -> str:
    return date.today().isoformat()


def _safe(name: str) -> str:
    """Filename hygiene: ASCII only, no emoji/unicode/arrows."""
    return re.sub(r"\s+", " ", re.sub(r"[^A-Za-z0-9 ._-]", "", name)).strip()


_DOI_RE = re.compile(r"(10\.\d{4,9}/[-._;()/:a-zA-Z0-9]+)")


def _linkify(text: str) -> str:
    """
    Provenance must be AUDITABLE: turn a bare DOI into a full, VISIBLE https://doi.org URL — not a
    markdown link (whose display text hides the URL and, in some file-preview panes, resolves the
    click as a local path). A raw URL is clickable in GitHub / chat / Slack and copy-pasteable
    everywhere, so an auditor always sees exactly where a citation points.
    """
    def repl(m):
        raw = m.group(1)
        doi = raw.rstrip(".,;)")
        trail = raw[len(doi):]
        pre = text[max(0, m.start() - 9):m.start()]
        if "doi.org/" in pre or pre.endswith("/"):   # already inside a URL
            return raw
        return f"https://doi.org/{doi}{trail}"
    return _DOI_RE.sub(repl, text)


def _target_path(gene: str) -> Path:
    return KB_DIR / "wiki" / "targets" / f"{_safe(gene)}.md"


def _disease_path(disease: str) -> Path:
    return KB_DIR / "wiki" / "diseases" / f"{_safe(disease)}.md"


def _topic_path(topic: str) -> Path:
    return KB_DIR / "wiki" / "topics" / f"{_safe(topic)}.md"


def _ensure() -> None:
    for p in ("wiki/targets", "wiki/diseases", "wiki/topics", "wiki/modules", "raw"):
        (KB_DIR / p).mkdir(parents=True, exist_ok=True)
    for f, header in (("index.md", "# KB index\n\nTarget profiles (one row per gene). Read this first.\n\n"),
                      ("log.md", "# Log\n\nAppend-only record of derivations, findings, and verdicts.\n\n"),
                      ("state.md", "# State\n\nOpen hypotheses under investigation and the current shortlist.\n\n")):
        p = KB_DIR / f
        if not p.exists():
            p.write_text(header)


def _append_log(msg: str) -> None:
    with (KB_DIR / "log.md").open("a") as f:
        f.write(f"- {_today()} — {msg}\n")


def _touch_index(gene: str) -> None:
    idx = KB_DIR / "index.md"
    txt = idx.read_text()
    rel = f"wiki/targets/{_safe(gene)}.md"
    if rel not in txt:
        with idx.open("a") as f:
            f.write(f"- [{gene}]({rel})\n")


def recall(entity: str) -> dict:
    """
    Read what the KB already knows about a target gene or a disease — BEFORE re-deriving it.
    Returns the stored profile(s), or a note that it's not in the KB yet.
    """
    _ensure()
    hits = {}
    for kind, path in (("target_profile", _target_path(entity)),
                       ("disease_profile", _disease_path(entity)),
                       ("topic_profile", _topic_path(entity))):
        if path.exists():
            hits[kind] = path.read_text()
    if not hits:
        return {"entity": entity, "known": False,
                "note": f"Nothing in the KB for {entity!r} yet. Derive it, then call kb_remember to file it."}
    return {"entity": entity, "known": True, **hits}


def remember(gene: str, finding: str, source: str, disease: str | None = None) -> dict:
    """
    Route a finding to the gene's target profile with provenance (full routing, no dumping).
    Creates the profile if new; updates the index + log.
    """
    _ensure()
    path = _target_path(gene)
    created = not path.exists()
    if created:
        path.write_text(
            f"# {gene}\n\n*CD4+ T-cell regulator — target profile. Data facts, novelty, "
            f"mechanism, and scientist verdicts, each with provenance.*\n\n## Findings\n\n")
    tag = f" ({disease})" if disease else ""
    line = f"- **{_today()}**{tag}: {_linkify(finding.strip())}  — *source: {_linkify(source.strip())}*\n"
    with path.open("a") as f:
        f.write(line)
    _append_log(f"remember {gene}{tag}: {finding[:80]}")
    _touch_index(gene)
    return {"gene": gene, "profile": str(path.relative_to(KB_DIR.parent)),
            "created_profile": created, "recorded": line.strip()}


def remember_signal(entity: str, posts: list[dict], query: str = "",
                    harvested: str = "", kind: str = "target", platform: str = "X/Twitter") -> dict:
    """
    File curated community (X/Twitter) chatter to an entity's profile under a dated
    'Community signal' block, with provenance (handle, date, link). Pre-paper signal —
    the field's current chatter, remembered so it ships even where live search can't run.
    `kind`: 'target' (a gene profile) or 'disease' (a disease profile).
    """
    _ensure()
    path = {"disease": _disease_path, "topic": _topic_path}.get(kind, _target_path)(entity)
    if not path.exists():
        if kind == "disease":
            path.write_text(f"# {entity}\n\n*Autoimmune disease profile — enriched T-cell programs, "
                            f"candidate targets, and community signal, each with provenance.*\n\n")
        elif kind == "topic":
            path.write_text(f"# {entity}\n\n*Immune pathway / mechanism — community signal, "
                            f"with provenance.*\n\n")
        else:
            remember(entity, "profile opened for community signal", "community_signal", None)
    when = harvested or _today()
    lines = [f"\n## Community signal ({platform}) — harvested {when}\n",
             f"*Query: `{query}`. Recent field chatter — pre-paper leads, not validated claims.*\n"]
    for p in posts:
        flag = " ⭐" if p.get("high_signal") else ""
        metric = f"♥{p.get('likes', 0)}"
        line = (f"- **@{p.get('handle', '?')}**{flag} ({p.get('author', '?')}) · "
                f"{p.get('date', '?')} · {metric}: {p.get('text', '')[:240]} "
                f"— {p.get('url', '')}")                          # raw, visible, copy-pasteable URL
        for lk in p.get("links", [])[:3]:      # expanded URLs the post points to (paper/lab/video)
            line += f" · {lk}"
        lines.append(line)
    with path.open("a") as f:
        f.write("\n".join(lines) + "\n")
    if kind == "target":
        _touch_index(entity)
    _append_log(f"community_signal {entity} ({kind}): filed {len(posts)} posts (harvested {when})")
    return {"entity": entity, "kind": kind, "profile": str(path.relative_to(KB_DIR.parent)),
            "filed": len(posts), "harvested": when}


def verdict(gene: str, disease: str, grade: str, rationale: str = "") -> dict:
    """
    Record the scientist's phone-a-friend verdict on a target — the reputation signal that
    accrues to the profile (e.g. 'put a student on it', 'probably wrong, skip').
    """
    _ensure()
    path = _target_path(gene)
    if not path.exists():
        remember(gene, "profile opened for a verdict", "scientist", disease)
    line = f"- **VERDICT {_today()}** ({disease}): **{grade}**{f' — {rationale.strip()}' if rationale else ''}\n"
    with path.open("a") as f:
        f.write(line)
    _append_log(f"verdict {gene} [{disease}]: {grade}")
    return {"gene": gene, "disease": disease, "grade": grade, "recorded": line.strip()}


# ── Fast retrieval index ──────────────────────────────────────────────────────
# recall() is already O(1) (a direct path lookup + file read). This index makes
# querying ACROSS the KB fast too — find profiles by name/attribute without reading
# every file. It's a *derived* artifact: the markdown stays the human-readable,
# git-diffable, shareable source of truth, and the index is cheaply rebuilt from it.
# At real scale (thousands of profiles + full-text search), swap this JSON index for
# SQLite FTS5 — same principle: markdown canonical, DB a rebuildable derived index.

def _index_path() -> Path:
    return KB_DIR / "_index.json"


def reindex() -> dict:
    """Scan the KB and (re)write kb/_index.json — a fast lookup of every profile + its attributes."""
    _ensure()
    entities = {}
    for kind, sub in (("target", "wiki/targets"), ("disease", "wiki/diseases"),
                      ("topic", "wiki/topics")):
        d = KB_DIR / sub
        if not d.exists():
            continue
        for f in sorted(d.glob("*.md")):
            txt = f.read_text()
            entities[f.stem] = {
                "kind": kind,
                "path": str(f.relative_to(KB_DIR)),
                "signal": "## Community signal" in txt,          # has baked community chatter
                "verdict": "**VERDICT" in txt,                    # has a scientist verdict
                "findings": txt.count("\n- **"),                  # rough richness (dated entries)
                "bytes": len(txt),
            }
    index = {"built": _today(), "n": len(entities), "entities": entities,
             "with_signal": sorted(k for k, v in entities.items() if v["signal"]),
             "with_verdict": sorted(k for k, v in entities.items() if v["verdict"])}
    _index_path().write_text(json.dumps(index, separators=(",", ":")))
    return index


def load_index(rebuild: bool = False) -> dict:
    """Return the KB index, building it if missing/unreadable (or when rebuild=True)."""
    p = _index_path()
    if rebuild or not p.exists():
        return reindex()
    try:
        return json.loads(p.read_text())
    except Exception:
        return reindex()


def search(term: str = "", kind: str | None = None, signal: bool | None = None,
           verdict: bool | None = None, content: bool = False, limit: int = 50) -> dict:
    """
    Fast query across the KB via the index. Matches entity names (and, with content=True, the
    profile text). Optionally filter by kind ('target'/'disease'), whether it carries community
    signal, or whether it has a verdict. Targets-with-signal-and-verdict sort first.
    """
    idx = load_index()
    term_l = term.lower().strip()
    hits = []
    for name, meta in idx.get("entities", {}).items():
        if kind and meta["kind"] != kind:
            continue
        if signal is not None and meta["signal"] != signal:
            continue
        if verdict is not None and meta["verdict"] != verdict:
            continue
        match = (not term_l) or (term_l in name.lower())
        if not match and content and term_l:
            try:
                match = term_l in (KB_DIR / meta["path"]).read_text().lower()
            except OSError:
                match = False
        if match:
            hits.append({"entity": name, **meta})
    hits.sort(key=lambda h: (h["kind"] != "target", not h["verdict"], not h["signal"],
                             -h["findings"], h["entity"]))
    return {"query": term, "n_total": len(hits), "results": hits[:limit]}
