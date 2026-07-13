# DOT1L — cleanest knockdown + selective-inhibitor experiment for the RA lead

> *Provenance: designed by Claude Science (Louis recursion loop), 2026-07-12; reconstructed here
> from that session's connector-verified summary. Screen numbers independently re-verified against
> the engine 2026-07-12 — DOT1L footprint Rest 122 / Stim8hr 175 / Stim48hr 435 (KD-verified 3/3,
> clean guide, activation-induced, 93.6th pct); RA module 38 fires at Rest, OR 2.9, fdr 4.5e-3,
> DOT1L a candidate handle alongside MEN1 + ARRDC4, risk genes incl. IL21R/PTGER4. Drug/novelty
> facts verified vs ChEMBL / ClinicalTrials.gov / PubMed on 2026-07-12 (see §7).*

**Target:** DOT1L (DOT1-like — the sole writer of H3K79me1/2/3)
**Disease context:** rheumatoid arthritis, CD4⁺ T-cell-intrinsic
**Screen provenance:** Marson/Pritchard genome-scale CRISPRi Perturb-seq — DOT1L is a **module-level
co-cluster handle** for RA risk-gene **module 38**, enriched at **Rest** (OR 2.9, fdr 4.5e-3; risk
genes IL21R, PTGER4, SELL, LEF1, CD6, CD28, ETS1, SATB1…). DOT1L's own footprint is **activation-
induced and peaks later** — Rest 122 → Stim8hr 175 → **Stim48hr 435** downstream genes (KD verified
3/3). This state asymmetry drives the design: **edge test at Rest, genome-wide confirmation at Stim48h.**
**Orthogonal anchor — absent, stated as such.** Unlike the HDAC7/UC lead (clean credible-set variant
rs11168249), DOT1L has **no human genetic RA anchor**: GWAS maps to osteoarthritis / WBC traits, and
its Open Targets RA score is an ontology-propagation artifact (0 direct RA evidence rows). This lead
rests on **novelty + fresh mechanism, not genetics** — a real difference from HDAC7 the design can't paper over.

## 0. What this experiment must prove (and cannot)

The screen gives a **co-cluster association, not a proven edge**. Four bars, in order — bar 3 is
elevated to a hard gate here for a target-specific reason (the Treg double-edge):

1. **Edge test (gate, at Rest)** — does DOT1L knockdown move module 38 (IL21R/PTGER4-led) coherently
   vs non-targeting, beyond the STAT3/BATF positive-control floor? Cheap — kills a wrong lead before any inhibitor spend.
2. **Mechanism** — catalytic (pinometostat-addressable) vs scaffold, resolved by catalytic-dead-rescue ↔ pinometostat-phenocopy agreement.
3. **Direction-of-effect (MANDATORY)** — DOT1L *supports Treg identity*, so inhibition could **worsen**
   RA. Must show the effector program down **without collapsing FOXP3 / suppression**.
4. **Target engagement** — H3K79me2 CUT&RUN strips at IL21R/PTGER4 specifically.

## 1. System

