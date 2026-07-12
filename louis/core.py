"""
Core logic for the Louis.

Turns the Marson/Pritchard genome-scale CD4+ T-cell Perturb-seq (Zhu, Dann, ...,
Pritchard, Marson 2025; CZI Virtual Cells Platform) into a self-serve
disease -> candidate-target workflow WITH a GRN + trust/rigor layer, for a bench
immunologist who does not want to touch a terminal or a bioinformatician.

The upstream science (GRN inference + autoimmune-disease enrichment + guide QC)
is precomputed by the dataset authors. This tool's value is the LAST MILE:
- pick a disease -> ranked candidate T-cell regulators/targets,
- each with GRN influence (how many downstream genes it controls),
- and a plain-English confidence flag derived from the dataset's own on-target
  knockdown verification + off-target flags (so the hit can be trusted),
- plus the Th1/Th2 polarization effect as a functional readout.
"""
from __future__ import annotations
import ast
from functools import lru_cache
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

_FILES = {
    "enrichment": "cluster_autoimmune_enrichment_results.csv",
    "de_stats": "DE_stats.csv",
    "kd": "guide_kd_efficiency.csv",
    "polarization": "Th2_Th1_polarization_signature_DE_results_full.csv",
    "sgrna": "sgrna_library_metadata.csv",
}


def _path(key: str) -> Path:
    p = DATA_DIR / _FILES[key]
    if not p.exists():
        raise FileNotFoundError(
            f"Missing {p.name}. Run `python scripts/download_data.py` first."
        )
    return p


@lru_cache(maxsize=None)
def load_enrichment() -> pd.DataFrame:
    return pd.read_csv(_path("enrichment"))


@lru_cache(maxsize=None)
def load_de_stats() -> pd.DataFrame:
    return pd.read_csv(_path("de_stats"))


@lru_cache(maxsize=None)
def load_polarization() -> pd.DataFrame:
    return pd.read_csv(_path("polarization"))


def _parse_gene_list(s) -> list[str]:
    """The enrichment table stores intersecting genes as a stringified list."""
    if isinstance(s, list):
        return s
    if not isinstance(s, str):
        return []
    try:
        v = ast.literal_eval(s)
        return [str(g) for g in v] if isinstance(v, (list, tuple)) else []
    except (ValueError, SyntaxError):
        return [g.strip() for g in s.strip("[]").replace("'", "").split(",") if g.strip()]


# ---------------------------------------------------------------------------
# GRN + trust layer, from the authors' authoritative per-perturbation stats
# ---------------------------------------------------------------------------

@lru_cache(maxsize=None)
def _grn_summary() -> pd.DataFrame:
    """
    One row per perturbed regulator (max across culture conditions):
      controls_n_genes  -- downstream genes significantly affected (GRN out-degree)
      kd_verified       -- on-target knockdown significant in >=1 condition
      offtarget_risk    -- off-target flagged in >=1 condition
    """
    de = load_de_stats()
    g = de.groupby("target_contrast_gene_name").agg(
        controls_n_genes=("n_downstream", "max"),
        kd_verified=("ontarget_significant", "any"),
        offtarget_risk=("offtarget_flag", "any"),
    )
    return g


@lru_cache(maxsize=None)
def _grn_out_degrees() -> pd.Series:
    """Out-degree (controls_n_genes) for every perturbed regulator, for percentiles."""
    return _grn_summary()["controls_n_genes"].dropna()


# ---------------------------------------------------------------------------
# Activation-state layer: a regulator's role shifts with the T cell's state.
# The screen was run in three activation states (Rest / Stim8hr / Stim48hr);
# ~87% of hub regulators change their GRN out-degree >=2x across them. Bench
# immunologists can't read that state-dependence without re-running the assay —
# so we surface the state the authors already measured, per target.
# ---------------------------------------------------------------------------
STATES = ("Rest", "Stim8hr", "Stim48hr")


@lru_cache(maxsize=None)
def _grn_state_table() -> pd.DataFrame:
    """Per regulator x activation state: GRN out-degree (columns Rest/Stim8hr/Stim48hr)."""
    de = load_de_stats()
    piv = (de.groupby(["target_contrast_gene_name", "culture_condition"])["n_downstream"]
             .max().unstack("culture_condition"))
    return piv[[c for c in STATES if c in piv.columns]]


