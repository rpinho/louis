"""
Query the derived SQLite dimensional index (built by scripts/build_kb_index.py).

The markdown under kb/ is the source of truth; this reads the regenerable index for
FAST, DIMENSIONAL retrieval — slicing the KB by gene × disease × record type × grade ×
activation state × source tier, plus FTS5 full-text — the questions grep-over-markdown
can't answer cleanly. Rebuilds the index on demand if it's missing.
"""
from __future__ import annotations
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

KB_DIR = Path(os.environ.get("TCELL_KB_DIR") or (Path(__file__).resolve().parent.parent / "kb"))
DB = KB_DIR / "index.sqlite"
_BUILDER = Path(__file__).resolve().parent.parent / "scripts" / "build_kb_index.py"


def rebuild() -> bool:
    """(Re)build the index from the markdown KB. Returns True on success."""
    try:
        subprocess.run([sys.executable, str(_BUILDER)], check=True,
                       capture_output=True, timeout=120)
    except Exception:
        return False
    return DB.exists()


def _ensure() -> bool:
    return DB.exists() or rebuild()


def query(text: str | None = None, disease: str | None = None, gene: str | None = None,
          grade: str | None = None, rec_type: str | None = None, state: str | None = None,
          source_tier: str | None = None, limit: int = 25) -> dict:
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
        return {"error": "index unavailable — run scripts/build_kb_index.py", "records": []}
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