- **Cells:** human primary CD4⁺ T cells, ≥4 healthy donors (unit of inference); confirm top readouts in 2–3 RA-patient donors.
- **Modality matches the screen:** lentiviral **CRISPRi (dCas9-KRAB)** — same perturbation class as the Perturb-seq.
- **States (the screen's axis):** **Rest** (module-38 edge test) and **Stim 48h** (DOT1L footprint peak → genome-wide confirmation); Stim8h optional. Stimulate anti-CD3/CD28.

## 2. Arm A — CRISPRi knockdown (PRIMARY)

Load-bearing arm: removes the whole protein (scaffold + catalytic), matches the screen, isolates DOT1L.

| Element | Spec |
|---|---|
| Guides | **≥2 independent DOT1L sgRNAs** at the TSS; one = the screen's validated guide |
| KD QC | RT-qPCR + protein per donor/guide; **≥70% mRNA KD**; plus **global H3K79me2-loss** QC (DOT1L is the sole H3K79 writer — a clean on-target readout) |
| Controls | **NT×2 + AAVS1 safe-harbor + STAT3/BATF positive-control guide** (proves the assay detects a real module shift); untransduced + dCas9-only |
| Rescue | **sgRNA-resistant DOT1L cDNA — WT vs catalytic-dead** (WT rescues / catalytic-dead fails ⇒ catalytic mechanism, and must agree with Arm B) |
| Concordance | two-guide agreement is itself a control (guide-specific effect = off-target, discard) |

## 3. Arm B — pinometostat (COMPLEMENT, genuinely selective)

Unlike the HDAC7 lead (no selective compound), DOT1L **has a selective clinical-stage probe**.

| Compound | Selectivity | Role |
|---|---|---|
| **pinometostat / EPZ-5676** (CHEMBL3414626) | selective DOT1L inhibitor; biochem IC50 **0.1–52 nM** (mostly low-single-digit nM) | dose–response ~1 nM → low µM, DMSO-matched, per-dose viability co-stain, H3K79me2 PD anchor |
| (optional) DOT1L degrader | protein-removing | mimics the KD's protein loss if a qualified one exists |

## 4. Target engagement
**H3K79me2 CUT&RUN at IL21R / PTGER4** in both KD and inhibitor arms — the direct molecular proof the handle acts on the module loci.

## 5. Treg direction-of-effect readout (MANDATORY — the elevated gate)
**FOXP3 stability + suppression assay**, in bulk-CD4 and Treg/iTreg arms. Rationale (Cameron et al.
preprint): Treg-restricted *Dot1L* deletion → fatal autoimmunity, and TET-enhancement rescues Treg
genes even under DOT1L inhibition. So a monotherapy that collapses Tregs is a **liability**; the readout
also points at a **Treg-sparing combination reframe** if that happens.

## 6. Tiered go/no-go (cheap gate first)
KD-QC (≥70% + H3K79me2 loss) → **module-38 edge at Rest** (flat vs positive-control floor ⇒ **stop the
lead**) → **Treg direction** (FOXP3/suppression collapse ⇒ stop / reframe to Treg-sparing) → mechanism
(catalytic-dead-rescue ↔ pinometostat agreement) → CUT&RUN engagement → Stim48h RNA-seq genome-wide confirmation.

## 7. Connector-verified facts (2026-07-12)
- **Pinometostat:** ChEMBL CHEMBL3414626, **max phase 2**, IV, **oncology-only**. 4 trials, all
  MLL-leukemia, **zero autoimmune** (NCT01684150 / NCT02141828 / NCT03701295 completed; NCT03724084 terminated, n=6 — program effectively halted).
- **RA whitespace:** DOT1L + RA + T-cell/CD4 = **0 PubMed papers**; the 3 DOT1L+RA hits are synovial/incidental, none a CD4 mechanism.
- **Mechanism paper (confidence-labeled):** Cameron et al., *"Dot1L licenses DNA demethylation to
  establish regulatory T cell identity"* — **bioRxiv PREPRINT** (PMID 41427413, DOI 10.64898/2025.12.03.692152), NOT peer-reviewed.

## 8. Biggest risk
**Direction-of-effect.** The same biology that makes DOT1L interesting (it runs the Treg epigenetic
program) means inhibition could destabilize Tregs and *worsen* RA — which is why the design forces that
question (bar 3) before any in-vivo bet.

## 9. What the data can / cannot support
- **Can:** whether DOT1L is a *functional* upstream regulator of the RA risk-gene module in the right
  state (edge test), the therapeutic direction (Treg-safe or not), the scaffold-vs-catalytic mechanism.
- **Cannot:** (i) causal attribution of any RA variant to DOT1L (there is no RA genetic anchor — the
  lead is novelty+mechanism); (ii) in-vivo RA efficacy (a cell-intrinsic CD4 result is necessary, not
  sufficient — a transfer / cKO arthritis model is the next tier); (iii) selectivity beyond pinometostat's known profile (the genetic arm carries selectivity).

## 10. Stress-test — failure modes & the first gate (Claude Science, 2026-07-12)

Three ways this design misleads, each with the cheapest fix:

**False positive #1 — global H3K79me2 collapse mistaken for module-38 specificity (the signature DOT1L
artifact).** DOT1L is the sole H3K79 writer and H3K79me2 marks the gene bodies of ~all actively
transcribed genes, so knockdown produces a genome-wide sag of highly-transcribed genes — IL21R / PTGER4
/ CD28 / SELL slide down *with everything else*. A module-only panel (normalized to housekeepers) then
shows a coherent "on-hypothesis" drop that is really loss of a housekeeping elongation mark. **Fix
(cheap):** add an **expression- and H3K79me2-occupancy-matched non-module control gene set** to the
Tier-1 panel; specificity = module 38 moves *beyond the genome-wide slump*, not merely ≠ 0.

**False positive #2 — composition / wrong-state shift, not a cell-intrinsic edge.** (a) *Treg-fraction
composition:* DOT1L supports Treg identity, so KD can shrink the FOXP3⁺ fraction; several module-38
genes (IL21R, CD28, SELL, LEF1) are DE Treg-vs-Tconv, so losing Tregs alone moves the bulk average — a
composition artifact, not cis-regulation. (b) *Wrong state:* the module fires at **Rest**, but DOT1L's
footprint peaks at **Stim48h**; reading at Stim48h sweeps IL21R/PTGER4 in as generic activation targets.
**Fix (cheap):** require the shift **inside the FOXP3⁻ Tconv gate** and **at Rest** (treat a Stim48h-only
shift as the activation footprint, not the module).

**False negative — a pinometostat (catalytic-only) null wrongly kills a real lead.** Pinometostat blocks
only methyltransferase activity; it cannot report DOT1L's **scaffold** role (DotCom / AF9–ENL–AF10). And
H3K79me2 is a stable, slow-turnover, replication-coupled mark — in barely-dividing resting cells a
standard 48–72 h window can give a *clock-artifact* null. **Fix:** make **CRISPRi KD the sole
load-bearing go/no-go arm**; demote pinometostat to a **mechanism classifier that can never trigger a
kill** (catalytic-null + positive KD ⇒ reclassify as scaffold → degrader follow-on); gate readouts on
**actual global H3K79me2 loss** (a clock, not a calendar day).

**→ Highest-value first gate:** the **Tier-1 module-38 edge test at Rest**, upgraded with the
matched-background panel (kills FP1) and run inside the FOXP3⁻ Tconv gate (kills FP2), entered only after
the H3K79me2-loss KD-QC (protects against the FN kinetics artifact). Cheapest readout, decisive kill, and
it neutralizes both false positives on the same plate. Honest caveat: it tests specificity *vs
background*, not *direct* regulation — that's what the Tier-3 CUT&RUN is for; it just shouldn't be the first spend.
