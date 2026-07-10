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
from .assistant import _clean  # JSON-safe coercion (import-safe: no anthropic at import)

mcp = FastMCP(
    "tcell-target-explorer",
    instructions=(
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
        "MEMORY: this tool has a knowledge base — ALWAYS call kb_recall(entity) BEFORE re-deriving; "
        "after deriving or verifying something new, call kb_remember to file it with provenance so "
        "it is never re-derived, and kb_verdict to record the scientist's judgment. This is how it learns."
    ),
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
    The full 'why this target' case for one gene in one disease: enrichment odds ratio + FDR, the
    other genes in its enriched program (program_peers), GRN out-degree and its percentile among all
    regulators screened, knockdown verification across culture conditions, Th1/Th2 polarization, and
    its activation-state pattern + per-state out-degree. Returns null if the gene is not a candidate.
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
def kb_recall(entity: str) -> dict:
    """
    Read what the knowledge base already knows about a target gene or a disease — CALL THIS FIRST,
    before re-deriving. Returns the stored profile(s) with prior findings, novelty assessments, and
    scientist verdicts, or a note that it is not in the KB yet.
    """
    return kb.recall(entity)


@mcp.tool()
def kb_remember(gene: str, finding: str, source: str, disease: str = "") -> dict:
    """
    File a finding to the gene's target profile with provenance, so it is never re-derived. Route
    each finding to its specific gene (no catch-all dumping). Use for a derived hypothesis, a
    novelty/literature assessment, or a mechanism. Always pass a real `source` (e.g. a tool name,
    a PMID, 'Claude Science', or 'scientist').
    """
    return kb.remember(gene, finding, source, disease or None)


@mcp.tool()
def kb_verdict(gene: str, disease: str, grade: str, rationale: str = "") -> dict:
    """
    Record the scientist's verdict on a target — the reputation signal that accrues to its profile
    (e.g. 'put a student on it', 'probably wrong, skip', 'already known'). This is what makes the
    KB learn from the human's judgment across sessions.
    """
    return kb.verdict(gene, disease, grade, rationale)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
