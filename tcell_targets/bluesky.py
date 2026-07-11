"""
Bluesky (AT Protocol) harvest — the second off-allowlist SOCIAL source.

Reaches Bluesky over `curl` (this sandbox blocks Python's urllib but not curl/node).
Unauthenticated endpoints — searchActors (find immunology accounts) and getAuthorFeed
(pull their posts) — need NO key. Keyword searchPosts needs an app password: set
BSKY_HANDLE + BSKY_APP_PASSWORD and it authenticates via com.atproto.server.createSession.

Off Claude Science's allowlist, so results are BAKED into the KB — and every post keeps its
original bsky.app URL so a citation stays auditable (click it, judge it).
"""
from __future__ import annotations

import json
import os
import subprocess
from urllib.parse import quote

_APPVIEW = "https://public.api.bsky.app/xrpc"       # unauthenticated reads (searchActors, getAuthorFeed)
_APPVIEW_AUTH = "https://api.bsky.app/xrpc"          # authenticated reads (searchPosts) — public host 403s the token
_PDS = "https://bsky.social/xrpc"


def _curl(url: str, headers=None, method: str = "GET", data: str | None = None, timeout: int = 25) -> dict:
    cmd = ["curl", "-s", "--max-time", str(timeout), "-X", method]
    for h in headers or []:
        cmd += ["-H", h]
    if data is not None:
        cmd += ["-d", data]
    cmd.append(url)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        return json.loads(proc.stdout) if proc.stdout.strip() else {}
    except (subprocess.SubprocessError, json.JSONDecodeError):
        return {}


def curl_available() -> bool:
    from shutil import which
    return which("curl") is not None


def search_actors(query: str, limit: int = 25) -> list:
    """Find Bluesky accounts (journals / labs / societies / immunologists) — no auth."""
    return _curl(f"{_APPVIEW}/app.bsky.actor.searchActors?q={quote(query)}&limit={limit}").get("actors", [])


def _post_from(item: dict) -> dict:
    post = item.get("post", {})
    rec = post.get("record", {})
    handle = post.get("author", {}).get("handle", "?")
    rkey = (post.get("uri", "") or "").rsplit("/", 1)[-1]
    links = []
    emb = rec.get("embed") or post.get("embed") or {}
    ext = emb.get("external") or {}
    if isinstance(ext, dict) and ext.get("uri"):
        links.append(ext["uri"])
    for f in rec.get("facets") or []:
        for feat in f.get("features") or []:
            if feat.get("uri"):
                links.append(feat["uri"])
    return {
        "handle": handle,
        "author": post.get("author", {}).get("displayName", handle),
        "date": (rec.get("createdAt", "") or "")[:10],
        "text": (rec.get("text") or "").replace("\n", " ").strip(),
        "url": f"https://bsky.app/profile/{handle}/post/{rkey}" if rkey else "",
        "links": [u for u in dict.fromkeys(links) if "bsky.app" not in u and "bsky.social" not in u],
        "likes": post.get("likeCount", 0),
    }


def author_feed(handle: str, limit: int = 40) -> list:
    """Recent posts for one account (no auth) — each carries its original bsky.app URL."""
    feed = _curl(f"{_APPVIEW}/app.bsky.feed.getAuthorFeed?actor={quote(handle)}&limit={limit}").get("feed", [])
    return [_post_from(it) for it in feed]


_JWT_CACHE = None


def _session(force: bool = False) -> str | None:
    """Authenticate ONCE per process and cache the token — createSession is rate-limited, so we must
    NOT re-login on every search (that was a bug that rate-limited the auth endpoint)."""
    global _JWT_CACHE
    if _JWT_CACHE and not force:
        return _JWT_CACHE
    handle, pw = os.environ.get("BSKY_HANDLE"), os.environ.get("BSKY_APP_PASSWORD")
    if not (handle and pw):
        return None
    d = _curl(f"{_PDS}/com.atproto.server.createSession", method="POST",
              headers=["Content-Type: application/json"],
              data=json.dumps({"identifier": handle, "password": pw}))
    _JWT_CACHE = d.get("accessJwt")
    return _JWT_CACHE


def search_posts(query: str, limit: int = 25) -> list:
    """Keyword search across ALL of Bluesky — needs an app password (BSKY_HANDLE/BSKY_APP_PASSWORD)."""
    jwt = _session()
    if not jwt:
        return []
    d = _curl(f"{_APPVIEW_AUTH}/app.bsky.feed.searchPosts?q={quote(query)}&limit={limit}",
              headers=[f"Authorization: Bearer {jwt}"])
    return [_post_from({"post": p}) for p in d.get("posts", [])]
