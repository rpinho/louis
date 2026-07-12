# Submission packet — Louis

The ~190-word summary, the 3-minute demo script, and the judging-criteria map.
Numbers are produced live (`python -m tcell_targets.core` re-checks the discovery
+ demo invariants on every run; `python scripts/build_kb_index.py` reports KB size).

---

## Submission summary (~200 words)

**Louis** is an **MCP server + Slack bot** that turns a genome-scale CD4⁺ T-cell CRISPRi
Perturb-seq screen (Zhu, Dann, …, Pritchard, Marson 2025) into a discovery, validation, and
memory assistant that lives *inside Claude* — no separate app, no API key. Named for Pasteur
("a hit is a clue, not a conviction"), Louis does five things:
**DISCOVER** — it wires understudied, druggable regulator "handles" to a disease's own GWAS
risk-gene modules, gated by CRISPRi knockdown QC (the **trust flag**) and tagged by activation
state; **VALIDATE** — it hands each lead to Claude Science's scientific web (Open Targets, ChEMBL,
PubMed, GWAS Catalog, ClinicalTrials) to grade novelty and druggability; **LISTEN** — it reads
what immunologists are posting on **X, Bluesky, and conference floors** *this week*, before it's a
paper; **REMEMBER** — it files the whole chain, with provenance *and confidence level*, to a
shareable knowledge base; **SYNTHESIZE** — it recurs handles across diseases to separate a single
mechanism from shared disease-wiring. For rheumatoid arthritis it surfaces **DOT1L** — novel,
druggable (pinometostat), with a regulator→risk-gene link in **no external database** — and the
listen layer corroborates it with same-week preprint + conference signal that Claude Science
structurally *cannot* reach. Every claim traces to a source. Built with Claude, living inside it,
and shared with the whole lab.

---

## The one-liner spine (what makes it win)

Louis doesn't just find a novel target — it **tells a genuine bleeding-edge bet from hype**, and
proves it: for the same panel of leads it graded **DOT1L a real pre-paper edge** (mechanism lives
only in a preprint + a conference abstract) while **killing MEN1 (menin buzz is all oncology),
GLS (signal is synoviocytes, wrong cell), and CBLB/RIPK1 (edge already closed/published).**
Separating edge from noise *is* the product.

---

## 3-minute demo script (beat by beat)

