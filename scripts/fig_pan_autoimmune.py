#!/usr/bin/env python3
"""Pan-autoimmune synthesis — the recurring handles recur via SHARED MODULES on shared GWAS spines,
NOT one convergent mechanism. All values are the verified columns of cross_disease_synthesis.csv
(#dis A/B graded, and OT genetic-assoc #dis>0.05). Genes are grouped by the module they share, so the
two module-mate pairs (DOT1L↔MEN1 on mod38, AHR↔DOCK2 on mod54) read as "same module, different mechanism".
The old whitespace panel is dropped — the opportunity map now does that job.

    python scripts/fig_pan_autoimmune.py   ->  docs/figures/pan_autoimmune_synthesis.png
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import matplotlib.pyplot as plt
import scripts.figstyle as S  # noqa

S.apply()

# (module label, state, is_pair, [(gene, n_graded_AB, n_genetic, verdict) ...])  — cross_disease_synthesis.csv
GROUPS = [
    ("mod 59", "activated", False, [("HDAC7", 4, 3, "pan-AI, IBD-skewed")]),
    ("mod 100", "activated", False, [("GLS", 4, 2, "recurs, locus-ambiguous")]),
    ("mod 38", "resting", True, [("DOT1L", 2, 1, "RA lead — novel"), ("MEN1", 1, 1, "weak / propagated")]),
    ("mod 54+27", "activated", True, [("AHR", 0, 3, "pan-AI but not novel"), ("DOCK2", 0, 1, "IBD-specific")]),
]
BAR_H, ROW_GAP, GROUP_GAP, MAXX = 0.34, 1.15, 0.75, 4

fig, ax = plt.subplots(figsize=(9.6, 5.8))
rows, spans, y = [], [], 0.0                       # build top-down (first group highest)
for mlabel, state, is_pair, genes in GROUPS:
    grows = []
    for gene, ng, gen, verdict in genes:
        rows.append((gene, ng, gen, verdict, y)); grows.append(y); y -= ROW_GAP
    spans.append((mlabel, state, is_pair, min(grows), max(grows)))
    y -= GROUP_GAP

for gene, ng, gen, verdict, yy in rows:
    ax.barh(yy + BAR_H / 2 + 0.03, gen, height=BAR_H, color=S.SLATE, zorder=2)
    ax.barh(yy - BAR_H / 2 - 0.03, ng, height=BAR_H, color=S.EMERALD, zorder=2)
    ax.text(-0.16, yy, gene, ha="right", va="center", family=S.SANS, fontsize=13, fontweight="bold", color=S.INK)
    ax.text(max(ng, gen) + 0.2, yy, verdict, ha="left", va="center", family=S.SANS,
            fontsize=10.5, fontstyle="italic", color=S.INK_FAINT)

# module brackets + horizontal labels on the left
BR_X = -1.45
for mlabel, state, is_pair, ymin, ymax in spans:
    ax.plot([BR_X, BR_X], [ymin - BAR_H - 0.06, ymax + BAR_H + 0.06], color="#CFCBBF",
            lw=2.6, clip_on=False, zorder=1, solid_capstyle="round")
    yc = (ymin + ymax) / 2
    ax.text(BR_X - 0.14, yc + 0.13, mlabel, ha="right", va="center", family=S.SANS, fontsize=11,
            fontweight="bold", color=S.INK_SOFT, clip_on=False)
    ax.text(BR_X - 0.14, yc - 0.19, state, ha="right", va="center", family=S.SANS, fontsize=9,
            color=S.INK_FAINT, clip_on=False)

# "same module, different mechanism" brace over each pair (right side)
BX = 5.1
for mlabel, state, is_pair, ymin, ymax in spans:
    if is_pair:
        ax.plot([BX, BX], [ymin, ymax], color=S.TERRA, lw=1.5, clip_on=False)
        for yy in (ymin, ymax):
            ax.plot([BX, BX + 0.09], [yy, yy], color=S.TERRA, lw=1.5, clip_on=False)
        ax.text(BX + 0.2, (ymin + ymax) / 2, "same module,\ndifferent mechanism", ha="left", va="center",
                family=S.SANS, fontsize=9.5, fontstyle="italic", color=S.TERRA, clip_on=False)

ax.set_xlim(0, MAXX + 0.35)
ax.set_ylim(min(r[4] for r in rows) - 0.85, max(r[4] for r in rows) + 0.8)
ax.set_yticks([])
ax.set_xticks(range(MAXX + 1))
ax.set_xlabel("number of diseases", family=S.SANS)
for s in ("left", "right", "top"):
    ax.spines[s].set_visible(False)

# legend below the axis (proxy handles), clear of the bars
h1 = ax.barh(0, 0, color=S.EMERALD, label="diseases where it's a graded A/B lead")
h2 = ax.barh(0, 0, color=S.SLATE, label="diseases with GWAS genetic support (OT > 0.05)")
ax.legend(handles=[h1, h2], loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=2, fontsize=10.5)

S.header(fig, "Pan-autoimmune synthesis", "Recurrence is module-conserved, not one mechanism",
         "Every recurring handle traces to a single shared module on shared GWAS spines (BACH2 / IRF8 / ETS1) — the honest answer is co-clustering, not convergent regulation.",
         top=0.985)
fig.subplots_adjust(top=0.70, bottom=0.16, left=0.25, right=0.80)

p = S.save(fig, "pan_autoimmune_synthesis.png")
print(f"wrote {p.relative_to(S.REPO)} ({p.stat().st_size} bytes)")
