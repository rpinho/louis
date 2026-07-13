# Verbatim Louis outputs — current build (learn · trust · bleeding-edge signal)

> Reproduced through the **exact Slack brain** (`louis.assistant.answer`) on **2026-07-13**, against
> a **throwaway copy of `kb/`** (real KB untouched). Tool traces shown.


---

## Science Beat 1 / Slack live-prompt #1 — DOT1L stress-test recall

**Prompt:** `is DOT1L a good novel target for rheumatoid arthritis? recall first, be honest about trust.`  
**Tools Louis called:** `kb_recall`

TL;DR — **No.** DOT1L looks like a dream novel RA lead on paper, but it was stress-tested and **downgraded A → C** — the RA "wiring" is a cross-disease artifact, not an RA-specific edge. A hit is a clue, not a conviction.

| Field | Read |
|---|---|
| **Current grade** | **C** (was A 2026-07-10 → **C** 2026-07-12) |
| **Lead** | H3K79 methyltransferase, drugged (pinometostat Ph2) |
| **Trust** | KD **verified**, clean guide ✓ — QC is *not* the problem |

**Why it fell (the load-bearing crack):**
- **Link is an artifact** — DOT1L is *not* in RA's own module-38 regulator set (enrichment **fdr = 0.68**, non-sig). It enters the pool only because regulators are unioned across all diseases (contributed by SLE/CAD rows).
- Systemically **only 1 of 77 regulator clusters** ever clears significance — the STAT3/Crohn's triad. The novel handles are co-cluster *hypotheses*, not proven edges. The DOT1L→IL21R edge is **untested by construction** (engine stores counts, not identities).

**The other holes:**
- **Direction bidirectional / open** — Cameron (bioRxiv preprint, PMID 41427413) says Treg-Dot1L loss → fatal autoimmunity (inhibition could *worsen* RA); Scheer 2020 (peer-reviewed) says loss impairs effectors (could *help*). Genuine to-test question, not load-bearing for the kill.
- **Not truly novel** — well-characterized CD4 epigenetic regulator (Scheer 2020); understudied *only in RA*.
- **No genetic anchor** — top own-gene GWAS hit is knee osteoarthritis; OT RA = 0.0095, literature co-mention.
- **Druggability stretch** — pinometostat is an IV oncology probe, 0 autoimmune trials.

**Who else:** 0 published DOT1L+RA+CD4 papers. Pre-paper floor: Cameron bioRxiv preprint (Treg identity) + ACR 2023 abstract #1589 (DNMT3A+DOT1L via AMPK) — adjacent, not RA-specific. Bluesky chatter is fibrosis/DC/leukemia, not RA. So: whitespace, but a *thin* one.

⚠ **Reviewer:** the direction-of-effect risk rests on an unreviewed bioRxiv preprint — hypothesis-strength only. The kill rests on the engine-verified link artifact (fdr 0.68), which is solid.

**Verdict — C: a resting-state mechanistic-probe hypothesis, not a top RA lead.** If you still want to touch it, **go/no-go #1 is a FOXP3/Treg direction-of-effect gate** — CRISPRi in the FOXP3⁻ Tconv gate at Rest with an expression-matched background panel, before anything else.

_Say **expand** for the full dossier + the filed experiment design._

---

## Slack live-prompt reply — skeptic: “why not just run pinometostat?”

**Prompt:** `but pinometostat's already in the clinic — why not just run it in RA?`  
**Tools Louis called:** `(none — answered from context)`

TL;DR — Because pinometostat being in the clinic tells you it's *druggable*, not that *DOT1L is the right RA target* — and here the target link is the part that failed, not the chemistry.

**The clinic status doesn't touch the load-bearing crack:**
- The RA "wiring" is a **cross-disease-union artifact** — DOT1L isn't in RA's own module-38 regulator set (enrichment **fdr 0.68**, non-sig). A clinical molecule pointed at a link that doesn't hold is still pointed at nothing.
- **No RA genetic anchor** (OT RA 0.0095, top own-gene GWAS is knee osteoarthritis). Nothing says DOT1L drives RA.

**And the molecule itself isn't RA-ready:**
- Pinometostat is **oncology-only** — MLL-leukemia, **max phase 2**, **continuous IV** infusion, **0 autoimmune trials**. That's a hospital leukemia regimen, not a chronic autoimmune drug.
- **Direction is open/adverse-risk** — Cameron (bioRxiv preprint) says Treg-DOT1L loss → *fatal autoimmunity*, i.e. an inhibitor could **worsen** RA. You don't want to find that out in an RA patient.
- Mechanistic catch: pinometostat is **catalytic-only** — it can't see DOT1L's DotCom scaffold role, and H3K79me2 is slow-turnover. A clean pinometostat null could *falsely kill* a real lead. That's why the filed design makes **CRISPRi KD the sole go/no-go arm** and uses pinometostat only to classify mechanism.

