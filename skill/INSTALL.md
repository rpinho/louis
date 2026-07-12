# Install the Louis skill in Claude

The **skill** packages all of Louis — the Perturb-seq engine, the dataset, and the validated,
provenance-tracked knowledge base — into one self-contained upload that runs *inside Claude's own
compute* and composes with Claude's scientific-web connectors (Open Targets, ChEMBL, PubMed, GWAS
Catalog, ClinicalTrials). No local server, no API key: Claude reasons on your subscription.

## 1. Build the skill zip

From the repo (after `pip install -e .` and `python scripts/download_data.py`):

```bash
python scripts/build_skill.py         # -> dist/louis-skill.zip
```

The build bundles `SKILL.md` + the `louis/` engine + the 3 data tables + the `kb/` knowledge base,
trims to **under Claude's 200-file skill cap**, and drops regenerable indexes. It hard-fails if the
result would exceed the cap, so the zip is always uploadable.

## 2. Upload it as a skill

In Claude — **Claude Science**, **Claude Desktop**, or **claude.ai** — open the **Skills** panel →
**Create / Upload a skill** → choose `dist/louis-skill.zip`. Claude reads `name: louis` and the
description from `SKILL.md`; the skill is then available by name.

> **Tip (Claude Science):** Science keys a skill's identity off the existing skill / the zip
> filename. If you're *replacing* an older upload and it still shows the old name, **delete the old
> skill first, then create a fresh one** from `louis-skill.zip` — a fresh create picks up `name: louis`
> and the current content cleanly.

## 3. Use it

Just ask, naming the skill:

> *"Using my Louis skill, what should I target for rheumatoid arthritis — and which can I trust?"*
>
> *"Using my Louis skill, design the cleanest experiment for the top UC lead."*

On first run the skill seeds its knowledge base into a writable directory (it sets `LOUIS_KB_DIR`
automatically; the skill folder itself may be read-only). Everything after that — discover, validate,
listen, remember, synthesize — runs from the bundled KB.

## What's inside the skill

- **`SKILL.md`** — the workflow Claude follows (discover → validate → listen → remember → synthesize),
  including the §5 cross-disease synthesis recipe.
- **`louis/`** — the engine (`disease_mechanisms`, `disease_targets`, `target_evidence`, `kb.*`, …).
- **`data/`** — the 3 precomputed Marson/Pritchard supplementary tables the shipped tools load.
- **`kb/`** — the validated, provenance-tracked knowledge base (target profiles + community signal +
  cross-disease verdicts + experiment designs), seeded from 9 connector-validated diseases.
