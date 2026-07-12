# HDAC7 — cleanest knockdown + selective-inhibitor experiment for the UC lead

> *Provenance: authored by Claude Science (Louis recursion loop), 2026-07-12. Screen numbers independently verified against the engine on 2026-07-12 — HDAC7 footprint Rest 84 / Stim8hr 56 / Stim48hr 134 (KD-verified, no off-target); UC module 59 = Stim8hr, OR 3.1, fdr 6.1e-3, HDAC7 a candidate handle.*

**Target:** HDAC7 (class IIa histone deacetylase)
**Disease context:** ulcerative colitis, CD4⁺ T-cell-intrinsic
**Screen provenance:** Marson/Pritchard genome-scale CRISPRi Perturb-seq — HDAC7 is a **module-level co-cluster handle** for UC risk-gene module 59, which is enriched at **Stim8hr** (odds ratio 3.1). HDAC7's own regulatory footprint is **activation-modulated** and *peaks later* — Rest 84 → Stim8hr 56 → **Stim48hr 134** downstream genes (KD verified in 3/3 conditions).
**Orthogonal anchor:** UC GWAS credible-set variant **rs11168249** maps cleanly to HDAC7 alone (12q13.11; UC hits p=6e-8 PMID37156999, p=3e-7 PMID28067908, p=7e-7 PMID26192919). OT direct-UC association 0.29 (genetic_association datatype 0.47) — the only non-artifactual direct signal of the five UC handles.

---

## 0. What this experiment must prove (and what it cannot)

The screen gives a **co-cluster association**, not a proven regulatory edge. A clean experiment therefore has to clear three bars, in order:

1. **Edge test** — does lowering HDAC7 actually move the *UC risk-gene module* (IL10, PRDM1, BACH2, CD28, FAS, RASGRP1, IRF8, RASGRP1, FOSL2, REL) coherently, in the activation state where the module fires? Not just "some phenotype" — the specific module.
2. **Direction test** — is the shift therapeutically coherent for UC (↓pathogenic Th17/IFN-γ, ↑ or preserved Treg/IL10)? HDAC7 carries a documented **Treg/self-tolerance double-edge**, so a Treg readout is mandatory, not optional.
3. **Mechanism test** — is the effect through HDAC7's **scaffold** function (recruiting SMRT/NCoR–HDAC3) or its weak catalytic activity? This decides whether a catalytic inhibitor could ever reproduce it.

The design is built so that a negative result at bar 1 kills the lead cheaply, before any inhibitor work.

---

## 1. System

