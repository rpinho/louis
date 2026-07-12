#!/usr/bin/env python3
"""Th2-conserved hub — PPM1D & METAP2 recur across asthma + atopic eczema in the SAME type-2
cytokine module (88); GLS/CBLB sit in the activation module (100), eczema-only. A dumbbell/
connection chart. Data verified against the asthma + eczema *_kb_verdicts.csv (module, disease).

    python scripts/fig_th2_hub.py   ->  docs/figures/th2_conserved_hub.png
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import matplotlib.pyplot as plt
import scripts.figstyle as S  # noqa

S.apply()

# (gene, in_asthma, in_eczema, module)   module 88 = type-2 cytokine hub; 100 = activation/costim
ROWS = [
    ("PPM1D",  True,  True,  88),
    ("METAP2", True,  True,  88),
    ("RASA2",  False, True,  88),
    ("GLS",    False, True,  100),
    ("CBLB",   False, True,  100),
]
COL = {"asthma": 1.0, "atopic eczema": 3.0}
MODCOL = {88: S.EMERALD, 100: S.CLAY}

fig, ax = plt.subplots(figsize=(9.2, 5.4))
ax.axis("off")
ax.set_xlim(-0.15, 4.35)
ax.set_ylim(0.3, 5.9)

n = len(ROWS)
for i, (gene, in_a, in_e, mod) in enumerate(ROWS):
    y = n - i
    ax.text(-0.05, y, gene, ha="right", va="center", family=S.SANS, fontsize=13.5,
            fontweight="bold", color=S.INK)
    col = MODCOL[mod]
    # connecting line first (behind dots) if it recurs across both diseases
    if in_a and in_e:
        ax.plot([COL["asthma"], COL["atopic eczema"]], [y, y], color=col, lw=2.4, alpha=0.55, zorder=1)
    for dz, present in (("asthma", in_a), ("atopic eczema", in_e)):
        if present:
            ax.scatter(COL[dz], y, s=560, color=col, edgecolor=S.PAPER, linewidth=2, zorder=3)
            ax.text(COL[dz], y, f"m{mod}", ha="center", va="center", family=S.SANS,
                    fontsize=9, fontweight="bold", color="white", zorder=4)

# column headers
for dz, xx in COL.items():
    ax.text(xx, 5.72, dz, ha="center", va="center", family=S.SANS, fontsize=13.5,
            fontweight="bold", color=S.INK_SOFT)

# the GLS bridge annotation
gy = n - 3
ax.annotate("GLS also recurs in Th1/Th17\ndiseases — via other modules",
            xy=(COL["atopic eczema"] + 0.18, gy), xytext=(COL["atopic eczema"] + 0.42, gy),
            ha="left", va="center", family=S.SANS, fontsize=10.5, fontstyle="italic", color=S.CLAY)

# legend (manual, bottom-left under the plot)
ly = 0.62
ax.scatter(0.35, ly, s=300, color=S.EMERALD, edgecolor=S.PAPER, linewidth=1.5)
ax.text(0.55, ly, "module 88 — type-2 cytokine hub (IL4 / IL13 / IL5)", va="center",
        family=S.SANS, fontsize=11, color=S.INK_SOFT)
ax.scatter(0.35, ly - 0.001, s=0)  # spacer noop
ax.scatter(2.75, ly, s=300, color=S.CLAY, edgecolor=S.PAPER, linewidth=1.5)
ax.text(2.95, ly, "module 100 — activation / costim (REL / EGR2 / BACH2)", va="center",
        family=S.SANS, fontsize=11, color=S.INK_SOFT)

S.header(fig, "Th2-conserved hub", "One hub recurs across both allergic diseases",
         "PPM1D and METAP2 sit in the same type-2 cytokine module in asthma and eczema — a shared Th2 axis, disjoint from the Th1/Th17 diseases.",
         top=0.99)
fig.subplots_adjust(top=0.72, bottom=0.02, left=0.11, right=0.98)

p = S.save(fig, "th2_conserved_hub.png")
print(f"wrote {p.relative_to(S.REPO)} ({p.stat().st_size} bytes)")
