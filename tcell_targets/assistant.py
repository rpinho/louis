"""
Claude-powered Q&A over the T-cell target data — the reasoning layer.

The scientist asks in plain English; Claude answers by *querying the same
precomputed evidence the rest of the app shows* (enrichment, GRN out-degree,
knockdown QC, polarization), grounds every quantitative claim in those tool
results, and leads with the trust verdict. Claude is the engine here — the tool
reasons over the data, it doesn't just display it.

Needs an Anthropic API key (env ANTHROPIC_API_KEY, or passed in from the UI).
"""
from __future__ import annotations
import os
import json
import math
from . import core

# Bio reasoning → default to Opus; override with TCELL_MODEL if desired.
MODEL = os.environ.get("TCELL_MODEL", "claude-opus-4-8")

SYSTEM = """You are a target-discovery assistant for a bench immunologist. You sit on top of a \
genome-scale CD4+ T-cell CRISPRi Perturb-seq screen (Zhu, Dann, ..., Pritchard, Marson 2025): every \
gene was knocked down in primary human CD4+ T cells, and the authors precomputed which regulators \
drive which programs, which programs are enriched in autoimmune-disease genetics, and the QC of each \
CRISPRi guide. Your job is to help the scientist find and *vet* candidate regulators to target.

How to answer:
- ALWAYS query the tools for real data before making any quantitative claim. Never invent numbers. \
Cite the actual values you get back (odds ratio, genes controlled, percentile, FDR).
- Lead with the trust verdict. The confidence flag is the whole point: say plainly whether a hit's \
knockdown was verified on-target and whether the guide is clean. A high disease-enrichment with an \
UNCONFIRMED knockdown is a caution, not a recommendation — call that out explicitly (it's the \
difference between a target worth bench time and one that will waste it).
- Surface the activation state. A T cell's regulators change with its state, and the screen measured \
three (Rest / Stim8hr / Stim48hr). When it matters, say which state a target acts in — e.g. \
'activation-induced' means it does little in resting cells and switches on only when the T cell is \
stimulated. This is exactly what bench immunologists say they can't self-serve, so lean into it; use \
state_profile for the per-state trajectory. Note you are surfacing the THREE measured states, not \
predicting unmeasured ones.
- Be decisive and concise: recommendation first, then the 2-4 numbers that justify it. Short beats long.
- You may add briefly established biology (e.g. STAT3/IRF4/BATF are core Th17 regulators) but keep it \
clearly separate from the data, and never claim clinical efficacy — these are hypotheses to \
prioritize experiments, not clinical claims.
- If asked something the data can't answer, say so rather than guessing."""

TOOLS = [
    {
        "name": "list_diseases",
        "description": "List the autoimmune diseases that have disease-enriched T-cell programs in this dataset.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "disease_targets",
        "description": (
            "Ranked candidate CD4+ T-cell regulator targets for a disease. Each row has: disease_odds_ratio "
            "(enrichment of the gene's program in the disease's genetics), controls_n_genes (GRN out-degree — "
            "how many downstream genes it controls when perturbed), kd_verified (was the CRISPRi knockdown "
            "confirmed on-target), offtarget_risk (is the guide off-target), th2_vs_th1_lfc (>0 Th2, <0 Th1), "
            "and a plain-English confidence flag. Ranked by enrichment then network influence."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "disease": {"type": "string", "description": "e.g. \"Crohn's disease\", \"asthma\""},
                "top": {"type": "integer", "description": "max rows to return (default 15)"},
            },
            "required": ["disease"],
        },
    },
    {
        "name": "target_evidence",
        "description": (
            "The full 'why this target' case for one gene in one disease: enrichment odds ratio + FDR, the "
            "other genes in its enriched program (program_peers), GRN out-degree and its percentile among all "
            "regulators screened, knockdown verification across culture conditions, and polarization."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "disease": {"type": "string"},
                "gene": {"type": "string", "description": "gene symbol, e.g. STAT3"},
            },
            "required": ["disease", "gene"],
        },
    },
    {
        "name": "regulator_detail",
        "description": (
            "Per-condition GRN out-degree and CRISPRi QC (knockdown verified, off-target) for one regulator "
            "gene across the screen's culture conditions (Rest, Stim8hr, Stim48hr)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"gene": {"type": "string"}},
            "required": ["gene"],
        },
    },
    {
        "name": "state_profile",
        "description": (
            "How a regulator's GRN influence shifts across T-cell activation states. Returns out-degree per "
            "state (Rest/Stim8hr/Stim48hr), which state it peaks in, and a label: 'activation-induced' (quiet "
            "at rest, switches on when the T cell is stimulated), 'resting-state' (fades with activation), "
            "'activation-modulated' (varies), 'constitutive' (steady), or 'minimal'. Use this to answer which "
            "targets act only in activated vs resting T cells — the state-dependence a bench scientist would "
            "otherwise need a whole experiment to read."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"gene": {"type": "string"}},
            "required": ["gene"],
        },
    },
]


def _clean(obj):
    """Make pandas/numpy/NaN values JSON-serializable."""
    if isinstance(obj, float) and math.isnan(obj):
        return None
    if isinstance(obj, dict):
        return {k: _clean(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_clean(v) for v in obj]
    if hasattr(obj, "item"):  # numpy scalar
        try:
            return obj.item()
        except Exception:
            return str(obj)
    return obj


_COLS = ["gene", "confidence", "disease_odds_ratio", "controls_n_genes",
         "state_pattern", "kd_verified", "offtarget_risk", "th2_vs_th1_lfc", "p_adj_fdr"]


def _dispatch(name: str, args: dict):
    try:
        if name == "list_diseases":
            return core.list_diseases()
        if name == "disease_targets":
            df = core.disease_targets(args["disease"])
            if df.empty:
                return {"note": f"no disease-enriched T-cell targets for {args['disease']!r}; "
                                "call list_diseases to check the exact name."}
            return _clean(df.head(int(args.get("top", 15)))[_COLS].to_dict("records"))
        if name == "target_evidence":
            return _clean(core.target_evidence(args["disease"], args["gene"]))
        if name == "regulator_detail":
            return _clean(core.regulator_detail(args["gene"]))
        if name == "state_profile":
            return _clean(core.state_profile(args["gene"]))
        return {"error": f"unknown tool {name}"}
    except Exception as e:  # let Claude see + recover from a bad call
        return {"error": f"{type(e).__name__}: {e}"}


def answer(question: str, history: list | None = None, api_key: str | None = None,
           max_rounds: int = 6):
    """
    Run the grounded tool-use loop and return (answer_text, tool_trace, messages).

    tool_trace is a list of (tool_name, input) for UI transparency; messages is the
    full running conversation (incl. tool exchanges) to pass back in as `history`.
    """
    from anthropic import Anthropic

    client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
    messages = list(history or [])
    messages.append({"role": "user", "content": question})
    trace: list[tuple[str, dict]] = []

    for _ in range(max_rounds):
        resp = client.messages.create(
            model=MODEL, max_tokens=1500, system=SYSTEM, tools=TOOLS, messages=messages,
        )
        if resp.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": resp.content})
            results = []
            for block in resp.content:
                if block.type == "tool_use":
                    trace.append((block.name, block.input))
                    out = _dispatch(block.name, block.input)
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(out, default=str),
                    })
            messages.append({"role": "user", "content": results})
            continue
        text = "".join(b.text for b in resp.content if b.type == "text").strip()
        messages.append({"role": "assistant", "content": resp.content})
        return text, trace, messages

    return ("I couldn't finish reasoning about that — try narrowing the question.", trace, messages)