- **Cells:** human primary CD4⁺ T cells, negatively isolated from PBMC. **≥4 healthy donors** for the core (biological replication across HLA/genetic backgrounds); a confirmatory **2–3 UC-patient-derived** donor set for the top readouts only (translational, run after the healthy-donor gate).
- **Modality matches the screen:** lentiviral **CRISPRi (dCas9-KRAB)**, the same perturbation class as the Perturb-seq screen — so a hit here is a same-modality confirmation, not a new assay with new failure modes.
- **Activation states (the screen's axis):** Rest, **Stim 8h** (module-firing state), **Stim 48h** (HDAC7 footprint peak). Stimulate with anti-CD3/CD28 (beads or plate-bound) ± Th17-polarizing cocktail (IL-6, IL-1β, TGF-β, IL-23) for the Th17-directionality readout.

---

## 2. Arm A — CRISPRi knockdown (PRIMARY, clean perturbation)

The genetic arm is the load-bearing one: it removes the whole protein (scaffold + catalytic), matches the screen, and is the only arm that can isolate HDAC7 from its paralogs.

| Element | Specification |
|---|---|
| Guides | **≥2 independent HDAC7 sgRNAs** targeting the TSS window, each validated for knockdown; use the screen's validated guide as one of the two |
| Knockdown QC | RT-qPCR + protein (WB/intracellular flow) per donor per guide; **require ≥70% mRNA knockdown** before a well counts |
| Delivery | dCas9-KRAB lentivirus, puromycin/blasticidin selection or dCas9⁺ marker sort; matched MOI across arms |
| States | Rest / Stim8h / Stim48h, all donors |

**Controls (Arm A):**
- **Non-targeting sgRNA** (≥2 distinct NT guides) — the primary comparator.
- **Safe-harbor sgRNA** (e.g. AAVS1) — controls for CRISPRi machinery load / dCas9-KRAB tox independent of a real gene.
- **Positive-control guide:** a known module/Th17 regulator from the same screen (e.g. STAT3 or BATF as the Th17 positive control) — proves the assay can detect a true module shift in this donor set.
- **Untransduced + dCas9-KRAB-only** wells — baseline and machinery-only.
- **Two-guide concordance** is itself a control: an effect real for HDAC7 must reproduce across both independent guides; a guide-specific effect = off-target, discard.

---

## 3. Arm B — pharmacology (COMPLEMENT, deliberately caveated)

**There is no HDAC7-selective compound.** This arm is explicitly labeled a translational/orthogonal complement, *not* a genetic-equivalent — and its central purpose is the **mechanism (scaffold vs catalytic) test**, not clean target isolation.

| Compound | Selectivity | Role |
|---|---|---|
| **TMP195** (and TMP269 as orthogonal chemotype) | **class IIa-selective** (HDAC4/5/7/9; HDAC7 IC50 ~26 nM) — NOT HDAC7-selective | Best available "on-class" catalytic probe. Dose–response + washout. |
| **Pan-HDACi (e.g. vorinostat)** | pan | Bridges to a recruiting vorinostat IBD proof-of-concept trial that includes UC (NCT03167437, verified 2026-07-12: open-label vorinostat for moderate–severe Crohn's / ulcerative colitis / CGD colitis with ustekinumab maintenance, RECRUITING); interpret only as class-context, high off-target |
| (Optional) **class-IIa / HDAC7 degrader** if a qualified one is available | scaffold-removing | The only pharmacological way to mimic the KD's scaffold loss |

**Controls (Arm B):**
- **Vehicle (DMSO) matched to top dose**, per state, per donor.
- **Dose–response (≥5 points)** — a real on-mechanism effect is dose-dependent and should track class IIa engagement; a flat or all-or-none response flags toxicity.
- **Viability/apoptosis co-stain at every dose** (7-AAD/Annexin-V) — HDACi cytotoxicity is the dominant confounder; gate all functional readouts on live cells and drop doses with >X% viability loss.
- **Catalytic-vs-scaffold discriminator:** if TMP195 (catalytic block) does **not** phenocopy the CRISPRi KD while a degrader does, the phenotype is scaffold-driven — a mechanistically decisive, publishable result and an explanation for why catalytic drugs might fail.

---

## 4. Rescue / specificity (closes the loop on Arm A)

- **sgRNA-resistant HDAC7 cDNA re-expression** in the CRISPRi-KD background → must **reverse** the phenotype. This is the definitive specificity control; a non-reversing phenotype is off-target.
- **Structure–function rescue** (mechanism): re-express (i) WT, (ii) **catalytic-dead** HDAC7, (iii) **SMRT/NCoR-binding-deficient** (scaffold-dead) mutant. Which mutant fails to rescue tells you catalytic vs scaffold — and cross-validates Arm B's discriminator by an independent (genetic) route.

---

## 5. Readouts (tiered — cheap gate first, expensive confirmation last)

**Tier 1 — module edge test (the gate).** Targeted RT-qPCR / NanoString / targeted RNA panel of the **UC module-59 risk genes** (IL10, PRDM1, BACH2, CD28, FAS, RASGRP1, IRF8, FOSL2, REL) + HDAC7 itself, at Stim8h and Stim48h. **Decision gate:** HDAC7 KD must move the module coherently vs NT beyond the STAT3/BATF positive-control's effect size floor. If not → stop; the co-cluster does not reflect a functional edge.

**Tier 2 — directionality (therapeutic coherence).**
- Th17 axis: intracellular IL-17A, RORγt; secreted IL-17 (ELISA/Legendplex).
- IL-2 de-repression (the PNAS 2024 HDAC7→IL2 mechanism): IL-2 by flow/ELISA.
- **Treg readout (mandatory, double-edge):** FOXP3⁺ frequency, and suppression assay if the FOXP3 shift is material.
- IFN-γ (Th1) and IL10.

**Tier 3 — mechanism / genome-wide confirmation (only for a Tier-1/2 hit).** Bulk RNA-seq (or CRISPRi Perturb-seq mini-pool) at Stim48h to confirm the module shift is genome-wide-coherent and to compare KD vs TMP195 vs degrader transcriptomes head-to-head. Optional CUT&RUN for HDAC7/SMRT occupancy at module-gene loci to test direct vs indirect regulation.

---

## 6. Design matrix, replication, powering

- **Factors:** perturbation (2 HDAC7 guides + 2 NT + safe-harbor + STAT3 pos-ctrl) × state (Rest/8h/48h) × donor (≥4) for Arm A; compound × dose (≥5) × state × donor (≥4) for Arm B.
- **Replication:** biological = donors (the unit of inference; treat donor as a random effect); ≥2 technical wells per condition per donor.
- **Powering:** power the Tier-1 module readout on the STAT3/BATF positive-control effect size from the screen; a lead worth pursuing should produce ≥ a pre-registered fraction of that effect. Fix the threshold and the analysis model (mixed-effects, donor random intercept; FDR across module genes) **before** unblinding.
- **Blinding:** randomize well/plate layout; analyst blind to guide identity until the mixed model is fit.

---

## 7. Decision gates (go/no-go)

1. **KD QC gate:** ≥70% knockdown, both guides, all donors — else re-guide.
2. **Edge gate (Tier 1):** coherent module shift, concordant across both guides, rescued by sgRNA-resistant cDNA, ≥ positive-control floor → proceed; else **stop the lead**.
3. **Direction gate (Tier 2):** ↓Th17/↑ or preserved Treg (net UC-coherent) → proceed to Tier 3 + UC-donor confirmation; a Treg-collapsing phenotype is a **liability flag**, report it.
4. **Mechanism gate:** scaffold-dead mutant fails to rescue AND TMP195 fails to phenocopy → prioritize **degrader** modality over catalytic inhibitor in any follow-on.

---

## 8. What the data can and cannot support

- **Can support:** whether HDAC7 is a *functional* upstream regulator of the UC risk-gene module in the correct activation state (edge test), the therapeutic direction, and the scaffold-vs-catalytic mechanism — all in the same human primary CD4⁺ system as the screen.
- **Cannot support (by design limits):** (i) HDAC7-*selective* pharmacology — no such tool exists, so Arm B speaks to class IIa, not HDAC7 alone; the genetic arm carries selectivity. (ii) Causal attribution of rs11168249 to HDAC7 regulation — the variant is intronic in gene-dense 12q13.11; this experiment tests HDAC7 function, not the variant's mechanism (that needs allelic/eQTL or base-editing work). (iii) In-vivo colitis efficacy — a cell-intrinsic CD4⁺ result is necessary, not sufficient; a T-cell-transfer or Hdac7-cKO colitis model is the next tier.