⚠ **Reviewer:** the "worsens RA" direction rests on an unreviewed preprint — hypothesis-strength. The reasons *not* to jump to a clinical trial (no link, no anchor, IV oncology drug) are the load-bearing ones.

**Verdict — a clinical-stage molecule shortens the *chemistry* path, not the *biology* path.** Next step isn't an RA trial; it's the **bench go/no-go**: CRISPRi in FOXP3⁻ Tconv at Rest with a matched background panel + a FOXP3/Treg direction-of-effect gate. Earn the target before you spend the drug.

---

## Slack Beat 3 — HDAC7, the survivor lead (named recall, honest legs)

**Prompt:** `is HDAC7 a CD4 handle I can trust for IBD / Th17-colitis? be honest about the weak legs`  
**Tools Louis called:** `kb_recall, target_evidence, state_profile, regulator_detail`

TL;DR — **HDAC7 is a real IBD/Th17-colitis handle at grade B** — worth pursuing because the *direction* is favorable (inhibition mitigates Th17 colitis, peer-reviewed), but the "wires-to-risk-genes" story is a co-cluster hypothesis, not a proven edge.

| Leg | Status |
|---|---|
| **Direction** | ✅ holds — carries the grade |
| **Genetics** | 🤔 own-gene but ambiguous |
| **Wiring** | ❌ cracked (FDR=1.00) |

**Lead** — class IIa HDAC; an inhibitor is predicted to *help* UC/Th17-colitis.

**Evidence (screen, verified)**
- Module 59 (Stim8hr): **OR 3.3, FDR 6.1e-3** — but this is the *downstream* module (real, yet pan-inflammatory, sig in ~9 diseases), not UC-specific.
- GRN out-degree **134** (86th pct), activation-modulated, peaks **Stim48hr** (84→56→134 across Rest/Stim8/Stim48).
- KD **verified on-target, clean guide in all 3 states** ✅.

**Where the legs are weak (your ask):**
1. **Wiring** — module-59 *regulator* enrichment is **FDR=1.00** across all 8 diseases (intersection = HDAC7 itself). It sits *near* the module, not a demonstrated controller. Statistically identical to DOT1L's failed leg.
2. **Genetics** — rs11168249 maps to HDAC7 at gene level, but 38 associations are **platelet/asthma-led**; UC real but minor (~6e-9), partly Ellinghaus 5-disease pleiotropy. **Not a detectable HDAC7 eQTL in CD4 T cells** → causal gene *and* cell ambiguous.
3. **Compound** — **zero HDAC7-selective molecules**; only pan-HDACi (vorinostat POC NCT03167437) + class-IIa tools TMP195/TMP269. Whitespace, not a validity threat since CRISPRi is the primary experiment.

**What actually carries the B** — DIRECTION: HDAC4/7 + Aiolos + SMRT/NCoR repress Th17 negative regulators; inhibiting HDAC4/7 mitigates Th17 colitis (**PNAS 2024, PMID 38657041, peer-reviewed**). This is why it beats DOT1L, which had a Treg trap. Treg double-edge here is MS/thymic, *not* UC.

**Field activity** — active class, thin gene: PNAS 2024 (Th17-colitis mechanism), pan-HDACi vorinostat Crohn's POC recruiting. No HDAC7-selective IBD trial. On Bluesky/pre-paper: quiet on HDAC7-specific colitis — the *mechanism* is already peer-reviewed (not bleeding-edge), the *selective handle* is open.

**⚠ Reviewer** — the favorable-direction claim rests on a single peer-reviewed paper (PMID 38657041) that's load-bearing; the wiring and genetics legs are hypothesis-strength at best. Verify the direction at *your* bench before an irreversible call.

**Verdict — B, trustworthy IF you lead on direction, not on "it controls the risk module."** Current UC grade is **B** (was B+ → B on 2026-07-12 stress-test). Next step: CRISPRi KD (≥2 guides + rescue) on Rest/Stim8/Stim48, readouts gated vs a STAT3/BATF positive-control floor, with a **mandatory FOXP3/Treg direction gate** — that's the one experiment that decides whether inhibition helps or backfires.

_Say expand for the full dossier (module spine, experiment protocol, cross-disease read)._

---

## Slack — experiment design (returns the schematic figure card)

