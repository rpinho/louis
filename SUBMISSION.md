# Submission packet — Louis

The ~190-word summary, the 3-minute demo script, and the judging-criteria map.
Numbers are produced live (`python -m louis.core` re-checks the discovery
+ demo invariants on every run; `python scripts/build_kb_index.py` reports KB size).

---

## Submission summary (100–200 words — official cap; this is ~195)

**Louis** is an **MCP server + Slack bot** that turns a genome-scale CD4⁺ T-cell CRISPRi Perturb-seq screen
(Marson/Pritchard 2025) into a discovery-and-memory assistant living *inside Claude* — no separate app, no
API key. Named for Pasteur, Louis **discovers** understudied, druggable regulator "handles" wired to a
disease's own GWAS risk genes, gated by CRISPRi knockdown QC and activation state; as a **blind positive
control**, the same ranking re-derives the known Th17 masters STAT3/BATF/IRF4 — **1 of 77 regulator clusters
clears significance, Crohn's q=0.025, disease-calibrated, not a hub**. It **validates** each lead against
Claude Science's connectors, **weighs every source by provenance** (a preprint or conference abstract is
hypothesis-strength, never decisive), and **reviews itself** — the Claude Science reviewer, rebuilt for
Slack. Its sharpest move is honesty: handed its own flagship RA lead **DOT1L**, Louis **red-teams it A→C** —
the wiring is a cross-disease artifact and an inhibitor likely *worsens* RA — and returns the survivor,
**HDAC7** for Th17-driven colitis (favorable, peer-reviewed direction), with the go/no-go experiment. It
**remembers** the whole chain with provenance, and the whole lab **writes back**. Built with Claude.

---

## The one-liner spine (what makes it win)

