"""
Console-script entrypoints that ISOLATE the knowledge base from the git tree.

The clone-based `louis-mcp` / `louis-slack` servers used to default their KB writes
to the repo's own `kb/` — a git-tracked directory. That's a privacy footgun: a lab's
private `kb_remember` / `kb_verdict` writes would land inside a tracked tree they might
later push. These wrappers seed a *user-writable* KB (`~/.louis/kb`) from the packaged
`kb/` on first run and point `LOUIS_KB_DIR` at it BEFORE the server imports the KB
module (`louis.kb` freezes `KB_DIR` at import) — so private writes never touch the repo.
Mirrors `mcpb/main.py` (the desktop-bundle shim), which already does this.

Curating the SHIPPED seed KB (the maintainer path) is unchanged: direct `louis.kb`
importers (scripts, tests, the Streamlit app) still default to the repo's `kb/`, and
you can force any launcher to write there too with `LOUIS_KB_DIR=./kb` (or any path).
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path


def _seed_and_redirect() -> None:
    """Point LOUIS_KB_DIR at a user-writable KB, seeding it from the packaged kb/ once."""
    target = Path(os.environ.get("LOUIS_KB_DIR") or (Path.home() / ".louis" / "kb"))
    seed = Path(__file__).resolve().parent.parent / "kb"          # the packaged/committed KB
    if not target.exists() and seed.exists() and seed.resolve() != target.resolve():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(seed, target)
    os.environ["LOUIS_KB_DIR"] = str(target)                       # set BEFORE importing louis.kb


def mcp() -> None:
    _seed_and_redirect()
    from louis.mcp_server import main
    main()


def slack() -> None:
    _seed_and_redirect()
    from louis.slack_app import main
    main()