def _classify_state(by_state: dict) -> tuple[str, str]:
    """(label, plain-English summary) for how out-degree shifts across activation states."""
    vals = [v for v in by_state.values() if v is not None]
    if not vals or max(vals) < 20:
        return "minimal", "minimal regulatory influence in any state"
    rest = by_state.get("Rest")
    stim = [by_state[s] for s in ("Stim8hr", "Stim48hr") if by_state.get(s) is not None]
    activated = max(stim) if stim else None
    hi, lo = max(vals), min(vals)
    fmt = lambda n: f"{int(n):,}"
    if rest is not None and activated is not None:
        if activated >= 100 and activated >= 3 * max(rest, 1):
            return "activation-induced", (
                f"switches on with activation — {fmt(rest)} at rest → {fmt(activated)} genes when stimulated")
        if rest >= 100 and rest >= 3 * max(activated, 1):
            return "resting-state", (
                f"active in resting cells ({fmt(rest)} genes) but fades with activation → {fmt(activated)}")
    if hi >= 2 * max(lo, 1):
        return "activation-modulated", f"influence shifts with activation state ({fmt(lo)}–{fmt(hi)} genes across states)"
    return "constitutive", f"active across all activation states ({fmt(lo)}–{fmt(hi)} genes)"


@lru_cache(maxsize=None)
def _state_info() -> pd.DataFrame:
    """One row per perturbed regulator: by_state out-degrees + state label + summary."""
    tab = _grn_state_table()
    recs = {}
    for gene, row in tab.iterrows():
        by = {s: (int(row[s]) if s in row.index and pd.notna(row[s]) else None) for s in STATES}
        label, summ = _classify_state(by)
        recs[gene] = {"state_pattern": label, "state_summary": summ, "by_state": by}
    return pd.DataFrame.from_dict(recs, orient="index")


@lru_cache(maxsize=None)
def _polarization_map() -> dict[str, float]:
    """gene -> Th2_vs_Th1 log2 fold change (most significant row). >0 = Th2, <0 = Th1."""
    pol = load_polarization()
    sig = pol[pol["adj_p_value"] < 0.05].sort_values("adj_p_value")
    sig = sig.drop_duplicates("variable", keep="first")  # most significant row per gene
    return dict(zip(sig["variable"], sig["log_fc"]))


@lru_cache(maxsize=None)
def _cluster_regulators_map() -> dict:
    """cluster id -> its regulator members (union of disease-intersecting regulators across diseases)."""
    enr = load_enrichment()
    reg = enr[enr["gene_set"] == "regulators"]
    out: dict[int, list[str]] = {}
    for cid, grp in reg.groupby("cluster"):
        genes: set[str] = set()
        for s in grp["intersecting_genes"]:
            genes |= set(_parse_gene_list(s))
        out[int(cid)] = sorted(genes)
    return out


def _confidence(kd_verified, offtarget, perturbed: bool) -> str:
    if not perturbed:
        return "Downstream only (not directly perturbed here)"
    if kd_verified and not offtarget:
        return "High — knockdown verified, clean guide"
    if kd_verified and offtarget:
        return "Medium — knockdown verified, off-target risk"
    return "Low — knockdown not confirmed"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def list_diseases() -> list[str]:
    return sorted(load_enrichment()["disease"].dropna().unique().tolist())


def disease_targets(disease: str, fdr: float = 0.05, top: int | None = None) -> pd.DataFrame:
    """
    For a disease, return ranked candidate target genes with a GRN + trust layer.

    One row per candidate gene (deduped to its strongest disease-enriched program),
    annotated with: GRN influence (controls_n_genes), on-target knockdown
    verification, off-target risk, a plain-English confidence flag, and the
    Th1/Th2 polarization effect.
    """
    enr = load_enrichment()
    hits = enr[(enr["disease"] == disease) & (enr["p_adj_fdr"] < fdr)].copy()
    if hits.empty:
        return pd.DataFrame()

    rows = []
    for _, r in hits.iterrows():
        for gene in _parse_gene_list(r["intersecting_genes"]):
            rows.append({
                "gene": gene,
                "disease_odds_ratio": float(r["odds_ratio"]),
                "p_adj_fdr": float(r["p_adj_fdr"]),
                "program": r["gene_set"],
                "cluster": int(r["cluster"]),
            })
    df = pd.DataFrame(rows)
    df = df.sort_values("disease_odds_ratio", ascending=False).drop_duplicates("gene")

    grn = _grn_summary()
    pol = _polarization_map()

    df["controls_n_genes"] = df["gene"].map(grn["controls_n_genes"]).astype("Int64")
    df["kd_verified"] = df["gene"].map(grn["kd_verified"]).fillna(False).astype(bool)
    df["offtarget_risk"] = df["gene"].map(grn["offtarget_risk"]).fillna(False).astype(bool)
    df["th2_vs_th1_lfc"] = df["gene"].map(pol)
    df["state_pattern"] = df["gene"].map(_state_info()["state_pattern"])
    perturbed = set(grn.index)
    df["confidence"] = [
        _confidence(k, o, g in perturbed)
        for g, k, o in zip(df["gene"], df["kd_verified"], df["offtarget_risk"])
    ]
    # rank: disease enrichment first, then GRN influence as a tie-breaker
    df = df.sort_values(["disease_odds_ratio", "controls_n_genes"],
                        ascending=[False, False]).reset_index(drop=True)
    return df.head(top) if top else df


