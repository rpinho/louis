"""
T-Cell Target Explorer — no-terminal target-discovery tool for a bench immunologist.

Run:  streamlit run app.py
Ask, in plain English, what to target for an immune disease — Claude answers by
reasoning over the CRISPR screen's own evidence (disease enrichment, GRN influence,
knockdown QC), trust-verdict first. Or browse the ranked, trust-flagged targets
directly. Built on the Marson/Pritchard genome-scale CD4+ T-cell Perturb-seq.
"""
import os
import streamlit as st
import pandas as pd
import altair as alt
from tcell_targets import list_diseases, disease_targets, target_evidence, state_profile
from tcell_targets.core import regulator_detail
from tcell_targets import assistant

st.set_page_config(page_title="T-Cell Target Explorer", page_icon="🧬", layout="wide")

st.title("🧬 T-Cell Target Explorer")
st.caption(
    "**Ask what to target for an immune disease and get a grounded, trust-ranked answer** — Claude "
    "reasons over the screen's own evidence (disease enrichment, GRN influence, CRISPRi knockdown QC) "
    "and leads with whether you can believe the hit. Or browse the ranked targets below. "
    "Built on the Marson/Pritchard genome-scale T-cell Perturb-seq."
)

with st.sidebar:
    st.header("Pick your question")
    diseases = list_diseases()
    disease = st.selectbox("Immune disease", diseases,
                           index=diseases.index("Crohn's disease") if "Crohn's disease" in diseases else 0)
    fdr = st.slider("Enrichment FDR cutoff", 0.001, 0.10, 0.05, 0.001, format="%.3f")
    hi_only = st.checkbox("High-confidence targets only", value=False)
    st.divider()
    env_key = os.environ.get("ANTHROPIC_API_KEY", "")
    api_key = env_key or st.text_input(
        "Anthropic API key", type="password",
        help="Enables the Ask panel. Or set ANTHROPIC_API_KEY in the environment before launching.")
    st.caption("✅ Key loaded from environment." if env_key else
               "🔑 Add a key to enable natural-language Q&A.")


# ============================ Ask the screen (the tool) ============================
st.subheader("💬 Ask the screen")
st.caption("Plain-English questions, answered from the screen's own data — recommendation and trust verdict first.")

if "chat_display" not in st.session_state:
    st.session_state.chat_display = []      # [{role, content, trace?}] for rendering
    st.session_state.chat_messages = []     # full API history (incl. tool calls)

EXAMPLES = [
    "What should I target for Crohn's, and which hits can I actually trust?",
    "Which Crohn's targets look enriched but aren't validated?",
    "Compare STAT3 vs IPMK for Crohn's — why prefer one?",
]
picked = None
for col, ex in zip(st.columns(len(EXAMPLES)), EXAMPLES):
    if col.button(ex, use_container_width=True, disabled=not api_key):
        picked = ex

with st.form("ask", clear_on_submit=False):
    typed = st.text_input("Your question", placeholder="e.g. Which asthma targets are high-influence and verified?",
                          label_visibility="collapsed", disabled=not api_key)
    submitted = st.form_submit_button("Ask", type="primary", disabled=not api_key)

if not api_key:
    st.info("Add your Anthropic API key in the sidebar to turn on the Ask panel. "
            "The browsable target report below works without it.")

# render conversation so far
def _render_trace(trace):
    if trace:
        with st.expander("🔎 evidence Claude queried to answer this"):
            for nm, inp in trace:
                st.caption(f"`{nm}` &nbsp; {inp}")

for turn in st.session_state.chat_display:
    with st.chat_message(turn["role"]):
        st.markdown(turn["content"])
        _render_trace(turn.get("trace"))

question = (typed.strip() if (submitted and typed.strip()) else None) or picked
if question and api_key:
    st.session_state.chat_display.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        try:
            with st.spinner("Reasoning over the screen…"):
                text, trace, messages = assistant.answer(
                    question, st.session_state.chat_messages, api_key=api_key)
            st.markdown(text)
            _render_trace(trace)
            st.session_state.chat_messages = messages
            st.session_state.chat_display.append({"role": "assistant", "content": text, "trace": trace})
        except Exception as e:
            st.session_state.chat_display.pop()  # drop the user turn we just added
            st.error(f"Q&A failed: {type(e).__name__}: {e}")

