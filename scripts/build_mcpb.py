#!/usr/bin/env python3
"""
Build the Claude Desktop .mcpb bundle from repo sources — reproducible packaging.

Layout: manifest.json + server/main.py + server/lib/ (pip-installed deps: pandas, mcp)
+ server/tcell_targets/ (the engine) + server/data/ (the 3 shipped CSVs) + server/kb/
(the seeded KB with baked community signal). Deps are pip-installed at build time rather
than vendored into git.

    python scripts/build_mcpb.py          ->  dist/tcell-target-explorer.mcpb
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BUILD = REPO / "dist" / "mcpb_build"
OUT = REPO / "dist" / "tcell-target-explorer.mcpb"
DEPS = ["pandas>=2.0", "mcp>=1.2"]
DATA_FILES = [
    "cluster_autoimmune_enrichment_results.csv",
    "DE_stats.csv",
    "Th2_Th1_polarization_signature_DE_results_full.csv",
]


def build() -> Path:
    if BUILD.exists():
        shutil.rmtree(BUILD)
    server = BUILD / "server"
    (server / "data").mkdir(parents=True)

    shutil.copy2(REPO / "mcpb" / "manifest.json", BUILD / "manifest.json")
    shutil.copy2(REPO / "mcpb" / "main.py", server / "main.py")

    print("pip-installing bundled deps into server/lib …")
    subprocess.run([sys.executable, "-m", "pip", "install", "--quiet",
                    "--target", str(server / "lib"), *DEPS], check=True)

    shutil.copytree(REPO / "tcell_targets", server / "tcell_targets",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for name in DATA_FILES:
        shutil.copy2(REPO / "data" / name, server / "data" / name)
    shutil.copytree(REPO / "kb", server / "kb",
                    ignore=shutil.ignore_patterns("__pycache__"))

    if OUT.exists():
        OUT.unlink()
    total = 0
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(BUILD.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(BUILD))
                total += path.stat().st_size
    print(f"built {OUT.relative_to(REPO)}")
    print(f"  uncompressed: {total / 1e6:.1f} MB   zipped: {OUT.stat().st_size / 1e6:.1f} MB")
    return OUT


if __name__ == "__main__":
    build()
