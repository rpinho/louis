"""
Core logic for the T-Cell Target Explorer.

Turns the Marson/Pritchard genome-scale CD4+ T-cell Perturb-seq (Zhu, Dann, ...,
Pritchard, Marson 2025; CZI Virtual Cells Platform) into a self-serve
disease -> candidate-target workflow WITH a trust/rigor layer, for a bench
immunologist who does not want to touch a terminal or a bioinformatician.

The upstream science (GRN clustering + autoimmune-disease enrichment + guide QC)
is precomputed by the dataset authors. This tool's value is the LAST MILE:
- pick a disease -> ranked candidate T-cell regulators/targets,
- each annotated with a confidence flag derived from the guide knockdown
  efficiency and off-target metadata (so the user can trust the hit),
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
def load_kd() -> pd.DataFrame:
    return pd.read_csv(_path("kd"))


@lru_cache(maxsize=None)
def load_polarization() -> pd.DataFrame:
    return pd.read_csv(_path("polarization"))


@lru_cache(maxsize=None)
def load_sgrna() -> pd.DataFrame:
    return pd.read_csv(_path("sgrna"))


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


def _gene_from_guide(guide_id: str) -> str:
    """Guide ids look like 'STAT3-2' -> gene 'STAT3'."""
    return str(guide_id).rsplit("-", 1)[0]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def list_diseases() -> list[str]:
    return sorted(load_enrichment()["disease"].dropna().unique().tolist())


@lru_cache(maxsize=None)
def _kd_effective_genes() -> frozenset[str]:
    """Genes with at least one guide showing a significant knockdown."""
    kd = load_kd()
    eff = kd[kd["signif_knockdown"] == True]  # noqa: E712
    genes = {_gene_from_guide(g) for g in eff.iloc[:, 0]}
    return frozenset(genes)


@lru_cache(maxsize=None)
def _polarization_map() -> dict[str, float]:
    """gene -> Th2_vs_Th1 log2 fold change (significant only). >0 = Th2, <0 = Th1."""
    pol = load_polarization()
    sig = pol[pol["adj_p_value"] < 0.05]
    return dict(zip(sig["variable"], sig["log_fc"]))


@lru_cache(maxsize=None)
def _offtarget_risky_genes() -> frozenset[str]:
    """Target genes whose guide library flags a nearby non-target gene / bidirectional promoter."""
    sg = load_sgrna()
    risk = pd.Series(False, index=sg.index)
    if "nearest_within2kb_nontarget_gene_name" in sg:
        risk |= sg["nearest_within2kb_nontarget_gene_name"].notna()
    if "putative_bidirectional_promoter" in sg:
        risk |= sg["putative_bidirectional_promoter"] == True  # noqa: E712
    col = "target_gene_name" if "target_gene_name" in sg else "designed_target_gene_name"
    return frozenset(sg.loc[risk, col].dropna().astype(str).unique().tolist())


def _confidence(kd_effective: bool, offtarget: bool, perturbed: bool) -> str:
    if not perturbed:
        return "Downstream only (not directly perturbed)"
    if kd_effective and not offtarget:
        return "High — verified knockdown, clean guide"
    if kd_effective and offtarget:
        return "Medium — verified knockdown, off-target risk"
    return "Low — knockdown not confirmed"


def disease_targets(disease: str, fdr: float = 0.05, top: int | None = None) -> pd.DataFrame:
    """
    For a disease, return ranked candidate target genes with a trust/rigor layer.

    One row per candidate gene (deduped to its strongest disease-enriched program),
    annotated with knockdown-verification, off-target risk, a plain-English
    confidence flag, and the Th1/Th2 polarization effect.
    """
    enr = load_enrichment()
    hits = enr[(enr["disease"] == disease) & (enr["p_adj_fdr"] < fdr)].copy()
    if hits.empty:
        return pd.DataFrame()

    rows = []
    for _, r in hits.iterrows():
        for g in _parse_gene_list(r["intersecting_genes"]):
            rows.append({
                "gene": g,
                "disease_odds_ratio": float(r["odds_ratio"]),
                "p_adj_fdr": float(r["p_adj_fdr"]),
                "program": r["gene_set"],
                "cluster": int(r["cluster"]),
                "cluster_size": int(r["cluster_size"]),
            })
    df = pd.DataFrame(rows)
    # keep each gene's strongest (highest odds ratio) disease-enriched program
    df = df.sort_values("disease_odds_ratio", ascending=False).drop_duplicates("gene")

    kd_eff = _kd_effective_genes()
    offt = _offtarget_risky_genes()
    pol = _polarization_map()
    perturbed = frozenset(_gene_from_guide(g) for g in load_kd().iloc[:, 0])

    df["kd_verified"] = df["gene"].isin(kd_eff)
    df["offtarget_risk"] = df["gene"].isin(offt)
    df["th2_vs_th1_lfc"] = df["gene"].map(pol)
    df["confidence"] = [
        _confidence(k, o, g in perturbed)
        for g, k, o in zip(df["gene"], df["kd_verified"], df["offtarget_risk"])
    ]
    df = df.reset_index(drop=True)
    return df.head(top) if top else df


def summary(disease: str, fdr: float = 0.05) -> dict:
    df = disease_targets(disease, fdr=fdr)
    return {
        "disease": disease,
        "n_candidates": len(df),
        "n_high_confidence": int(df["confidence"].str.startswith("High").sum()) if len(df) else 0,
        "top_targets": df["gene"].head(8).tolist() if len(df) else [],
    }


if __name__ == "__main__":  # tiny smoke test
    print(f"{len(list_diseases())} diseases available")
    for dz in ["Crohn's disease", "asthma", "rheumatoid arthritis"]:
        s = summary(dz)
        print(f"\n{dz}: {s['n_candidates']} candidates, "
              f"{s['n_high_confidence']} high-confidence -> {s['top_targets'][:6]}")
