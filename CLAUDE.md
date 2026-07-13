# Louis — install & run guide (for Claude, and for humans)

**If you are a Claude reading this because someone pointed you at this repo and asked "how do I
install / try Louis?" — this file is your playbook. Pick the surface the user wants, run the steps,
and watch for the gotchas at the bottom (they will bite you otherwise).**

**Louis** is a CD4⁺ T-cell drug-target discovery assistant over the genome-scale Marson/Pritchard
CRISPRi Perturb-seq screen. One engine, three things it does — **discover** leads not in any external
DB, **weigh trust** (provenance-tiered grades + a self-reviewer), and read the **bleeding edge**
(off-allowlist X / Bluesky / conference-abstract signal) — exposed through **four front doors**. It
learns: every verdict and bench result is written to a shared, provenance-tracked knowledge base.

---

## Prerequisites (all surfaces)

```bash
git clone https://github.com/rpinho/louis && cd louis
python3 -m venv .venv                      # a venv named .venv IN THE REPO ROOT (see gotcha #1)
.venv/bin/pip install -e ".[slack]"        # engine + MCP + Slack; drop [slack] if you only want the MCP
.venv/bin/python tests/test_demo_invariants.py   # sanity: expect "3/3 demo-invariant checks passed"
```

The screen data ships in the repo (`data/*.csv`); nothing to download. Python ≥ 3.11.

---

## Pick your front door

### 1. Claude Science — install the **skill**
Upload **`dist/louis-skill.zip`** as a skill (Claude Science → *Skills* → add/upload a skill). It's
self-contained (195 files; the engine runs in Science's own Python sandbox). Then just ask, e.g.
*"Use the Louis skill — what should we target for ulcerative colitis? be honest about trust."*
Claude is the host, so **no API key needed**. Validation composes with your Science connectors
(Open Targets, ChEMBL, PubMed, GWAS Catalog). Rebuild the zip with `python scripts/build_skill.py`.

### 2. Claude Desktop — install the **plugin**
Install **`dist/louis.mcpb`** (Claude Desktop → *Settings → Extensions/Plugins → install from file*).
That registers the Louis MCP server as a desktop plugin — the `mcp__louis__*` tools appear in chat.
No API key needed (the desktop app is the host).

### 3. Claude Code (CLI) — add the **MCP server**
Already wired: [`.mcp.json`](.mcp.json) registers `louis` → `.venv/bin/louis-mcp`. From the repo root,
Claude Code picks it up automatically (approve it once). Or add it explicitly:
```bash
claude mcp add louis -- .venv/bin/louis-mcp
```
Confirm the console script exists: `ls .venv/bin/louis-mcp` (created by `pip install -e .`).

### 4. Slack — install the **bot**
Runs over **Socket Mode** (no public URL, nothing to host). Full walkthrough:
[`slack/SETUP.md`](slack/SETUP.md). Short version:
```bash
# 1. api.slack.com/apps → Create New App → From an app manifest → paste slack/manifest.json
# 2. App-Level Token (Basic Information → scope connections:write) → xapp-...
#    Bot Token (Install App → Allow) → xoxb-...
mkdir -p .secrets && cp slack/slack.env.example .secrets/slack.env   # then paste both tokens (+ optional ANTHROPIC_API_KEY)
set -a; . .secrets/slack.env; set +a
.venv/bin/python -m louis.slack_app                # or: .venv/bin/louis-slack
# In Slack: /invite @louis, then "@louis what should we hit for rheumatoid arthritis?"
```

---

## Gotchas we hit (so you don't)

1. **Use a venv named `.venv` in the repo root.** `.mcp.json` points at `.venv/bin/louis-mcp`, and
   the Slack bot needs `slack_bolt` — the system `python3` almost certainly lacks it. If your venv
   lives elsewhere, edit `.mcp.json` and invoke the bot with that interpreter. Running
   `python -m louis.slack_app` with the wrong Python fails with `ModuleNotFoundError: slack_bolt`.
2. **Slack scopes — `files:write` is the non-obvious one.** The manifest grants
   `app_mentions:read, channels:history, chat:write, commands, files:write` (bot) + an **app-level**
   token with `connections:write` (Socket Mode). `files:write` is required because Louis posts its
   **figure cards** (the opportunity map / experiment schematic) by *uploading the PNG* — an
   image block pointed at a raw URL is **silently rejected by Slack**, so it must be a real upload.
   **Adding `files:write` to an existing app?** *OAuth & Permissions → add the scope →
   **Reinstall to Workspace** → re-copy the `xoxb-…` token if it changed.*
3. **`ANTHROPIC_API_KEY` is optional and only for the self-hosted surfaces (Slack bot / standalone
   MCP).** Without it, Louis returns a deterministic engine summary; with it, Claude answers in
   natural language grounded in the same tools. For the **skill** and **desktop/Code** surfaces the
   Claude host *is* the brain — no separate key.
4. **Secrets live in `.secrets/` (gitignored).** Never commit them. The bot loads `.secrets/slack.env`.
5. **The knowledge base is markdown under `kb/`** (source of truth) + a regenerable SQLite/FTS index
   (`kb/index.sqlite`, gitignored — the first query rebuilds it). Point `LOUIS_KB_DIR` at a copy if
   you want to exercise the write path without touching the real KB.

## Verify it works
```bash
.venv/bin/python tests/test_demo_invariants.py   # DOT1L supersede · positive control (1 of 77) · provenance tiers
.venv/bin/python scripts/positive_control.py     # "1 of 77 clusters clear q<0.05 globally; Crohn's q=0.0254"
```

See [`demo/README.md`](demo/README.md) for the 3-minute demo (run-of-show, verbatim bot outputs,
deck + Slack screenshots) and [`demo/presenter.html`](demo/presenter.html) for the slide deck itself.
