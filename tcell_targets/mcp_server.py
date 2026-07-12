"""
T-Cell Target Explorer — MCP server.

Runs the engine as agent-native tools *inside* Claude (Desktop / Code / any MCP
host). The host LLM does the reasoning on the user's subscription — no API key,
no metered credits, no separate app — and this server grounds every answer in the
real CD4+ T-cell Perturb-seq evidence: disease enrichment, GRN influence, CRISPRi
knockdown QC (the trust flag), and activation-state dependence.

Run (stdio transport, for Claude Desktop / Claude Code):

    python -m tcell_targets.mcp_server

Register in Claude Code:

    claude mcp add tcell-target-explorer -- \
        /path/to/.venv/bin/python -m tcell_targets.mcp_server
"""
from __future__ import annotations
from mcp.server.fastmcp import FastMCP
from . import core
from . import kb
from . import community
from .assistant import _clean, default_use_memory  # import-safe: no anthropic at import


def _no_memory() -> bool:
    """No-memory mode (env TCELL_NO_MEMORY truthy): the kb_* tools are inert and nothing reads kb/."""
    return not default_use_memory()


# In no-memory mode the memory tools short-circuit and won't touch kb/, so tell the host not
# to lean on them: derive fresh from the live tools instead of recall-before-derive.
_MEMORY_DISABLED = {"disabled": True, "note": "memory disabled (no-memory mode) — kb/ not consulted"}

_INSTRUCTIONS_HEAD = (
    "Tools for finding and vetting candidate CD4+ T-cell regulator targets for autoimmune "
    "diseases, from a genome-scale CRISPRi Perturb-seq screen (Marson/Pritchard 2025). "
    "Always lead with the TRUST verdict: a target's confidence flag comes from whether its "
    "knockdown was verified on-target and whether the guide is clean — a high disease-"
    "enrichment with an unconfirmed knockdown is a caution, not a recommendation. Also surface "
    "the ACTIVATION STATE a target acts in (Rest/Stim8hr/Stim48hr): 'activation-induced' means "
    "it does little in resting cells and switches on only when the T cell is stimulated. These "
    "are hypotheses to prioritize bench work, not clinical claims. "
    "For DISCOVERY (novel leads, not the obvious known target), use disease_mechanisms: it wires "
    "druggable regulator handles to the disease's own risk-gene modules — recover the obvious "
    "Th17 handles as a positive control, then surface understudied ones and assess their NOVELTY "
    "yourself (your knowledge + web/PubMed). "
    "LISTEN (bleeding-edge): community_signal pulls what immunologists are posting on X/Twitter "
    "RIGHT NOW about a gene or disease — lab announcements, preprint drops, pipeline news that "
    "isn't in the literature yet. This is signal the paper/database connectors can't see. It runs "
    "live where X access exists (Claude Code/Desktop); "
)
_INSTRUCTIONS_MEMORY = (
    "elsewhere read the baked signal via kb_recall. "
    "MEMORY: this tool has a knowledge base — ALWAYS call kb_recall(entity) BEFORE re-deriving; "
    "after deriving or verifying something new, call kb_remember to file it with provenance so "
    "it is never re-derived, kb_remember_signal to preserve the community chatter, and kb_verdict "
    "to record the scientist's judgment. The workflow is discover -> validate -> listen -> remember. "
    "This is how it learns."
)
_INSTRUCTIONS_NOMEMORY = (
    "elsewhere it simply returns a note (no baked signal in this mode). "
    "NO-MEMORY MODE: the knowledge base is DISABLED for this instance — the kb_* tools are inert "
    "(they read and write nothing) and there is no stored history. Do NOT rely on recall; derive "
    "every answer fresh from the live tools (discover -> validate -> listen) and your own reasoning."
)

mcp = FastMCP(
    "tcell-target-explorer",
    instructions=_INSTRUCTIONS_HEAD + (_INSTRUCTIONS_NOMEMORY if _no_memory() else _INSTRUCTIONS_MEMORY),
)

_COLS = ["gene", "confidence", "disease_odds_ratio", "controls_n_genes",
         "state_pattern", "kd_verified", "offtarget_risk", "th2_vs_th1_lfc", "p_adj_fdr"]


@mcp.tool()
def list_diseases() -> list[str]:
    """List the autoimmune diseases that have disease-enriched CD4+ T-cell programs in the screen."""
    return core.list_diseases()


