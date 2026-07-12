"""
Derived SQLite dimensional index over the markdown knowledge base — BUILD + QUERY.

The markdown under kb/ is the source of truth; this module builds a regenerable SQLite
index (dimension columns + an FTS5 full-text index) for FAST cross-cutting retrieval, and
queries it. It is SELF-CONTAINED — build and query live here — so it works inside the
shipped skill (Claude Science) with no external build script: the first kb_query rebuilds
the index from the packaged markdown if it's missing.

Slices the KB by gene × disease × record type × grade × activation state × source tier,
plus FTS5 full-text — the questions grep-over-markdown can't answer cleanly:
'all grade-A druggable leads', 'the epigenetic axis across diseases', 'who's active on DOT1L'.
"""
from __future__ import annotations
import os
import re
import sqlite3
from pathlib import Path

KB_DIR = Path(os.environ.get("LOUIS_KB_DIR") or (Path(__file__).resolve().parent.parent / "kb"))
DB = KB_DIR / "index.sqlite"

# ---- parse a KB markdown list line into a structured record -----------------
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
    if "slack" in source.lower():        # lab-contributed via Slack — a provenance tier that beats rec_type
        return "lab"
    blob = (text + " " + source).lower()
    if rec_type == "verdict":
        return "verdict"
    if rec_type == "lit_scan":
        return "lit_scan"
    if rec_type in ("community_post", "preprint", "conference"):
        return "community"
    if "claude science" in blob:
        return "claude_science"
    if "perturb-seq" in blob or "disease_mechanisms" in blob or "marson" in blob:
        return "screen"
    return "other"


def _parse_line(line: str, gene: str):
    if not line.startswith("- **"):
        return None
    dmatch = _DATE.search(line)
    date = dmatch.group(1) if dmatch else None
    dm = _DISEASE.search(line)
    disease = dm.group(1).strip() if dm else None
    text = line[dm.end():].strip() if dm else line[2:].strip()
    sm = re.search(r"\*source:\s*(.+?)\*", line)
    src = sm.group(1).strip() if sm else ""
    rec_type = _rec_type(line, text)
    if rec_type == "verdict":
        g = _VERDICT_GRADE.search(line)
        grade = g.group(1) if g else None
    else:
        g = _SCAN_GRADE.search(text)
        grade = g.group(1).upper() if g else None
    st = _STATE.search(text)
    urls = _URL.findall(line)
    return {
        "gene": gene, "disease": disease, "rec_type": rec_type, "grade": grade,
        "state": st.group(1).lower() if st else None,
        "source_tier": _source_tier(text, src, rec_type),
        "date": date, "url": urls[-1].rstrip(".,;·") if urls else None, "text": text,
    }


# ---- build ------------------------------------------------------------------
def build() -> dict:
    """(Re)build the index from the markdown KB. Returns summary stats."""
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
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


def rebuild() -> bool:
    try:
        build()
    except Exception:
        return False
    return DB.exists()


def _ensure() -> bool:
    return DB.exists() or rebuild()


# ---- query ------------------------------------------------------------------
def query(text: str | None = None, disease: str | None = None, gene: str | None = None,
          grade: str | None = None, rec_type: str | None = None, state: str | None = None,
          source_tier: str | None = None, exclude_tier=None, limit: int = 25) -> dict:
    """
    Dimensional + full-text search across the whole knowledge base. Every argument is
    optional and ANDs together:
      text        FTS query over record text (e.g. 'epigenetic OR methyltransferase', 'inhibitor')
      disease     substring match (e.g. 'lupus', 'multiple sclerosis')
      gene        exact gene symbol (e.g. 'DOT1L')
      grade       exact grade ('A','B+','B','C+','C','D')
      rec_type    'verdict' | 'finding' | 'community_post' | 'preprint' | 'conference' | 'lit_scan'
      state       activation state substring ('rest','stim8hr','stim48hr','activation-induced'...)
      source_tier 'screen' | 'claude_science' | 'lit_scan' | 'community' | 'verdict'
    Returns {n, records:[{gene,disease,rec_type,grade,state,source_tier,date,url,text}]}.
    """
    if not _ensure():
        return {"error": "index unavailable", "records": []}
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    where, params = [], []
    if disease:
        where.append("disease LIKE ?"); params.append(f"%{disease}%")
    if gene:
        where.append("gene = ?"); params.append(gene)
    if grade:
        where.append("grade = ?"); params.append(grade)
    if rec_type:
        where.append("rec_type = ?"); params.append(rec_type)
    if state:
        where.append("state LIKE ?"); params.append(f"%{state.lower()}%")
    if source_tier:
        where.append("source_tier = ?"); params.append(source_tier)
    if exclude_tier:                                     # provenance-scoped memory: drop these tiers (e.g. 'lab')
        _ex = [exclude_tier] if isinstance(exclude_tier, str) else list(exclude_tier)
        where.append("source_tier NOT IN (%s)" % ",".join(["?"] * len(_ex))); params.extend(_ex)
    if text:
        where.append("id IN (SELECT rowid FROM records_fts WHERE records_fts MATCH ?)")
        params.append(text)
    sql = ("SELECT gene, disease, rec_type, grade, state, source_tier, date, url, text FROM records"
           + (" WHERE " + " AND ".join(where) if where else "")
           + " ORDER BY (grade IS NULL), grade, gene LIMIT ?")
    params.append(int(limit))
    try:
        rows = [dict(r) for r in con.execute(sql, params).fetchall()]
    except sqlite3.OperationalError as e:
        con.close()
        return {"error": f"query error ({e}); check the FTS syntax in `text`", "records": []}
    con.close()
    for r in rows:  # keep payload scannable
        if r.get("text") and len(r["text"]) > 400:
            r["text"] = r["text"][:400] + "…"
    return {"n": len(rows), "records": rows}
