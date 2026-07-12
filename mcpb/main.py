"""
Louis — .mcpb bundle entry point (Claude Desktop).

Runs the MCP server over stdio. Self-contained: bundled deps in lib/, dataset in
data/, engine in louis/. The knowledge base is copied to a user-writable dir
on first run (the installed bundle dir may be read-only), so kb_remember / kb_verdict /
kb_remember_signal work. On Desktop the home dir is writable, so the KB persists there
across sessions. Live community_signal works here too (Desktop has the xurl CLI on PATH).
"""
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))   # bundled third-party deps
sys.path.insert(0, str(HERE))           # the louis package

# Make the KB writable: seed a user dir from the bundled kb/ once, point the KB at it.
kb_target = Path(os.environ.get("LOUIS_KB_DIR") or (Path.home() / ".louis" / "kb"))
bundled_kb = HERE / "kb"
if not kb_target.exists() and bundled_kb.exists():
    kb_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(bundled_kb, kb_target)
os.environ["LOUIS_KB_DIR"] = str(kb_target)

from louis.mcp_server import main

if __name__ == "__main__":
    main()
