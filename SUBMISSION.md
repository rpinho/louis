# Submission packet — T-Cell Target Explorer

The 150-word summary, the 3-minute demo script, and the judging-criteria map.
Numbers below are produced live by the tool (`python -m tcell_targets.core`
re-checks the headline STAT3 invariant on every run).

---

## Submission summary (~160 words)

**T-Cell Target Explorer** is an **MCP server** that puts trust-ranked CD4+ T-cell drug
targets *inside Claude* — no separate app, no API key, no metered credits. A bench
immunologist asks Claude, in plain English, what to target for an autoimmune disease;
Claude calls the server and answers — grounded in a genome-scale CRISPRi Perturb-seq
screen (Marson/Pritchard 2025) and leading with the one thing that decides whether to
spend bench time: **can you trust the hit?** The trust flag comes from the screen's own
QC — was the CRISPRi knockdown verified, is the guide off-target — so a target that's
disease-enriched but unvalidated (IPMK) gets flagged, not recommended. It also surfaces
the **activation state** a target acts in (resting vs. stimulated) — the state-dependence
bench scientists say needs a whole experiment — and it recovers known biology (STAT3/Th17;
the TCR signalosome) as a built-in positive control. The hardest thing isn't the analysis;
it's getting scientists to *use* the data. So we meet them where they already are: in Claude.

---

## 3-minute demo script (beat by beat)

> Setup: Claude Desktop (or Claude Code) with the **tcell-target-explorer** MCP connected.
> The whole demo is a conversation with Claude — no separate app, no key. Screen-record Claude.

### Beat 1 — The real problem (0:00–0:25)
- **[SCREEN]** The dataset page / an AnnData filename, then cut to a normal Claude chat window.
- **[SAY]** "This is a genome-scale CRISPR screen of human T cells — a map of autoimmune drug targets. But the hardest thing in biology isn't the analysis; it's getting a bench scientist to actually *use* a dataset like this. It's locked behind AnnData and a bioinformatician. So we didn't build another website. We put it **inside Claude** — where they already are."

### Beat 2 — Ask, and trust comes first (0:25–1:10)
- **[SCREEN]** Type into Claude: *"For Crohn's disease, what should I target — and which hits can I actually trust?"* Show Claude calling the `tcell-target-explorer` tools.
- **[SAY]** "No terminal, no API key — this runs on your Claude subscription. Watch it query the real screen." Read the answer: "**STAT3** — most disease-enriched program, odds ratio 58; a top-1% network hub, 1,592 genes controlled where the median is four; and the knockdown was **verified clean** in all three conditions. It even sits with IRF4 and BATF — the known Th17 axis. That's the hit you can believe."

### Beat 3 — The trust triage — the payoff (1:10–1:45)
- **[SCREEN]** Ask: *"IPMK is in the same program with the same enrichment — why not target it instead?"*
- **[SAY]** "Here's the whole point. IPMK has the *identical* disease score as STAT3 — rank on the biology alone and it's a top hit. But Claude flags it **Low confidence**: the screen never confirmed the knockdown actually worked. That's a month of bench time you *don't* spend. Surfacing that QC as a plain-English verdict — that's the product."

### Beat 4 — When does it act? (recovers known biology) (1:45–2:25)
- **[SCREEN]** Ask: *"Which of these only switch on when the T cell is activated?"* Then: *"Do the same for asthma."*
- **[SAY]** "A regulator's role changes with the T cell's state. It flags EGR2 as activation-induced — near-silent at rest. And for asthma it surfaces **ITK: one gene at rest, 3,392 when activated.** Crucially, the switch-on list *is* the TCR signalosome — LAT, ITK, BCL10 — real biology, recovered from the data. It rediscovers what we know, which is exactly why you can trust the calls you *don't* know yet."

### Beat 5 — Why this shape, and what it means (2:25–3:00)
- **[SAY]** "No new app, no key, no bioinformatician — it lives in the tool they already trust. The science is the authors'; what we built is the **last mile** — trust-ranked, activation-state-aware target leads a bench immunologist can act on in thirty seconds. There are thousands of labs that can run the experiment and are starved for a lead they can believe. This hands them one. That's T-Cell Target Explorer — built with Claude, and living inside it."

---

## How it maps to the judging criteria

- **Demo (30%)** — one clean conversation inside Claude, a single memorable payoff (IPMK vs
  STAT3: identical enrichment, opposite trust), and a positive-control-then-novel arc that
  recovers known biology (Th17 axis, TCR signalosome) so the novel calls are believable.
- **Impact (25%)** — attacks the bottleneck a bench scientist named as *the hardest thing*:
  adoption, not analysis. It meets them in Claude, the trust flag prevents wasted bench months,
  and it democratizes target triage for any wet-lab that can't afford a bioinformatician.
- **Claude use (25%)** — it *is* an MCP: it extends Claude directly, the host model does the
  reasoning grounded in the server's tools (no separate model, no API cost), and it packages a
  real dataset into something agent-native — the "meet them where they are" distribution the
  community keeps reaching for.
- **Depth (20%)** — a genuine GRN + QC trust layer and an activation-state axis (out-degree
  percentiles, per-state classification, on-/off-target across culture conditions) on the
  authors' precomputed tables; recovers the TCR signalosome as validation; locked demo invariant.
