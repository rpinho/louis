# Slack bot setup (~3 minutes)

Meet your lab where they work: `@louis` (or `/ask-louis`) in a **public**
channel returns trust-ranked T-cell target leads + the live community signal, from the
same engine as the MCP tools. `/remember` files a finding to the **shared** knowledge
base so the whole lab's questions compound into one memory.

Runs over **Socket Mode** — no public URL, no server to host.

## 1. A workspace you control
If you don't have a personal one, create a free workspace at <https://slack.com/create>
(don't use a work workspace for the demo).

## 2. Create the app from the manifest
1. Go to <https://api.slack.com/apps> → **Create New App** → **From an app manifest**.
2. Pick your workspace.
3. Paste the contents of [`manifest.json`](manifest.json) and create.

## 3. Get the two tokens
- **App-level token (Socket Mode):** app settings → **Basic Information** → *App-Level Tokens*
  → **Generate Token and Scopes** → add scope `connections:write` → copy the `xapp-…` token.
- **Bot token:** **Install App** (left nav) → *Install to Workspace* → Allow → copy the
  **Bot User OAuth Token** `xoxb-…` (also shown under *OAuth & Permissions*).

Paste both into `.secrets/slack.env` (gitignored — a template is already there):
```bash
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
#ANTHROPIC_API_KEY=sk-ant-...          # optional: enables natural-language answers
```

## Permissions the app needs (set automatically by the manifest)

Creating the app **from the manifest** grants exactly these — no clicking through scope lists — but here they are so you know what Louis touches and why:

| Scope | Why |
|---|---|
| `app_mentions:read` | see `@louis` mentions |
| `channels:history` | read untagged thread follow-ups, so you don't re-tag him mid-conversation |
| `chat:write` | post answers |
| `commands` | the `/ask-louis` and `/remember` slash commands |
| `files:write` | upload the **figure cards** — the opportunity map, the experiment schematic — inline in a thread |
| `users:read` | resolve who reported a correction/bench result to a readable `@handle` for write-provenance (so a labmate's KD files as `@jordan`, not a raw user ID) |
| `connections:write` *(app-level)* | Socket Mode (no public URL, nothing to host) |

Louis posts only in channels you invite it to, reads only threads it's part of, and never touches DMs. **Upgrading an existing app** (e.g. adding `files:write` for the figure cards): *OAuth & Permissions* → add the scope → **Reinstall to Workspace** → re-copy the `xoxb-…` token if it changed.

## 4. Run it
```bash
pip install -e ".[slack]"              # or: pip install "louis[slack]"
set -a; . .secrets/slack.env; set +a   # load the tokens into the environment
python -m louis.slack_app
```

## 5. Use it
In Slack, invite the bot to a public channel: `/invite @louis`, then:
- `@louis what should we hit for rheumatoid arthritis?`
- `/ask-louis type 1 diabetes`
- `/remember DOT1L | RA lead, methyltransferase, pinometostat in Ph2`

Without `ANTHROPIC_API_KEY` the bot still works — it returns a deterministic engine
summary (discovery handles + community signal). With the key, Claude answers in natural
language, grounded in the same tools.

## Collaborative memory + demo controls

Louis **writes** to the shared KB, not just reads it — tell him something in a thread and he
files it, attributed to you:
- *"@louis actually we tested DOT1L — the module edge didn't hold, that verdict's too strong"* → he downgrades the verdict + files the result.
- *"@louis note that John's already running DOCK2"* → he files it as field activity, so nobody gets scooped.

Provenance-scoped **memory flags** (append to any question) control what he draws on — handy for demos:

| Flag | Effect |
|---|---|
| *(none)* | full shared memory |
| `--nolab` | answer on the **validated** KB only — exclude lab-contributed (Slack) knowledge (the "before the lab weighed in" view) |
| `--exclude <tier>` | exclude any provenance tier: `lab`, `community`, `claude_science`, `lit_scan`, `screen`, `verdict` |
| `--nomem` | no memory at all — answer from the live screen + reasoning only (the from-scratch contrast) |

Reset the lab-contributed knowledge for a clean demo take (the validated KB is untouched):

```bash
python scripts/reset_lab_knowledge.py            # dry-run — show what would be removed
python scripts/reset_lab_knowledge.py --apply    # remove + reindex
```
