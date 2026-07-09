"""
T-Cell Target Explorer — no-terminal UI for a bench immunologist.

Run:  streamlit run app.py
Pick a disease -> ranked candidate T-cell targets, each with a trust flag you can
actually believe (knockdown verified? off-target risk?) and its Th1/Th2 effect.
Built on the Marson/Pritchard genome-scale CD4+ T-cell Perturb-seq.
"""
import streamlit as st
import pandas as pd
from tcell_targets import list_diseases, disease_targets

st.set_page_config(page_title="T-Cell Target Explorer", page_icon="🧬", layout="wide")

st.title("🧬 T-Cell Target Explorer")
st.caption(
    "Pick an immune disease → candidate CD4+ T-cell regulators to target, each with a "
    "**trust flag** (was the knockdown verified? off-target risk?) so you can believe the hit — "
    "no terminal, no bioinformatician. Built on the Marson/Pritchard genome-scale T-cell Perturb-seq."
)

with st.sidebar:
    st.header("Pick your question")
    disease = st.selectbox("Immune disease", list_diseases(),
                           index=(list_diseases().index("Crohn's disease")
                                  if "Crohn's disease" in list_diseases() else 0))
    fdr = st.slider("Enrichment FDR cutoff", 0.001, 0.10, 0.05, 0.001, format="%.3f")
    hi_only = st.checkbox("High-confidence targets only", value=False)

df = disease_targets(disease, fdr=fdr)

if df.empty:
    st.warning(f"No disease-enriched T-cell programs for **{disease}** at FDR < {fdr:g}. "
               "Loosen the cutoff in the sidebar.")
    st.stop()

if hi_only:
    df = df[df["confidence"].str.startswith("High")]

n_hi = int(df["confidence"].str.startswith("High").sum())
c1, c2, c3 = st.columns(3)
c1.metric("Candidate targets", len(df))
c2.metric("High-confidence", n_hi)
c3.metric("Top target", df.iloc[0]["gene"] if len(df) else "—")

st.subheader(f"Candidate targets for **{disease}**")

def _pol(x):
    if pd.isna(x):
        return "—"
    return f"Th2 (+{x:.1f})" if x > 0 else f"Th1 ({x:.1f})"

view = df.assign(**{
    "Th1/Th2 effect": df["th2_vs_th1_lfc"].map(_pol),
    "disease OR": df["disease_odds_ratio"].round(1),
    "FDR": df["p_adj_fdr"].map(lambda p: f"{p:.1e}"),
}).rename(columns={"gene": "Gene", "confidence": "Confidence", "program": "Program"})

st.dataframe(
    view[["Gene", "Confidence", "disease OR", "FDR", "Th1/Th2 effect", "Program"]],
    use_container_width=True, hide_index=True,
)

st.download_button(
    "⬇️ Download this target report (CSV)",
    df.to_csv(index=False).encode(),
    file_name=f"tcell_targets_{disease.replace(' ', '_')}.csv",
    mime="text/csv",
)

with st.expander("How to read this / what the confidence flag means"):
    st.markdown(
        "- **Gene** — a T-cell regulator whose perturbation program is enriched in this disease's genetics.\n"
        "- **Confidence** — *High* = the gene's CRISPRi knockdown was verified effective **and** the guide is clean; "
        "*Medium* = verified but with off-target risk; *Low* = knockdown not confirmed; "
        "*Downstream only* = appears as an affected gene, not itself directly perturbed.\n"
        "- **disease OR** — odds ratio for enrichment of this gene's program in the disease gene set.\n"
        "- **Th1/Th2 effect** — the gene's polarization signature (functional readout).\n\n"
        "*Upstream GRN clustering, enrichment, and guide QC are precomputed by the dataset authors "
        "(Zhu, Dann, …, Pritchard, Marson 2025). This tool packages them into a trustworthy, "
        "self-serve target report.*"
    )
