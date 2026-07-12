# CBLB

*CD4+ T-cell regulator — target profile. Data facts, novelty, mechanism, and scientist verdicts, each with provenance.*

## Findings

- **2026-07-11**: profile opened for community signal  — *source: community_signal*
- **2026-07-11** (systemic lupus erythematosus): SLE Perturb-seq: co-clusters in module 100 (Stim8hr, OR=3.7, FDR=0.0025), kd_verified=True, regulates 1027 genes; risk genes in module: TRAF1, IRF8, PTPN22, IL18RAP, REL, EGR2, ETS1, CSK, CD226, ADO, HIVEP3, BACH2, CD47  — *source: Marson/Pritchard CD4+ Perturb-seq (Zhu, Dann et al. 2025)*
- **2026-07-11** (systemic lupus erythematosus): Open Targets SLE (MONDO_0007915) association score=0.032, datatypes={'literature': 0.263}; SM tractability=['Structure with Ligand', 'High-Quality Ligand']  — *source: Open Targets Platform GraphQL v4*
- **2026-07-11** (systemic lupus erythematosus): GWAS Catalog SLE/lupus gene-mapped hits=0. no direct SLE GWAS signal  — *source: GWAS Catalog (associations_for_gene)*
- **2026-07-11** (systemic lupus erythematosus): PubMed novelty: 779 total / 16 lupus / 10 lupus+T-cell papers  — *source: PubMed E-utilities*
- **2026-07-11** (systemic lupus erythematosus): Clinical compound: None — no clinical compound (preclinical CBL-B inhibitors; 1949 ChEMBL bioactivities); direction: inhibitor ENHANCES T-cell activation — wrong polarity for autoimmunity  — *source: ChEMBL + Open Targets + ClinicalTrials.gov*
- **VERDICT 2026-07-11** (systemic lupus erythematosus): **C+** — DIRECTIONAL MISMATCH. Strong module (OR 3.7, mod100), kd-verified clean guide, broad regulatory footprint (1027 genes). Well-grounded T-cell autoimmunity biology (Tfh/Treg; Immunity 2024, lupus-nephritis Tfh paper). Active drug-discovery target: 1949 ChEMBL bioactivities, CBL-B inhibitors advancing in immuno-oncology. CRITICAL: CBL-B is a NEGATIVE regulator of T-cell activation — available compounds INHIBIT it to ENHANCE T-cell responses (IO use). Autoimmunity would need CBL-B AGONISM/stabilization, opposite of the clinical pipeline. No approved/late-clinical compound (OT count=0). Interesting biology, mismatched tooling.
- **2026-07-11** (multiple sclerosis): Co-clusters with MS GWAS module 100 (Stim8hr): risk genes PTPN22, IRF8, BACH2, REL, BCL6, ETS1. High-trust handle. Unlike the other handles, CBLB ALSO carries its own MS GWAS signal.  — *source: tcell-target-explorer Perturb-seq engine + GWAS Catalog*
- **2026-07-11** (multiple sclerosis): Own genome-wide MS lead variants rs2289746 (p=5e-12) and rs9657904 (p=2e-10), both single-gene (clean) loci. Only handle with an Open Targets genetic_association datatype for MS (0.65; overall 0.40).  — *source: GWAS Catalog (MONDO_0005301) + Open Targets Platform*
- **2026-07-11** (multiple sclerosis): NOT novel: 12 MS PubMed papers incl. an MS-associated CBLB variant linking risk to type-I-IFN function (PMID 25261476) and CBL-B dynamics in MS PBLs (PMID 18565657). Emerging inhibitor NX-1607 (Ph1, onc/IO); small-molecule E3-ligase druggability still early (OT: preclinical SM only).  — *source: PubMed (verified titles) + ChEMBL*
- **2026-07-11** (multiple sclerosis): No MS clinical trials.  — *source: ClinicalTrials.gov*
- **VERDICT 2026-07-11** (multiple sclerosis): **B** — Genetically validated T-cell tolerance checkpoint: own MS GWAS lead variants (rs2289746, rs9657904) and the ONLY handle with an OT genetic_association datatype for MS (0.65); emerging inhibitor (NX-1607, Ph1). Gap: NOT novel/understudied — well-characterized in MS/EAE; small-molecule E3-ligase druggability still early (preclinical SM only).

## Community signal (Bluesky) — harvested 2026-07-11

*Query: `Bluesky searchPosts: CBLB`. Recent field chatter — pre-paper leads, not validated claims.*

- **@cellclub.bsky.social** ⭐ (Cell Biology J-Club) · 2026-03-27 · ♥5: Small-molecule CBLB inhibitor abolishes EGFR ubiquitination, reduces receptor endocytosis, and diminishes cell motility signaling | PNAS www.pnas.org/doi/10.1073/... — https://bsky.app/profile/cellclub.bsky.social/post/3mi2ym5srec2b · https://www.pnas.org/doi/10.1073/pnas.2524664123
- **@sciencebriefing.bsky.social** ⭐ (Science Briefing) · 2026-03-30 · ♥0: Today’s Cell Biology Science Briefing | March 30th 2026, 1:00:02 pm  Key Highlights • A new small-molecule inhibitor can block the CBLB protein, which stops it from tagging the Epidermal Growth Factor Receptor (EGFR) with a "recycle" signal — https://bsky.app/profile/sciencebriefing.bsky.social/post/3mibjs4z3vk22 · https://blog.sciencebriefing.com/todays-cell-biology-science-briefing-march-30th-2026-10002-pm/?utm_source=bluesky&utm_medium=jetpack_social
