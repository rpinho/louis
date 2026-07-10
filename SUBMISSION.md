# Submission packet — T-Cell Target Explorer

Everything a judge needs: the 150-word summary, the 3-minute demo script, and how the
project maps to the judging criteria. Numbers below are produced live by the app
(`python -m tcell_targets.core` re-checks the headline STAT3 invariant on every run).

---

## Submission summary (~155 words)

**T-Cell Target Explorer** turns a genome-scale CD4+ T-cell Perturb-seq screen
(Marson/Pritchard, 2025) into a self-serve tool a bench immunologist can actually use —
no terminal, no bioinformatician. Pick an autoimmune disease and get a ranked list of
candidate T-cell regulators to target, each carrying the three things a wet-lab scientist
needs to trust a hit: how strongly its program is enriched in the disease's genetics
(odds ratio), how central it is in the gene-regulatory network (how many downstream genes
it controls), and a plain-English **confidence flag** derived from the screen's own QC —
was the CRISPRi knockdown verified, and is the guide off-target? For Crohn's disease it
surfaces **STAT3**: a top-1% network hub (1,592 downstream genes), verified clean
knockdown, sitting in a program with IRF4 and BATF — the known Th17 axis. The upstream
science is the authors'; our contribution is the **last mile** — packaging rigor into a
trustworthy, shareable target report. Built with Claude.

---

## 3-minute demo script (beat by beat)

> Format: **[SCREEN]** = what to show · **[SAY]** = voiceover. Total ≈ 3:00.
> Start with the app already running on `http://localhost:8501`, disease = Crohn's disease.

### Beat 1 — The problem (0:00–0:25)
- **[SCREEN]** Briefly show the dataset page / an AnnData filename or a hash-named notebook cell, then cut to the app.
- **[SAY]** "This is a genome-scale Perturb-seq screen — every gene knocked down in human CD4+ T cells, mapped to autoimmune-disease genetics. It's a goldmine of drug targets. But it's locked behind AnnData objects and a bioinformatician. A bench immunologist who just wants *'what should I target for Crohn's, and can I trust it?'* can't get in. That's the gap we close."

### Beat 2 — Ask the question (0:25–0:50)
- **[SCREEN]** Sidebar: the disease dropdown is on **Crohn's disease**. Point to the three metrics: 98 candidate targets, 76 high-confidence, top target STAT3.
- **[SAY]** "No code — you pick a disease. Crohn's gives 98 candidate T-cell regulators, 76 of them high-confidence. And the top recommendation is STAT3. Here's why it earns that spot."

### Beat 3 — The evidence panel (0:50–1:45) ← the heart of the demo
- **[SCREEN]** Walk across the four pillars of the "Recommended target" panel, left to right.
- **[SAY]** "Four independent lines of evidence, on one screen. **One** — its regulatory program is enriched in Crohn's genetics, odds ratio 58. **Two** — perturbing STAT3 moves 1,592 downstream genes; that's the top 1.3% of all 11,500 regulators screened, where the median is *four*. It's a genuine network hub. **Three** — and this is the part nobody surfaces — the CRISPRi knockdown was *verified* on-target in all three conditions, with a clean guide. **Four** — functionally it skews cells toward Th1. And notice it shares its program with IRF4 and BATF — the known Th17 regulators — so the top hit is biologically coherent, not a fluke."

### Beat 4 — Why the trust flag is the whole point (1:45–2:20)
- **[SCREEN]** Scroll to the ranked table. Point at the **IPMK** row: same OR (58.2), but Confidence = *Low — knockdown not confirmed*.
- **[SAY]** "Here's the payoff. IPMK sits in that *same* enriched program as STAT3 — identical disease odds ratio. Rank on enrichment alone and it looks like a top hit. But its confidence is **Low**: the screen never confirmed the knockdown actually worked. That's a month of bench time you *don't* spend. Surfacing that QC as a plain-English flag — that's the deliverable."

### Beat 5 — A usable, shareable report (2:20–2:40)
- **[SCREEN]** Open the "Inspect a regulator" drill-down for STAT3 (per-condition GRN table), then click **Download this target report (CSV)**.
- **[SAY]** "Drill into any regulator for the per-condition detail a scientist would ask for — and export the whole ranked report as a CSV you can hand to a colleague. A real deliverable, not a notebook."

### Beat 6 — It generalizes, and the framing (2:40–3:00)
- **[SCREEN]** Switch the dropdown to **asthma** — the panel recomputes live to **ITK** (3,392 genes controlled).
- **[SAY]** "Switch to asthma and it recomputes instantly — ITK, an even bigger hub. We didn't re-derive any biology; the authors did the hard science. Our contribution is the last mile — turning it into something a bench scientist can trust and use in thirty seconds. That's T-Cell Target Explorer, built with Claude."

---

## How it maps to the judging criteria

- **Demo (30%)** — one tight workflow (disease → evidence panel → trust flag → CSV), a single
  memorable payoff (IPMK vs STAT3: same enrichment, opposite trust), real biologically-credible output.
- **Impact (25%)** — collapses a bioinformatician-gated analysis into a 30-second self-serve step
  for the wet-lab scientist who actually picks targets; the confidence flag prevents wasted bench months.
- **Claude use (25%)** — built with Claude; packages Claude-Science-style upstream analysis into a
  usable deliverable (the gap the hackathon community keeps hitting), rather than re-deriving it.
- **Depth (20%)** — a real GRN + QC trust layer (out-degree percentiles, on-/off-target flags across
  culture conditions) on top of the authors' precomputed tables, with a locked demo invariant.