Louis's sharpest move is that it **red-teams its own flagship**. On the same RA panel where it first graded
**DOT1L a top novel lead (A)**, Louis turns its own trust machinery on that call and downgrades it **A→C**:
the regulator→risk-gene "wiring" is a *non-significant cross-disease-union artifact* (DOT1L isn't even in
RA's own regulator set), and DOT1L supports Tregs — so an inhibitor likely **worsens** RA. A discovery tool
that kills its own darling, with receipts, is one you can trust with the survivors. And it **discriminates**:
the *same instrument* that dims DOT1L keeps **HDAC7 for Th17-driven colitis** lit at **B** (favorable,
peer-reviewed direction), and, run blind, re-derives the textbook Th17 masters STAT3/BATF/IRF4 (**1 of 77
regulator clusters clears significance, Crohn's q=0.025** — calibration, not a hub). Telling a calibrated
call from an over-confident one *is* the product.

The **opportunity map** makes it visual — candidate **grade** (y) against **novelty** (x), each point a
connector-graded verdict:

<p align="center">
  <img src="docs/figures/opportunity_map.png" width="90%" alt="The opportunity map — grade vs novelty. DOT1L is the killed flagship (downgraded to C); the survivors HDAC7, PPM1D, DOCK2 earn their grades on their own evidence.">
</p>

**DOT1L is no longer the green-corner win — it's the killed flagship, the trust demonstration.** The
survivors earn their grades on their *own* evidence: **HDAC7** (Th17-colitis, favorable direction), **PPM1D**,
**DOCK2** (understudied whitespace), each honestly caveated. The known genes (IL21R, STAT3, ZAP70, AHR) sit
right, validated but crowded; INSR is the screen grading its own artifact a D. The positive control
*calibrates the method* — it re-derives the known masters — but it **licenses no single pick**; every lead
still earns its grade. And the honesty is in what's *absent*: MEN1 and GLS aren't plotted, because their
story is misattributed buzz and cross-disease grade drift, not a clean grade × novelty point.

---

## 3-minute demo script (Framing A — the honest instrument)

> Two parts — **Claude Science** (before → after) then **Slack** (where a lab actually talks). All Anthropic,
> all on the subscription — no third-party app, no API key. TL;DR-first, scannable (it's a video). Hard **3:00**.

### Part 1 — Claude Science (before → after)
- **Before:** naive Claude Science, *no Louis*, confidently recommends **DOT1L** for RA — and gets the
  *direction wrong* (frames inhibition as good; never notices DOT1L props up regulatory T cells).
- **After:** Louis's skill on, same question → Louis **recalls its own red-team and overrules its grade-A,
  DOT1L A→C**: the RA "wiring" is a *non-significant cross-disease-union artifact* (DOT1L isn't in RA's own
  regulator set), and an inhibitor likely *worsens* RA (Treg risk). It **tiers its evidence** — the kill
  rests on the engine fact; the Treg mechanism is a *preprint* its own **reviewer** flags hypothesis-strength.
  *The memory is the trust mechanism.* Paired in-frame with the survivor (**HDAC7 holds at B**), so it reads
  "calibrated instrument," never "tool was wrong."
- **Calibration + moat, shown:** the same ranking, run blind, re-derives the Th17 masters STAT3/BATF/IRF4
  (**1 of 77 clusters, Crohn's q=0.025** — disease-calibrated, not a hub); it *discriminates* (DOT1L cracks,
  HDAC7 holds) — the control calibrates the **method**, it licenses no pick. On screen: the off-allowlist
  **ACR abstract** Science can't confirm, and the **recursion** (`kb_remember` writing a verdict back to the KB).

### Part 2 — Slack (Louis where a lab works)
- **Discovery:** `@louis` for IBD / Th17-driven colitis → **HDAC7, trust B**, led on the *peer-reviewed
  direction* (HDAC4/7 drive Th17; inhibition mitigates Th17 colitis — PNAS 2024) + the screen-unique legs
  (verified KD all 3 states, activation state); honest that the wiring is a co-cluster hypothesis and the
  genetics is locus-ambiguous. ELI5 on demand. Pre-empts the "IL-17 blockade worsened Crohn's" objection.
- **The lab teaches Louis (the closer):** a labmate reports the co-cluster edge didn't hold → Louis files it
  *attributed to them*, **retracts that leg**, keeps the lead lit on the evidence that holds, and hands the
  sharpened go/no-go experiment. `--nolab` shows the answer before the lab weighed in. **Discover, validate,
  listen, remember — and learn, together. Built with Claude, living inside it, shared with your whole lab.**

---

## How it maps to the judging criteria

- **Demo (30%)** — a conversation whose spine is **honesty you can watch**: Louis red-teams its *own*
  flagship (DOT1L A→C — the wiring is a cross-disease artifact, an inhibitor likely worsens RA), paired
  in-frame with a survivor that holds (HDAC7, favorable peer-reviewed direction) and the blind positive
  control, so it always reads "calibrated instrument," never "tool was wrong" — then hands over the survivor
  + its go/no-go experiment, and learns from a bench result in the Slack coda. Every claim traces to a
  source *and* its provenance tier.
- **Impact (25%)** — attacks the bottleneck a bench scientist named as *the hardest thing*: adoption,
  not analysis. It hands a wet-lab that can't afford a bioinformatician a novel, druggable, testable
  lead (Claude Science independently confirmed the regulator→risk-gene edge exists in no external
  database) plus the experiment to test it, and a Slack bot spreads it to the whole lab (public
  channels, so knowledge compounds instead of siloing).
- **Claude Use (25%)** — built with Claude Code, and creative in ways that go past a basic app: Louis
  *is* an MCP (the host reasons on the subscription, **no API cost**); it *composes with Claude Science's*
  connectors for validation; its **listen** layer adds a data source even Science lacks — the field's
  pre-paper chatter on X/Bluesky/conference floors. The standout, and the part that surprised us building
  it: the knowledge base was deepened by **recursion** — Louis's own skill run *inside* Claude Science
  across nine diseases, its findings ingested back with provenance. And because it's an MCP + a tool-using
  agent it's **open-ended** — add a tool (~20 lines) or point Claude at your lab's own MCP server
  (ELN / LIMS / your screens) and Louis reasons over your whole stack; the shared-memory writes were
  added exactly that way.
- **Depth & Execution (20%)** — a **blind positive control** grounds the method: told only a disease's GWAS risk
  genes and no known targets, the *same* unsupervised ranking re-derives the textbook Th17 master triad
  **STAT3 / BATF / IRF4** as its top-3 for the core inflammatory diseases (**1 of 77 regulator clusters clears
  significance, and the top hit survives a global BH across all 1,309 tests, Crohn's q=0.025** — disease-
  calibrated, dark in RA/SLE/T1D, not a hub; one-command repro, `scripts/positive_control.py`). It calibrates
  the *method* — it **licenses no single pick**; every lead still earns its own grade. On top of that: an
  **evidence-provenance tier** (engine/peer-reviewed = load-bearing; preprint/abstract = hypothesis-strength;
  social = signal) and a **self-reviewer** that flags any grade resting on weak provenance — the Claude
  Science reviewer, rebuilt for Slack; a real GRN + CRISPRi-QC trust layer, an
  activation-state axis, and a module→risk-gene discovery engine on the authors' tables; a community-signal
  engine that self-filters by gene symbol and vetoes wellness noise; a knowledge base in a mature PKM shape
  (routing, provenance, recall-before-derive, dimensional `kb_query`, cross-disease synthesis, and a
  grade × novelty opportunity map that prioritizes the whole portfolio at a glance). Honest resolution
  stated throughout: module-level co-cluster hypotheses to *test*, not proven gene-level edges; the
  positive control is a recovery sanity check, not a held-out predictive AUROC.

---

## How this was built with Claude (the recursion)

The seed KB was small. To deepen it, Louis's **own skill was uploaded into Claude Science** and run
across **nine autoimmune diseases** — RA, SLE, Crohn's, MS, UC, psoriasis, type-1 diabetes, asthma,
atopic eczema — each session validating the leads against Open Targets / ChEMBL / PubMed / GWAS Catalog /
ClinicalTrials, grading A–D, and writing findings back with per-source provenance. Those write-backs were
ingested into the repo KB (additive, deduped, corrections kept — several times catching Claude Science
stating a drug's phase *from memory* when its own ChEMBL lookup said otherwise, and re-verifying every
screen number against the engine). A cross-disease synthesis recipe was folded back into the skill; the
community moat (X / Bluesky / conference abstracts — off Science's allowlist) was harvested and baked in.

The result: **195 target profiles, ~1,070 provenance-stamped records**, nine connector-verified diseases,
new leads per disease (**DOCK2, HIF1A, PPM1D, RASA2** — DOCK2 independently corroborated the same week by
a Bluesky post from the Waggoner Lab), two full experiment designs, and a portfolio synthesis whose
punchline is *honesty*: the recurring handles are **module-conservation on shared GWAS hubs, not one
convergent mechanism** — with two disjoint conserved axes, Th1/Th17 and Th2. And the sharpest recursion
result of all: the red-team ran **on Louis's own flagship** — Claude Science, driving Louis's skill,
downgraded **DOT1L A→C** (the RA wiring is a cross-disease artifact; an inhibitor likely worsens RA), and
Louis wrote that verdict *back to its own KB* — so it now **recalls the red-team on its former darling**.
A system that went looking everywhere else first, then turned that scrutiny on itself.
