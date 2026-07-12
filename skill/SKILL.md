---
name: louis
description: Louis — discover, validate, and remember novel CD4+ T-cell drug targets for autoimmune diseases from the Marson/Pritchard genome-scale CRISPRi Perturb-seq screen. Use when the user asks what to target for an autoimmune disease (Crohn's, rheumatoid arthritis, type 1 diabetes, asthma, lupus, MS, etc.), wants novel/understudied/druggable T-cell regulator leads wired to a disease's own GWAS risk genes, wants to trust-rank targets by CRISPRi knockdown QC or activation state, or wants to validate and record target hypotheses. Discovers mechanistic leads with disease_mechanisms(), validates them against the scientific-web connectors AND the field's live community signal, and remembers findings in a provenance-tracked knowledge base.
---

# Louis — CD4+ T-cell target discovery, validation & memory

Turns a genome-scale CD4+ T-cell CRISPRi Perturb-seq screen (Zhu, Dann, …, Pritchard, Marson 2025)
into a **discover → validate → listen → remember** workflow. The engine runs here in this compute
environment (Python + pandas); validation composes with your scientific-web connectors (Open Targets,
ChEMBL, PubMed, GWAS Catalog, ClinicalTrials, OpenAlex) **and** a baked community-signal layer — what
immunologists were posting on X about each target, pre-harvested into the knowledge base.

**Lead every answer with the TRUST verdict, and surface the activation state.** These are
hypotheses to prioritize bench work — not clinical claims.

## Setup (run once at the start of a session)

The skill bundles the engine (`louis/`), the dataset (`data/`), and a seeded knowledge
base (`kb/`) that already contains validated target profiles + community signal. Make the package
importable and point the KB at a writable directory (the skill folder may be read-only):

```python
import os, sys, shutil, tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).parent if "__file__" in dir() else Path.cwd()
# If louis isn't importable, set SKILL_DIR to the folder that contains this SKILL.md
# and the louis/ package, then re-run.
sys.path.insert(0, str(SKILL_DIR))

# KB must be writable. The sandbox HOME dir (~) is read-only — use the workspace, else a temp dir.
kb_dir = Path(os.environ.get("LOUIS_KB_DIR") or (Path.cwd() / "louis_kb"))
try:
    kb_dir.mkdir(parents=True, exist_ok=True)
except OSError:
    kb_dir = Path(tempfile.mkdtemp(prefix="louis_kb_"))
shutil.copytree(SKILL_DIR / "kb", kb_dir, dirs_exist_ok=True)   # seed from the bundled validated KB
os.environ["LOUIS_KB_DIR"] = str(kb_dir)

try:
    import pandas  # noqa
except ImportError:
    os.system(f"{sys.executable} -m pip install -q pandas")
```

## 1 — DISCOVER (novel, mechanistic, trust-ranked leads)

```python
from louis import list_diseases, disease_mechanisms, disease_targets, target_evidence
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
from louis import kb
kb.recall("AHR")                    # baked community signal is embedded in the profile
kb.recall("rheumatoid arthritis")   # disease-level chatter (labs/journals) too
```

The KB ships with a **community-signal** layer: recent X/Twitter chatter (labs, journals, news
desks — wellness noise filtered out) about each discovered gene and disease, harvested from the
tool's own leads. This is signal the paper/database connectors don't have yet — lab announcements,
preprint drops, pipeline news. See `kb/community_signal.md` for the index of which leads the field
is actively discussing. Treat posts as leads to weigh, not validated claims.

*Live refresh:* `from louis import community; community.community_signal("DOT1L")` pulls
fresh chatter where X access exists (Claude Code / Desktop). In this sandbox there is no X access,
so read the **baked** signal from the KB via `kb.recall`.

**Be the "phone-a-friend" that knows what isn't in a database yet.** For each lead, don't stop at the
tweet — chase it, and know which sources you already have vs. which are baked in because you can't reach them:
- **Follow the links** in the community posts (each carries expanded URLs). Papers → pull the abstract
  with **your own connectors** (PubMed, bioRxiv, OpenAlex, Crossref — all on your allowlist); labs →
  who's working on it. Preprints are **not** a gap: search your **bioRxiv / OpenAlex** connectors
  (`SRC:PPR`) directly for the freshest work — the tweet just tells you *which* one the field is excited about.
- **The off-allowlist sources are the point.** Your sandbox can only reach allowlisted scientific
  domains — so **X/Twitter**, **Bluesky**, and **conference-abstract sites are unreachable from here**,
  which is exactly why they're **baked into this KB**. Read them via `kb.recall`; that social + conference
  signal (e.g. the ACR abstract linking DNMT3A and DOT1L) is what you *can't* get any other way in this sandbox.
  (Bluesky harvest, no auth needed: `app.bsky.actor.searchActors` to find immunology journals/labs/researchers,
  then `app.bsky.feed.getAuthorFeed` per account — e.g. Nature Reviews Immunology, J Immunol, a bioRxiv-immunology feed.)
- **Conferences** are pre-paper knowledge — the "presenting at a conference, not published yet" gap.
  Baked in; recall them per gene. Searchable archives (off your allowlist, so harvested externally and
  baked): **acrabstracts.org** (ACR Convergence), **scientific.sparx-ip.net/archiveeular** (EULAR,
  2001+), and AAI/FOCIS/Keystone for immunology.
Record anything new with `kb.remember`, and **always label its confidence** — peer-reviewed paper vs.
preprint vs. conference abstract vs. a tweet (a preprint/abstract/post is a lead, not an established result).

## 4 — REMEMBER (so nothing is re-derived, and it's shareable)

```python
kb.recall("DOT1L")                                             # ALWAYS recall before re-deriving
kb.remember("DOT1L", "<finding>", "<source>", "rheumatoid arthritis")   # provenance-tracked
kb.verdict("DOT1L", "rheumatoid arthritis", "<grade>", "<rationale>")   # the scientist's judgment
```

Route each finding to its own target profile with a real source. A target profile is a reputation
record: data facts + literature novelty + community signal + validation + verdicts accrue to it.
The KB is git-tracked markdown — shareable with a student or a lab.

## 5 — SYNTHESIZE ACROSS DISEASES (the cross-disease / pan-autoimmune view)

When the question is *portfolio-level* — "which handles recur across diseases, and is
there ONE mechanism behind it?" — don't re-derive per disease. Run this five-step recipe.
It reads the accumulated verdicts, finds what recurs, and grades each recurrer as
**pan-autoimmune vs disease-specific** with the connectors. Output: a synthesis table +
verdicts filed back to each profile.

**Skeptic's frame:** recurrence in this screen is almost always *module-conserved* — the
same GRN module lights up in several diseases because those diseases share GWAS risk genes,
NOT because one regulator convergently controls them. Step 3 is what separates "shared
disease wiring" from "one mechanism." Everything here is module-level co-cluster
association, not a proven gene-level edge.

### Step 1 — Pull every graded verdict, find the recurrers

```python
from louis import kb_index
verds = kb_index.query(rec_type="verdict", limit=200)["records"]   # every verdict, all diseases

# grade-A/B set; best grade per (gene,disease); recurrence = A/B in >=2 diseases
def is_AB(g): return g and g[0] in ("A", "B")
from collections import defaultdict
gene_dis = defaultdict(dict)
for v in verds:
    if is_AB(v["grade"]):
        gene_dis[v["gene"]][v["disease"]] = v["grade"]
recur = {g: d for g, d in gene_dis.items() if len(d) >= 2}   # rank by len(d) desc
```
*MCP-tool equivalent:* `kb_query(rec_type="verdict", limit=200)`. Note the grade parser only
reads a bare `**B**` token — file verdicts with a clean leading grade if you want them
`grade`-queryable.

### Step 2 — Anchor each recurrer to its module / state / risk-gene spine

```python
from louis import disease_mechanisms
for dis in {v["disease"] for v in verds if v["disease"]}:
    for m in disease_mechanisms(dis, top_modules=60):        # keys: module, fires_in_state,
        names = [h["gene"] if isinstance(h, dict) else h      #       odds_ratio, fdr,
                 for h in m["candidate_handles"]]             #       disease_risk_genes,
        # record (disease, m["module"], m["fires_in_state"], m["odds_ratio"], m["disease_risk_genes"])
        # for each recurrer gene found in `names`
```
A handle that recurs sits in **one fixed module** across diseases. Read off (a) is it the
SAME module each time? (b) same activation state? (c) what risk genes are shared across the
spines? Same module + shared spine (e.g. IRF8/PTPN22/REL/EGR2/ETS1) = the recurrence is
disease-risk-gene overlap, not a convergent regulator.

### Step 3 — Grade pan-autoimmune vs disease-specific with the connectors

All connector calls run in the **`repl` tool** via `host.mcp(...)`. Resolve IDs first
(Open Targets `search` over `entityNames:["target"]` / `["disease"]`), then per handle:

```python
# (a) Tractability + which diseases have a GENETIC (not just literature) association
host.mcp("clinical-genomics", "open_targets_graphql",
         query="query($id:String!){target(ensemblId:$id){tractability{modality label value}}}",
         variables={"id": ensembl_id})
host.mcp("clinical-genomics", "open_targets_graphql",           # per-disease datatype split
         query="query($id:String!,$efos:[String!]){target(ensemblId:$id){associatedDiseases"
               "(Bs:$efos){rows{disease{id name} score datatypeScores{id score}}}}}",
         variables={"id": ensembl_id, "efos": efo_list})
#   -> read datatypeScores: genetic_association present & >0 in >1 disease = broader genetic base

# (b) GWAS Catalog — do the hits map to the gene ITSELF, and to which traits?
host.mcp("human-genetics", "gwas_associations_for_gene", gene_symbol=g, max_records=500)
#   filter efo_traits/reported_trait to autoimmune terms; check mapped_genes (own gene vs flanking
#   = causal-gene-ambiguous locus) and whether traits are T-cell autoimmune vs allergy/OA/other
host.mcp("human-genetics", "gwas_get_variant", rs_id=lead_rs)   # confirm locus/consequence

# (c) ClinicalTrials — is a SELECTIVE compound already tried in ANY autoimmune indication?
host.mcp("clinical-trials", "search_trials", intervention="<drug OR class terms>",
         condition="rheumatoid arthritis OR lupus OR multiple sclerosis OR colitis OR "
                   "Crohn OR psoriasis OR autoimmune", count_total=True, page_size=20)
#   distinguish selective vs class-level (e.g. pan-HDAC != HDAC7-selective)

# (d) PubMed — mechanism novelty for THIS gene x CD4/Treg, and the unifying-mechanism test
host.mcp("pubmed", "search_articles", query="<GENE> AND (Treg OR CD4 T cell)", max_results=5)
host.mcp("pubmed", "get_article_metadata", pmids=[...])          # pull the load-bearing abstracts
```
Write `host.mcp` results to `./handoff/*.json`; do the tabulation in the `python` tool.
**Verify any load-bearing citation** (confirm it exists; peer-reviewed vs preprint).

### Step 4 — Decide the ONE-mechanism question, then classify each handle

- **One mechanism?** Only if the recurrers share module AND state AND a genetic axis. If they
  sit in different modules / different activation states (Rest vs Stim8hr) / different classes
  (metabolic vs epigenetic), the recurrence is shared disease wiring — say so explicitly.
- **Pan-autoimmune** = genetic association (own-gene GWAS, OT `genetic_association`) in
  multiple diseases, not one shared ambiguous locus. **Disease-specific** = recurs at module
  level but genetics concentrate in one disease / map to a non-autoimmune trait.

### Step 5 — Record verdicts + findings, snapshot the KB

```python
from louis import kb, kb_index
kb.remember(gene, "<cross-disease finding>", "<connector + provenance>")      # per handle
kb.verdict(gene, "pan-autoimmune (cross-disease)", "<grade>", "<rationale>")  # the judgment
kb.remember_signal("<mechanism topic>", [{...}], kind="topic",
                   platform="Claude Science synthesis")                        # the axis note
kb.reindex(); kb_index.build()                                                 # rebuild both indices
```
*MCP-tool equivalents:* `kb_remember`, `kb_verdict`. Then zip `kb/` and save
`cross_disease_synthesis.csv` + `louis_kb_snapshot.zip` as artifacts.