def disease_mechanisms(disease: str, fdr: float = 0.05, top_modules: int = 8) -> list[dict]:
    """
    Mechanistic discovery — beyond ranking known regulators.

    For a disease, returns the GRN modules whose DOWNSTREAM program is enriched in the disease's
    own risk genes, each with: the specific risk genes, the activation state it fires in, and the
    candidate regulator HANDLES (druggable entry points) that co-cluster with that module —
    annotated with trust (knockdown QC) and activation state.

    This is the substrate for novel, testable hypotheses — "perturb handle X to move the disease
    risk program [genes] in state S" — rather than re-surfacing the obvious top-enrichment gene.
    Handles are sorted trust-first. NOTE: these are module-level (co-cluster) associations, i.e.
    candidate upstream controllers to test, not proven gene-level edges.
    """
    enr = load_enrichment()
    dwn = enr[(enr["disease"] == disease)
              & (enr["gene_set"].str.startswith("downstream"))
              & (enr["p_adj_fdr"] < fdr)].sort_values("odds_ratio", ascending=False)
    if dwn.empty:
        return []

    regmap = _cluster_regulators_map()
    grn = _grn_summary()
    sinfo = _state_info()
    perturbed = set(grn.index)

    out, seen = [], set()
    for _, r in dwn.iterrows():
        cid = int(r["cluster"])
        if cid in seen:
            continue
        seen.add(cid)
        handles = []
        for h in regmap.get(cid, []):
            if h in perturbed:
                g = grn.loc[h]
                controls = int(g["controls_n_genes"]) if pd.notna(g["controls_n_genes"]) else None
                handles.append({
                    "gene": h,
                    "confidence": _confidence(bool(g["kd_verified"]), bool(g["offtarget_risk"]), True),
                    "kd_verified": bool(g["kd_verified"]),
                    "controls_n_genes": controls,
                    "state_pattern": sinfo.loc[h, "state_pattern"] if h in sinfo.index else None,
                })
            else:
                handles.append({"gene": h, "confidence": "not perturbed in screen",
                                "kd_verified": False, "controls_n_genes": None, "state_pattern": None})
        # trust-first, then most influential
        handles.sort(key=lambda d: (d["kd_verified"], d["controls_n_genes"] or 0), reverse=True)
        out.append({
            "module": cid,
            "fires_in_state": r["gene_set"].replace("downstream_", ""),
            "odds_ratio": round(float(r["odds_ratio"]), 1),
            "fdr": float(r["p_adj_fdr"]),
            "disease_risk_genes": _parse_gene_list(r["intersecting_genes"]),
            "candidate_handles": handles[:12],
        })
        if len(out) >= top_modules:
            break
    return out


def regulator_detail(gene: str) -> dict:
    """GRN + QC card for a single regulator, across culture conditions."""
    de = load_de_stats()
    sub = de[de["target_contrast_gene_name"] == gene]
    if sub.empty:
        return {"gene": gene, "perturbed": False}
    by_cond = {
        r["culture_condition"]: {
            "controls_n_genes": int(r["n_downstream"]),
            "n_up": int(r["n_up_genes"]),
            "n_down": int(r["n_down_genes"]),
            "kd_verified": bool(r["ontarget_significant"]),
            "offtarget": bool(r["offtarget_flag"]),
        }
        for _, r in sub.iterrows()
    }
    return {"gene": gene, "perturbed": True, "by_condition": by_cond,
            "max_controls": int(sub["n_downstream"].max())}


def state_profile(gene: str) -> dict | None:
    """
    How a regulator's GRN influence shifts across T-cell activation states.

    The screen measured each perturbation in Rest / Stim8hr / Stim48hr; this returns
    the out-degree per state, which state it peaks in, and a plain-English label
    (activation-induced / resting-state / activation-modulated / constitutive) — the
    state-dependence a bench immunologist otherwise needs a whole experiment to read.
    Returns None if the gene was not directly perturbed.
    """
    info = _state_info()
    if gene not in info.index:
        return None
    r = info.loc[gene]
    by = r["by_state"]
    present = [s for s in STATES if by.get(s) is not None]
    peak = max(present, key=lambda s: by[s], default=None)
    stim = [by[s] for s in ("Stim8hr", "Stim48hr") if by.get(s) is not None]
    return {
        "gene": gene,
        "by_state": by,
        "state_pattern": r["state_pattern"],
        "summary": r["state_summary"],
        "peak_state": peak,
        "resting": by.get("Rest"),
        "activated_max": max(stim) if stim else None,
    }


