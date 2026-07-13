#!/usr/bin/env python3
"""The Louis opportunity map — grade × novelty, the discovery thesis in one figure.

Two axes a bench scientist actually decides on:
  Y = candidate grade (A–D, the trust-ranked verdict = "how good a lead is this?")
  X = novelty        (PubMed papers on this gene × disease × CD4/T cell, log — understudied ↔ crowded)

The zone that matters is TOP-LEFT: high grade + understudied = novel AND well-founded — what Louis is for.
Data are the connector-verified verdicts + CD4/disease PubMed counts from the 9-disease Claude Science runs.

Renders a self-contained SVG (no plotting lib) and — if `qlmanage` is present (macOS) — a crisp PNG for
the README, so custom fonts + filters bake in and GitHub can't sanitize them away.

    python scripts/opportunity_map.py     ->  docs/figures/opportunity_map.svg  (+ .png on macOS)
"""
from __future__ import annotations
import math
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "docs" / "figures" / "opportunity_map.svg"

# (gene, disease, grade, cd4_disease_pubs, note, hero)   grades verified against *_kb_verdicts.csv.
# Each point is one gene x disease "cell" (a gene may recur — e.g. DOT1L in RA and psoriasis).
# cd4_disease_pubs = PubMed hits for gene x disease x CD4/T-cell (the novelty axis), from the same run.
# Curated for readability: MEN1 (graded B in RA but its story is hype-misattribution, not grade) and
# GLS (grade swings B+->C+ across diseases) are told in the LISTEN/synthesis narrative, not this map.
DATA = [
    ("HDAC7", "UC",        "B",  1,  "survivor lead", True),
    ("DOT1L", "RA",        "C",  0,  "red-teamed to C", False),
    ("HDAC7", "MS",        "B-", 2,  "", False),
    ("PPM1D", "asthma",    "C+", 2,  "Th9 backup", False),
    ("RASA2", "eczema",    "B+", 0,  "undruggable", False),
    ("HIF1A", "T1D",       "B",  2,  "pleiotropic", False),
    ("IL21R", "T1D",       "B",  19, "", False),
    ("STAT3", "T1D",       "B",  29, "positive control", False),
    ("ZAP70", "asthma",    "B-", 19, "", False),
    ("AHR",   "psoriasis", "C",  29, "approved drug", False),
    ("DOCK2", "psoriasis", "B-", 0,  "scarred survivor", False),
    ("INSR",  "T1D",       "D",  2,  "low-confidence", False),
]

GRADE = {"A": 6.0, "A-": 5.5, "B+": 5.0, "B": 4.0, "B-": 3.5, "C+": 3.0, "C": 2.0, "C-": 1.5, "D": 1.0}

# --- design tokens -----------------------------------------------------------
SERIF = "'Iowan Old Style','Charter',Georgia,'Times New Roman',serif"     # editorial title (macOS)
SANS = "'Avenir Next','Helvetica Neue',-apple-system,'Segoe UI',sans-serif"
INK, INK_SOFT, INK_FAINT = "#1B1F24", "#5A6068", "#9AA0A6"
PAPER0, PAPER1, GRID = "#FAF9F5", "#F1F0EA", "#E4E1D8"
EMERALD, EMERALD_DK = "#12805C", "#0D6446"        # hero accent — the prize
SLATE, CLAY, STONE = "#5C7A99", "#B7823B", "#9A968C"   # muted supports, so green owns the eye
GUIDE = "#C8674A"                                   # understudied|studied divider (muted terracotta)
FILL = {"target": EMERALD, "crowded": SLATE, "early": CLAY, "known": STONE}

# --- canvas + scales ---------------------------------------------------------
W, H = 1120, 740
L, R, T, B = 104, 215, 140, 120
PW, PH = W - L - R, H - T - B                       # 801 x 480
X_INSET, X_MAX = 16, math.log10(50)
Y_MIN, Y_MAX = 0.5, 7.0          # headroom above grade A for a clean zone-caption band
PUB_DIV, GRADE_DIV = 15, 3.75
LEFT_LABEL = {("IL21R", "T1D")}


def x(pubs):
    return L + X_INSET + (math.log10(pubs + 1) / X_MAX) * (PW - X_INSET)


def y(score):
    return T + PH - ((score - Y_MIN) / (Y_MAX - Y_MIN)) * PH


def zone(score, pubs):
    strong, novel = score >= GRADE_DIV, pubs <= PUB_DIV
    return "target" if (strong and novel) else "crowded" if strong else "early" if novel else "known"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def _reticle(cx, cy, col):
    return (f'<g stroke="{col}" stroke-width="1.6" fill="none">'
            f'<circle cx="{cx}" cy="{cy}" r="7.5"/><circle cx="{cx}" cy="{cy}" r="3"/>'
            f'<line x1="{cx}" y1="{cy-10.5}" x2="{cx}" y2="{cy-5}"/><line x1="{cx}" y1="{cy+5}" x2="{cx}" y2="{cy+10.5}"/>'
            f'<line x1="{cx-10.5}" y1="{cy}" x2="{cx-5}" y2="{cy}"/><line x1="{cx+5}" y1="{cy}" x2="{cx+10.5}" y2="{cy}"/></g>'
            f'<circle cx="{cx}" cy="{cy}" r="1.5" fill="{col}"/>')


