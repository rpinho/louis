"""
Bulk community-signal harvest — the "run the engine, then listen for each lead" pipeline.

It runs the discovery engine to enumerate every candidate target the tool surfaces
(druggable regulator HANDLES + the disease RISK GENES / markers, across all diseases),
then searches X for EACH gene in an immune context and files the chatter into that gene's
KB profile. This is how the gene-indexed community layer gets built and shipped: the tool's
own discoveries become the search terms, so the field's bleeding-edge chatter is tied
directly to the leads we surface.

Recent-search is rate-limited (~60 requests / 15 min on the Basic tier), so the harvest
throttles and backs off; it writes to the KB as it goes, so partial progress always persists.

Run:
    python -m louis.harvest                 # priority set (handles + top markers)
    python -m louis.harvest --all           # every discovered gene (long; backs off)
    python -m louis.harvest --limit 40      # cap the number of genes
"""
from __future__ import annotations

import re
import sys
import time
from datetime import datetime

from . import core, community, kb

STATES_TOP_MODULES = 8


def _attribute(posts: list, genes: list) -> dict:
    """Map each returned post to whichever batch gene(s) it names (word-boundary, case-insensitive)."""
    out: dict[str, list] = {}
    compiled = [(g, re.compile(rf"(?<![A-Za-z0-9]){re.escape(g)}(?![A-Za-z0-9])", re.I)) for g in genes]
    for p in posts:
        txt = p["text"]
        for g, rx in compiled:
            if rx.search(txt):
                out.setdefault(g, []).append(p)
    return out


def _already_harvested_today(gene: str, today: str) -> bool:
    """True if this gene's profile already has today's harvest block (keeps re-runs idempotent)."""
    p = kb._target_path(gene)
    return p.exists() and f"harvested {today}" in p.read_text()


def collect_targets(top_modules: int = STATES_TOP_MODULES):
    """Enumerate {gene: sorted[diseases]} for druggable handles and for risk genes/markers."""
    handles: dict[str, set] = {}
    risk: dict[str, set] = {}

    def _sym(x):
        return x if isinstance(x, str) else (x.get("gene") or x.get("symbol") or "")

    for d in core.list_diseases():
        for m in core.disease_mechanisms(d, top_modules=top_modules):
            for h in m.get("candidate_handles", []):
                g = _sym(h)
                if g:
                    handles.setdefault(g, set()).add(d)
            for rg in m.get("disease_risk_genes", []):
                g = _sym(rg)
                if g:
                    risk.setdefault(g, set()).add(d)
    return handles, risk


def prioritized_genes(handles: dict, risk: dict, risk_min_diseases: int = 3):
    """
    Order genes by value: druggable handles first (the discovery output, the whole point),
    each by how many diseases it cuts across; then the recognizable cross-cutting markers
    (risk genes appearing in >= risk_min_diseases diseases). The obscure single-disease risk
    genes are left for a --all sweep.
    """
    h_sorted = sorted(handles, key=lambda g: (-len(handles[g]), g))
    r_sorted = [g for g in sorted(risk, key=lambda g: (-len(risk[g]), g))
                if len(risk[g]) >= risk_min_diseases and g not in handles]
    return h_sorted, r_sorted


def _search_with_backoff(gene, per_gene_top, cooldown, max_retries, verbose):
    """community_signal for one gene, retrying through rate-limit windows (~15 min on Basic)."""
    for attempt in range(max_retries + 1):
        sig = community.community_signal(gene, kind="target", top=per_gene_top)
        if not sig.get("rate_limited"):
            return sig
        if attempt < max_retries:
            if verbose:
                print(f"  … rate-limited on {gene}; cooling {cooldown}s "
                      f"(retry {attempt + 1}/{max_retries}).", flush=True)
            time.sleep(cooldown)
    return sig  # still rate-limited after retries


