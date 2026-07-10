# 🧬 T-Cell Target Explorer

**Ask Claude what to target for an autoimmune disease — and get trust-ranked CD4+ T-cell candidates grounded in a real CRISPR screen, right inside your Claude session.**

An **MCP server**: no separate app, no API key, no metered credits. You talk to Claude the way you already do; this server grounds every answer in the **Marson/Pritchard genome-scale CD4+ T-cell Perturb-seq** (Zhu, Dann, …, Pritchard, Marson 2025; [preprint](https://www.biorxiv.org/content/10.64898/2025.12.23.696273v1) · [CZI Virtual Cells Platform](https://virtualcellmodels.cziscience.com/dataset/genome-scale-tcell-perturb-seq)) — disease enrichment, gene-network influence, CRISPRi knockdown QC, and activation-state dependence.

*Built for the Built with Claude: Life Sciences hackathon (Builder track).*

---

## The problem (a real one)

That screen perturbed **every gene in primary human CD4+ T cells** and mapped which regulators drive which programs, and which programs are enriched in autoimmune-disease genetics — i.e. **candidate drug targets**. But the hardest thing in biology isn't the analysis; it's getting a bench scientist to actually *use* a dataset like this. It lives behind AnnData objects and a bioinformatician. A wet-lab immunologist who just wants *"what should I target for Crohn's, and can I trust it?"* can't self-serve it — and won't touch a new website to try.

So don't make one. **Meet them where they already are: inside Claude.**

## What it does

Add the server to Claude, then just ask. Claude calls the tools, reads the real numbers, and answers — **trust verdict first**.

> **You:** *For Crohn's, what should I target, and which hits can I actually trust?*
>
> **Claude** *(via the MCP)*: **STAT3** — the #1 candidate. Its regulatory program is the most disease-enriched (odds ratio 58, FDR 3.3e-4), it's a top-1% network hub (controls 1,592 genes vs. a median of 4), and its CRISPRi knockdown was **verified clean** in all three conditions. It sits with IRF4 and BATF — the core Th17 axis — so it's biologically coherent. ⚠️ **IPMK** sits in that *same* program with the *identical* enrichment score, but its knockdown was never confirmed — enrichment alone would rank it a top hit; don't spend bench time on it.
>
> **You:** *Which Crohn's targets only switch on when the T cell is activated?*
>
> **Claude**: EGR2 is **activation-induced** (854 genes when stimulated, near-silent at rest)… *(For asthma, ITK goes 1 → 3,392 genes rest → activated — the TCR signalosome, recovered from the data.)*

The tools (all grounded, no LLM guessing):

| Tool | Returns |
|---|---|
| `list_diseases` | the 17 autoimmune diseases in the screen |
| `disease_targets` | ranked candidates + OR, GRN influence, **trust flag**, **activation state**, Th1/Th2 |
| `target_evidence` | the full "why this target" case for one gene, with program peers + per-state trajectory |
| `regulator_detail` | per-condition GRN out-degree + CRISPRi QC |
| `state_profile` | how a regulator's influence shifts Rest → Stim8hr → Stim48hr |

## Quick start

```bash
git clone https://github.com/rpinho/tcell-target-explorer && cd tcell-target-explorer
python3 -m venv .venv && source .venv/bin/activate
pip install -e .                      # core engine + MCP server
python scripts/download_data.py       # small public tables (~34 MB), MIT
```

**Claude Code** — the repo ships a `.mcp.json`, so just open the project and approve the `tcell-target-explorer` server (or `claude mcp add tcell-target-explorer -- .venv/bin/tcell-targets-mcp`). Then ask your question.

**Claude Desktop** — add to `claude_desktop_config.json` (the editable install makes the command location-independent):

```json
{
  "mcpServers": {
    "tcell-target-explorer": {
      "command": "/ABSOLUTE/PATH/tcell-target-explorer/.venv/bin/tcell-targets-mcp"
    }
  }
}
```

Restart Claude, and ask: *"Using tcell-target-explorer, what should I target for rheumatoid arthritis, and which are verified?"*

Sanity-check the engine + server without Claude:

```bash
python -m tcell_targets.core     # prints top targets, asserts the Crohn's→STAT3 demo invariant
```

## What makes a hit trustworthy — and *when* it acts

Two layers a literature search can't give you, because they live in the assay, not the papers:

- **Trust flag.** Derived from the screen's own QC — was the CRISPRi **knockdown verified on-target**, and is the guide **off-target**? *High* = verified + clean; *Low* = knockdown not confirmed. This is what stops you spending months on a hit that only *looks* good (see IPMK above).
- **Activation state.** A T cell's regulators shift with its state, and the screen measured three (Rest / Stim8hr / Stim48hr). ~87% of hub regulators change their influence ≥2× across them. The server surfaces which state a target acts in — *activation-induced*, *resting-state*, *constitutive* — the state-dependence a bench immunologist otherwise needs a whole experiment to read. (It's surfacing the **three measured states**, not modeling unmeasured ones.)

## Optional: local visual browser

A Streamlit UI (disease dropdown → ranked table → evidence panel → per-state chart → CSV) is included for a visual, click-through view of the same data:

```bash
pip install -e ".[app]" && streamlit run app.py   # → http://localhost:8501
```

![The optional Streamlit browser — Crohn's → STAT3 with the evidence panel and activation-state layer](docs/screenshot.png)

## Data

Uses the authors' **precomputed** supplementary tables (auto-downloaded): cluster↔disease enrichment, per-perturbation DE stats (with `n_downstream` = GRN out-degree, per `culture_condition`), guide knockdown efficiency, sgRNA off-target library, Th1/Th2 signature. The full ~22M-cell AnnData is **not** required. Those tables are distributed by the study authors under the MIT License via their public analysis repo; this project re-uses them and does not redistribute the underlying single-cell data.

## Scope / honesty

17 autoimmune diseases, 185 significant disease↔program links. This surfaces and *trust-ranks* candidate targets from a published dataset — hypothesis generation and prioritization for a bench scientist, **not** a validated clinical claim. Confidence flags reflect experimental QC of the CRISPRi perturbation, not therapeutic efficacy.

*License: [MIT](LICENSE). New code written for the hackathon; public dataset.*
