"""
T-Cell Target Explorer — no-terminal UI for a bench immunologist.

Run:  streamlit run app.py
Pick a disease -> ranked candidate T-cell targets, each with its GRN influence
(how many genes it controls), a trust flag you can believe (knockdown verified?
off-target risk?), and its Th1/Th2 effect. Built on the Marson/Pritchard
genome-scale CD4+ T-cell Perturb-seq.
"""
import streamlit as st
import pandas as pd
from tcell_targets import list_diseases, disease_targets, target_evidence
from tcell_targets.core import regulator_detail

st.set_page_config(page_title="T-Cell Target Explorer", page_icon="🧬", layout="wide")

st.title("🧬 T-Cell Target Explorer")
st.caption(
    "Pick an immune disease → candidate CD4+ T-cell regulators to target, each with its "
    "**GRN influence** (how many genes it controls) and a **trust flag** (knockdown verified? "
    "off-target risk?) so you can believe the hit — no terminal, no bioinformatician. "
    "Built on the Marson/Pritchard genome-scale T-cell Perturb-seq."
)

with st.sidebar:
    st.header("Pick your question")
    diseases = list_diseases()
    disease = st.selectbox("Immune disease", diseases,
                           index=diseases.index("Crohn's disease") if "Crohn's disease" in diseases else 0)
    fdr = st.slider("Enrichment FDR cutoff", 0.001, 0.10, 0.05, 0.001, format="%.3f")
    hi_only = st.checkbox("High-confidence targets only", value=False)

df = disease_targets(disease, fdr=fdr)
if df.empty:
    st.warning(f"No disease-enriched T-cell programs for **{disease}** at FDR < {fdr:g}. "
               "Loosen the cutoff in the sidebar.")
    st.stop()
if hi_only:
    df = df[df["confidence"].str.startswith("High")].reset_index(drop=True)
    if df.empty:
        st.warning("No high-confidence targets at this cutoff. Uncheck the filter or loosen the FDR.")
        st.stop()

n_hi = int(df["confidence"].str.startswith("High").sum())
c1, c2, c3 = st.columns(3)
c1.metric("Candidate targets", len(df))
c2.metric("High-confidence", n_hi)
c3.metric("Top target", df.iloc[0]["gene"] if len(df) else "—")


# ---- the recommendation: full evidence case for the #1 target ----------------
def _confidence_pillar(ev: dict) -> tuple[str, str]:
    if ev["kd_verified"] and not ev["offtarget_risk"]:
        return "✅ Verified", f"{ev['n_conditions_verified']}/{ev['n_conditions']} conditions · clean guide"
    if ev["kd_verified"] and ev["offtarget_risk"]:
        return "⚠️ Off-target", f"verified in {ev['n_conditions_verified']}/{ev['n_conditions']} · off-target risk"
    return "❓ Unconfirmed", "knockdown not verified in the screen"


top_gene = df.iloc[0]["gene"]
ev = target_evidence(disease, top_gene, fdr=fdr)
if ev:
    with st.container(border=True):
        st.markdown(f"### 🎯 Recommended target for {disease}: **{ev['gene']}**")
        bits = ["the most disease-enriched T-cell program"]
        if ev["percentile"] is not None and ev["percentile"] >= 90:
            hub_pct = max(1, round(100 - ev["percentile"]))
            bits.append(f"a top-{hub_pct}% network hub")
        if ev["kd_verified"] and not ev["offtarget_risk"]:
            bits.append("a verified, clean CRISPRi knockdown")
        st.markdown(
            f"**{ev['gene']}** is the #1 candidate — " + ", ".join(bits[:-1]) +
            (f", and {bits[-1]}" if len(bits) > 1 else bits[0]) + "."
        )

        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Disease enrichment", f"{ev['odds_ratio']:.1f}",
                  f"odds ratio · FDR {ev['fdr']:.1e}", delta_color="off")
        if ev["controls_n_genes"] is not None:
            p2.metric("Genes it controls", f"{ev['controls_n_genes']:,}",
                      f"top {100 - ev['percentile']:.1f}% of {ev['n_regulators']:,} screened",
                      delta_color="off")
        else:
            p2.metric("Genes it controls", "—", "not directly perturbed", delta_color="off")
        val, sub = _confidence_pillar(ev)
        p3.metric("CRISPRi knockdown", val, sub, delta_color="off")
        if ev["polarization"]:
            p4.metric("T-helper skew", ev["polarization"],
                      f"Th2/Th1 log2FC {ev['th2_vs_th1_lfc']:+.2f}", delta_color="off")
        else:
            p4.metric("T-helper skew", "—", "no significant signature", delta_color="off")

        if ev["program_peers"]:
            peers = ", ".join(f"**{g}**" for g in ev["program_peers"][:4])
            st.caption(
                f"Its enriched program (cluster {ev['cluster']}) also contains {peers} — "
                "so the top hit sits with the program's known regulators, not alone. "
                "Enrichment, GRN out-degree, and knockdown QC are all precomputed by the "
                "dataset authors; this tool assembles them into one trust-ranked call."
            )

