# Slack bot setup (~3 minutes)

Meet your lab where they work: `@target-explorer` (or `/ask-target`) in a **public**
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
  **Bot User OAuth Token** `xoxb-…`.

## 4. Run it
```bash
pip install -e ".[slack]"              # or: pip install "tcell-target-explorer[slack]"
export SLACK_BOT_TOKEN=xoxb-...
export SLACK_APP_TOKEN=xapp-...
export ANTHROPIC_API_KEY=sk-ant-...    # optional: enables natural-language answers
python -m tcell_targets.slack_app
```

## 5. Use it
In Slack, invite the bot to a public channel: `/invite @target-explorer`, then:
- `@target-explorer what should we hit for rheumatoid arthritis?`
- `/ask-target type 1 diabetes`
- `/remember DOT1L | RA lead, methyltransferase, pinometostat in Ph2`

Without `ANTHROPIC_API_KEY` the bot still works — it returns a deterministic engine
summary (discovery handles + community signal). With the key, Claude answers in natural
language, grounded in the same tools.
