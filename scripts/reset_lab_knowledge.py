#!/usr/bin/env python3
"""Reset lab-contributed knowledge — remove every Slack-written (lab-tier) line from the KB and
rebuild the indices, so the collaborative-memory demo re-runs from a clean slate. The validated
KB (screen data, Claude Science verdicts, community signal) is untouched — only what the lab typed
into Slack (`source: Slack · @user`) is removed.

    python scripts/reset_lab_knowledge.py            # dry-run: show what WOULD be removed
    python scripts/reset_lab_knowledge.py --apply    # remove + reindex
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


def main() -> None:
    apply = "--apply" in sys.argv
    removed = []
    for f in sorted((REPO / "kb" / "wiki").rglob("*.md")):
        lines = f.read_text().splitlines()
        kept = [ln for ln in lines if not (ln.startswith("- **") and "source: Slack" in ln)]
        cut = [ln for ln in lines if ln.startswith("- **") and "source: Slack" in ln]
        if cut and apply:
            f.write_text("\n".join(kept) + "\n")
        removed += [(f.stem, ln) for ln in cut]

    verb = "REMOVED" if apply else "WOULD REMOVE"
    print(f"{verb} {len(removed)} lab-contributed line(s):")
    for gene, ln in removed:
        print(f"  [{gene}] {re.sub(r'\s+', ' ', ln)[:100]}")
    if apply and removed:
        from louis import kb, kb_index
        kb.reindex(); kb_index.build()
        print("rebuilt indices.")
    elif not apply:
        print("\n(dry-run) re-run with --apply to remove + reindex.")


if __name__ == "__main__":
    main()
