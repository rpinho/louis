# DOT1L RA — minimal experiment for a Treg-SPARING therapeutic window

> *Companion to [DOT1L_rheumatoid_arthritis.md]. Designed by Claude Science (Louis loop), 2026-07-12.
> Turns the parent design's biggest risk — DOT1L inhibition destabilizing Tregs — into a falsifiable
> window hypothesis. Citation anchor: **Cameron et al., "Dot1L licenses DNA demethylation to establish
> regulatory T cell identity," bioRxiv PREPRINT (NOT peer-reviewed), PMID 41427413 / PMC12712901 / DOI
> 10.64898/2025.12.03.692152.** Identifiers connector-returned (PubMed get_article_metadata) and the
> paper was independently PubMed-verified in a prior Louis session; the DOI prefix 10.64898 is this
> environment's normal preprint prefix (used 127× across the KB), not an anomaly. Still a preprint — the
> TET-rescue clause it rests on is itself part of what experiment (a) tests, not an assumption it leans on.*

## Hypothesis
The RA **benefit** of DOT1L inhibition (module-38 / IL21R–PTGER4 effector program down in FOXP3⁻ Tconv)
and its **cost** (FOXP3 identity + suppressive function lost in Treg) are **separable** — either
pharmacologically (TET-enhancement rescues the Treg cost but not the effector benefit) or by dose/timing
(the Tconv effector program is more DOT1L-sensitive than established-Treg maintenance). If separable, a
therapeutic window exists; if benefit and cost are the *same* H3K79me2-dependent event at the same dose,
there is **no window** and DOT1L is not worth pursuing in RA.

## System (minimal, paired)
- Paired subsets from the **same ≥3–4 donors**: FACS-sorted **Tconv** (CD4⁺CD25⁻CD127⁺, FOXP3⁻) and
  **Treg** (CD4⁺CD25ʰⁱCD127ˡᵒ). Run both an **established-Treg maintenance** arm (sorted nTreg, already
  TSDR-demethylated) and an **iTreg induction** arm (TGF-β/IL-2 ± ATRA from naïve) — the maintenance-vs-
  induction split is where the timing window lives.
- **Perturbation:** pinometostat/EPZ-5676 (selective, on-target catalytic) — a *catalytic-window* test,
  the modality a real drug would use, so a catalytic result is the decision-relevant one here (unlike the
  parent design's go/no-go, which must not rest on the catalytic arm).
- Every readout **gated on confirmed global H3K79me2 loss** so a null is biology, not the slow-mark clock.

## (a) Does a window EXIST — the divergence plot
At a fixed pinometostat dose that suppresses the Tconv effector program, add the **TET enhancer**
(ascorbate; orthogonal α-KG / TET-overexpression check on the winner only) and measure in parallel:
- **Treg cost recovered** = fraction of the DOT1Li-induced deficit in suppressive function (Treg:Tresp
  suppression assay) + FOXP3 / TSDR-demethylation restored by +TET.
- **Tconv benefit retained** = fraction of module-38 / IL-21 suppression that persists under +TET.

Plot on a **benefit-vs-cost plane**: DMSO = (high Treg, no benefit); DOT1Li alone = (low Treg, high
benefit); the **window corner** = DOT1Li+TET at (high Treg, high benefit). Reaching that corner turns
Cameron's "TET rescues Treg genes even under DOT1L inhibition" into a selectivity assay. **Built-in
control:** +TET must NOT also lift the Tconv effector program — if it rescues both, it's non-selective.

## (b) Dose / timing window — the separation index
Two dose–response curves on the same donors: **separation index = EC50(Treg cost) / EC50(Tconv benefit).**
Index **>1 (target ≥3–5×)** = a dose band that suppresses effectors before touching Tregs → a dose window
even without TET. Then **iTreg induction vs established-Treg maintenance**: Cameron's mechanism is about
*establishing* identity, so induction ≫ maintenance in DOT1L sensitivity is predicted — a window that
holds for committed Tregs supports dosing after Treg establishment.

## (c) The single result that KILLS DOT1L for RA
The two dose–response curves are **superimposable (separation index ≈ 1)** AND the TET enhancer shifts
**both** curves together instead of selectively rescuing Treg. That means benefit and cost are the same
H3K79me2-dependent demethylation event in two lineages — no dose, no timing, no rescue decouples them →
**no window, drop DOT1L for RA.** A clean, publishable negative that retires the lead cheaply.

## Order (cheapest kill first)
Separation-index dose–response **(b)** → if index ≈ 1 you're most of the way to the **(c)** kill, just add
the TET arm → suppression assay + TSDR **(a)** only if some separation appears → orthogonal TET check +
timing only to characterize a confirmed window.