@mcp.tool()
def disease_targets(disease: str, top: int = 15) -> list[dict]:
    """
    Ranked candidate CD4+ T-cell regulator targets for an autoimmune disease.

    Each row: disease_odds_ratio (enrichment of the gene's program in the disease's genetics),
    controls_n_genes (GRN out-degree — downstream genes it controls when perturbed), state_pattern
    (activation-induced / resting-state / activation-modulated / constitutive / minimal),
    kd_verified + offtarget_risk (CRISPRi QC), a plain-English confidence flag, and th2_vs_th1_lfc
    (>0 Th2, <0 Th1). Ranked by disease enrichment then network influence.
    """
    df = core.disease_targets(disease)
    if df.empty:
        return []
    return _clean(df.head(int(top))[_COLS].to_dict("records"))


@mcp.tool()
def target_evidence(disease: str, gene: str) -> dict | None:
    """
    The full 'why this target' case for one gene in one disease. Resolves BOTH kinds of candidate:
    a ranked enrichment target (kind='ranked_target') returns its odds ratio + FDR, program_peers,
    GRN out-degree + percentile, knockdown QC, Th1/Th2 polarization, and activation-state pattern;
    a module co-cluster HANDLE from disease_mechanisms (kind='module_handle') returns the risk-gene
    module(s) it controls plus its out-degree/percentile/state/trust — so a handle you discovered
    resolves here instead of dead-ending. Returns null only if the gene is not in the screen for the disease.
    """
    return _clean(core.target_evidence(disease, gene))


@mcp.tool()
def regulator_detail(gene: str) -> dict:
    """
    Per-condition GRN out-degree and CRISPRi QC (knockdown verified, off-target) for one regulator
    gene across the screen's culture conditions (Rest, Stim8hr, Stim48hr).
    """
    return _clean(core.regulator_detail(gene))


@mcp.tool()
def state_profile(gene: str) -> dict | None:
    """
    How a regulator's GRN influence shifts across T-cell activation states. Returns out-degree per
    state (Rest/Stim8hr/Stim48hr), which state it peaks in, and a label: 'activation-induced' (quiet
    at rest, switches on when stimulated), 'resting-state' (fades with activation), 'activation-
    modulated' (varies), 'constitutive' (steady), or 'minimal'. Answers which targets act only in
    activated vs resting T cells — the state-dependence a bench scientist would otherwise need a
    whole experiment to read. Returns null if the gene was not directly perturbed.
    """
    return _clean(core.state_profile(gene))


@mcp.tool()
def disease_mechanisms(disease: str, top_modules: int = 8) -> list[dict]:
    """
    MECHANISTIC DISCOVERY — go beyond the obvious top-enrichment gene.

    Returns the GRN modules whose downstream program is enriched in the disease's OWN risk genes,
    each with: the specific risk genes, the activation state it fires in, and the candidate
    regulator HANDLES (druggable entry points) that co-cluster with that module — trust-first,
    with knockdown QC and activation state.

    Use this to generate novel, testable hypotheses: 'perturb handle X to move the disease risk
    program [genes] in state S'. The obvious Th17 handles (STAT3/BATF) show up as the positive
    control; the value is the understudied, druggable handles (e.g. metabolic/epigenetic enzymes)
    wired to known risk genes. Assess each handle's NOVELTY yourself (your knowledge + web/PubMed),
    then persist it with kb_remember so it is not re-derived. NOTE: module-level co-cluster links,
    i.e. candidate upstream controllers to TEST — not proven gene-level edges.
    """
    return _clean(core.disease_mechanisms(disease, top_modules=int(top_modules)))


@mcp.tool()
def community_signal(entity: str, kind: str = "target", top: int = 10, min_engagement: int = 0) -> dict:
    """
    LISTEN — the bleeding-edge, pre-paper layer. Recent X/Twitter chatter about a target gene
    (kind='target') or a disease (kind='disease') in a CD4+ T-cell / immunology context: lab
    announcements, preprint drops, conference posts, therapy-pipeline news — the signal that is
    NOT in the literature yet, and that the paper/database connectors can't see.

    Returns curated recent posts (labs / journals / news desks surfaced first) with handle, date,
    engagement, text, and link. `min_engagement` filters out low-signal posts. Runs live only where
    X access exists (Claude Code/Desktop); in the Claude Science sandbox it returns a note — read
    the baked signal via kb_recall there. Treat posts as leads to verify, not validated claims;
    after reviewing, persist the notable ones with kb_remember_signal.
    """
    return _clean(community.community_signal(entity, kind=kind, top=int(top),
                                             min_engagement=int(min_engagement)))


