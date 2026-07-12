"""
Louis — the Louis Slack bot (the "share it with your lab" surface).

Louis is the assistant persona (named for Louis Pasteur: nothing trusted until verified).
Meet scientists where they already work. @mention the bot or use /ask-louis in a
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
  LOUIS_KB_DIR       optional    shared KB location (defaults to the repo's kb/)

Run:  pip install "louis[slack]"  &&  python -m louis.slack_app
"""
from __future__ import annotations

import os
import re

from . import core, community, kb
from .assistant import default_use_memory  # import-safe: assistant loads no anthropic at import


# macOS python.org builds don't trust the system CA store, so slack_sdk's HTTPS calls fail
# with CERTIFICATE_VERIFY_FAILED. Point SSL at certifi's bundle if nothing else is configured.
if not os.environ.get("SSL_CERT_FILE"):
    try:
        import certifi
        os.environ["SSL_CERT_FILE"] = certifi.where()
    except Exception:
        pass


# ---- formatting -------------------------------------------------------------

def _to_mrkdwn(text: str) -> str:
    """Markdown -> Slack mrkdwn: **bold** becomes *bold*, [t](u) becomes <u|t>."""
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r"<\2|\1>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"*\1*", text)
    return text


# Internal tool names → the plain-English EVIDENCE SOURCE a scientist recognizes.
# The footer's job is to inspire confidence, so it must never expose raw function names.
_SOURCE_LABELS = {
    "disease_targets": "the CRISPRi Perturb-seq screen",
    "target_evidence": "the CRISPRi Perturb-seq screen",
    "regulator_detail": "the CRISPRi Perturb-seq screen",
    "state_profile": "the screen's activation-state data",
    "disease_mechanisms": "the disease's risk-gene modules",
    "community_signal": "live community signal (X/Twitter)",
    "kb_recall": "the shared lab knowledge base",
    "kb_search": "the shared lab knowledge base",
    "kb_query": "the shared lab knowledge base",
    "list_diseases": "",  # trivial lookup — not worth citing
}


def _source_label(tool_name: str) -> str:
    """Plain-English evidence source for a tool (falls back to the name if unmapped)."""
    return _SOURCE_LABELS.get(tool_name, tool_name)


def _format_trace(trace: list) -> str:
    """A confidence-inspiring provenance footer, in plain English — never raw tool names."""
    seen, sources = set(), []
    for name, _ in trace or []:
        label = _source_label(name)
        if label and label not in seen:
            seen.add(label)
            sources.append(label)
    if not sources:
        return ""
    if len(sources) == 1:
        joined = sources[0]
    elif len(sources) == 2:
        joined = f"{sources[0]} and {sources[1]}"
    else:
        joined = ", ".join(sources[:-1]) + f", and {sources[-1]}"
    return f"_Grounded in {joined}._"


# ---- memory toggle (demo both modes from ONE running bot) --------------------
# A trailing flag on a message forces from-scratch (no-KB) mode for THAT message;
# without it, the instance default applies (env TCELL_NO_MEMORY, else with-memory).
_NOMEM_TOKENS = ("--nomem", "/nomem", "[scratch]")
_NOLAB_TOKENS = ("--nolab", "--baseline", "/nolab")


def _mode_header(use_memory: bool, exclude=None) -> str:
    if not use_memory:
        return "🆕 **no memory — from scratch**"
    if exclude:
        return f"🧠 **with memory — excluding {', '.join(sorted(exclude))}**"
    return "🧠 **with lab memory**"


def _parse_mode(text: str) -> tuple[str, bool, set | None]:
    """Parse trailing memory-control flags → (clean_text, use_memory, exclude_tiers). Provenance-scoped:
    --nomem / [scratch]  → no memory at all (use_memory=False).
    --nolab / --baseline → answer on the validated KB but EXCLUDE lab-contributed (Slack) knowledge.
    --exclude <tier,...> → exclude any provenance tier(s): lab, community, claude_science, lit_scan, screen, verdict."""
    t = (text or "").strip()
    for tok in _NOMEM_TOKENS:
        if t.lower().endswith(tok):
            return t[: -len(tok)].strip(), False, None
    m = re.search(r"--exclude[:\s]+([a-z_,\s]+)$", t, re.I)
    if m:
        tiers = {x.strip().lower() for x in re.split(r"[,\s]+", m.group(1)) if x.strip()}
        return t[: m.start()].strip(), True, (tiers or None)
    for tok in _NOLAB_TOKENS:
        if t.lower().endswith(tok):
            return t[: -len(tok)].strip(), True, {"lab"}
    return t, default_use_memory(), None


