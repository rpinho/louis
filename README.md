# 🧬 T-Cell Target Explorer

**Pick an immune disease → get candidate CD4+ T-cell drug targets you can actually trust — no terminal, no bioinformatician.**

Built for the *Built with Claude: Life Sciences* hackathon (Builder track) on the **Marson/Pritchard genome-scale CD4+ T-cell Perturb-seq** dataset (Zhu, Dann, …, Pritchard, Marson 2025; [preprint](https://www.biorxiv.org/content/10.64898/2025.12.23.696273v1) · [CZI Virtual Cells Platform](https://virtualcellmodels.cziscience.com/dataset/genome-scale-tcell-perturb-seq)).

---

## The problem (a real one, not invented)

That dataset perturbed **every gene in primary human CD4+ T cells** and mapped which regulators drive which T-cell programs, and which programs are enriched in autoimmune-disease genetics — i.e. **candidate drug targets**. The analysis is powerful but locked behind AnnData objects, hash-named code chunks, and a bioinformatician. A bench immunologist who just wants *"what should I target for Crohn's, and can I trust it?"* can't self-serve it.

## What this does

Pick a disease → a **ranked list of candidate T-cell regulators**, each annotated with a **plain-English trust flag** so the hit is believable:

| Gene | Confidence | disease OR | Th1/Th2 effect |
|---|---|---|---|
| STAT3 | High — verified knockdown, clean guide | 58.2 | … |
| IRF4 | High — verified knockdown, clean guide | 58.2 | … |
| ITK *(asthma)* | High — verified knockdown, clean guide | 20.4 | … |

The **confidence flag is the point**: it's derived from the guide **knockdown efficiency** (did the CRISPRi actually work?) and the **off-target metadata** (is the guide clean?) — so a wet-lab scientist knows which hits to trust before spending months at the bench. Results are biologically legit out of the box (Crohn's → STAT3/IRF4/BATF; asthma → ITK/STAT6; RA → CTLA4/STAT4).

## Why it's a *builder* project, not "a worse Claude Science"

- The upstream **science is precomputed by the dataset authors** (GRN clustering, disease enrichment, guide QC) — we don't re-derive biology.
- The value is the **last mile**: packaging it into a **self-serve, trustworthy, shareable** target report for a named non-technical user, with the rigor/QC surfaced as a confidence flag. That's the gap the community keeps hitting ("how do I get a usable deliverable out?").
- Builds **on** the data (and can use Claude Science as an engine), rather than competing with it.

## Run it

```bash
pip install -r requirements.txt
python scripts/download_data.py     # small public tables (~30 MB), MIT-licensed
streamlit run app.py                # then pick a disease
```

Programmatic:
```python
from tcell_targets import disease_targets
df = disease_targets("Crohn's disease")   # ranked genes + confidence + Th1/Th2 effect
```

## Data

Uses the authors' **precomputed** supplementary tables (auto-downloaded): cluster↔autoimmune-disease enrichment, guide knockdown efficiency, sgRNA off-target library, Th1/Th2 polarization signature. The full ~22M-cell AnnData is **not** required. Optional GRN-edge detail (`GWCD4i.DE_stats.h5ad`, 33,983 perturbations × 10,282 genes) is available via the CZI Virtual Cells Platform.

## Scope / honesty

17 autoimmune diseases, 185 significant disease↔program links. This surfaces and *trust-ranks* candidate targets from a published dataset — it is a hypothesis-generation and prioritization tool for bench scientists, **not** a validated clinical claim. Confidence flags reflect experimental QC of the CRISPRi perturbation, not therapeutic efficacy.

*License: MIT (data and code). New code written for the hackathon; public dataset.*
