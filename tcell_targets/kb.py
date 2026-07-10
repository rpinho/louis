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
import re
from datetime import date
from pathlib import Path

KB_DIR = Path(__file__).resolve().parent.parent / "kb"


def _today() -> str:
    return date.today().isoformat()


def _safe(name: str) -> str:
    """Filename hygiene: ASCII only, no emoji/unicode/arrows."""
    return re.sub(r"\s+", " ", re.sub(r"[^A-Za-z0-9 ._-]", "", name)).strip()


def _target_path(gene: str) -> Path:
    return KB_DIR / "wiki" / "targets" / f"{_safe(gene)}.md"


def _disease_path(disease: str) -> Path:
    return KB_DIR / "wiki" / "diseases" / f"{_safe(disease)}.md"


def _ensure() -> None:
    for p in ("wiki/targets", "wiki/diseases", "wiki/modules", "raw"):
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
    for kind, path in (("target_profile", _target_path(entity)), ("disease_profile", _disease_path(entity))):
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
    line = f"- **{_today()}**{tag}: {finding.strip()}  — *source: {source.strip()}*\n"
    with path.open("a") as f:
        f.write(line)
    _append_log(f"remember {gene}{tag}: {finding[:80]}")
    _touch_index(gene)
    return {"gene": gene, "profile": str(path.relative_to(KB_DIR.parent)),
            "created_profile": created, "recorded": line.strip()}


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
