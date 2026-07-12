# MLKL

*CD4+ T-cell regulator — target profile. Data facts, novelty, mechanism, and scientist verdicts, each with provenance.*

## Findings

- **2026-07-11**: profile opened for community signal  — *source: community_signal*
- **2026-07-11** (Crohn's disease): Co-clusters in module 78 (fires in Rest, module OR=4.7, FDR=1.2e-04) with IBD/Crohn's GWAS risk genes; network out-degree 79. MODULE-LEVEL CO-CLUSTER ASSOCIATION — candidate upstream controller to test, NOT a proven gene-level edge.  — *source: Zhu/Dann/Pritchard/Marson 2025 CD4+ Perturb-seq (tcell-target-explorer disease_mechanisms)*
- **2026-07-11** (Crohn's disease): Open Targets Crohn's: indirect(ontology-propagated) overall=0.874 vs DIRECT-only=0.006 (IBD direct=0.122). Gap = propagation from related diseases; direct score is the honest disease link.  — *source: Open Targets Platform GraphQL (enableIndirect true vs false)*
- **2026-07-11** (Crohn's disease): Tractability (SM buckets): ['Structure with Ligand', 'High-Quality Ligand', 'Druggable Family']. Clinical compound: no clinical compound targeting this protein.  — *source: Open Targets tractability + ChEMBL get_mechanism/compound_search*
- **2026-07-11** (Crohn's disease): Handle is NOT itself a GWAS risk gene for IBD/Crohn's — association is via co-clustered module risk genes only. Module risk genes with real IBD/Crohn GWAS signal: ['PTPN22', 'IKZF1', 'PRKCB', 'CYLD', 'NCOR2'].  — *source: GWAS Catalog (gwas_associations_for_gene / gwas_get_variant)*
- **2026-07-11** (Crohn's disease): PubMed novelty: 2694 total abstracts; 77 with IBD/Crohn/colitis; 4 with IBD + T-cell.  — *source: PubMed search_articles (Title/Abstract counts)*
- **VERDICT 2026-07-11** (Crohn's disease): **D** — Terminal necroptosis executioner — mechanistically downstream of and redundant with the already-pursued RIPK1 axis. Pseudokinase = poor small-molecule tractability (no clinical compound exists). Direct Crohn's evidence collapses to 0.006. Novel as a *named* IBD target but the drugging path is the weakest of the five.

## Community signal (Bluesky) — harvested 2026-07-11

*Query: `Bluesky searchPosts: MLKL T cell`. Recent field chatter — pre-paper leads, not validated claims.*

- **@natcellbio.nature.com** ⭐ (Nature Cell Biology) · 2025-09-24 · ♥5: 💫NEW: Yang, Li, Huang, Ji, Luo, Jiang et al report that chemotherapy induces MLKL PARylation and #necroptosis in tumor endothelial cells, which in turn affects tumor-associated #macrophages and CD8⁺ T cells, promoting #immunosuppression and — https://bsky.app/profile/natcellbio.nature.com/post/3lzksp3p4pk2k · https://bit.ly/4njRM4p
- **2026-07-11** (ulcerative colitis): UC validation (Claude Science, Louis loop): OT direct/indirect, GWAS Catalog, ChEMBL/OT drugs, PubMed novelty, ClinicalTrials. See verdict.  — *source: Claude Science validation 2026-07-12 (Open Targets/ChEMBL/GWAS Catalog/PubMed/ClinicalTrials)*
- **VERDICT 2026-07-11** (ulcerative colitis): **D** (#4) — Named as a novel UC handle but the drugging path is weakest: pseudokinase = poor small-molecule tractability, no clinical compound (necrosulfonamide is a preclinical human-MLKL tool). Direct UC genetic ~0.01; 0 GWAS IBD/UC hits. Terminal necroptosis executioner — downstream of and redundant with the already-pursued RIPK1 axis. 34 UC papers = not whitespace. Module 78 (Rest) co-clusters PTPN22/IKZF1/TNFRSF14.