> The whole demo is a conversation with **Louis**, in Slack and in Claude. Discover, listen,
> remember run through the Louis MCP/skill; validate + experiment-design run in Claude Science;
> the Slack coda shows where a lab actually talks. All Anthropic, all on the subscription — no
> third-party app, no API key. Every answer is TL;DR-first and scannable (it's a video). Screen-record it.

### Beat 1 — the real problem (0:00–0:25)
- **[SAY]** "This is a genome-scale CRISPR screen of human T cells — a map of autoimmune drug
  targets. The hardest thing in biology isn't the analysis; it's getting a bench scientist to
  *use* a dataset like this. So we didn't build a website. We put it inside Claude — and named it
  Louis, after Pasteur. It discovers, it doesn't just look up."

### Beat 2 — DISCOVER + TRUST (0:25–1:05)
- **[SCREEN]** In Slack: *`@louis for rheumatoid arthritis, skip the obvious targets — novel
  druggable handles wired to the risk genes, and which can I trust?`*
- **[SAY]** "It doesn't hand me STAT3. It wires **DOT1L** — an epigenetic enzyme, pinometostat in
  the clinic — to a module carrying the RA risk genes **IL21R** and **PTGER4** in *resting* T cells,
  knockdown verified clean. And it leads with the **trust flag**: a high-enrichment hit whose
  knockdown was never confirmed is a *caution*, not a recommendation. The regulator→risk-gene link
  exists in **no external database** — only in this screen."

### Beat 3 — LISTEN: who else, and is it real? (1:05–1:55) ← the moat + the honesty
- **[SCREEN]** *`@louis who else is working on DOT1L — and is the buzz real edge or hype?`*
- **[SAY]** "Claude Science reads *published papers* — but its sandbox is a strict allowlist; it
  literally cannot reach Twitter, Bluesky, or a conference site. That's our moat. Louis grades
  **DOT1L a genuine pre-paper edge**: the Treg-identity/DNA-demethylation mechanism that supports
  it exists *only* as a bioRxiv preprint and an **ACR conference abstract** — off the allowlist.
  And in the same breath it **rejects the hype**: the menin-inhibitor buzz around **MEN1** is all
  leukemia, orthogonal; the **GLS** signal is synoviocytes, wrong cell type. Five sources converge
  on DOT1L, and two of them Science *cannot see*. That's the friend who says: chase it — and here's
  who's presenting it."

### Beat 4 — EVALUATE: design the experiment (1:55–2:30)
- **[SCREEN]** *`@louis is DOT1L a good bet — design the cleanest experiment.`* (Louis + Claude Science)
- **[SAY]** "It returns a real two-arm protocol on the screen's own activation-state axis: CRISPRi
  knockdown as the primary arm, pinometostat as the pharmacology complement, an **sgRNA-resistant +
  catalytic-dead rescue** for specificity, **H3K79me2 CUT&RUN** target-engagement at IL21R, a
  **mandatory Treg readout** because DOT1L supports Treg identity — and cheap-gate-first go/no-go
  gates so a negative result kills the lead before any inhibitor work. *(We ran the same for the UC
  lead, HDAC7 — full protocol shipped in the repo.)*"

### Beat 5 — REMEMBER, and the trust chain (2:30–2:55)
- **[SCREEN]** *`@louis remember DOT1L`* → then `kb_recall(DOT1L)` — one profile: discovery + novelty
  + validation + community signal + verdict + experiment, each cited. Then flip **`--nomem`**.
- **[SAY]** "It files the whole chain to a shareable KB — recall it and it's there, no re-derivation.
  Watch the trust go all the way down: Claude Science's *own* reviewer flagged a citation it couldn't
  confirm; an independent check confirmed the paper is real — but a *preprint*, a precision even the
  validator missed. And the contrast: ask the same question with **memory off** and you get a generic
  answer; with memory on, the whole compounded case. Every claim traces to a source **and its
  confidence level**."

### Beat 6 — share it with the lab (2:55–3:20)
- **[SCREEN]** Slack, public channel: the trust-ranked leads + community signal appear; `/remember`
  files to the **shared** KB.
- **[SAY]** "Because knowledge has to be shared, it meets a lab where they already talk — Slack,
  public channels only, every question compounding into one memory. Discover, validate, listen,
  remember, synthesize — inside Claude, no API key, no bioinformatician. It produces a novel,
  druggable, testable lead a bench scientist would actually chase: DOT1L, not textbook STAT3.
  That's Louis — built with Claude, living inside it, shared with your whole lab."

---

## How it maps to the judging criteria

- **Demo (30%)** — a live, five-move conversation (discover → validate → listen → remember →
  synthesize) with a novel hero (DOT1L, not STAT3), a memorable spine (**edge vs hype**: it
  corroborates DOT1L *and* rejects MEN1/GLS in the same answer), a real bench experiment, and a
  Slack coda — every claim traced to a source *and* its confidence level.
- **Impact (25%)** — attacks the bottleneck a bench scientist named as *the hardest thing*: adoption,
  not analysis. It hands a wet-lab that can't afford a bioinformatician a novel, druggable, testable
  lead (Claude Science independently confirmed the regulator→risk-gene edge exists in no external
  database) plus the experiment to test it, and a Slack bot spreads it to the whole lab (public
  channels, so knowledge compounds instead of siloing).
- **Claude use (25%)** — it *is* an MCP (the host reasons on the subscription, no API cost); it
  *composes with Claude Science's* connectors for validation; and its **listen** layer adds a data
  source even Science lacks — the field's pre-paper chatter on X/Bluesky/conference floors. The
  knowledge base was itself deepened by **recursion**: Louis's own skill run *inside* Claude Science
  across five diseases, its findings ingested back with provenance.
- **Depth (20%)** — a real GRN + CRISPRi-QC trust layer, an activation-state axis, and a
  module→risk-gene discovery engine on the authors' tables; a community-signal engine that self-filters
  by gene symbol and vetoes wellness noise; a knowledge base in a mature PKM shape (routing, provenance,
  recall-before-derive, dimensional `kb_query`, cross-disease synthesis). Honest resolution stated
  throughout: module-level co-cluster hypotheses to *test*, not proven gene-level edges.

---

## How this was built with Claude (the recursion)

The seed KB was small. To deepen it, Louis's **own skill was uploaded into Claude Science** and run
across RA, SLE, Crohn's, MS, and UC — each session validating the leads against Open Targets / ChEMBL /
PubMed / GWAS Catalog / ClinicalTrials, grading A–D, and writing findings back with per-source
provenance. Those write-backs were ingested into the repo KB (additive, deduped, corrections kept),
a cross-disease synthesis recipe was folded back into the skill, and the community moat (X / Bluesky /
conference abstracts — everything off Science's allowlist) was harvested and baked in so it ships even
inside the sandbox. The result: **191 target profiles, ~1,030 provenance-stamped records**, four
connector-verified diseases, and a hero lead (DOT1L) whose pre-paper edge was confirmed by a system
that went looking everywhere else first.