def harvest(genes, disease_map=None, per_gene_top=6, pause=1.5,
            cooldown=900, max_retries=3, verbose=True):
    """
    Search X for each gene (immune context) and file kept posts to its KB profile.
    Idempotent per day; retries through rate-limit windows so no gene is silently skipped.
    Returns {filed: {gene: n}, empty: [...], rate_limited: [...], errors: {...}, skipped: [...]}.
    """
    filed, empty, rate_limited, errors, skipped = {}, [], [], {}, []
    today = datetime.now().strftime("%Y-%m-%d")
    for i, gene in enumerate(genes, 1):
        if _already_harvested_today(gene, today):
            skipped.append(gene)
            continue
        sig = _search_with_backoff(gene, per_gene_top, cooldown, max_retries, verbose)
        if sig.get("rate_limited"):
            rate_limited.append(gene)
            if verbose:
                print(f"  [{i}/{len(genes)}] {gene}: rate-limited (skipped)", flush=True)
            continue
        posts = sig.get("posts", [])
        if sig.get("error"):
            errors[gene] = sig["error"]
        if posts:
            kb.remember_signal(gene, posts, query=sig.get("query", ""),
                               harvested=sig.get("harvested", ""), kind="target")
            filed[gene] = len(posts)
            if verbose:
                top = posts[0]
                print(f"  [{i}/{len(genes)}] {gene}: {len(posts)} posts  "
                      f"(top: @{top['handle']} — {top['text'][:60]})", flush=True)
        else:
            empty.append(gene)
            if verbose:
                print(f"  [{i}/{len(genes)}] {gene}: —", flush=True)
        time.sleep(pause)
    return {"filed": filed, "empty": empty, "rate_limited": rate_limited,
            "errors": errors, "skipped": skipped}


def harvest_batched(genes, batch_size=16, per_gene_top=6, pause=1.5,
                    cooldown=900, max_retries=3, verbose=True):
    """
    Bulk harvest via OR-batched search — ~1 call per `batch_size` genes instead of one per gene,
    so the whole priority set fits in a rate-limit window or two. Attributes each returned post to
    its gene(s), keeps the research-grade ones, and files them. Idempotent per day.
    """
    filed, rate_limited, errors = {}, [], {}
    today = datetime.now().strftime("%Y-%m-%d")
    todo = [g for g in genes if not _already_harvested_today(g, today)]
    skipped = [g for g in genes if g not in set(todo)]
    batches = [todo[i:i + batch_size] for i in range(0, len(todo), batch_size)]
    if verbose:
        print(f"{len(todo)} genes to harvest in {len(batches)} batches "
              f"({len(skipped)} already done today).", flush=True)

    for bi, batch in enumerate(batches, 1):
        res = community.search_batch(batch, kind="target")
        for attempt in range(max_retries):        # ride out rate-limit windows
            if not res.get("rate_limited"):
                break
            if verbose:
                print(f"  batch {bi}: rate-limited, cooling {cooldown}s (retry {attempt + 1}/{max_retries})",
                      flush=True)
            time.sleep(cooldown)
            res = community.search_batch(batch, kind="target")
        if res.get("rate_limited"):
            rate_limited.extend(batch)
            if verbose:
                print(f"  batch {bi}/{len(batches)}: rate-limited (skipped {len(batch)} genes)", flush=True)
            continue
        if res.get("error"):
            errors[f"batch{bi}"] = res["error"]
        posts = res.get("posts", [])
        by_gene = _attribute(posts, batch)
        hits = []
        for g in batch:
            final = community._finalize(by_gene.get(g, []), per_gene_top)
            if final:
                kb.remember_signal(g, final, query=res.get("query", ""),
                                   harvested=res.get("harvested", ""), kind="target")
                filed[g] = len(final)
                hits.append(f"{g}({len(final)})")
        if verbose:
            print(f"  batch {bi}/{len(batches)} [{len(batch)} genes, {len(posts)} posts]: "
                  f"{', '.join(hits) if hits else '—'}", flush=True)
        time.sleep(pause)

    empty = [g for g in todo if g not in filed and g not in set(rate_limited)]
    return {"filed": filed, "empty": empty, "rate_limited": rate_limited,
            "errors": errors, "skipped": skipped}


