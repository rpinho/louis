#!/usr/bin/env python3
"""
Build the Claude Science skill zip from repo sources — reproducible packaging.

Assembles: SKILL.md (at zip root) + louis/ (the engine, incl. the community
listen layer) + data/ (the 3 CSVs the shipped tools actually load) + kb/ (the seeded,
validated knowledge base with baked community signal). The two large CSVs
(guide_kd_efficiency, sgrna_library_metadata) are intentionally excluded — the shipped
tools don't load them, and dropping them keeps the zip under Science's 30 MB cap.

    python scripts/build_skill.py         ->  dist/louis-skill.zip
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "dist" / "louis-skill.zip"   # zip name = the skill brand (Claude Science may key the name off the filename)

# Only the CSVs the shipped tools load (see louis/core.py).
DATA_FILES = [
    "cluster_autoimmune_enrichment_results.csv",
    "DE_stats.csv",
    "Th2_Th1_polarization_signature_DE_results_full.csv",
]
MAX_UNCOMPRESSED_MB = 30   # Claude Science skill size limit
MAX_FILES = 195            # Claude Science skill file-count cap is 200 — leave margin


def _post_count(p: Path) -> int:
    return sum(1 for line in p.read_text().splitlines() if line.startswith("- **@"))


def _is_lead(p: Path) -> bool:
    """A real lead carries a verdict or a data/validation finding — not just community chatter."""
    for line in p.read_text().splitlines():
        if line.startswith("- **VERDICT"):
            return True
        if (line.startswith("- **20") and "source:" in line
                and not line.startswith("- **@") and "profile opened" not in line):
            return True
    return False


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

        for py in sorted((REPO / "louis").glob("*.py")):
            _add(zf, py, f"louis/{py.name}", sizes)

        for name in DATA_FILES:
            src = REPO / "data" / name
            if not src.exists():
                sys.exit(f"missing data file: {src}")
            _add(zf, src, f"data/{name}", sizes)

        # non-gene-profile kb files (skip the regenerable index.sqlite)
        targets_dir = REPO / "kb" / "wiki" / "targets"
        for path in sorted((REPO / "kb").rglob("*")):
            if (path.is_file() and "__pycache__" not in path.parts
                    and targets_dir not in path.parents and path.name != "index.sqlite"):
                _add(zf, path, f"kb/{path.relative_to(REPO / 'kb')}", sizes)

        # gene profiles: every real LEAD + the highest-signal markers, within the file budget
        # (Claude Science caps skills at 200 files; the harvest minted many thin marker profiles).
        profiles = sorted(targets_dir.glob("*.md"))
        lead_set = {p for p in profiles if _is_lead(p)}
        markers = sorted((p for p in profiles if p not in lead_set), key=_post_count, reverse=True)
        budget = MAX_FILES - len(sizes)
        keep = lead_set | set(markers[:max(0, budget - len(lead_set))])
        for p in sorted(keep):
            _add(zf, p, f"kb/wiki/targets/{p.name}", sizes)
        print(f"  gene profiles: kept {len(keep)}/{len(profiles)} "
              f"({len(lead_set)} leads + {len(keep) - len(lead_set)} top-signal markers; "
              f"dropped {len(profiles) - len(keep)} thin markers)")

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
    if len(sizes) > 200:
        sys.exit(f"ERROR: {len(sizes)} files exceeds Claude Science's 200-file cap — trim before upload.")
    return OUT


if __name__ == "__main__":
    build()
