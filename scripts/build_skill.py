#!/usr/bin/env python3
"""
Build the Claude Science skill zip from repo sources — reproducible packaging.

Assembles: SKILL.md (at zip root) + tcell_targets/ (the engine, incl. the community
listen layer) + data/ (the 3 CSVs the shipped tools actually load) + kb/ (the seeded,
validated knowledge base with baked community signal). The two large CSVs
(guide_kd_efficiency, sgrna_library_metadata) are intentionally excluded — the shipped
tools don't load them, and dropping them keeps the zip under Science's 30 MB cap.

    python scripts/build_skill.py         ->  dist/tcell-target-explorer-skill.zip
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "dist" / "tcell-target-explorer-skill.zip"

# Only the CSVs the shipped tools load (see tcell_targets/core.py).
DATA_FILES = [
    "cluster_autoimmune_enrichment_results.csv",
    "DE_stats.csv",
    "Th2_Th1_polarization_signature_DE_results_full.csv",
]
MAX_UNCOMPRESSED_MB = 30  # Claude Science skill limit


def _add(zf: zipfile.ZipFile, src: Path, arcname: str, sizes: dict):
    zf.write(src, arcname)
    sizes[arcname] = src.stat().st_size


def build() -> Path:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        OUT.unlink()
    sizes: dict[str, int] = {}
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        _add(zf, REPO / "skill" / "SKILL.md", "SKILL.md", sizes)

        for py in sorted((REPO / "tcell_targets").glob("*.py")):
            _add(zf, py, f"tcell_targets/{py.name}", sizes)

        for name in DATA_FILES:
            src = REPO / "data" / name
            if not src.exists():
                sys.exit(f"missing data file: {src}")
            _add(zf, src, f"data/{name}", sizes)

        for path in sorted((REPO / "kb").rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                _add(zf, path, f"kb/{path.relative_to(REPO / 'kb')}", sizes)

    uncompressed = sum(sizes.values())
    zipped = OUT.stat().st_size
    print(f"built {OUT.relative_to(REPO)}")
    print(f"  files: {len(sizes)}")
    print(f"  uncompressed: {uncompressed / 1e6:.1f} MB (limit {MAX_UNCOMPRESSED_MB} MB)")
    print(f"  zipped:       {zipped / 1e6:.1f} MB")
    kb_files = sum(1 for a in sizes if a.startswith("kb/"))
    print(f"  kb/ files: {kb_files}  (target profiles + disease profiles + community signal)")
    if uncompressed > MAX_UNCOMPRESSED_MB * 1e6:
        sys.exit(f"ERROR: uncompressed size exceeds {MAX_UNCOMPRESSED_MB} MB — trim before upload.")
    return OUT


if __name__ == "__main__":
    build()