# Curated immune pathways / mechanisms — the "and pathways" axis. Searched with the disease
# tech-basket (research-anchored), filed as topic profiles in the KB.
PATHWAYS = [
    "Th17", "Treg", "T follicular helper", "JAK-STAT", "IL-23", "IL-17", "IL-2 signaling",
    "interferon signaling", "TCR signaling", "immune checkpoint", "T cell exhaustion",
    "immunometabolism", "autoimmune tolerance", "Th1 Th2 balance", "CAR-T autoimmune",
    "epigenetic T cell", "gut mucosal immunity", "cytokine signaling",
]


def harvest_pathways(pathways=None, per_top=8, pause=2.0, cooldown=900, max_retries=3, verbose=True):
    """Harvest community signal for immune pathways/mechanisms — filed as KB topic profiles."""
    pathways = pathways or PATHWAYS
    filed, empty, rate_limited = {}, [], []
    today = datetime.now().strftime("%Y-%m-%d")
    for i, topic in enumerate(pathways, 1):
        p = kb._topic_path(topic)
        if p.exists() and f"harvested {today}" in p.read_text():
            continue
        sig = community.community_signal(topic, kind="disease", top=per_top)
        for attempt in range(max_retries):
            if not sig.get("rate_limited"):
                break
            if verbose:
                print(f"  pathways: rate-limited on {topic}, cooling {cooldown}s "
                      f"(retry {attempt + 1}/{max_retries})", flush=True)
            time.sleep(cooldown)
            sig = community.community_signal(topic, kind="disease", top=per_top)
        if sig.get("rate_limited"):
            rate_limited.append(topic)
            continue
        posts = sig.get("posts", [])
        if posts:
            kb.remember_signal(topic, posts, query=sig.get("query", ""),
                               harvested=sig.get("harvested", ""), kind="topic")
            filed[topic] = len(posts)
            if verbose:
                print(f"  [{i}/{len(pathways)}] {topic}: {len(posts)} posts "
                      f"(top: @{posts[0]['handle']})", flush=True)
        else:
            empty.append(topic)
            if verbose:
                print(f"  [{i}/{len(pathways)}] {topic}: —", flush=True)
        time.sleep(pause)
    idx = kb.reindex()
    print(f"Reindexed KB: {idx['n']} profiles.")
    return {"filed": filed, "empty": empty, "rate_limited": rate_limited}


# The DRUGS/compounds dimension — the clinical matter our validation surfaces for each lead.
# Searching the drug names closes the loop over ALL the tool's outputs (genes + pathways + DRUGS).
DRUG_MAP = {
    "DOT1L": ["pinometostat"],
    "MEN1": ["revumenib", "ziftomenib"],
    "GLS": ["telaglenastat", "CB-839"],
    "AHR": ["tapinarof"],
    "RIPK1": ["eclitasertib"],
    "JAK2": ["upadacitinib", "baricitinib"],
    "TYK2": ["deucravacitinib"],
    "IL23R": ["risankizumab", "guselkumab"],
    "HDAC7": ["vorinostat"],
}


def harvest_drugs(drug_map=None, per_top=6, pause=2.0, verbose=True):
    """Search X for the clinical compounds tied to each validated target; file to that target's profile."""
    drug_map = drug_map or DRUG_MAP
    filed = {}
    for target, drugs in drug_map.items():
        for drug in drugs:
            p = kb._target_path(target)
            if p.exists() and f"drug:{drug} —" in p.read_text():   # already filed — idempotent
                if verbose:
                    print(f"  {target}/{drug}: (already filed)", flush=True)
                continue
            sig = community.community_signal(drug, kind="drug", top=per_top)  # clinical/pipeline context
            posts = sig.get("posts", [])
            if posts:
                kb.remember_signal(target, posts, kind="target",
                                   query=f"drug:{drug} — {sig.get('query', '')}",
                                   harvested=sig.get("harvested", ""))
                filed[f"{target}/{drug}"] = len(posts)
            if verbose:
                print(f"  {target}/{drug}: {len(posts) if posts else '—'}", flush=True)
            time.sleep(pause)
    idx = kb.reindex()
    print(f"Reindexed KB: {idx['n']} profiles.")
    return filed


