#!/usr/bin/env python3
"""
Build a derived SQLite index over the markdown knowledge base — the fast, dimensional
retrieval layer. The markdown under kb/ stays the human-readable, git-tracked source of
truth; this index is regenerable at any time (like the skill zip) and never authoritative.

It flattens every KB record (finding / verdict / community post / preprint / conference /
lit-scan) into one row with the DIMENSIONS a scientist slices by — gene, disease,
record type, grade, activation state, source tier, date, url — plus an FTS5 full-text
index over the record text. That lets Louis answer questions grep-over-markdown can't:
"all grade-A druggable leads in whitespace", "everything epigenetic across diseases",
"who's active on DOT1L", "resting-state handles for lupus".

    python -m scripts.build_kb_index          # writes kb/index.sqlite
"""
from __future__ import annotations
import os
import re
import sqlite3
from pathlib import Path

KB_DIR = Path(os.environ.get("TCELL_KB_DIR") or (Path(__file__).resolve().parent.parent / "kb"))
DB_PATH = KB_DIR / "index.sqlite"

_DATE = re.compile(r"\*\*(?:VERDICT\s+)?(\d{4}-\d{2}-\d{2})\*\*")
_DISEASE = re.compile(r"\*\*(?:VERDICT\s+)?\d{4}-\d{2}-\d{2}\*\*\s*\(([^)]+)\):")
_VERDICT_GRADE = re.compile(r"\):\s*\*\*([A-D][+-]?)\*\*")
_SCAN_GRADE = re.compile(r"grade\s+([A-D][+-]?)", re.I)
_STATE = re.compile(r"\b(Rest|Stim8hr|Stim48hr|resting[- ]state|activation-induced|activation-modulated|constitutive)\b", re.I)
_URL = re.compile(r"(https?://[^\s)]+)")


def _rec_type(line: str, text: str) -> str:
    if line.startswith("- **VERDICT"):
        return "verdict"
    if line.startswith("- **@"):
        return "community_post"
    if "AUTOMATED LIT-SCAN" in text:
        return "lit_scan"
    if "CONFERENCE ABSTRACT" in text:
        return "conference"
    if "PREPRINT" in text.upper():
        return "preprint"
    return "finding"


def _source_tier(text: str, source: str, rec_type: str) -> str:
    blob = (text + " " + source).lower()
    if rec_type == "verdict":
        return "verdict"
    if rec_type == "lit_scan":
        return "lit_scan"
    if rec_type == "community_post":
        return "community"
    if rec_type in ("preprint", "conference"):
        return "community"
    if "claude science" in blob:
        return "claude_science"
    if "perturb-seq" in blob or "disease_mechanisms" in blob or "marson" in blob:
        return "screen"
    return "other"


def _parse_line(line: str, gene: str):
    """Return a record dict for a KB list line, or None if it isn't a record."""
    if not line.startswith("- **"):
        return None
    date = (_DATE.search(line) or [None, None])[1] if _DATE.search(line) else None
    dm = _DISEASE.search(line)
    disease = dm.group(1).strip() if dm else None
    # text = everything after the "(disease):" (or after the leading bold for community posts)
    if dm:
        text = line[dm.end():].strip()
    else:
        text = line[2:].strip()
    src = ""
    sm = re.search(r"\*source:\s*(.+?)\*", line)
    if sm:
        src = sm.group(1).strip()
    rec_type = _rec_type(line, text)
    grade = None
    if rec_type == "verdict":
        g = _VERDICT_GRADE.search(line)
        grade = g.group(1) if g else None
    else:
        g = _SCAN_GRADE.search(text)
        grade = g.group(1).upper() if g else None
    state = (_STATE.search(text).group(1) if _STATE.search(text) else None)
    urls = _URL.findall(line)
    url = urls[-1].rstrip(".,;·") if urls else None
    return {
        "gene": gene, "disease": disease, "rec_type": rec_type, "grade": grade,
        "state": state.lower() if state else None,
        "source_tier": _source_tier(text, src, rec_type),
        "date": date, "url": url, "text": text,
    }


def build() -> dict:
    if DB_PATH.exists():
        DB_PATH.unlink()
    con = sqlite3.connect(DB_PATH)
    con.executescript("""
        CREATE TABLE records (
          id INTEGER PRIMARY KEY, gene TEXT, disease TEXT, rec_type TEXT, grade TEXT,
          state TEXT, source_tier TEXT, date TEXT, url TEXT, text TEXT
        );
        CREATE VIRTUAL TABLE records_fts USING fts5(text, content='records', content_rowid='id');
    """)
    n = 0
    for md in sorted((KB_DIR / "wiki" / "targets").glob("*.md")):
        gene = md.stem
        for line in md.read_text().splitlines():
            rec = _parse_line(line, gene)
            if not rec:
                continue
            cur = con.execute(
                "INSERT INTO records (gene,disease,rec_type,grade,state,source_tier,date,url,text) "
                "VALUES (:gene,:disease,:rec_type,:grade,:state,:source_tier,:date,:url,:text)", rec)
            con.execute("INSERT INTO records_fts (rowid, text) VALUES (?, ?)", (cur.lastrowid, rec["text"]))
            n += 1
    con.commit()
    stats = {
        "records": n,
        "genes": con.execute("SELECT COUNT(DISTINCT gene) FROM records").fetchone()[0],
        "diseases": con.execute("SELECT COUNT(DISTINCT disease) FROM records WHERE disease IS NOT NULL").fetchone()[0],
        "by_type": dict(con.execute("SELECT rec_type, COUNT(*) FROM records GROUP BY rec_type").fetchall()),
        "by_tier": dict(con.execute("SELECT source_tier, COUNT(*) FROM records GROUP BY source_tier").fetchall()),
    }
    con.close()
    return stats


if __name__ == "__main__":
    s = build()
    print(f"built {DB_PATH}")
    print(f"  {s['records']} records | {s['genes']} genes | {s['diseases']} diseases")
    print(f"  by type: {s['by_type']}")
    print(f"  by tier: {s['by_tier']}")