st.divider()


# ============================ Browse the underlying evidence ============================
st.subheader("🔬 Browse the trust-ranked report")
st.caption("The same evidence the Ask panel reasons over — pick a disease in the sidebar.")

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
        with p1:
            st.metric("Disease enrichment", f"{ev['odds_ratio']:.1f}")
            st.caption(f"odds ratio · FDR {ev['fdr']:.1e}")
        with p2:
            if ev["controls_n_genes"] is not None:
                st.metric("Genes it controls", f"{ev['controls_n_genes']:,}")
                st.caption(f"top {100 - ev['percentile']:.1f}% of {ev['n_regulators']:,} screened")
            else:
                st.metric("Genes it controls", "—")
                st.caption("not directly perturbed in the screen")
        with p3:
            val, sub = _confidence_pillar(ev)
            st.metric("CRISPRi knockdown", val)
            st.caption(sub)
        with p4:
            if ev["polarization"]:
                st.metric("T-helper skew", ev["polarization"])
                st.caption(f"Th2/Th1 log2FC {ev['th2_vs_th1_lfc']:+.2f}")
            else:
                st.metric("T-helper skew", "—")
                st.caption("no significant signature")

        if ev.get("state_summary"):
            st.markdown(
                f"🔄 &nbsp;**Activation state — {ev['state_pattern']}.** {ev['gene']} "
                f"{ev['state_summary']}. *(A T cell's regulators shift with its activation state; "
                "the screen measured Rest → Stim8hr → Stim48hr — the state-dependence bench "
                "immunologists usually can't read without re-running the experiment.)*"
            )

        if ev["program_peers"]:
            peers = ", ".join(f"**{g}**" for g in ev["program_peers"][:4])
            st.caption(
                f"Its enriched program (cluster {ev['cluster']}) also contains {peers} — "
                "so the top hit sits with the program's known regulators, not alone. "
                "Enrichment, GRN out-degree, and knockdown QC are all precomputed by the "
                "dataset authors; this tool assembles them into one trust-ranked call."
            )

def _pol(x):
    if pd.isna(x):
        return "—"
    return f"Th2 (+{x:.1f})" if x > 0 else f"Th1 ({x:.1f})"

view = df.assign(**{
    "Th1/Th2 effect": df["th2_vs_th1_lfc"].map(_pol),
    "disease OR": df["disease_odds_ratio"].round(1),
    "controls (genes)": df["controls_n_genes"],
    "activation state": df["state_pattern"].fillna("—"),
    "FDR": df["p_adj_fdr"].map(lambda p: f"{p:.1e}"),
}).rename(columns={"gene": "Gene", "confidence": "Confidence"})

st.dataframe(
    view[["Gene", "Confidence", "disease OR", "controls (genes)", "activation state", "Th1/Th2 effect", "FDR"]],
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
    sp = state_profile(gene)
    if sp and sp["state_pattern"] != "minimal":
        st.markdown(f"🔄 **Activation-state pattern: {sp['state_pattern']}** — {sp['summary']}.")
        order = [s for s in ("Rest", "Stim8hr", "Stim48hr") if sp["by_state"].get(s) is not None]
        cdf = pd.DataFrame({"activation state": order,
                            "genes controlled": [sp["by_state"][s] for s in order]})
        chart = (alt.Chart(cdf).mark_bar(color="#0d9488", size=90)
                 .encode(x=alt.X("activation state:N", sort=order, title=None,
                                 axis=alt.Axis(labelAngle=0)),
                         y=alt.Y("genes controlled:Q", title="genes controlled"),
                         tooltip=["activation state", "genes controlled"])
                 .properties(width="container", height=260))
        st.altair_chart(chart, use_container_width=True)
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
        "target report and a grounded Q&A layer — hypothesis generation, not a clinical claim.*"
    )