_BSKY_JUNK = {"rridrobot.bsky.social", "cbs6-richmond", "newsarea", "autismcapital-rtm", "scienceofpd"}


def _bsky_filter(posts, per_top):
    kept = []
    for p in posts:
        if p["handle"] in _BSKY_JUNK or len(p["text"]) < 40:
            continue
        u = {"name": p.get("author", ""), "username": p["handle"], "verified": False}
        p["high_signal"] = community._signal_name(u)
        if not p["high_signal"] and community._count(p["text"], community._NOISE_TERMS) > 0:
            continue
        if not (p["high_signal"] or community._count(p["text"], community._RESEARCH_TERMS) >= 2):
            continue
        p["_score"] = community._score(p["text"], u, {"like_count": p.get("likes", 0), "retweet_count": 0})
        kept.append(p)
    kept.sort(key=lambda x: -x["_score"])
    seen, ded = set(), []
    for p in kept:
        k = "".join(p["text"].lower().split())[:80]
        if k in seen:
            continue
        seen.add(k); ded.append(p)
    return ded[:per_top]


def bluesky_terms():
    """
    Leads as Bluesky search terms, VALUE-ORDERED so the loop sweeps the best first:
    druggable handles (by #diseases) -> cross-cutting markers -> pathways -> diseases -> obscure tail.
    Gene searches carry a ' T cell' immune context (a bare symbol like ACTA2 pulls smooth-muscle chatter).
    """
    handles, risk = collect_targets()
    h_sorted = sorted(handles, key=lambda g: (-len(handles[g]), g))
    r_sorted = [g for g in sorted(risk, key=lambda g: (-len(risk[g]), g))
                if len(risk[g]) >= 3 and g not in handles]
    tail = [g for g in sorted(risk) if g not in handles and g not in set(r_sorted)]
    return ([(f"{g} T cell", g, "target") for g in h_sorted + r_sorted]
            + [(t, t, "topic") for t in PATHWAYS]
            + [(d, d, "disease") for d in core.list_diseases()]
            + [(f"{g} T cell", g, "target") for g in tail])


def harvest_bluesky(terms=None, per_top=5, pause=0.7, limit=None, verbose=True):
    """Authenticated Bluesky keyword sweep of the leads -> filed with provenance. Idempotent per day."""
    from . import bluesky
    if not bluesky._session():
        print("Bluesky: no auth — set BSKY_HANDLE/BSKY_APP_PASSWORD (source .secrets/bsky.env).")
        return {}
    terms = terms or bluesky_terms()
    today = datetime.now().strftime("%Y-%m-%d")
    paths = {"target": kb._target_path, "disease": kb._disease_path, "topic": kb._topic_path}
    # Swept-ledger: record EVERY attempted lead (even 0-yield) so the tail isn't re-swept forever
    # (a baked profile is the marker for hits; this covers the misses). Resets daily.
    ledger_file = kb.KB_DIR / "_bluesky_swept.txt"
    ledger = set()
    if ledger_file.exists():
        rows = ledger_file.read_text().splitlines()
        if rows and rows[0] == today:
            ledger = set(rows[1:])
    filed, done = {}, 0
    for term, entity, kind in terms:
        if entity in ledger:
            continue
        p = paths[kind](entity)
        if p.exists() and f"Community signal (Bluesky) — harvested {today}" in p.read_text():
            ledger.add(entity); continue          # already baked -> mark done
        posts = _bsky_filter(bluesky.search_posts(term, limit=25), per_top)
        if posts:
            kb.remember_signal(entity, posts, query=f"Bluesky searchPosts: {term}",
                               kind=kind, platform="Bluesky", harvested=today)
            filed[entity] = len(posts)
            if verbose:
                print(f"  {term:<28} -> {entity} ({kind}): {len(posts)}", flush=True)
        ledger.add(entity)                          # mark attempted (hit OR miss)
        done += 1
        if limit and done >= limit:
            break
        time.sleep(pause)
    ledger_file.write_text(today + "\n" + "\n".join(sorted(ledger)))
    kb.reindex()
    print(f"Bluesky: filed {sum(filed.values())} posts across {len(filed)} leads (swept {done} terms).")
    return filed


