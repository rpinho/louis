#!/usr/bin/env python3
"""The Louis opportunity map — grade × novelty, the discovery thesis in one figure.

Two axes a bench scientist actually decides on:
  Y = candidate grade (A–D, the trust-ranked verdict = "how good a lead is this?")
  X = novelty        (PubMed papers on this gene × this disease × CD4/T cell, log — understudied ↔ crowded)

The zone that matters is TOP-LEFT: high grade + understudied = novel AND well-founded — what Louis is for.
Data are the connector-verified verdicts + CD4/disease PubMed counts from the 9-disease Claude Science runs.
Renders a self-contained SVG (no plotting lib) so it ships in the README + regenerates from source.

    python scripts/opportunity_map.py            ->  docs/figures/opportunity_map.svg
"""
from __future__ import annotations
import math
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "docs" / "figures" / "opportunity_map.svg"

# (gene, disease, grade, cd4_disease_pubs, note, hero)   grades verified against *_kb_verdicts.csv.
# Each point is one gene x disease "cell" (a gene may recur — e.g. DOT1L in RA and psoriasis).
# cd4_disease_pubs = PubMed hits for gene x disease x CD4/T-cell (the novelty axis), from the same run.
# Curated for readability: MEN1 (graded B in RA but its story is hype-misattribution, not grade) and
# GLS (grade swings B+->C+ across diseases) are told in the LISTEN/synthesis narrative, not this map.
DATA = [
    ("DOT1L", "RA",        "A",  0,  "novel + druggable", True),
    ("HDAC7", "MS",        "A",  2,  "", False),
    ("PPM1D", "asthma",    "B+", 2,  "new Th2 lead", False),
    ("RASA2", "eczema",    "B+", 0,  "undruggable", False),
    ("HIF1A", "T1D",       "B",  2,  "pleiotropic", False),
    ("DOT1L", "psoriasis", "B",  0,  "recurs", False),
    ("IL21R", "T1D",       "B",  19, "", False),
    ("STAT3", "T1D",       "B",  29, "positive control", False),
    ("ZAP70", "asthma",    "B-", 19, "", False),
    ("AHR",   "psoriasis", "C",  29, "approved drug", False),
    ("DOCK2", "T1D",       "C",  0,  "discovery-stage", False),
    ("INSR",  "T1D",       "D",  2,  "low-confidence", False),
]

GRADE = {"A": 6.0, "A-": 5.5, "B+": 5.0, "B": 4.0, "B-": 3.5, "C+": 3.0, "C": 2.0, "C-": 1.5, "D": 1.0}

# --- canvas + scales ---------------------------------------------------------
W, H = 1060, 700
L, R, T, B = 92, 250, 78, 112         # plot margins (R leaves room for zone labels)
LEFT_LABEL = {("IL21R", "T1D")}       # anchor these labels left so they don't hit a neighbour's dot
PW, PH = W - L - R, H - T - B
X_MAX = math.log10(50)                 # log10(pubs+1) domain; CD4/disease counts top out ~29
Y_MIN, Y_MAX = 0.6, 6.4
PUB_DIV, GRADE_DIV = 15, 3.75          # understudied|studied at 15 papers; strong|weak between B and C+


X_INSET = 16  # keep pubs=0 points off the y-axis line


def x(pubs):  # log10(pubs+1) -> px, inset so 0 doesn't sit on the axis
    return L + X_INSET + (math.log10(pubs + 1) / X_MAX) * (PW - X_INSET)


def y(score):
    return T + PH - ((score - Y_MIN) / (Y_MAX - Y_MIN)) * PH


def zone(score, pubs):
    strong, novel = score >= GRADE_DIV, pubs <= PUB_DIV
    if strong and novel:  return "target"     # top-left sweet spot
    if strong:            return "crowded"     # top-right
    if novel:             return "early"       # bottom-left
    return "known"                             # bottom-right


FILL = {"target": "#1a9850", "crowded": "#4575b4", "early": "#d9a441", "known": "#9aa0a6"}


def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")