def _baked_memory_lines(disease: str) -> list[str]:
    """Prior verdicts / baked community signal from the shared KB (a READ — memory mode only)."""
    rec = kb.recall(disease)
    if not rec.get("known"):
        return []
    text = rec.get("disease_profile", "") or ""
    verdicts = [ln.strip().lstrip("- ").strip() for ln in text.splitlines() if "**VERDICT" in ln][:2]
    out = ["", "🧠 *From lab memory (shared KB) — reused, not re-derived:*"]
    out += [f"• {v}" for v in verdicts]
    if "## Community signal" in text:
        out.append("• baked community signal on file (harvested in earlier sessions)")
    if not verdicts and "## Community signal" not in text:
        out.append(f"• prior profile on file for *{disease}*")
    return out


def _engine_summary(disease: str, use_memory: bool = True) -> str:
    """Deterministic fallback (no API key): discovery handles + community signal for a disease.
    With use_memory it also surfaces baked KB intelligence (verdicts/signal); with it off it
    reads nothing from kb/ — pure live engine."""
    disease = disease.strip()
    if not disease or disease.lower() in ("help", "diseases", "list"):
        ds = ", ".join(core.list_diseases())
        return f"*Diseases I cover:*\n{ds}\n\nTry: `/ask-louis rheumatoid arthritis`"
    mods = core.disease_mechanisms(disease, top_modules=4)
    if not mods:
        return (f"No disease-enriched T-cell program for *{disease}*. "
                f"`/ask-louis list` shows the ones I cover.")
    lines = [f"*{disease}* — top mechanistic leads (discover → listen):", ""]
    handles: list[str] = []
    for m in mods:
        for h in m.get("candidate_handles", [])[:4]:
            g = h if isinstance(h, str) else h.get("gene", "")
            if g and g not in handles:
                handles.append(g)
    lines.append("*Druggable handles wired to the disease's own risk genes:* " +
                 ", ".join(f"`{g}`" for g in handles[:8]))
    sig = community.community_signal(disease, kind="disease", top=3, allow_baked=True)
    posts = sig.get("posts", [])
    if posts:
        lines += ["", "*What the field is saying this week:*"]
        for p in posts:
            lines.append(f"• *@{p['handle']}* ({p['date']}): {p['text'][:160]} <{p['url']}|link>")
    elif sig.get("note"):
        lines += ["", f"_community signal: {sig['note']}_"]
    if use_memory:                      # only touch kb/ when memory is on
        lines += _baked_memory_lines(disease)
    lines += ["", "_Hypotheses to prioritize bench work — not clinical claims._"]
    return "\n".join(lines)


