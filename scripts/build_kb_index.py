#!/usr/bin/env python3
"""
Build the derived SQLite dimensional index over the markdown KB.

Thin wrapper — the build + query logic lives in tcell_targets/kb_index.py so the shipped
skill (Claude Science) carries a self-contained builder (no dependency on this script).

    python scripts/build_kb_index.py          # writes kb/index.sqlite
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from tcell_targets import kb_index  # noqa: E402

if __name__ == "__main__":
    s = kb_index.build()
    print(f"built {kb_index.DB}")
    print(f"  {s['records']} records | {s['genes']} genes | {s['diseases']} diseases")
    print(f"  by type: {s['by_type']}")
    print(f"  by tier: {s['by_tier']}")
