# METAP2

*CD4+ T-cell regulator — target profile. Data facts, novelty, mechanism, and scientist verdicts, each with provenance.*

## Findings

- **2026-07-11** (Crohn's disease): Co-clusters in module 88 (fires in Stim48hr, module OR=4.0, FDR=6.5e-04) with IBD/Crohn's GWAS risk genes; network out-degree 771. MODULE-LEVEL CO-CLUSTER ASSOCIATION — candidate upstream controller to test, NOT a proven gene-level edge.  — *source: Zhu/Dann/Pritchard/Marson 2025 CD4+ Perturb-seq (tcell-target-explorer disease_mechanisms)*
- **2026-07-11** (Crohn's disease): Open Targets Crohn's: indirect(ontology-propagated) overall=0.757 vs DIRECT-only=0.000 (IBD direct=0.000). Gap = propagation from related diseases; direct score is the honest disease link.  — *source: Open Targets Platform GraphQL (enableIndirect true vs false)*
- **2026-07-11** (Crohn's disease): Tractability (SM buckets): ['Advanced Clinical', 'Structure with Ligand', 'High-Quality Ligand', 'Med-Quality Pocket', 'Druggable Family']. Clinical compound: BELORANIB (CHEMBL4297504) max_phase=3.0.  — *source: Open Targets tractability + ChEMBL get_mechanism/compound_search*
- **2026-07-11** (Crohn's disease): Handle is NOT itself a GWAS risk gene for IBD/Crohn's — association is via co-clustered module risk genes only. Module risk genes with real IBD/Crohn GWAS signal: ['CD226', 'IL2', 'STAT3', 'CD6'].  — *source: GWAS Catalog (gwas_associations_for_gene / gwas_get_variant)*
- **2026-07-11** (Crohn's disease): PubMed novelty: 243 total abstracts; 0 with IBD/Crohn/colitis; 0 with IBD + T-cell.  — *source: PubMed search_articles (Title/Abstract counts)*
- **VERDICT 2026-07-11** (Crohn's disease): **D** — Clearest 'data cannot support' case: ZERO direct Crohn's/IBD Open Targets evidence and ZERO IBD PubMed — its 0.76 headline score is 100% ontology-propagation artifact. Highest network influence (out-degree 771) drove the co-cluster, but the disease wiring is absent. Lead compound beloranib reached Ph3 (obesity) then was discontinued on thrombosis safety. Do not pursue for IBD on this basis.
- **2026-07-11** (Crohn's disease): Beloranib (CHEMBL4297504, METAP2 inhibitor) reached Phase 3 for OBESITY, then discontinued after venous-thrombosis safety signals; no IBD/Crohn's program. No active Crohn's/IBD trials for any METAP2 inhibitor.  — *source: ChEMBL max_phase; ClinicalTrials.gov (0 beloranib IBD trials)*
- **VERDICT 2026-07-12** (asthma): **B** — mod 88 (Stim48hr, OR 2.6; type-2 cytokine cluster). Best tractability (OT Advanced Clinical; clinical inhibitors beloranib max_phase=3 obesity, fumagillin max_phase=2 — ChEMBL-verified, NONE in asthma/immune). BUT zero asthma genetics, 0 asthma pubs, 0 immune trials — a pure co-cluster, repurposing hypothesis only.