_REDDIT_JUNK = {"AutoModerator", "[deleted]"}


def _reddit_filter(posts, per_top):
    """Keep research-grade Reddit posts. No curated-handle signal here (reddit authors aren't the
    immunology accounts we track), so lean on research-term density + noise rejection; the fact that
    we searched research subreddits already does a lot of the filtering."""
    kept = []
    for p in posts:
        if p["handle"] in _REDDIT_JUNK or len(p["text"]) < 40:
            continue
        research = community._count(p["text"], community._RESEARCH_TERMS)
        p["high_signal"] = research >= 3
        if not p["high_signal"] and community._count(p["text"], community._NOISE_TERMS) > 0:
            continue
        if research < 2:
            continue
        u = {"name": p.get("author", ""), "username": p["handle"], "verified": False}
        p["_score"] = community._score(p["text"], u, {"like_count": p.get("likes", 0), "retweet_count": 0})
        kept.append(p)
    kept.sort(key=lambda x: -x["_score"])
    seen, ded = set(), []
    for p in kept:
        k = "".join(p["text"].lower().split())[:80]
        if k in seen:
            continue
        seen.add(k); ded.append(p)
    return ded[:per_top]


def reddit_terms():
    """
    Leads as Reddit search terms, VALUE-ORDERED (handles -> cross-cutting markers -> pathways ->
    diseases -> obscure tail), same as Bluesky. Gene searches carry a ' T cell' immune context so a
    bare symbol doesn't pull unrelated chatter; diseases/pathways search as-is across research subs.
    """
    handles, risk = collect_targets()
    h_sorted = sorted(handles, key=lambda g: (-len(handles[g]), g))
    r_sorted = [g for g in sorted(risk, key=lambda g: (-len(risk[g]), g))
                if len(risk[g]) >= 3 and g not in handles]
    tail = [g for g in sorted(risk) if g not in handles and g not in set(r_sorted)]
    return ([(f"{g} T cell", g, "target") for g in h_sorted + r_sorted]
            + [(t, t, "topic") for t in PATHWAYS]
            + [(d, d, "disease") for d in core.list_diseases()]
            + [(f"{g} T cell", g, "target") for g in tail])


def harvest_reddit(terms=None, per_top=5, pause=0.8, limit=None, verbose=True):
    """Reddit research-subreddit sweep of the leads -> filed with provenance. Idempotent per day."""
    from . import reddit
    if not reddit.curl_available():
        print("Reddit: curl unavailable — cannot reach the API.")
        return {}
    mode = "OAuth" if reddit._token() else "public .json (no app; set REDDIT_CLIENT_ID/SECRET to upgrade)"
    if verbose:
        print(f"Reddit: auth mode = {mode}", flush=True)
    terms = terms or reddit_terms()
    today = datetime.now().strftime("%Y-%m-%d")
    paths = {"target": kb._target_path, "disease": kb._disease_path, "topic": kb._topic_path}
    ledger_file = kb.KB_DIR / "_reddit_swept.txt"
    ledger = set()
    if ledger_file.exists():
        rows = ledger_file.read_text().splitlines()
        if rows and rows[0] == today:
            ledger = set(rows[1:])
    filed, done = {}, 0
    for term, entity, kind in terms:
        if entity in ledger:
            continue
        p = paths[kind](entity)
        if p.exists() and f"Community signal (Reddit) — harvested {today}" in p.read_text():
            ledger.add(entity); continue
        posts = _reddit_filter(reddit.search_research(term, limit=25), per_top)
        if posts:
            kb.remember_signal(entity, posts, query=f"Reddit search (research subs): {term}",
                               kind=kind, platform="Reddit", harvested=today)
            filed[entity] = len(posts)
            if verbose:
                print(f"  {term:<28} -> {entity} ({kind}): {len(posts)}", flush=True)
        ledger.add(entity)
        done += 1
        if limit and done >= limit:
            break
        time.sleep(pause)
    ledger_file.write_text(today + "\n" + "\n".join(sorted(ledger)))
    kb.reindex()
    print(f"Reddit: filed {sum(filed.values())} posts across {len(filed)} leads (swept {done} terms).")
    return filed