**Prompt:** `design the HDAC7 knockdown experiment for ulcerative colitis`  
**Tools Louis called:** `kb_recall, target_evidence, state_profile, regulator_detail`

Good — there's already a filed experiment design and a stress-test verdict I can build the protocol from, not re-derive.

**TL;DR —** Knock HDAC7 down with **CRISPRi in stimulated CD4+ T cells** (footprint peaks Stim48hr, KD clean & on-target in all 3 states) to test whether it controls UC risk-module 59 — but the load-bearing rationale is the **favorable Th17-colitis DIRECTION** (PNAS 2024), *not* clean genetics, and you **must gate on a Treg/FOXP3 readout**.

**The screen facts (engine-verified)**

| Metric | Value |
|---|---|
| GRN out-degree | **134** (86.9th pct) |
| State pattern | **activation-modulated**, peak **Stim48hr** |
| Per-state footprint | **84 / 56 / 134** (Rest/Stim8/Stim48) |
| KD verified | **✅ all 3 states, guide clean** |
| UC module | **59** (Stim8hr), OR **3.1**, FDR **6.1e-3** |
| Current UC grade | **B** (B+→B stress-test) |

**Design — two arms**

- **Arm A (PRIMARY): CRISPRi** dCas9-KRAB, matches screen modality. **≥2 guides** + **sgRNA-resistant cDNA rescue**, including **catalytic-dead** and **scaffold-dead** mutants — this decides degrader-vs-inhibitor downstream.
- **Arm B (pharmacology, caveated):** class-IIa tool compounds **TMP195 / TMP269** + pan-HDACi **vorinostat** (UC POC NCT03167437). ⚠ **No HDAC7-selective compound exists** — Arm B is orthogonal support, not the test.

**States & readouts**
- Run the **Rest / Stim8hr / Stim48hr** axis — footprint is biggest at Stim48hr, so that's your main window; Stim8hr is where module 59 fires.
- Readout tiers **gated against a STAT3/BATF positive-control floor** (validates method, not the pick).
- **Mandatory FOXP3/Treg readout** — HDAC7 has a real self-tolerance double-edge (MS/thymic, PMID 36516268/23103766). Favorable direction is UC-specific; don't assume it.
- Primary edge test: does KD move **module-59 risk genes** (IL10, BACH2, PRDM1, CD28, IRF8, FAS…)?

**What this experiment can and can't settle**
- ✅ Tests the **co-cluster hypothesis** — module 59 is a *candidate* controller relationship, **not a proven edge** (regulator-level enrichment FDR=1.00; the real signal is the downstream module, which is pan-inflammatory, not UC-specific).
- The genetics anchor (rs11168249) is **own-gene but allergy/platelet-led and NOT a CD4 eQTL** — so causal gene + cell are ambiguous. Direction + mechanism carry this, not the locus.

**⚠ Reviewer pass:** the decisive DIRECTION-of-effect ("inhibiting HDAC4/7 helps Th17 colitis") rests on **PNAS 2024 PMID 38657041** — peer-reviewed (load-bearing), good. But its *application to UC specifically* is inference; the FOXP3 gate is what verifies you're not tripping the Treg double-edge. Don't skip it.

Full protocol is already filed at `kb/experiments/HDAC7_ulcerative_colitis.md`. _Say **expand** for the tiered readout list and rescue-mutant logic._

---

## Slack Beat 4 — ELI5

**Prompt:** `eli5 — my PI corners me in 10 seconds`  
**Tools Louis called:** `(none — answered from context)`

**HDAC7.** It's a switch on the inflammation-driving T-cells in gut disease — turn it down and the disease should ease, and nobody's chasing it from this angle yet. Catch: we've got a good reason to think it *sits* in the right circuit, but we haven't proven it *runs* that circuit — that's the experiment.

---

## Slack Beat 5 WRITE — a labmate teaches Louis (bench result flows into memory, attributed)

**Prompt:** `we ran HDAC7 KD in primary CD4 — the module-59 genes barely moved, the co-cluster edge doesn't hold.`  
**Tools Louis called:** `kb_recall`

Perfect — the KB already anticipated exactly this. Your result confirms a leg everyone knew was cracked, and — importantly — it does **not** move the UC grade.

**TL;DR —** Your HDAC7 KD result *confirms* the module-59 co-cluster was only a hypothesis (it was already at **fdr=1.00**) — so it retires that already-cracked leg, but it does **not** lower the UC **B**, because that grade never rode on the wiring; it rides on peer-reviewed direction.