def _answer(question: str, use_memory: bool = True, on_tool=None, history=None, speaker=None, exclude=None) -> tuple[str, list, list]:
    """NL answer via Claude if a key is set; else a deterministic engine summary.
    use_memory=False skips all KB reads/writes (from-scratch, faster).
    on_tool(name) fires as each source is queried — used to stream live status.
    history is the running per-thread conversation (so follow-ups like 'expand' keep context);
    returns the updated message list to store back."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            from .assistant import answer
            text, trace, messages = answer(question, history=history, use_memory=use_memory, on_tool=on_tool, speaker=speaker, exclude=exclude)
            return text, trace, messages
        except Exception as e:  # fall back rather than fail the demo
            return (_engine_summary(question, use_memory=use_memory) + f"\n\n_(NL layer error: {type(e).__name__})_",
                    [], history or [])
    return _engine_summary(question, use_memory=use_memory), [], history or []


# ---- thread follow-through --------------------------------------------------
# thread_ts -> running assistant conversation. Presence means Louis has spoken in this thread,
# so a scientist can keep replying WITHOUT re-@mentioning him AND follow-ups like 'expand' /
# 'what about CBLB?' / 'why?' keep full context. In-memory; resets on restart (fine for a demo).
_THREAD_HISTORY: dict = {}

# Slack user id -> readable @handle, so writes to the SHARED memory are attributed to who told Louis. Cached.
_SPEAKER_CACHE: dict = {}


def _speaker(client, user_id) -> str | None:
    """Resolve a Slack user id to a readable @handle for write-provenance (who reported the correction/claim)."""
    if not user_id:
        return None
    if user_id not in _SPEAKER_CACHE:
        try:
            u = client.users_info(user=user_id)["user"]
            _SPEAKER_CACHE[user_id] = "@" + (u.get("name") or u.get("profile", {}).get("display_name") or user_id)
        except Exception:
            _SPEAKER_CACHE[user_id] = f"@{user_id}"
    return _SPEAKER_CACHE[user_id]


def _reply(raw_text: str, thread: str, say, client, channel: str, speaker=None) -> bool:
    """Post an instant placeholder, stream Louis's progress as he queries each source,
    then deliver the finished dossier as a FRESH message and clear the placeholder — so
    the answer the lab keeps (and the camera sees) never carries an '(edited)' tag.
    False if there was nothing to answer."""
    text, use_memory, exclude = _parse_mode(raw_text)
    if not text:
        return False
    ph = say(text="🔎 _Louis is on the case…_", thread_ts=thread)
    ts = ph["ts"]

    def _status(msg: str) -> None:
        try:
            client.chat_update(channel=channel, ts=ts, text=msg)
        except Exception:
            pass

    def on_tool(name: str) -> None:
        label = _source_label(name)
        if label:
            _status(f"🔎 _Louis is consulting {label}…_")

    answer, trace, messages = _answer(text, use_memory=use_memory, on_tool=on_tool,
                                      history=_THREAD_HISTORY.get(thread) or None, speaker=speaker, exclude=exclude)
    _THREAD_HISTORY[thread] = messages                   # carry the conversation for follow-ups
    md = _mode_header(use_memory, exclude) + "\n\n" + answer   # RAW GFM — tables render in a markdown block
    if trace:
        md += "\n\n" + _format_trace(trace)
    # Clear the transient status, then post the dossier fresh (no "(edited)" tag).
    try:
        client.chat_delete(channel=channel, ts=ts)
    except Exception:
        pass
    try:                                                  # markdown block renders GFM tables
        say(text=md[:400], blocks=[{"type": "markdown", "text": md}], thread_ts=thread)
    except Exception:                                     # older Slack → plain-text fallback
        say(text=_to_mrkdwn(md), thread_ts=thread)
    return True


# ---- app --------------------------------------------------------------------

def build_app():
    from slack_bolt import App

    app = App(token=os.environ["SLACK_BOT_TOKEN"])

    @app.event("app_mention")
    def on_mention(event, say, client):
        thread = event.get("thread_ts") or event.get("ts")
        _THREAD_HISTORY.setdefault(thread, [])        # engage the thread; follow-ups won't need a tag
        raw = re.sub(r"<@[^>]+>", "", event.get("text", "")).strip()
        if not _reply(raw, thread, say, client, event["channel"], speaker=_speaker(client, event.get("user"))):
            say(text="I'm *Louis*. Name a disease and I'll find + vet the T-cell targets — "
                     "e.g. *what should we hit for rheumatoid arthritis?*  "
                     "_(add `--nomem` to answer from scratch, no lab memory.)_",
                thread_ts=thread)

    @app.event("message")
    def on_message(event, say, client, context):
        """Untagged FOLLOW-UPS in a thread Louis is already in — so you don't re-tag him.
        Everything else in the channel is left alone (top-level messages, other threads)."""
        if event.get("subtype") or event.get("bot_id"):
            return                                    # edits / joins / bot posts (incl. Louis's own)
        thread = event.get("thread_ts")
        if not thread or thread not in _THREAD_HISTORY:
            return                                    # only threads Louis has already spoken in
        bot_id = context.get("bot_user_id")
        if bot_id and f"<@{bot_id}>" in event.get("text", ""):
            return                                    # tagged → on_mention handles it (no double reply)
        _reply(re.sub(r"<@[^>]+>", "", event.get("text", "")).strip(), thread, say, client, event["channel"], speaker=_speaker(client, event.get("user")))

    def on_ask(ack, command, respond):
        ack()
        text, use_memory, exclude = _parse_mode(command.get("text", ""))
        answer, trace, _ = _answer(text, use_memory=use_memory, exclude=exclude)
        md = _mode_header(use_memory, exclude) + "\n\n" + answer
        if trace:
            md += "\n\n" + _format_trace(trace)
        try:                                              # markdown block renders GFM tables
            respond(text=md[:400], blocks=[{"type": "markdown", "text": md}], response_type="in_channel")
        except Exception:
            respond(text=_to_mrkdwn(md), response_type="in_channel")
    app.command("/ask-louis")(on_ask)
    app.command("/ask-target")(on_ask)   # legacy alias — pre-rebrand installs registered /ask-target

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


def _require_tokens() -> None:
    """Fail with a clear, actionable message (not a raw KeyError) if tokens are unset
    or still hold the .secrets/slack.env placeholder (`xoxb-...` / `xapp-...`)."""
    def _unset(n: str) -> bool:
        v = os.environ.get(n, "")
        return not v or v.endswith("...")
    missing = [n for n in ("SLACK_BOT_TOKEN", "SLACK_APP_TOKEN") if _unset(n)]
    if missing:
        raise SystemExit(
            "Missing Slack token(s): " + ", ".join(missing) + ".\n"
            "Put them in .secrets/slack.env and load it, then run again:\n"
            "  set -a; . .secrets/slack.env; set +a\n"
            "  python -m louis.slack_app\n"
            "See slack/SETUP.md for where each token comes from."
        )


def main() -> None:
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    _require_tokens()
    from slack_bolt.adapter.socket_mode import SocketModeHandler
    app = build_app()
    print("Louis Slack bot — Socket Mode. Ctrl-C to stop.")
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()


if __name__ == "__main__":
    main()
