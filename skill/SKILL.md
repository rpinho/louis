---
name: tcell-target-explorer
description: Discover, validate, and remember novel CD4+ T-cell drug targets for autoimmune diseases from the Marson/Pritchard genome-scale CRISPRi Perturb-seq screen. Use when the user asks what to target for an autoimmune disease (Crohn's, rheumatoid arthritis, type 1 diabetes, asthma, lupus, MS, etc.), wants novel/understudied/druggable T-cell regulator leads wired to a disease's own GWAS risk genes, wants to trust-rank targets by CRISPRi knockdown QC or activation state, or wants to validate and record target hypotheses. Discovers mechanistic leads with disease_mechanisms(), validates them against the scientific-web connectors AND the field's live community signal, and remembers findings in a provenance-tracked knowledge base.
---

# T-Cell Target Explorer

Turns a genome-scale CD4+ T-cell CRISPRi Perturb-seq screen (Zhu, Dann, …, Pritchard, Marson 2025)
into a **discover → validate → listen → remember** workflow. The engine runs here in this compute
environment (Python + pandas); validation composes with your scientific-web connectors (Open Targets,
ChEMBL, PubMed, GWAS Catalog, ClinicalTrials, OpenAlex) **and** a baked community-signal layer — what
immunologists were posting on X about each target, pre-harvested into the knowledge base.

**Lead every answer with the TRUST verdict, and surface the activation state.** These are
hypotheses to prioritize bench work — not clinical claims.

## Setup (run once at the start of a session)

The skill bundles the engine (`tcell_targets/`), the dataset (`data/`), and a seeded knowledge
base (`kb/`) that already contains validated target profiles + community signal. Make the package
importable and point the KB at a writable directory (the skill folder may be read-only):

```python
import os, sys, shutil, tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).parent if "__file__" in dir() else Path.cwd()
# If tcell_targets isn't importable, set SKILL_DIR to the folder that contains this SKILL.md
# and the tcell_targets/ package, then re-run.
sys.path.insert(0, str(SKILL_DIR))

# KB must be writable. The sandbox HOME dir (~) is read-only — use the workspace, else a temp dir.
kb_dir = Path(os.environ.get("TCELL_KB_DIR") or (Path.cwd() / "tcell_target_kb"))
try:
    kb_dir.mkdir(parents=True, exist_ok=True)
except OSError:
    kb_dir = Path(tempfile.mkdtemp(prefix="tcell_kb_"))
shutil.copytree(SKILL_DIR / "kb", kb_dir, dirs_exist_ok=True)   # seed from the bundled validated KB
os.environ["TCELL_KB_DIR"] = str(kb_dir)

try:
    import pandas  # noqa
except ImportError:
    os.system(f"{sys.executable} -m pip install -q pandas")
```

## 1 — DISCOVER (novel, mechanistic, trust-ranked leads)

```python
from tcell_targets import list_diseases, disease_mechanisms, disease_targets, target_evidence
list_diseases()                                    # the 17 diseases available
mods = disease_mechanisms("rheumatoid arthritis")  # the discovery call
```

`disease_mechanisms(disease)` returns the disease's GWAS-risk-gene **modules**, each with the
specific risk genes, the **activation state** it fires in, and the candidate druggable **handles**
that co-cluster with it (sorted trust-first). The obvious Th17 handles (STAT3/BATF/IRF4) are the
positive control; the value is the **understudied, druggable** handles (e.g. DOT1L, GLS) wired to
known risk genes. `disease_targets(disease)` gives the ranked gene-level view with trust flag +
state; `target_evidence(disease, gene)` gives the full case for one gene.

**Honest resolution:** these are module-level co-cluster associations — candidate upstream
controllers to *test*, not proven gene-level edges.

## 2 — VALIDATE (with the scientific-web connectors)

For each promising handle, use the connectors to grade it:
- **Open Targets / ChEMBL** — druggability/tractability, clinical-stage compounds. (Be skeptical:
  Open Targets aggregate association scores can be ontology-propagation artifacts — check the
  actual evidence rows, not just the score.)
- **PubMed / bioRxiv / OpenAlex** — how novel is it as a target for *this disease + CD4 T cells*
  specifically (vs. other diseases)?
- **ClinicalTrials** — is it already being pursued for this disease?

Verify any load-bearing citation before relying on it (confirm the paper exists, and whether it is
peer-reviewed or a preprint).

## 3 — LISTEN (the field's bleeding-edge, pre-paper signal)

```python
from tcell_targets import kb
kb.recall("AHR")                    # baked community signal is embedded in the profile
kb.recall("rheumatoid arthritis")   # disease-level chatter (labs/journals) too
```

The KB ships with a **community-signal** layer: recent X/Twitter chatter (labs, journals, news
desks — wellness noise filtered out) about each discovered gene and disease, harvested from the
tool's own leads. This is signal the paper/database connectors don't have yet — lab announcements,
preprint drops, pipeline news. See `kb/community_signal.md` for the index of which leads the field
is actively discussing. Treat posts as leads to weigh, not validated claims.

*Live refresh:* `from tcell_targets import community; community.community_signal("DOT1L")` pulls
fresh chatter where X access exists (Claude Code / Desktop). In this sandbox there is no X access,
so read the **baked** signal from the KB via `kb.recall`.

**Follow the pointers, and reach the PRE-PAPER sources (this is the whole product — be the
"phone-a-friend" that knows what isn't published yet).** For each lead, don't stop at the tweet —
chase it and pull the pre-paper record the published-literature connectors lag on:
- **Follow the links** in the community posts (each post carries expanded URLs). Papers → pull the
  abstract; labs → who's working on it; videos/long-forms → the content. Use your connectors /
  web fetch; **Europe PMC** (open) resolves most DOIs, including **bioRxiv/medRxiv preprints**.
- **Preprints** — search Europe PMC with `SRC:PPR` (or OpenAlex) for the gene + a T-cell/autoimmune
  context: the freshest bioRxiv/medRxiv work, often weeks ahead of PubMed.
- **Conferences** — the exact gap ("presenting at a conference, not published yet"). Rheumatology
  abstracts are searchable at **acrabstracts.org** (ACR Convergence) and EULAR's *Annals* supplement;
  immunology at AAI/FOCIS/Keystone. Conference abstracts are pre-paper knowledge.
Record what you find with `kb.remember`, and **always label its confidence** — peer-reviewed paper vs.
preprint vs. conference abstract (a preprint/abstract is a lead, not an established result).

## 4 — REMEMBER (so nothing is re-derived, and it's shareable)

```python
kb.recall("DOT1L")                                             # ALWAYS recall before re-deriving
kb.remember("DOT1L", "<finding>", "<source>", "rheumatoid arthritis")   # provenance-tracked
kb.verdict("DOT1L", "rheumatoid arthritis", "<grade>", "<rationale>")   # the scientist's judgment
```

Route each finding to its own target profile with a real source. A target profile is a reputation
record: data facts + literature novelty + community signal + validation + verdicts accrue to it.
The KB is git-tracked markdown — shareable with a student or a lab.
