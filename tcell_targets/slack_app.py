"""
T-Cell Target Explorer — Slack bot (the "share it with your lab" surface).

Meet scientists where they already work. @mention the bot or use /ask-target in a
PUBLIC channel and it answers with trust-ranked, activation-state-aware target leads
+ the live community signal — reusing the SAME engine + Claude brain as the MCP tools
— and lets the lab grow one SHARED knowledge base (/remember), so everyone's questions
compound into a single memory instead of scattering across DMs.

Public-channel-first by design — the Spotify agent ethos: knowledge is shared, not
siloed. Runs over Socket Mode, so there is no public URL and nothing to host.

Env:
  SLACK_BOT_TOKEN    xoxb-...    Bot User OAuth token (scopes: app_mentions:read, chat:write, commands)
  SLACK_APP_TOKEN    xapp-...    App-level token for Socket Mode (scope: connections:write)
  ANTHROPIC_API_KEY  sk-ant-...  the NL brain (optional; without it, a deterministic engine summary is used)
  TCELL_KB_DIR       optional    shared KB location (defaults to the repo's kb/)

Run:  pip install "tcell-target-explorer[slack]"  &&  python -m tcell_targets.slack_app
"""
from __future__ import annotations

import os
import re

from . import core, community, kb


# ---- formatting -------------------------------------------------------------

def _to_mrkdwn(text: str) -> str:
    """Markdown -> Slack mrkdwn: **bold** becomes *bold*, [t](u) becomes <u|t>."""
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r"<\2|\1>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"*\1*", text)
    return text


def _format_trace(trace: list) -> str:
    if not trace:
        return ""
    steps = ", ".join(f"`{name}`" for name, _ in trace)
    return f"_grounded in:_ {steps}"


def _engine_summary(disease: str) -> str:
    """Deterministic fallback (no API key): discovery handles + community signal for a disease."""
    disease = disease.strip()
    if not disease or disease.lower() in ("help", "diseases", "list"):
        ds = ", ".join(core.list_diseases())
        return f"*Diseases I cover:*\n{ds}\n\nTry: `/ask-target rheumatoid arthritis`"
    mods = core.disease_mechanisms(disease, top_modules=4)
    if not mods:
        return (f"No disease-enriched T-cell program for *{disease}*. "
                f"`/ask-target list` shows the ones I cover.")
    lines = [f"*{disease}* — top mechanistic leads (discover → listen):", ""]
    handles: list[str] = []
    for m in mods:
        for h in m.get("candidate_handles", [])[:4]:
            g = h if isinstance(h, str) else h.get("gene", "")
            if g and g not in handles:
                handles.append(g)
    lines.append("*Druggable handles wired to the disease's own risk genes:* " +
                 ", ".join(f"`{g}`" for g in handles[:8]))
    sig = community.community_signal(disease, kind="disease", top=3)
    posts = sig.get("posts", [])
    if posts:
        lines += ["", "*What the field is saying this week:*"]
        for p in posts:
            lines.append(f"• *@{p['handle']}* ({p['date']}): {p['text'][:160]} <{p['url']}|link>")
    elif sig.get("note"):
        lines += ["", f"_community signal: {sig['note']}_"]
    lines += ["", "_Hypotheses to prioritize bench work — not clinical claims._"]
    return "\n".join(lines)


def _answer(question: str) -> tuple[str, list]:
    """NL answer via Claude if a key is set; else a deterministic engine summary."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            from .assistant import answer
            text, trace, _ = answer(question)
            return text, trace
        except Exception as e:  # fall back rather than fail the demo
            return _engine_summary(question) + f"\n\n_(NL layer error: {type(e).__name__})_", []
    return _engine_summary(question), []


# ---- app --------------------------------------------------------------------

def build_app():
    from slack_bolt import App

    app = App(token=os.environ["SLACK_BOT_TOKEN"])

    @app.event("app_mention")
    def on_mention(event, say):
        text = re.sub(r"<@[^>]+>", "", event.get("text", "")).strip()
        thread = event.get("thread_ts") or event.get("ts")
        if not text:
            say(text="Ask me what to target — e.g. *what should we hit for rheumatoid arthritis?*",
                thread_ts=thread)
            return
        answer, trace = _answer(text)
        say(text=_to_mrkdwn(answer), thread_ts=thread)
        if trace:
            say(text=_format_trace(trace), thread_ts=thread)

    @app.command("/ask-target")
    def on_ask(ack, command, respond):
        ack()
        answer, trace = _answer(command.get("text", ""))
        blocks = _to_mrkdwn(answer)
        if trace:
            blocks += "\n\n" + _format_trace(trace)
        respond(text=blocks, response_type="in_channel")  # public — the lab sees it

    @app.command("/remember")
    def on_remember(ack, command, respond):
        ack()
        raw = command.get("text", "")
        gene, _, finding = raw.partition("|")
        gene, finding = gene.strip(), finding.strip()
        if not gene or not finding:
            respond(text="Usage: `/remember GENE | finding text` — e.g. "
                         "`/remember DOT1L | RA lead, methyltransferase, pinometostat Ph2`",
                    response_type="ephemeral")
            return
        r = kb.remember(gene, finding, source="Slack (lab)", disease=None)
        respond(text=f"📌 Filed to the shared KB → `{r['profile']}`: {finding}",
                response_type="in_channel")

    return app


def main() -> None:
    from slack_bolt.adapter.socket_mode import SocketModeHandler
    app = build_app()
    print("T-Cell Target Explorer Slack bot — Socket Mode. Ctrl-C to stop.")
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()


if __name__ == "__main__":
    main()
