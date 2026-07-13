# Verbatim Louis outputs — current build (stress-test / provenance-tier / self-reviewer)

> Reproduced through the **exact Slack brain** (`louis.assistant.answer`), the same code the
> `@louis` bot runs, on **2026-07-13**. Every capture ran against a **throwaway copy of `kb/`**
> (real KB untouched). Tool traces shown so you can see what Louis actually called.


---

## Science Beat 1 / Slack live-prompt #1 — DOT1L stress-test recall

**Prompt:** `is DOT1L a good novel target for rheumatoid arthritis? recall first, be honest about trust.`  
**Tools Louis called:** `kb_recall`

TL;DR — **DOT1L for RA is a C, not a novel top lead** — the RA "wiring" is a cross-disease-union artifact (DOT1L isn't in RA's own significant regulator set, enrichment FDR 0.68), so the headline doesn't survive its own stress-test.

**Current call: `C`** (stress-test downgrade **A→C**, 2026-07-12) — supersedes the original A-grade.

| Pillar | Read |
|---|---|
| **Link** | 🔴 union artifact |
| **Direction** | 🟡 open, Treg risk |
| **Novelty** | 🟡 RA-only whitespace |
| **Druggability** | 🟡 pinometostat, onc-only |

**Why it fell (load-bearing):**
- DOT1L is **not** in RA's own module-38 regulator set — that set is MEN1/ARRDC4, regulator enrichment **FDR 0.68** (non-sig). It enters the pool only because the engine unions regulators across all diseases.
- Systemically only **1 of 77** regulator clusters ever clears significance (the STAT3/Crohn's triad, q=0.025). The novel handles are co-cluster *hypotheses*, not enriched edges. The DOT1L→IL21R edge is untested by construction (engine stores counts, not identities).

**Trust / QC:** knockdown **verified, clean guide**, module 38 fires at **Rest** — that part is solid. The problem is the *link*, not the CRISPRi QC.

**Direction:** genuinely open, not "backwards." Cameron (bioRxiv, unreviewed) says Treg-DOT1L loss → autoimmunity (inhibition could *worsen* RA); Scheer 2020 (peer-reviewed) shows DOT1L also sustains Th1 effectors → loss could be protective. Net effect is a to-test question.

**Field activity:** RA+DOT1L+T-cell = **0 published papers** (real whitespace), but DOT1L is a well-known CD4 regulator (Scheer 2020). Adjacent Treg work is preprint-stage (Cameron). No autoimmune trials — pinometostat is oncology-only, IV, Ph2.

⚠ **Reviewer:** the direction-of-effect risk rests on a **bioRxiv preprint** (PMID 41427413, not peer-reviewed) — hypothesis-strength. The *kill*, though, rests on the engine-verified enrichment FDR, which is load-bearing and direction-independent.

**Verdict:** Keep as a resting-state mechanistic-probe hypothesis, not a top lead. **Next step:** FOXP3/Treg direction-of-effect gate is go/no-go #1; the Tier-1 test is the module-38 edge at Rest with an expression-matched background panel (DOT1L is the sole H3K79 writer — global collapse mimics specificity).

_Say expand for the full dossier._

---

## Slack live-prompt reply — skeptic: “why not just run pinometostat?”

**Prompt:** `but pinometostat's already in the clinic — why not just run it in RA?`  
**Tools Louis called:** `(none — answered from context)`

TL;DR — **A clinical-stage molecule is a convenience, not a reason to target the gene** — and here it's exactly the trap the stress-test flagged: druggability was over-weighted over a non-significant, direction-inverted RA hypothesis.

**Three reasons "it's in the clinic" doesn't rescue it:**

- **The RA link still isn't real.** Having a drug doesn't fix that DOT1L isn't in RA's own significant regulator set (enrichment **FDR 0.68**). You'd be running a good tool compound against a **union artifact**. Clinic-readiness ≠ RA relevance.

- **You might dose it the wrong way.** DOT1L supports Treg identity (Cameron, bioRxiv — *unreviewed*). If inhibition collapses Tregs, pinometostat could **worsen** RA. Net direction is unresolved (Scheer 2020 cuts the other way for Th1). Running a phase-2 onc drug in an autoimmune indication before settling that is how you get an avoidable safety signal.

- **Pinometostat can't even test the hypothesis cleanly.** It's a **catalytic** inhibitor — blind to DOT1L's DotCom **scaffold** role, and H3K79me2 is slow-turnover. A catalytic-only null could falsely kill a real scaffold-mediated lead. That's why in the filed design **CRISPRi KD is the sole go/no-go arm**; pinometostat only classifies mechanism.

Also practically: pinometostat is **IV, continuous-infusion, oncology-only, 0 autoimmune trials**, program largely halted — not a plug-and-play RA asset.

⚠ **Reviewer:** the "worsens RA" direction rests on a **preprint** — hypothesis-strength. The reason not to jump to clinic rests on the **engine-verified FDR 0.68** (load-bearing) plus the catalytic-vs-scaffold pharmacology (established biology).

**Verdict:** Don't run pinometostat in RA yet. **Do first:** CRISPRi KD in resting primary CD4, gated on real H3K79me2 loss, read the module-38 edge against a matched background **and** a FOXP3/Treg direction-of-effect gate. If those clear, *then* pinometostat earns a dose-response — as a mechanism probe, not the go/no-go.

---

## Slack Beat 3 — HDAC7 discovery (honest, direction-led)

**Prompt:** `for IBD / Th17-colitis, a novel CD4 handle I can trust — be honest about the weak legs`  
**Tools Louis called:** `disease_mechanisms, disease_targets, kb_recall, target_evidence, target_evidence, state_profile`

The KB has this one worked hard already — and it's been stress-tested. Here's the honest read.

**TL;DR —** For Th17-colitis, **HDAC7** is your novel CD4 handle worth trusting on *direction* — an inhibitor is predicted to help (HDAC4/7 drive Th17; blocking them mitigates colitis, PNAS 2024) — but its "wired to IBD risk genes" story is a co-cluster hypothesis (FDR=1.00), not a proven edge, so lead on mechanism, not genetics.

**Lead — HDAC7** · module 59 tolerance node, Stim8hr · **current grade B** (Crohn's/UC, stress-tested from B+)

| Leg | Read |
|---|---|
| Direction | 👍 **holds** — inhibitor helps Th17-colitis |
| Wiring | 🤔 co-cluster, **FDR=1.00** |
| Genetics | 🤔 own-gene but allergy/platelet-led |

**Evidence (screen, verified):**
- Module 59 downstream: **OR 3.3, FDR 6.1e-3** — real, but a *pan-inflammatory* tolerance module (IL10/BACH2/PRDM1/CD28), not IBD-specific.
- GRN out-degree **134**, ~87th pct; **activation-modulated**, peaks **Stim48hr** (84→56→134).
- **KD verified clean in all 3 states.**

**The weak legs — honestly:**
- ⚠ **Wiring is not an edge.** Module-59 *regulator* enrichment is **FDR=1.00** across all diseases — HDAC7 sits *near* a real module, not proven to control it.
- ⚠ **Genetics is locus-ambiguous.** rs11168249 is own-gene but led by platelet count + asthma; **not a CD4 eQTL** for HDAC7. Causal gene *and* cell ambiguous.
- ⚠ **No HDAC7-selective compound** — pan-HDACi only (vorinostat POC, NCT03167437). Translational whitespace, not a validity problem for a CRISPRi test.

**Field activity:** Active but *not* crowded on the CD4/IBD angle — PNAS 2024 (PMID 38657041) defined the HDAC4/7→Th17 mechanism; Hafler/Verdin own the *MS/Treg* angle (opposite direction). The selective-HDAC7 Th17-colitis handle is genuinely open.

**Verdict — B, worth pursuing, lead on direction not genetics.** Next bench step: CRISPRi KD of HDAC7 (≥2 guides + rescue) on the Rest/Stim8hr/Stim48hr axis, test the module-59 edge vs a STAT3/BATF positive-control floor — with a **mandatory FOXP3/Treg readout** to catch the self-tolerance double-edge.

⚠ Reviewer: the favorable *direction* rests on one peer-reviewed paper (PNAS 2024) — load-bearing but single-source; the wiring FDR=1.00 is engine-verified. Grade is capped at B for exactly these reasons.

_Say **expand** for the full dossier, or I can pull the alternative handles (MBD2, KAT7, MED15) if you want to compare._

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