def write_rollup(summary: dict, handles: dict, risk: dict):
    """Write a navigable index of genes that lit up this week -> kb/community_signal.md."""
    lines = ["# Community signal index",
             "",
             "*Genes from the discovery engine that have live immune-context chatter on X "
             "this week. Built by `python -m louis.harvest`. Each links to that gene's "
             "profile, where the posts are filed with provenance.*",
             ""]
    filed = summary.get("filed", {})
    for gene in sorted(filed, key=lambda g: -filed[g]):
        role = "handle" if gene in handles else "marker"
        ndis = len((handles.get(gene) or risk.get(gene) or set()))
        lines.append(f"- **[{gene}](wiki/targets/{gene}.md)** — {filed[gene]} posts "
                     f"({role}, {ndis} diseases)")
    lines.append("")
    (kb.KB_DIR / "community_signal.md").write_text("\n".join(lines))
    return kb.KB_DIR / "community_signal.md"


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)

    if "--bluesky" in argv:
        lim = int(argv[argv.index("--limit") + 1]) if "--limit" in argv else None
        print(f"Bluesky keyword sweep of the leads (limit={lim})…")
        harvest_bluesky(limit=lim)
        return

    if "--reddit" in argv:
        lim = int(argv[argv.index("--limit") + 1]) if "--limit" in argv else None
        print(f"Reddit research-subreddit sweep of the leads (limit={lim})…")
        harvest_reddit(limit=lim)
        return

    if "--drugs" in argv:
        n = sum(len(v) for v in DRUG_MAP.values())
        print(f"Harvesting community signal for {n} clinical compounds across {len(DRUG_MAP)} targets…")
        filed = harvest_drugs()
        print(f"\nDone. filed={len(filed)}: {', '.join(f'{k}({v})' for k, v in filed.items())}")
        return filed

    if "--pathways" in argv:
        print(f"Harvesting community signal for {len(PATHWAYS)} pathways/mechanisms…")
        summary = harvest_pathways()
        print(f"\nDone. filed={len(summary['filed'])}  empty={len(summary['empty'])}  "
              f"rate_limited={len(summary['rate_limited'])}")
        if summary["filed"]:
            print("Pathways with chatter:",
                  ", ".join(f"{t}({n})" for t, n in summary["filed"].items()))
        return summary

    handles, risk = collect_targets()
    h_sorted, r_sorted = prioritized_genes(handles, risk)

    if "--all" in argv:
        genes = h_sorted + r_sorted + [g for g in risk if g not in handles and g not in r_sorted]
    else:
        genes = h_sorted + r_sorted  # priority: all handles + cross-cutting markers

    if "--limit" in argv:
        n = int(argv[argv.index("--limit") + 1])
        genes = genes[:n]

    print(f"Harvesting community signal for {len(genes)} genes "
          f"({len(handles)} handles + {len(r_sorted)} cross-cutting markers in priority set)…")
    summary = harvest_batched(genes)
    print(f"\nDone. filed={len(summary['filed'])}  empty={len(summary['empty'])}  "
          f"rate_limited={len(summary['rate_limited'])}  errors={len(summary['errors'])}")
    if summary["filed"]:
        path = write_rollup(summary, handles, risk)
        print(f"Rollup -> {path}")
        hot = sorted(summary["filed"], key=lambda g: -summary["filed"][g])[:15]
        print("Genes with the most chatter:", ", ".join(f"{g}({summary['filed'][g]})" for g in hot))
    idx = kb.reindex()   # rebuild the fast lookup index after writing profiles
    print(f"Reindexed KB: {idx['n']} profiles ({len(idx['with_signal'])} with community signal).")
    return summary


if __name__ == "__main__":
    main()