def build() -> Path:
    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="-apple-system,Segoe UI,Roboto,sans-serif">')
    s.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
    # sweet-spot shading (top-left)
    s.append(f'<rect x="{L}" y="{T}" width="{x(PUB_DIV)-L}" height="{y(GRADE_DIV)-T}" fill="#1a9850" opacity="0.07"/>')
    # zone dividers
    s.append(f'<line x1="{x(PUB_DIV)}" y1="{T}" x2="{x(PUB_DIV)}" y2="{T+PH}" stroke="#e15759" stroke-width="1.4" stroke-dasharray="6 5"/>')
    s.append(f'<line x1="{L}" y1="{y(GRADE_DIV)}" x2="{L+PW}" y2="{y(GRADE_DIV)}" stroke="#bbb" stroke-width="1" stroke-dasharray="4 5"/>')
    # frame
    s.append(f'<line x1="{L}" y1="{T+PH}" x2="{L+PW}" y2="{T+PH}" stroke="#333" stroke-width="1.5"/>')
    s.append(f'<line x1="{L}" y1="{T}" x2="{L}" y2="{T+PH}" stroke="#333" stroke-width="1.5"/>')
    # title + subtitle
    s.append(f'<text x="{L}" y="34" font-size="21" font-weight="700" fill="#1a1a1a">The opportunity map — where the novel, well-founded targets are</text>')
    s.append(f'<text x="{L}" y="56" font-size="13.5" fill="#666">Each point is a lead (gene × disease). Up = better-graded candidate · Left = less-studied. The green corner is the prize.</text>')
    # zone captions — drawn target reticle instead of an emoji (renders when GitHub serves the SVG)
    rx, ry = L + 26, T + 17
    s.append(f'<g stroke="#1a9850" stroke-width="1.6" fill="none">'
             f'<circle cx="{rx}" cy="{ry}" r="7.5"/><circle cx="{rx}" cy="{ry}" r="3"/>'
             f'<line x1="{rx}" y1="{ry-10}" x2="{rx}" y2="{ry-5}"/><line x1="{rx}" y1="{ry+5}" x2="{rx}" y2="{ry+10}"/>'
             f'<line x1="{rx-10}" y1="{ry}" x2="{rx-5}" y2="{ry}"/><line x1="{rx+5}" y1="{ry}" x2="{rx+10}" y2="{ry}"/></g>'
             f'<circle cx="{rx}" cy="{ry}" r="1.5" fill="#1a9850"/>')
    s.append(f'<text x="{rx+16}" y="{ry+5}" font-size="14.5" font-weight="700" fill="#1a9850">TARGET THESE — novel &amp; well-founded</text>')
    s.append(f'<text x="{x(PUB_DIV)+12}" y="{T+22}" font-size="13" font-weight="600" fill="#4575b4">Validated but crowded</text>')
    s.append(f'<text x="{L+10}" y="{T+PH-14}" font-size="13" font-weight="600" fill="#b5852b">Whitespace — not yet a lead</text>')
    s.append(f'<text x="{x(PUB_DIV)+12}" y="{T+PH-14}" font-size="13" font-weight="600" fill="#8a8f94">Known / lower-priority</text>')
    # y axis (grades)
    for g, sc in [("A", 6), ("B+", 5), ("B", 4), ("C+", 3), ("C", 2), ("D", 1)]:
        yy = y(sc)
        s.append(f'<text x="{L-12}" y="{yy+4}" font-size="12.5" font-weight="600" fill="#444" text-anchor="end">{g}</text>')
    s.append(f'<text x="26" y="{T+PH/2}" font-size="13.5" font-weight="600" fill="#333" text-anchor="middle" transform="rotate(-90 26 {T+PH/2})">candidate grade →</text>')
    # x axis (log pubs)
    for p in [0, 1, 3, 10, 30]:
        xx = x(p)
        s.append(f'<line x1="{xx}" y1="{T+PH}" x2="{xx}" y2="{T+PH+5}" stroke="#333"/>')
        s.append(f'<text x="{xx}" y="{T+PH+20}" font-size="11.5" fill="#555" text-anchor="middle">{p}</text>')
    s.append(f'<text x="{L+PW/2}" y="{H-46}" font-size="13.5" font-weight="600" fill="#333" text-anchor="middle">PubMed papers on this gene × disease × CD4 T cell  (log scale) →</text>')
    s.append(f'<text x="{x(PUB_DIV)}" y="{T+PH+38}" font-size="11" fill="#e15759" text-anchor="middle">understudied ← | → studied</text>')
    # points — curated so grades map to distinct rows; no stacking to disentangle
    for gene, dz, grade, pubs, note, hero in DATA:
        sc = GRADE[grade]
        px, py = x(pubs), y(sc)
        z = zone(sc, pubs)
        if hero:  # faint halo to draw the eye to the corner lead
            s.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="13" fill="none" stroke="{FILL[z]}" stroke-width="2" opacity="0.45"/>')
        r = 8 if hero else 6.5
        s.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r}" fill="{FILL[z]}" stroke="#fff" stroke-width="1.5"/>')
        weight = 700 if hero else 600
        left = (gene, dz) in LEFT_LABEL
        lx, anchor = (px - 12, "end") if left else (px + 12, "start")
        lbl = f'{gene} <tspan font-size="10.5" font-weight="400" fill="#888">({dz})</tspan>'
        s.append(f'<text x="{lx:.1f}" y="{py+4:.1f}" font-size="12.5" font-weight="{weight}" fill="#222" text-anchor="{anchor}">{lbl}</text>')
        if note:
            s.append(f'<text x="{lx:.1f}" y="{py+16:.1f}" font-size="9.5" fill="#6a6a6a" font-style="italic" text-anchor="{anchor}">{esc(note)}</text>')
    # footnote (two lines so it never overflows the right edge)
    s.append(f'<text x="{L}" y="{H-26}" font-size="10.5" fill="#999">Grade = trust-ranked verdict (screen QC · genetics · novelty · druggability), connector-verified. Novelty = gene × disease × CD4 PubMed count.</text>')
    s.append(f'<text x="{L}" y="{H-11}" font-size="10.5" fill="#999">Druggability is a separate 3rd axis — see each lead\'s profile (e.g. RASA2 grades on genetics but is undruggable). Source: Louis KB · 9 Claude Science disease runs.</text>')
    s.append("</svg>")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(s))
    return OUT


if __name__ == "__main__":
    p = build()
    print(f"wrote {p.relative_to(REPO)}  ({p.stat().st_size} bytes, {len(DATA)} leads)")