**What your result touches**
- **Module-59 wiring** — was always a **co-cluster hypothesis, not a proven edge** (regulator enrichment **fdr=1.00** across all diseases). Your KD leaving mod-59 flat = the honest confirmation it was never a demonstrated controller. ✅ retire the leg.
- **UC grade B** — rests **decisively on DIRECTION** (HDAC4/7 repress Th17 neg-regulators; inhibition mitigates Th17 colitis — PNAS 2024, **PMID 38657041**, peer-reviewed), with own-gene GWAS (rs11168249) as a weak anchor. **Untouched** by a wiring-falsifying KD.

**So — the grade holds.** Per the 2026-07-13 grade-basis note: falsifying a leg that never carried the grade doesn't move the grade. A downgrade would need the *direction* to fall (KD **worsens** colitis / collapses Tregs), not the wiring.

**What I'd file (with your OK):**
- ✍️ a **finding** on HDAC7 / UC: *"Bench: HDAC7 CRISPRi KD in primary CD4 — module-59 genes barely moved; co-cluster edge does not hold. Confirms mod-59 regulator wiring was a co-cluster hypothesis (fdr=1.00), not a demonstrated edge."* — source: Slack · jordan.
- **No verdict change** — UC stays **B** on peer-reviewed direction.

One thing before I write, so the record is precise:
- Was the KD **verified on-target** in this run (guide QC / knockdown confirmed)? And which **state** — Rest / Stim8hr / Stim48hr? Mod-59 fires at **Stim8hr**; a flat readout only cleanly kills the edge if the KD was on-target *in the state the module fires in*.

Want me to file the finding as-is? Say the word and I'll log it.

---

## Slack Beat 5 READ — the grade HOLDS (falsifying a non-load-bearing leg doesn't move it)

**Prompt:** `does Jordan's negative KD change HDAC7's grade for ulcerative colitis, or does the B hold?`  
**Tools Louis called:** `kb_recall`

TL;DR — **The B holds.** Jordan's negative KD falsifies the module-59 *wiring* leg — but the UC grade never rode on that leg; it rides on peer-reviewed **direction**, which is untouched.

**Current call:** HDAC7 / UC = **B** (2026-07-12 stress-test; not superseded)

**Which leg does the B rest on?**
| Leg | Status | Carries grade? |
|---|---|---|
| **Direction** | Holds (PNAS 2024, peer-reviewed) | **YES — decisive** |
| **Own-gene GWAS** | Weak/ambiguous | Minor support |
| **Module-59 wiring** | Already cracked (fdr=1.00) | **NO** |

**Why Jordan doesn't move it**
- The module-59 "HDAC7 *controls* the risk module" claim was **already a co-cluster hypothesis at fdr=1.00** — HDAC7 "sits *near* a real module, not a demonstrated controller." It was never part of the B's basis.
- A KD leaving module-59 flat **confirms the co-cluster was only a hypothesis** and retires an already-cracked leg. Falsifying a leg that never carried the grade doesn't move the grade. (Same provenance logic that let DOT1L's kill rest on the engine artifact, not the preprint.)
- **What WOULD downgrade it:** a result falsifying **DIRECTION** — a KD that *worsens* colitis or collapses Tregs. Jordan's result isn't that.

⚠ **Reviewer:** the surviving load-bearing leg (direction) rests on a peer-reviewed paper (PMID 38657041) — that's tier-1, so the B stands on solid footing. But confirm Jordan's readout was specifically the **module-59 downstream program going flat** (wiring), *not* a colitis/Treg phenotype (direction) — those land on different legs.

**Verdict:** **B holds.** Next step tightens to the leg that IS decisive — a **FOXP3/Treg direction-of-effect gate**, not another wiring test.

Want me to **file Jordan's negative KD** to the HDAC7 profile as a finding (retiring the module-59 leg, grade unchanged)? I won't write it without your go — say the word and give me Jordan's exact readout.

---

## Slack — the BLEEDING EDGE (3rd pillar): reads the harvested off-allowlist X/Bluesky/conference signal, tiers it

**Prompt:** `what's the community saying about DOCK2 — any off-allowlist signal (X, Bluesky, conference abstracts) the papers haven't caught?`  
**Tools Louis called:** `community_signal, kb_recall`

**TL;DR —** The off-allowlist floor on DOCK2 is *ahead* of the papers: a Dec-2025 Immunity paper says the **TCR-SUB1-DOCK2 axis drives pathogenic CD4+ T-cell tissue infiltration**, and it's converging with a fresh **CCR7→DOCK2 relocalization** mechanism (Science, May-2026) — both point the same way: **blocking DOCK2 is protective**.