def build() -> Path:
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">']
    # defs: paper gradient, prize wash, hero glow, soft dot shadow
    s.append(
        '<defs>'
        f'<linearGradient id="paper" x1="0" y1="0" x2="0.35" y2="1">'
        f'<stop offset="0" stop-color="{PAPER0}"/><stop offset="1" stop-color="{PAPER1}"/></linearGradient>'
        f'<linearGradient id="prize" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{EMERALD}" stop-opacity="0.15"/>'
        f'<stop offset="1" stop-color="{EMERALD}" stop-opacity="0.015"/></linearGradient>'
        f'<radialGradient id="glow"><stop offset="0" stop-color="{EMERALD}" stop-opacity="0.30"/>'
        f'<stop offset="1" stop-color="{EMERALD}" stop-opacity="0"/></radialGradient>'
        '<filter id="dot" x="-60%" y="-60%" width="220%" height="220%">'
        '<feDropShadow dx="0" dy="1.4" stdDeviation="1.7" flood-color="#1B1F24" flood-opacity="0.22"/></filter>'
        '</defs>')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#paper)"/>')

    # --- faint grade gridlines so a point reads back to its grade across the wide middle ---
    for _sc in (6, 5, 4, 3, 2, 1):
        s.append(f'<line x1="{L}" y1="{y(_sc):.1f}" x2="{L+PW}" y2="{y(_sc):.1f}" stroke="#ECEAE3" stroke-width="1"/>')

    # --- plot backdrop: prize wash + soft quadrant guides ---
    s.append(f'<rect x="{L}" y="{T}" width="{x(PUB_DIV)-L:.1f}" height="{y(GRADE_DIV)-T:.1f}" fill="url(#prize)"/>')
    s.append(f'<line x1="{L}" y1="{y(GRADE_DIV):.1f}" x2="{L+PW}" y2="{y(GRADE_DIV):.1f}" stroke="{GRID}" stroke-width="1"/>')
    s.append(f'<line x1="{x(PUB_DIV):.1f}" y1="{T}" x2="{x(PUB_DIV):.1f}" y2="{T+PH}" stroke="{GUIDE}" stroke-width="1.1" stroke-opacity="0.55" stroke-dasharray="2 5"/>')
    # open axes (left + bottom only)
    s.append(f'<line x1="{L}" y1="{T+PH}" x2="{L+PW}" y2="{T+PH}" stroke="#C9C6BD" stroke-width="1.4"/>')
    s.append(f'<line x1="{L}" y1="{T}" x2="{L}" y2="{T+PH}" stroke="#C9C6BD" stroke-width="1.4"/>')

    # --- title block ---
    s.append(f'<text x="{L}" y="46" font-family="{SANS}" font-size="12.5" font-weight="700" letter-spacing="2.4" fill="{EMERALD}">OPPORTUNITY MAP</text>')
    s.append(f'<text x="{L}" y="82" font-family="{SERIF}" font-size="31" font-weight="700" fill="{INK}">Where the novel, well-founded targets are</text>')
    s.append(f'<text x="{L}" y="108" font-family="{SANS}" font-size="14" fill="{INK_SOFT}">Each point is a lead (gene × disease). Up = better-graded candidate · left = less-studied. The green corner is the prize.</text>')

    # --- zone captions ---
    rx, ry = L + 24, T + 20
    s.append(_reticle(rx, ry, EMERALD_DK))
    s.append(f'<text x="{rx+16}" y="{ry+5}" font-family="{SANS}" font-size="13.5" font-weight="700" letter-spacing="1.4" fill="{EMERALD_DK}">TARGET THESE</text>')
    s.append(f'<text x="{rx+16}" y="{ry+21}" font-family="{SANS}" font-size="11.5" font-style="italic" fill="{INK_SOFT}">novel &amp; well-founded — what Louis surfaces</text>')
    cxr = x(PUB_DIV) + 16
    s.append(f'<text x="{cxr}" y="{T+20}" font-family="{SANS}" font-size="13" font-weight="700" letter-spacing="0.8" fill="{SLATE}">VALIDATED BUT CROWDED</text>')
    s.append(f'<text x="{cxr}" y="{T+36}" font-family="{SANS}" font-size="11.5" font-style="italic" fill="{INK_FAINT}">where a database would send you</text>')
    s.append(f'<text x="{L+12}" y="{T+PH-14}" font-family="{SANS}" font-size="12.5" font-weight="700" letter-spacing="0.8" fill="{CLAY}">WHITESPACE — NOT YET A LEAD</text>')
    s.append(f'<text x="{cxr}" y="{T+PH-14}" font-family="{SANS}" font-size="12.5" font-weight="700" letter-spacing="0.8" fill="{STONE}">KNOWN / LOWER-PRIORITY</text>')

    # --- axes ticks/labels ---
    for g, sc in [("A", 6), ("B+", 5), ("B", 4), ("C+", 3), ("C", 2), ("D", 1)]:
        s.append(f'<text x="{L-14}" y="{y(sc)+4.5:.1f}" font-family="{SANS}" font-size="13" font-weight="600" fill="{INK_SOFT}" text-anchor="end">{g}</text>')
    s.append(f'<text x="34" y="{T+PH/2:.0f}" font-family="{SANS}" font-size="12.5" font-weight="600" letter-spacing="1" fill="{INK_SOFT}" text-anchor="middle" transform="rotate(-90 34 {T+PH/2:.0f})">CANDIDATE GRADE →</text>')
    for p in [0, 1, 3, 10, 30]:
        s.append(f'<line x1="{x(p):.1f}" y1="{T+PH}" x2="{x(p):.1f}" y2="{T+PH+5}" stroke="#C9C6BD"/>')
        s.append(f'<text x="{x(p):.1f}" y="{T+PH+20}" font-family="{SANS}" font-size="12" fill="{INK_FAINT}" text-anchor="middle" style="font-variant-numeric:tabular-nums">{p}</text>')
    s.append(f'<text x="{L+PW/2:.0f}" y="{H-42}" font-family="{SANS}" font-size="12.5" font-weight="600" letter-spacing="1" fill="{INK_SOFT}" text-anchor="middle">PUBMED PAPERS · GENE × DISEASE × CD4 T CELL  (LOG) →</text>')
    s.append(f'<text x="{x(PUB_DIV):.1f}" y="{T+PH+38}" font-family="{SANS}" font-size="11" font-style="italic" fill="{GUIDE}" text-anchor="middle">understudied ← | → studied</text>')

    # --- points ---
    for gene, dz, grade, pubs, note, hero in DATA:
        sc = GRADE[grade]
        px, py, z = x(pubs), y(sc), zone(sc, pubs)
        if hero:
            s.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="26" fill="url(#glow)"/>')
            s.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="13.5" fill="none" stroke="{EMERALD}" stroke-width="1.6" stroke-opacity="0.5"/>')
        r = 9.5 if hero else 7
        s.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r}" fill="{FILL[z]}" stroke="{PAPER0}" stroke-width="1.6" filter="url(#dot)"/>')
        left = (gene, dz) in LEFT_LABEL
        lx, anchor = (px - 13, "end") if left else (px + 13, "start")
        gcol = EMERALD_DK if hero else INK
        s.append(f'<text x="{lx:.1f}" y="{py-1:.1f}" font-family="{SANS}" font-size="13.5" font-weight="700" fill="{gcol}" text-anchor="{anchor}">{gene} '
                 f'<tspan font-size="11" font-weight="400" fill="{INK_FAINT}">({dz})</tspan></text>')
        if note:
            ncol = EMERALD if hero else INK_SOFT
            s.append(f'<text x="{lx:.1f}" y="{py+12.5:.1f}" font-family="{SANS}" font-size="10.5" font-style="italic" fill="{ncol}" text-anchor="{anchor}">{esc(note)}</text>')

    # --- footnote ---
    s.append(f'<text x="{L}" y="{H-24}" font-family="{SANS}" font-size="10.5" fill="{INK_FAINT}">Grade = trust-ranked verdict (screen QC · genetics · novelty · druggability), connector-verified.  Novelty = gene × disease × CD4 PubMed count.</text>')
    s.append(f'<text x="{L}" y="{H-10}" font-family="{SANS}" font-size="10.5" fill="{INK_FAINT}">Druggability is a separate 3rd axis — see each lead\'s profile (e.g. RASA2 grades on genetics but is undruggable today).  Source: Louis KB · 9 Claude Science disease runs.</text>')
    s.append("</svg>")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(s))
    return OUT


