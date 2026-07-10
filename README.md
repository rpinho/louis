# 🧬 T-Cell Target Explorer

**Pick an immune disease → get candidate CD4+ T-cell drug targets you can actually trust — no terminal, no bioinformatician.**

Built for the *Built with Claude: Life Sciences* hackathon (Builder track) on the **Marson/Pritchard genome-scale CD4+ T-cell Perturb-seq** dataset (Zhu, Dann, …, Pritchard, Marson 2025; [preprint](https://www.biorxiv.org/content/10.64898/2025.12.23.696273v1) · [CZI Virtual Cells Platform](https://virtualcellmodels.cziscience.com/dataset/genome-scale-tcell-perturb-seq)).

![T-Cell Target Explorer — Crohn's disease → STAT3, with the full evidence panel](docs/screenshot.png)

---

## The problem (a real one, not invented)

That dataset perturbed **every gene in primary human CD4+ T cells** and mapped which regulators drive which T-cell programs, and which programs are enriched in autoimmune-disease genetics — i.e. **candidate drug targets**. The analysis is powerful but locked behind AnnData objects, hash-named code chunks, and a bioinformatician. A bench immunologist who just wants *"what should I target for Crohn's, and can I trust it?"* can't self-serve it.

## What this does

Pick a disease → a **ranked list of candidate T-cell regulators**, and — for the #1 hit — a **"why this target" evidence panel** that assembles the whole case on one screen:

| Evidence | For Crohn's → **STAT3** |
|---|---|
| **Disease enrichment** | STAT3's regulatory program is enriched in Crohn's genetics — odds ratio **58.2** (FDR 3.3e-04) |
| **Network influence** | Perturbing STAT3 moves **1,592** downstream genes — **top 1.3%** of all 11,526 regulators screened (median: 4) |
| **Trust / rigor** | CRISPRi knockdown **verified** on-target in all 3 culture conditions; guide is clean (no off-target flag) |
| **Function** | Skews CD4+ polarization toward **Th1** (Th2/Th1 log2FC −0.14) |

The **confidence flag is the point**: it's derived from the guide **knockdown efficiency** (did the CRISPRi actually work?) and the **off-target metadata** (is the guide clean?) — so a wet-lab scientist knows which hits to trust *before* spending months at the bench. And STAT3's program also contains **IRF4** and **BATF** — the other core Th17 regulators — so the top hit is biologically coherent, not a statistical fluke.

Results are legit out of the box for any of the 17 diseases: **Crohn's → STAT3**, **asthma → ITK** (controls 3,392 genes), **rheumatoid arthritis → EGR2**. Every report is one click to **download as CSV**.

## Why it's a *builder* project, not "a worse Claude Science"

- The upstream **science is precomputed by the dataset authors** (GRN clustering, disease enrichment, guide QC) — we don't re-derive biology.
- The value is the **last mile**: packaging it into a **self-serve, trustworthy, shareable** target report for a named non-technical user, with the rigor/QC surfaced as a confidence flag. That's the gap the community keeps hitting ("how do I get a usable deliverable out?").
- Builds **on** the data (and can use Claude Science as an engine), rather than competing with it.

## Run it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/download_data.py     # small public tables (~34 MB), MIT-licensed
streamlit run app.py                # opens http://localhost:8501 — then pick a disease
```

Sanity-check the engine (prints the top targets and asserts the Crohn's → STAT3 demo invariant):

```bash
python -m tcell_targets.core
```

Programmatic:
```python
from tcell_targets import disease_targets, target_evidence
df = disease_targets("Crohn's disease")            # ranked genes + confidence + GRN + Th1/Th2
ev = target_evidence("Crohn's disease", "STAT3")   # the full evidence case for one target
```

## Data

Uses the authors' **precomputed** supplementary tables (auto-downloaded): cluster↔autoimmune-disease enrichment, per-perturbation DE stats (with `n_downstream` = GRN out-degree), guide knockdown efficiency, sgRNA off-target library, and the Th1/Th2 polarization signature. The full ~22M-cell AnnData is **not** required. Optional GRN-edge detail (`GWCD4i.DE_stats.h5ad`, 33,983 perturbations × 10,282 genes) is available via the CZI Virtual Cells Platform.

## Scope / honesty

17 autoimmune diseases, 185 significant disease↔program links. This surfaces and *trust-ranks* candidate targets from a published dataset — it is a hypothesis-generation and prioritization tool for bench scientists, **not** a validated clinical claim. Confidence flags reflect experimental QC of the CRISPRi perturbation, not therapeutic efficacy.

*License: [MIT](LICENSE) (data and code). New code written for the hackathon; public dataset.*