def _handle_evidence(disease: str, gene: str, fdr: float = 0.05) -> dict | None:
    """Evidence for a gene that is a module co-cluster HANDLE (from disease_mechanisms) rather
    than a top-ranked enrichment target. Its disease link is the risk-gene MODULE(s) it
    co-regulates — not its own program's enrichment — so target_evidence composes with the
    discovery call. Returns None only if the gene is neither a handle here nor perturbed."""
    mods = disease_mechanisms(disease, fdr=fdr, top_modules=100)
    hits = [m for m in mods if any(h["gene"] == gene for h in m.get("candidate_handles", []))]
    det = regulator_detail(gene)
    if not hits and not det.get("perturbed"):
        return None
    entry = next((h for m in hits for h in m["candidate_handles"] if h["gene"] == gene), None)
    controls = entry["controls_n_genes"] if entry else None
    if controls is None:
        grn = _grn_summary()
        if gene in grn.index and pd.notna(grn.loc[gene, "controls_n_genes"]):
            controls = int(grn.loc[gene, "controls_n_genes"])
    dist = _grn_out_degrees()
    percentile = float((dist < controls).mean() * 100) if controls is not None else None
    conds = det.get("by_condition", {}) if det.get("perturbed") else {}
    n_verified = sum(1 for c in conds.values() if c["kd_verified"])
    sp = state_profile(gene)
    return {
        "disease": disease,
        "gene": gene,
        "kind": "module_handle",
        "note": ("Module co-cluster HANDLE (surfaced by disease_mechanisms), not a top-ranked "
                 "enrichment target — so it has no own-program enrichment odds ratio. Its disease "
                 "link is the risk-gene MODULE(s) it co-regulates, listed below: a candidate upstream "
                 "controller to test, NOT a proven gene-level edge."),
        "handle_for_modules": [
            {"module": m["module"], "fires_in_state": m["fires_in_state"],
             "odds_ratio": m["odds_ratio"], "fdr": m["fdr"],
             "disease_risk_genes": m["disease_risk_genes"]}
            for m in hits],
        "controls_n_genes": controls,
        "percentile": percentile,
        "n_regulators": int(len(dist)),
        "median_out_degree": int(dist.median()),
        "kd_verified": bool(entry["kd_verified"]) if entry else any(c["kd_verified"] for c in conds.values()),
        "n_conditions": len(conds),
        "n_conditions_verified": n_verified,
        "state_pattern": sp["state_pattern"] if sp else None,
        "state_summary": sp["summary"] if sp else None,
        "by_state": sp["by_state"] if sp else None,
        "peak_state": sp["peak_state"] if sp else None,
    }