**Harvested signal — Bluesky · conference, freshest first**

| Date | Who | Signal |
|---|---|---|
| 2026-05-01 | Brett Garabedian ⭐ | **CCR7→DOCK2** relocalization; prolonged DC engagement → dysfunctional Teff |
| 2025-12-09 | Waggoner Lab / Immunity ⭐ | **TCR-SUB1-DOCK2 axis** drives pathogenic CD4 tissue infiltration |
| 2024-10-09 | ACR Journals ⭐ | **CPYPP** (DOCK2 inhibitor) ameliorates Sjögren mouse model |

**What the papers haven't caught / the read**
- **New axis wiring** — the SUB1 upstream link and the CCR7-relocalization mechanism are the bleeding edge; direction-of-effect (inhibit = protective) is now supported by **two peer-reviewed lines**, not just chatter.
- **Chemistry is still tool-stage** — CPYPP isn't even in ChEMBL; a real DOCK2 series exists (~7 IC50 <100 nM) but **zero clinical compound, zero trials any indication**.
- **Ceiling, not trap** — DOCK2 *deficiency* is a human combined immunodeficiency (OT 0.85) → full blockade risks broad immunosuppression. That's a selectivity/dosing question.

**Field crowding:** heating up but *not* crowded on the drug side — active mechanism biology (Waggoner, Garabedian), one mouse-inhibitor paper, **no human trials**. Whitespace on the therapeutic entry.

**KB verdicts already on file:** psoriasis **B−** (stress-test recalibrated B→B−), T1D **C**, pan-AI **C** — its own genetics anchor to **IBD/UC**, not psoriasis/T1D.

⚠ **Reviewer:** the axis/direction claims rest on **preprint-adjacent + peer-reviewed papers** (Immunity, Science, ACR) — hypothesis-to-load-bearing on direction, but the *disease wiring in our screen is a union-artifact* (min FDR 1.00). Verify the DOCK2→module-54 edge with a **bench knockdown** before any med-chem bet.

_Say **expand** for the full dossier, or want me to file any of this as fresh field-activity?_

---

## Slack — the --nolab (validated-only) view: HDAC7 B before the lab weighed in

**Prompt:** `best novel CD4 handle for ulcerative colitis?  [--nolab]`  
**Tools Louis called:** `kb_recall, disease_mechanisms, target_evidence, kb_recall, state_profile, kb_recall, kb_query`

Good — this is already well-worked in the KB. Here's the honest read.

**TL;DR —** The best *novel* UC handle is **HDAC7 (grade B)** — the one lead with clean, direct UC genetics — but its module wiring is weak (co-cluster FDR≈1.0), so the genetics carry it, not the network.

### UC handles — current grades

| Gene | Grade | Why |
|---|---|---|
| **HDAC7** | **B** | direct UC GWAS, druggable class |
| **BPTF** | **B** | epigenetic whitespace, direction risk |
| **GLS** | **B** | CB-839 clinical tool, low novelty |
| **CBLB** | **D** | directional mismatch — skip |

### Best novel pick: HDAC7
- **Genetics:** rs11168249 maps to **HDAC7 alone** (not locus-shared) — UC/IBD hits p=6e-8, 3e-7, 7e-7. OT direct UC **0.29**. The *only* non-artifactual direct UC signal of the set.
- **State:** peaks **Stim8hr** (module 59) — an activated-T-cell handle.
- **Trust:** KD verified. But ⚠ the **wiring leg cracks** — module-59 regulator FDR = **1.00** (non-significant co-cluster). The downstream module is real but pan-inflammatory, not UC-specific.
- **Field:** HDAC inhibitors are a crowded class broadly; the *CD4-intrinsic HDAC7-in-UC* angle is the fresher part. Not whitespace, but not scooped either.

**If you want true whitespace over druggability:** **BPTF** — a tool-stage bromodomain in genuine UC whitespace, but carries a real reversed-direction risk (BPTF supports Treg function, so inhibition could *worsen* UC).

**Verdict:** HDAC7 is the strongest *novel* call, but it rests on genetics, not network — B, not higher. **Next step:** CRISPRi HDAC7 in 8h-stim CD4, read out Th17/Treg balance; the module edge is a hypothesis, so confirm the downstream program is UC-relevant and not generic inflammation.

⚠ Reviewer: HDAC7's UC genetics are load-bearing (GWAS Catalog / OT, verified). The "novel handle" framing rests partly on the co-cluster, which is FDR≈1.0 — treat the wiring as hypothesis, not proven edge.

_Say **expand** for the full dossier, or name one gene to go deep._
