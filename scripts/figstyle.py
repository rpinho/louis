"""Shared editorial style for Louis's figures — one visual family (palette + type) so the whole
README figure set reads as a designed system, matching the hand-authored opportunity map.

The opportunity map is hand-SVG (qlmanage-rendered); these matplotlib figures share its palette and
its Iowan Old Style / Avenir Next type, so the set feels cohesive while staying reproducible.
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FIG = REPO / "docs" / "figures"

# palette — identical to scripts/opportunity_map.py
INK, INK_SOFT, INK_FAINT = "#1B1F24", "#5A6068", "#9AA0A6"
PAPER = "#FAF9F5"
EMERALD, EMERALD_DK = "#12805C", "#0D6446"
SLATE, CLAY, STONE = "#5C7A99", "#B7823B", "#9A968C"
TERRA, GRID = "#C8674A", "#E4E1D8"
SERIF, SANS = "Iowan Old Style", "Avenir Next"


def apply():
    mpl.rcParams.update({
        "figure.facecolor": PAPER, "axes.facecolor": PAPER, "savefig.facecolor": PAPER,
        "font.family": SANS, "font.size": 12, "text.color": INK,
        "axes.edgecolor": "#C9C6BD", "axes.linewidth": 1.1,
        "axes.labelcolor": INK_SOFT, "axes.labelsize": 12.5,
        "xtick.color": INK_FAINT, "ytick.color": INK_SOFT,
        "xtick.labelsize": 11.5, "ytick.labelsize": 12,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.titlesize": 14, "axes.titleweight": "bold", "axes.titlecolor": INK,
        "legend.frameon": False, "legend.fontsize": 11.5,
        "figure.dpi": 150, "svg.fonttype": "none",
    })


def header(fig, eyebrow, headline, sub=None, x=0.045, top=0.965, hsize=21):
    """Eyebrow (emerald caps) + serif headline + optional sans subtitle — the opportunity-map masthead."""
    fig.text(x, top, " ".join(eyebrow.upper()), family=SANS, fontsize=11, fontweight="bold", color=EMERALD)
    fig.text(x, top - 0.062, headline, family=SERIF, fontsize=hsize, fontweight="bold", color=INK)
    if sub:
        fig.text(x, top - 0.115, sub, family=SANS, fontsize=12.5, color=INK_SOFT)


def save(fig, name, pad=0.3):
    FIG.mkdir(parents=True, exist_ok=True)
    p = FIG / name
    fig.savefig(p, dpi=200, bbox_inches="tight", pad_inches=pad)
    plt.close(fig)
    return p