st.subheader(f"Candidate targets for **{disease}**")

def _pol(x):
    if pd.isna(x):
        return "—"
    return f"Th2 (+{x:.1f})" if x > 0 else f"Th1 ({x:.1f})"

view = df.assign(**{
    "Th1/Th2 effect": df["th2_vs_th1_lfc"].map(_pol),
    "disease OR": df["disease_odds_ratio"].round(1),
    "controls (genes)": df["controls_n_genes"],
    "FDR": df["p_adj_fdr"].map(lambda p: f"{p:.1e}"),
}).rename(columns={"gene": "Gene", "confidence": "Confidence"})

st.dataframe(
    view[["Gene", "Confidence", "disease OR", "controls (genes)", "Th1/Th2 effect", "FDR"]],
    width="stretch", hide_index=True,
)

st.download_button(
    "⬇️ Download this target report (CSV)",
    df.to_csv(index=False).encode(),
    file_name=f"tcell_targets_{disease.replace(' ', '_')}.csv",
    mime="text/csv",
)

# ---- drill into one regulator (the GRN evidence a bench scientist wants) ----
st.subheader("🔬 Inspect a regulator")
gene = st.selectbox("Regulator", df["gene"].tolist())
det = regulator_detail(gene)
if not det.get("perturbed"):
    st.info(f"{gene} appears as a downstream gene here, but was not itself directly perturbed in the screen.")
else:
    st.markdown(f"**{gene}** controls up to **{det['max_controls']:,} downstream genes** across conditions — "
                "its GRN out-degree (a proxy for how central a regulator it is).")
    st.table(pd.DataFrame(det["by_condition"]).T.rename(columns={
        "controls_n_genes": "controls (genes)", "n_up": "↑ up", "n_down": "↓ down",
        "kd_verified": "KD verified", "offtarget": "off-target",
    }))

with st.expander("How to read this / what the flags mean"):
    st.markdown(
        "- **Gene** — a T-cell regulator whose perturbation program is enriched in this disease's genetics.\n"
        "- **Confidence** — *High* = the gene's CRISPRi knockdown was verified on-target **and** the guide is clean; "
        "*Medium* = verified but off-target risk; *Low* = knockdown not confirmed; "
        "*Downstream only* = an affected gene, not itself directly perturbed.\n"
        "- **disease OR** — enrichment odds ratio of this gene's program in the disease gene set.\n"
        "- **controls (genes)** — GRN out-degree: how many downstream genes are significantly affected when it's perturbed.\n"
        "- **Th1/Th2 effect** — the gene's polarization signature (functional readout).\n\n"
        "*Upstream GRN inference, disease enrichment, and guide QC are precomputed by the dataset authors "
        "(Zhu, Dann, …, Pritchard, Marson 2025). This tool packages them into a trustworthy, self-serve "
        "target report — hypothesis generation, not a clinical claim.*"
    )
