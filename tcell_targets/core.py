"""
Core logic for the T-Cell Target Explorer.

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


@lru_cache(maxsize=None)
def _polarization_map() -> dict[str, float]:
    """gene -> Th2_vs_Th1 log2 fold change (most significant row). >0 = Th2, <0 = Th1."""
    pol = load_polarization()
    sig = pol[pol["adj_p_value"] < 0.05].sort_values("adj_p_value")
    sig = sig.drop_duplicates("variable", keep="first")  # most significant row per gene
    return dict(zip(sig["variable"], sig["log_fc"]))


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
    perturbed = set(grn.index)
    df["confidence"] = [
        _confidence(k, o, g in perturbed)
        for g, k, o in zip(df["gene"], df["kd_verified"], df["offtarget_risk"])
    ]
    # rank: disease enrichment first, then GRN influence as a tie-breaker
    df = df.sort_values(["disease_odds_ratio", "controls_n_genes"],
                        ascending=[False, False]).reset_index(drop=True)
    return df.head(top) if top else df


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
        return None
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

    return {
        "disease": disease,
        "gene": gene,
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
    print(
        f"\n✓ demo invariant OK — Crohn's #1 = STAT3: "
        f"OR {ev['odds_ratio']:.1f}, controls {ev['controls_n_genes']} genes "
        f"(top {100 - ev['percentile']:.1f}% of {ev['n_regulators']:,}), "
        f"{ev['n_conditions_verified']}/{ev['n_conditions']} conditions verified, "
        f"program peers {ev['program_peers']}"
    )