def target_evidence(disease: str, gene: str, fdr: float = 0.05) -> dict | None:
    """
    Assemble the full 'why this target' case for one gene in one disease.

    Bundles the four independent lines of evidence a bench scientist weighs before
    committing to a target — disease link, network influence, experimental trust,
    and functional readout — each computed from the authors' precomputed tables.
    Returns None if the gene is not a candidate for the disease.
    """
    df = disease_targets(disease, fdr=fdr)
    if df.empty or gene not in set(df["gene"]):
        # Not a top-ranked enrichment target — but it may be a module co-cluster HANDLE
        # (surfaced by disease_mechanisms). Resolve that so discover -> evidence composes,
        # instead of a bare None that dead-ends the workflow.
        return _handle_evidence(disease, gene, fdr=fdr)
    row = df[df["gene"] == gene].iloc[0]
    rank = int(df.index[df["gene"] == gene][0]) + 1

    # --- disease link: which enriched program placed this gene, and its peers ---
    enr = load_enrichment()
    hits = enr[(enr["disease"] == disease) & (enr["p_adj_fdr"] < fdr)].copy()
    hits = hits[hits["intersecting_genes"].map(lambda s: gene in _parse_gene_list(s))]
    best = hits.sort_values("odds_ratio", ascending=False).iloc[0]
    peers = [g for g in _parse_gene_list(best["intersecting_genes"]) if g != gene]

    # --- network influence: out-degree percentile among all perturbed regulators ---
    controls = row["controls_n_genes"]
    controls = int(controls) if pd.notna(controls) else None
    dist = _grn_out_degrees()
    percentile = float((dist < controls).mean() * 100) if controls is not None else None

    # --- experimental trust: on-target KD + off-target flag, across conditions ---
    det = regulator_detail(gene)
    conds = det.get("by_condition", {}) if det.get("perturbed") else {}
    n_verified = sum(1 for c in conds.values() if c["kd_verified"])

    # --- functional readout: Th1/Th2 polarization ---
    lfc = row["th2_vs_th1_lfc"]
    lfc = float(lfc) if pd.notna(lfc) else None
    polarization = None if lfc is None else ("Th2" if lfc > 0 else "Th1")

    # --- activation state: where in the T cell's life this target actually acts ---
    sp = state_profile(gene)

    return {
        "disease": disease,
        "gene": gene,
        "kind": "ranked_target",
        "rank": rank,
        "confidence": row["confidence"],
        # disease link
        "odds_ratio": float(best["odds_ratio"]),
        "fdr": float(best["p_adj_fdr"]),
        "program": str(best["gene_set"]),
        "cluster": int(best["cluster"]),
        "program_peers": peers,
        # network influence
        "controls_n_genes": controls,
        "percentile": percentile,
        "n_regulators": int(len(dist)),
        "median_out_degree": int(dist.median()),
        # experimental trust
        "kd_verified": bool(row["kd_verified"]),
        "offtarget_risk": bool(row["offtarget_risk"]),
        "n_conditions": len(conds),
        "n_conditions_verified": n_verified,
        # functional readout
        "th2_vs_th1_lfc": lfc,
        "polarization": polarization,
        # activation state
        "state_pattern": sp["state_pattern"] if sp else None,
        "state_summary": sp["summary"] if sp else None,
        "by_state": sp["by_state"] if sp else None,
        "peak_state": sp["peak_state"] if sp else None,
    }


def summary(disease: str, fdr: float = 0.05) -> dict:
    df = disease_targets(disease, fdr=fdr)
    if df.empty:
        return {"disease": disease, "n_candidates": 0, "n_high_confidence": 0, "top_targets": []}
    return {
        "disease": disease,
        "n_candidates": len(df),
        "n_high_confidence": int(df["confidence"].str.startswith("High").sum()),
        "top_targets": df["gene"].head(8).tolist(),
    }


if __name__ == "__main__":  # smoke test + demo-invariant check
    print(f"{len(list_diseases())} diseases available")
    for dz in ["Crohn's disease", "asthma", "rheumatoid arthritis"]:
        s = summary(dz)
        print(f"\n{dz}: {s['n_candidates']} candidates, {s['n_high_confidence']} high-confidence")
        df = disease_targets(dz, top=4)
        for _, r in df.iterrows():
            print(f"   {r['gene']:8} OR={r['disease_odds_ratio']:.1f}  "
                  f"controls {r['controls_n_genes']} genes  [{r['confidence']}]")

    # Lock the demo story: Crohn's -> STAT3 must stay the #1, high-confidence hit.
    ev = target_evidence("Crohn's disease", "STAT3")
    assert ev and ev["rank"] == 1, "REGRESSION: STAT3 is no longer the top Crohn's target"
    assert ev["confidence"].startswith("High"), "REGRESSION: STAT3 lost High confidence"
    assert ev["kd_verified"] and not ev["offtarget_risk"], "REGRESSION: STAT3 trust flags changed"
    # Activation-state layer: ITK must read as activation-induced (the demo beat).
    itk = state_profile("ITK")
    assert itk and itk["state_pattern"] == "activation-induced", "REGRESSION: ITK state pattern changed"
    print(f"✓ activation-state layer OK — ITK: {itk['summary']}")
    # Discovery: RA must surface druggable handles wired to its risk-gene modules.
    ra_mech = disease_mechanisms("rheumatoid arthritis")
    ra_handles = {h["gene"] for m in ra_mech for h in m["candidate_handles"]}
    assert ra_mech and {"DOT1L", "AHR", "GLS"} & ra_handles, "REGRESSION: RA discovery handles changed"
    print(f"✓ discovery OK — RA surfaces {len(ra_mech)} risk-gene modules; "
          f"handles incl {sorted({'DOT1L','AHR','GLS'} & ra_handles)}")
    print(
        f"\n✓ demo invariant OK — Crohn's #1 = STAT3: "
        f"OR {ev['odds_ratio']:.1f}, controls {ev['controls_n_genes']} genes "
        f"(top {100 - ev['percentile']:.1f}% of {ev['n_regulators']:,}), "
        f"{ev['n_conditions_verified']}/{ev['n_conditions']} conditions verified, "
        f"program peers {ev['program_peers']}"
    )