def _render_png(svg: Path):
    """Render SVG -> PNG via macOS Quick Look so custom fonts + filters bake in (GitHub-safe).
    qlmanage emits a SQUARE thumbnail (letterboxed), so crop the padding back to the true aspect."""
    if not shutil.which("qlmanage"):
        return None
    png = svg.with_suffix(".png")
    size = 1680     # ~2x the README display width — crisp on retina, lean repo asset
    subprocess.run(["qlmanage", "-t", "-s", str(size), "-o", str(svg.parent), str(svg)],
                   capture_output=True, timeout=60)
    thumb = svg.parent / (svg.name + ".png")     # qlmanage writes <name>.svg.png
    if not thumb.exists():
        return None
    thumb.replace(png)
    if shutil.which("sips"):                       # strip the square letterbox -> real W:H
        subprocess.run(["sips", "-c", str(round(size * H / W)), str(size), str(png)],
                       capture_output=True, timeout=30)
    return png


if __name__ == "__main__":
    p = build()
    png = _render_png(p)
    print(f"wrote {p.relative_to(REPO)}  ({p.stat().st_size} bytes, {len(DATA)} leads)"
          + (f"\nwrote {png.relative_to(REPO)}  ({png.stat().st_size} bytes)" if png else "\n(no qlmanage — SVG only)"))
