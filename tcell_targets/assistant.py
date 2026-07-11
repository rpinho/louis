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
from . import community
from . import kb

# Bio reasoning → default to Opus; override with TCELL_MODEL if desired.
MODEL = os.environ.get("TCELL_MODEL", "claude-opus-4-8")


def _env_truthy(name: str) -> bool:
    """A value like 1/true/yes/on (case-insensitive, non-empty, not 0/false/no/off) reads truthy."""
    return os.environ.get(name, "").strip().lower() not in ("", "0", "false", "no", "off")


def default_use_memory() -> bool:
    """Default for the memory toggle: OFF (from scratch) when TCELL_NO_MEMORY is set truthy, else ON."""
    return not _env_truthy("TCELL_NO_MEMORY")

SYSTEM = """You are **Louis** — a target-discovery assistant for a bench immunologist, named for \
Louis Pasteur and built in his spirit: nothing is trusted until it's verified. You're a sharp, warm, \
slightly dry lab colleague — not an institution. You sit on top of a genome-scale CD4+ T-cell CRISPRi \
Perturb-seq screen (Zhu, Dann, ..., Pritchard, Marson 2025): every gene was knocked down in primary \
human CD4+ T cells, and the authors precomputed which regulators drive which programs, which programs \
are enriched in autoimmune-disease genetics, and the QC of each CRISPRi guide. Your job is to help the \
scientist find and *vet* candidate regulators to target.

Voice: concise, plain-spoken, a touch of dry wit; never pompous, never hypey. Your creed: \
**"A hit is a clue, not a conviction."** Lead with the verdict, be honest about what you don't know, \
and always name the next experiment.

How to answer — present a target like a case file, in this order (skip a heading only if it's truly empty):
- **Lead** — the target (gene) and, in one line, why it's on the table.
- **Evidence** — the screen data, queried live: enrichment odds ratio + FDR, GRN out-degree + \
percentile, activation state. ALWAYS query the tools for real data before any quantitative claim. Never \
invent numbers; cite the actual values you get back.
- **Counter-evidence** — the trust verdict, and it's the whole point: say plainly whether the knockdown \
was verified on-target and whether the guide is clean. A high disease-enrichment with an UNCONFIRMED \
knockdown is a caution, not a recommendation — call it out (it's the difference between a target worth \
bench time and one that will waste it).
- **Quiet signal** — what the field is saying pre-paper (community_signal): recent X/Twitter chatter \
from labs/journals about the gene or disease. Treat posts as leads to weigh, not validated claims, and \
say so. If it's unavailable in this environment, note that and rely on kb_recall for baked signal.
- **Verdict** — your trust call in one line, plus the single next bench step that would settle it.

Rules of the house:
- Surface the activation state. A T cell's regulators change with its state, and the screen measured \
three (Rest / Stim8hr / Stim48hr). When it matters, say which state a target acts in — e.g. \
'activation-induced' means it does little in resting cells and switches on only when the T cell is \
stimulated. This is exactly what bench immunologists say they can't self-serve, so lean into it; use \
state_profile for the per-state trajectory. Note you are surfacing the THREE measured states, not \
predicting unmeasured ones.
- Be decisive and concise: recommendation first, then the 2-4 numbers that justify it. Short beats long.
- For DISCOVERY (novel leads beyond the obvious top hit), use disease_mechanisms: it wires druggable \
regulator handles to the disease's own risk-gene modules. Recover the obvious Th17 handles (STAT3/BATF) \
as a positive control, then surface the understudied, druggable ones and judge their novelty yourself.
- MEMORY: call kb_recall FIRST for a gene/disease to reuse what's already known (data facts, novelty, \
the community signal, prior verdicts) instead of re-deriving.
- You may add briefly established biology (e.g. STAT3/IRF4/BATF are core Th17 regulators) but keep it \
clearly separate from the data, and never claim clinical efficacy — these are hypotheses to \
prioritize experiments, not clinical claims.
- If asked something the data can't answer, say so rather than guessing."""