@mcp.tool()
def kb_remember_signal(entity: str, kind: str = "target") -> dict:
    """
    MEMORY — harvest current community signal for a gene/disease AND file it to the KB profile in
    one step (fetch + remember). Preserves the pre-paper chatter with provenance (handle, date, link)
    so it is remembered across sessions and ships with the tool even where live X search can't run.
    Use after discovery/validation to capture what the field is saying right now.
    """
    if _no_memory():
        return dict(_MEMORY_DISABLED, entity=entity)
    sig = community.community_signal(entity, kind=kind, top=12)
    if not sig.get("posts"):
        return {"entity": entity, "filed": 0,
                "note": sig.get("note") or sig.get("error") or "no community posts found"}
    return kb.remember_signal(entity, sig["posts"], query=sig.get("query", ""),
                              harvested=sig.get("harvested", ""), kind=kind)


@mcp.tool()
def kb_recall(entity: str) -> dict:
    """
    Read what the knowledge base already knows about a target gene or a disease — CALL THIS FIRST,
    before re-deriving. Returns the stored profile(s) with prior findings, novelty assessments, and
    scientist verdicts, or a note that it is not in the KB yet.
    """
    if _no_memory():
        return dict(_MEMORY_DISABLED, entity=entity)
    return kb.recall(entity)


@mcp.tool()
def kb_query(text: str = "", disease: str = "", gene: str = "", grade: str = "",
             rec_type: str = "", state: str = "", source_tier: str = "", limit: int = 25) -> dict:
    """
    DIMENSIONAL SEARCH across the WHOLE knowledge base at once (not one entity) — the fast way to answer
    cross-cutting questions: 'all grade-A druggable leads', 'the epigenetic axis across diseases',
    'resting-state handles for lupus', 'what is active on DOT1L across every disease'. Every filter is
    optional and ANDs together; combine with a full-text `text` query (FTS5). rec_type: verdict | finding
    | community_post | preprint | conference | lit_scan. source_tier: screen | claude_science | lit_scan |
    community | verdict. Use kb_recall for one gene/disease; kb_query for portfolio / cross-disease views.
    """
    if _no_memory():
        return dict(_MEMORY_DISABLED, query=text or gene or disease)
    from . import kb_index
    return kb_index.query(text=text or None, disease=disease or None, gene=gene or None,
                          grade=grade or None, rec_type=rec_type or None, state=state or None,
                          source_tier=source_tier or None, limit=limit)


@mcp.tool()
def kb_search(term: str = "", kind: str = "", has_signal: bool = False,
              has_verdict: bool = False, content: bool = False, limit: int = 25) -> dict:
    """
    MEMORY/SEARCH — fast lookup ACROSS the knowledge base, backed by an index (not a full scan).
    Find target/disease profiles by name (or, with content=True, by any text inside them), and filter
    to those with community signal (has_signal) or a recorded verdict (has_verdict). Use to see what
    the KB already knows before deriving, or to browse accumulated leads (e.g. all targets the field
    is currently discussing). Targets with a verdict + signal rank first.
    """
    if _no_memory():
        return dict(_MEMORY_DISABLED, query=term)
    return kb.search(term=term, kind=kind or None, signal=has_signal or None,
                     verdict=has_verdict or None, content=content, limit=int(limit))


@mcp.tool()
def kb_remember(gene: str, finding: str, source: str, disease: str = "") -> dict:
    """
    File a finding to the gene's target profile with provenance, so it is never re-derived. Route
    each finding to its specific gene (no catch-all dumping). Use for a derived hypothesis, a
    novelty/literature assessment, or a mechanism. Always pass a real `source` (e.g. a tool name,
    a PMID, 'Claude Science', or 'scientist').
    """
    if _no_memory():
        return dict(_MEMORY_DISABLED, gene=gene)
    return kb.remember(gene, finding, source, disease or None)


@mcp.tool()
def kb_verdict(gene: str, disease: str, grade: str, rationale: str = "") -> dict:
    """
    Record the scientist's verdict on a target — the reputation signal that accrues to its profile
    (e.g. 'put a student on it', 'probably wrong, skip', 'already known'). This is what makes the
    KB learn from the human's judgment across sessions.
    """
    if _no_memory():
        return dict(_MEMORY_DISABLED, gene=gene)
    return kb.verdict(gene, disease, grade, rationale)


def main() -> None:
    """stdio by default (Claude Code/Desktop). Set TCELL_MCP_TRANSPORT=http to serve over
    streamable-HTTP instead — for hosts that connect by URL (e.g. Claude Science's Remote URL,
    whose sandbox blocks executing a local command)."""
    import os
    transport = os.environ.get("TCELL_MCP_TRANSPORT", "stdio").lower()
    if transport in ("http", "streamable-http", "sse"):
        mcp.settings.host = os.environ.get("TCELL_MCP_HOST", "127.0.0.1")
        mcp.settings.port = int(os.environ.get("TCELL_MCP_PORT", "8766"))
        mcp.run(transport="sse" if transport == "sse" else "streamable-http")
    else:
        mcp.run()


if __name__ == "__main__":
    main()
