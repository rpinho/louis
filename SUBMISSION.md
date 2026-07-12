# Submission packet — Louis

The 150-word summary, the 3-minute demo script, and the judging-criteria map.
Numbers are produced live (`python -m tcell_targets.core` re-checks the discovery
+ demo invariants on every run).

---

## Submission summary (~190 words)

**Louis** is an **MCP server + Slack bot** (built on the T-Cell Target Explorer engine) that turns a
genome-scale CD4+ T-cell CRISPRi Perturb-seq screen (Marson/Pritchard 2025) into a discovery,
validation, and memory assistant that lives *inside Claude* — no separate app, no API key. Ask it for drug targets for an autoimmune disease and it does four
things: **(1) DISCOVER** — it wires druggable regulator "handles" to the disease's own GWAS risk
genes through the screen's gene-regulatory modules, gated by CRISPRi knockdown QC (the trust flag)
and tagged by activation state; **(2) VALIDATE** — it hands each lead to Claude Science's scientific
web (Open Targets, ChEMBL, PubMed, GWAS Catalog) to grade novelty and druggability; **(3) LISTEN** —
it turns its own discoveries into search terms and pulls what immunologists are posting on X *this
week*, before it's a paper (labs/journals first, wellness noise vetoed); **(4) REMEMBER** — it files
the whole chain, with provenance *and confidence level*, to a shareable knowledge base so it's never
re-derived. For rheumatoid arthritis it surfaces **DOT1L** — a novel, druggable, testable lead whose
regulator→risk-gene link exists in **no external database**, only in the Perturb-seq — and the listen
layer independently corroborates it with a same-week journal post on a *sister* methyltransferase.
A Slack bot shares it all with the lab. Every claim traces to a source. Built with Claude, and living inside it.

---

## 3-minute demo script (beat by beat)

> The whole demo is a conversation. **Discover**, **Listen**, and **Remember** run through the
> `tcell-target-explorer` MCP/skill in Claude (Code, Desktop, or Science); **Validate** runs in
> Claude Science; the **Slack** coda shows the same engine where a lab actually talks. All Anthropic,
> all on the subscription — no third-party app, no API key. Screen-record it.

### Beat 1 — The real problem (0:00–0:25)
- **[SAY]** "This is a genome-scale CRISPR screen of human T cells — a map of autoimmune drug targets. But the hardest thing in biology isn't the analysis; it's getting a bench scientist to *use* a dataset like this. So we didn't build a website. We put it inside Claude — and made it discover, not just look up."

### Beat 2 — DISCOVER (0:25–1:15)
- **[SCREEN]** In Claude: *"For rheumatoid arthritis, skip the obvious targets — use disease_mechanisms to find understudied, druggable handles wired to the disease's own risk genes."*
- **[SAY]** "It doesn't hand me STAT3. It wires **DOT1L** — an epigenetic enzyme — to a module carrying the RA risk genes IL21R and PTGER4, in *resting* T cells; **GLS**, a metabolic enzyme, to a PTPN22/TRAF1 module in *activated* cells — each with its knockdown QC and the state it acts in. Mechanistic, testable leads — and the regulator→risk-gene links exist nowhere else."

### Beat 3 — VALIDATE (1:05–1:50) ← the heart
- **[SCREEN]** Hand the leads to Claude Science: *"Validate these against Open Targets, ChEMBL, PubMed, GWAS Catalog, ClinicalTrials."* Show the ranked figure.
- **[SAY]** "Claude Science pressure-tests them and ranks **DOT1L** #1 — no RA literature, but fresh 2026 CD4/Treg biology and a Phase-2 tool compound. It *catches* that the Open Targets scores are ontology-propagation artifacts, not real RA evidence. And the punchline: after querying every major database, it concludes the regulator→risk-gene edges **live only in your Perturb-seq**. The tool's whole reason to exist, confirmed by a system that went looking everywhere else."

### Beat 4 — LISTEN: the phone-a-friend (1:50–2:30) ← the moat
- **[SCREEN]** *"Now be my friend — what's the field actually saying about these leads?"* `community_signal` + `kb_recall(DOT1L)`.
- **[SAY]** "Claude Science reads *published papers* — but its sandbox is a strict allowlist; it literally cannot reach Twitter or a conference website. That's our moat, and here's what lives there. Our data flagged **DOT1L**, a methyltransferase. The tool listens: **@ACR_Journals** is posting about **DNMT3A** — *another* methyltransferase in RA T cells — so it follows the link to the actual **Karolinska paper**, pulls a **bioRxiv preprint** on Treg methylation, and surfaces an **ACR conference abstract that independently links DNMT3A *and* DOT1L in one mechanism.** Five sources — data, social, paper, preprint, conference floor — converging on one thesis, and two of them Science *cannot see*. That's the friend who says: *yes, chase it — and here's who's presenting it.*"

### Beat 5 — REMEMBER, and the trust chain (2:30–2:55)
- **[SCREEN]** *"Remember the top lead."* Then `kb_recall(DOT1L)` — one profile: discovery + novelty + validation + community signal + verdict, each cited.
- **[SAY]** "It files the whole chain to a shareable knowledge base — recall it and it's there, no re-derivation. And watch the trust go all the way down: Claude Science's *own* reviewer flagged one citation it couldn't confirm; an independent PubMed check confirmed the paper is real — but a *preprint*, a precision even the validator missed. Every claim traces to a source **and its confidence level**."

### Beat 6 — Share it with the lab, and what it is (2:55–3:20)
- **[SCREEN]** Flip to Slack. In a public channel: *`@target-explorer what should we hit for RA?`* → the same trust-ranked leads + community signal appear; `/remember` files to the shared KB.
- **[SAY]** "And because knowledge has to be shared, it meets a lab where they already talk — Slack, public channels only, every question compounding into one memory. Discover, validate, listen, remember — inside Claude, no API key, no bioinformatician. It produces a novel, druggable, testable lead a bench scientist would actually chase: DOT1L, not textbook STAT3. That's Louis — built with Claude, living inside it, and shared with your whole lab."

---

## How it maps to the judging criteria

- **Demo (30%)** — a live, four-move conversation (discover → validate → listen → remember) with a
  novel hero (DOT1L, not the obvious STAT3), a memorable spine (a trust chain where each check catches
  the previous one's gap), a same-week convergence beat (DNMT3A), and a Slack coda that lands the
  adoption story — ending with every claim traced to a source *and* its confidence level.
- **Impact (25%)** — attacks the bottleneck a bench scientist named as *the hardest thing*: adoption,
  not analysis. It hands a wet-lab that can't afford a bioinformatician a novel, druggable, testable
  lead — Claude Science independently confirmed the leads exist in no external database — and a Slack
  bot spreads it to the whole lab (public channels only, so knowledge compounds instead of siloing).
- **Claude use (25%)** — it *is* an MCP (the host reasons on the subscription, no API cost), it
  *composes with Claude Science's* scientific-web connectors for validation, and its **listen** layer
  adds a data source even Science lacks — the field's pre-paper chatter. The missing primary-data +
  social-signal layer inside the Claude science stack, not a standalone.
- **Depth (20%)** — a real GRN + QC trust layer, an activation-state axis, and a module→risk-gene
  discovery engine on the authors' tables; a community-signal engine that turns the engine's own
  leads into queries, self-filters via gene symbols, vetoes wellness noise, and OR-batches around the
  X rate limit; and a knowledge base in a mature PKM shape (full routing, provenance, recall-before-
  derive). Honest resolution stated throughout: module-level co-cluster hypotheses to *test*, not
  proven gene-level edges.