def _system(use_memory: bool = True) -> str:
    """The system prompt. In no-memory mode, drop the recall-before-derive rule and the
    'fall back to the KB' pointer — the model answers purely from the live tools + reasoning."""
    if use_memory:
        return SYSTEM
    s = SYSTEM.replace(
        "If it's unavailable in this environment, note that and rely on kb_recall for baked signal.",
        "If it's unavailable in this environment, say so and reason from the live tool data and your own knowledge.")
    s = s.replace(
        "- MEMORY: call kb_recall FIRST for a gene/disease to reuse what's already known "
        "(data facts, novelty, the community signal, prior verdicts) instead of re-deriving.",
        "- NO-MEMORY MODE: there is NO knowledge base this session — no stored findings, prior verdicts, "
        "or baked community signal. Derive every answer fresh from the live tools and your own reasoning; "
        "do not claim to recall prior results.")
    return s


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
    {
        "name": "disease_mechanisms",
        "description": (
            "DISCOVERY — go beyond the obvious top hit. Returns the GRN modules whose downstream program is "
            "enriched in the disease's OWN risk genes, each with the risk genes, the activation state it fires "
            "in, and the candidate regulator HANDLES (druggable entry points) that co-cluster with it. The "
            "obvious Th17 handles (STAT3/BATF) appear as a positive control; the value is the understudied, "
            "druggable ones. Module-level co-cluster links (candidate controllers to test), not proven edges."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "disease": {"type": "string"},
                "top_modules": {"type": "integer", "description": "max modules (default 8)"},
            },
            "required": ["disease"],
        },
    },
    {
        "name": "community_signal",
        "description": (
            "LISTEN — recent X/Twitter chatter (labs/journals/news first) about a gene (kind='target') or a "
            "disease (kind='disease') in a CD4+ T-cell / immunology context: the bleeding-edge, pre-paper "
            "signal the literature doesn't have yet. Runs live only where X access exists; otherwise returns a "
            "note (rely on kb_recall for baked signal). Treat posts as leads to weigh, not validated claims."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "entity": {"type": "string", "description": "gene symbol or disease name"},
                "kind": {"type": "string", "description": "'target' (gene) or 'disease'"},
                "top": {"type": "integer", "description": "max posts (default 8)"},
            },
            "required": ["entity"],
        },
    },
    {
        "name": "kb_recall",
        "description": (
            "MEMORY — read what the knowledge base already knows about a gene or disease (data facts, novelty "
            "assessments, community signal, prior scientist verdicts) BEFORE re-deriving. Returns the stored "
            "profile(s) or a note that it's not in the KB yet."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"entity": {"type": "string"}},
            "required": ["entity"],
        },
    },
]


# The KB-backed tools handed to Claude. In no-memory mode these are withheld so the
# model cannot read the knowledge base (community_signal is the LIVE engine, not the KB).
_MEMORY_TOOLS = {"kb_recall"}


def _tools(use_memory: bool = True) -> list:
    return TOOLS if use_memory else [t for t in TOOLS if t["name"] not in _MEMORY_TOOLS]


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
        if name == "disease_mechanisms":
            return _clean(core.disease_mechanisms(args["disease"], top_modules=int(args.get("top_modules", 8))))
        if name == "community_signal":
            return _clean(community.community_signal(
                args["entity"], kind=args.get("kind", "target"), top=int(args.get("top", 8))))
        if name == "kb_recall":
            return _clean(kb.recall(args["entity"]))
        return {"error": f"unknown tool {name}"}
    except Exception as e:  # let Claude see + recover from a bad call
        return {"error": f"{type(e).__name__}: {e}"}


def answer(question: str, history: list | None = None, api_key: str | None = None,
           max_rounds: int = 6, use_memory: bool | None = None):
    """
    Run the grounded tool-use loop and return (answer_text, tool_trace, messages).

    tool_trace is a list of (tool_name, input) for UI transparency; messages is the
    full running conversation (incl. tool exchanges) to pass back in as `history`.

    use_memory=False answers purely from the live engine + reasoning: the KB tools are
    withheld and the recall/remember instructions are dropped, so no kb/ read or write
    happens (and it's faster — no KB I/O). Defaults to TCELL_NO_MEMORY (env) → True.
    """
    from anthropic import Anthropic

    if use_memory is None:
        use_memory = default_use_memory()
    system, tools = _system(use_memory), _tools(use_memory)
    client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
    messages = list(history or [])
    messages.append({"role": "user", "content": question})
    trace: list[tuple[str, dict]] = []

    for _ in range(max_rounds):
        resp = client.messages.create(
            model=MODEL, max_tokens=1500, system=system, tools=tools, messages=messages,
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
