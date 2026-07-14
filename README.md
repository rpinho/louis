<p align="center">
  <img src="docs/louis.png" width="150" alt="Louis — a CD4+ T-cell target detective">
</p>

# 🔎 Louis

*A CD4+ T-cell target detective — named for Louis Pasteur (pronounced "Louie"; like Claude, a French name): **nothing trusted until it's verified.** Grounded in the Marson/Pritchard genome-scale CD4+ T-cell Perturb-seq screen.*

**Ask Louis to discover novel, druggable CD4+ T-cell drug targets for an autoimmune disease — grounded in a real CRISPR screen, validated against the scientific web AND the field's live community signal, and remembered in a shared lab knowledge base.**

An **MCP server**: no separate app, no API key, no metered credits. You talk to Claude the way you already do; this server grounds every answer in the **Marson/Pritchard genome-scale CD4+ T-cell Perturb-seq** (Zhu, Dann, …, Pritchard, Marson 2025; [preprint](https://www.biorxiv.org/content/10.64898/2025.12.23.696273v1) · [CZI Virtual Cells Platform](https://virtualcellmodels.cziscience.com/dataset/genome-scale-tcell-perturb-seq)) — disease enrichment, gene-network influence, CRISPRi knockdown QC, and activation-state dependence.

*Built for the Built with Claude: Life Sciences hackathon (Builder track).*

<p align="center">
  <b><a href="https://claude.ai/code/artifact/b4a412b5-2eeb-4447-992c-0771fad5398c">🌐 Try Louis live</a> &nbsp;·&nbsp; <a href="https://github.com/rpinho/louis/blob/main/demo/README.md">🎥 The 3-minute demo</a> &nbsp;·&nbsp; <a href="#install--three-ways-to-use-louis">Install</a></b>
</p>

> **✓ Blind positive control.** Told only a disease's GWAS risk genes — *no* known targets — Louis re-derives the textbook **Th17 master-regulator triad STAT3 · BATF · IRF4** as its top-3 blind candidates for the core inflammatory diseases (the validated Th17 network core, Ciofani et al., *Cell* 2012). **1 of 77 regulator clusters clears significance, and the top hit survives a global BH correction across all 1,309 tests (Crohn's q=0.025) — disease-calibrated, dark in RA/SLE/T1D, not a hub.** This calibrates the *method*; it **licenses no single pick** — every novel lead still earns its own grade on its own evidence. Reproduce in one command: `python scripts/positive_control.py` ([details](#what-it-found--validated-across-9-diseases)).

---

<p align="center">
  <img src="docs/figures/opportunity_map.png" width="92%" alt="The opportunity map — every lead plotted by trust grade (y-axis) against novelty (x-axis, PubMed papers for that gene × disease × CD4 T cell). The green top-left corner holds the novel, well-founded survivors (HDAC7-UC highlighted, RASA2, HIF1A, DOCK2); DOT1L (RA) sits at C — the stress-tested former flagship, not a green-corner win; IL21R / STAT3 / ZAP70 / AHR sit right as validated-but-crowded.">
</p>
<p align="center"><em><b>The whole board in one picture.</b> Ask Louis <em>“what are your grade-A leads across all diseases?”</em> and it plots every lead by <b>trust grade</b> (how good) × <b>novelty</b> (how understudied, in T cells). A database sends you to the crowded right; Louis is built for the <b>green corner</b>. <a href="#what-it-found--validated-across-9-diseases">Full read-out ↓</a></em></p>

## The problem (a real one)

That screen perturbed **every gene in primary human CD4+ T cells** and mapped which regulators drive which programs, and which programs are enriched in autoimmune-disease genetics — i.e. **candidate drug targets**. But the hardest thing in biology isn't the analysis; it's getting a bench scientist to actually *use* a dataset like this. It lives behind AnnData objects and a bioinformatician. A wet-lab immunologist who just wants *"what should I target for Crohn's, and can I trust it?"* can't self-serve it — and won't touch a new website to try.

So don't make one. **Meet them where they already are: inside Claude.**

## What it does

Add the server to Claude, then just ask. It does four things — **discover, validate, listen, remember** — grounded in the screen and trust-verdict first.

**Discover** — not the obvious target, the novel one:
> **You:** *For rheumatoid arthritis, skip the obvious targets — find understudied, druggable handles wired to the disease's own risk genes.*
>
> **Claude** *(via the MCP)*: **DOT1L** — an epigenetic enzyme (pinometostat is in the clinic) — co-clusters with a module carrying the RA risk genes **IL21R** and **PTGER4** in *resting* T cells, knockdown verified clean. **GLS** (glutaminase) sits over a **PTPN22 / TRAF1** module in *activated* cells. Mechanistic, testable leads — candidate handles to *validate*, and the regulator→risk-gene links exist in **no external database**, only in this screen. *(DOT1L is Louis's flagship — and, once validated, exactly the lead it stress-tests; see below.)*

**Validate — and stress-test** — hand the leads to Claude Science's scientific web (Open Targets, ChEMBL, PubMed, GWAS Catalog), **weigh every source by provenance**, and turn the trust machinery on the call itself. In our run Claude Science first ranked **DOT1L** the top novel RA lead — then, driving Louis's own skill, it **stress-tested that call and downgraded DOT1L A→C**: the regulator→risk-gene "wiring" is a non-significant cross-disease-union artifact (DOT1L isn't in RA's own regulator set) — that engine-verified artifact is the load-bearing kill. The *direction* is a genuine open question: DOT1L supports Tregs (an inhibitor might *worsen* RA), but it also sustains pathogenic effector programs (Scheer 2020) — a preprint-grade risk Louis's own **reviewer** flags to *test*, not a claim. A discovery tool that kills its own flagship, with receipts, is the product.

**Listen** — take the engine's own discoveries (every handle + risk gene) and search **X/Twitter** for each, in an immune context: what labs, journals, and news desks are saying *this week*, before it's a paper. Wellness noise is vetoed; gene symbols self-filter (nobody but immunologists tweets "PTPN22"). Our data flagged **DOT1L**, a methyltransferase, for RA — and the listen layer independently surfaced **@ACR_Journals** the same week on **DNMT3A**, *another* methyltransferase in autoreactive CD4+ T cells reducing RA joint inflammation. Convergent, current, and surfaced from the field's live chatter — not a literature search. This runs live where X access exists, and is **baked into the KB** so it ships everywhere.

**Remember** — the knowledge base files the whole chain with provenance *and confidence level*; `kb_recall(DOT1L)` returns discovery + novelty + validation + community signal + verdict in one shareable profile, so it's never re-derived.

> **See it converge:** [a visual target dossier for DOT1L](docs/dot1l-dossier.html) — six sources ranked by confidence, and the two (X/Twitter + a conference abstract) that sit off Claude Science's allowlist.

Underneath it all, the **trust flag** — the difference between a hit worth bench time and one that wastes it:
> **You:** *For Crohn's, what should I target, and which can I trust?*
>
> **Claude**: **STAT3** — verified clean knockdown, top-1% network hub. ⚠️ **IPMK** sits in the *same* program with the *identical* enrichment, but its knockdown was never confirmed — enrichment alone would rank it a co-top hit; don't spend bench time on it.

The tools (all grounded, no LLM guessing):

| Tool | Returns |
|---|---|
| `disease_mechanisms` | **discovery** — druggable handles wired to a disease's risk-gene modules, per activation state |
| `disease_targets` | ranked candidates + OR, GRN influence, **trust flag**, activation state, Th1/Th2 |
| `target_evidence` | the full "why this target" case for one gene |
| `regulator_detail` · `state_profile` | per-condition GRN + CRISPRi QC · activation-state trajectory |
| `community_signal` | **listen** — recent X/Twitter chatter (labs/journals first) about a gene or disease, pre-paper |
| `kb_recall` · `kb_remember` · `kb_remember_signal` · `kb_verdict` | the **knowledge base** — recall before deriving, file findings + community signal with provenance, record verdicts |
| `list_diseases` | the 17 autoimmune diseases in the screen |

## Install — three ways to use Louis

**Meet the scientist where they already work — don't make them come to you.** A tool that's *another website* is a tax: one more URL to remember, one more workflow to abandon, a tab nobody keeps open. So Louis isn't a website. It's **one engine + one shared memory** wearing whatever surface you already live in — a **skill** in Claude Science, an **MCP server** in Claude Code, a **bot** in Slack. Same brain, same memory, three front doors. Pick the one that fits:

| Surface | Best for | Setup |
|---|---|---|
| **MCP server** | Louis inside **Claude Code / Claude Desktop** | §A below (~2 min) |
| **Skill** | Louis inside **Claude Science / Claude** (composes with its scientific-web connectors) | §B below → [`skill/INSTALL.md`](skill/INSTALL.md) |
| **Slack bot** | Louis shared with a **whole lab** in a channel | §C below → [`slack/SETUP.md`](slack/SETUP.md) |

First get the code + data (all three build from this):

```bash
git clone https://github.com/rpinho/louis && cd louis
python3 -m venv .venv && source .venv/bin/activate
pip install -e .                      # core engine + MCP server + CLIs
python scripts/download_data.py       # small public tables (~34 MB), MIT
python -m louis.core                  # sanity check — asserts the Crohn's→STAT3 demo invariant
```

### A) MCP server — Claude Code / Claude Desktop

**Claude Code** — the repo ships a `.mcp.json`, so open the project and approve the `louis` server (or `claude mcp add louis -- .venv/bin/louis-mcp`). Then ask.

**Claude Desktop** — either **one-click**: `python scripts/build_mcpb.py` → open the resulting `dist/louis.mcpb` in Claude Desktop; **or** add to `claude_desktop_config.json` (the editable install makes the path stable):

```json
{ "mcpServers": { "louis": { "command": "/ABSOLUTE/PATH/louis/.venv/bin/louis-mcp" } } }
```

Restart Claude, then ask: *"Using louis, what should I target for rheumatoid arthritis, and which are verified?"*

### B) Skill — Claude Science / Claude

Package Louis (engine + dataset + validated KB) into one self-contained skill that runs *inside* Claude's own compute and composes with its scientific-web connectors:

```bash
python scripts/build_skill.py         # -> dist/louis-skill.zip  (self-contained, <200 files)
```

Then in Claude (**Science**, **Desktop**, or **claude.ai**) → **Skills** → **Create / Upload a skill** → choose `dist/louis-skill.zip`. It reads `name: louis` from `SKILL.md` and is ready — ask *"Using my Louis skill, what should I target for asthma?"* Full walkthrough + gotchas (file-count cap, the fresh-create tip): **[`skill/INSTALL.md`](skill/INSTALL.md)**.

### C) Slack bot — share it with a lab

Put Louis where a lab already talks. Socket Mode — no hosting, no public URL:

```bash
pip install -e ".[slack]"             # adds slack-bolt
# create the app + set SLACK_BOT_TOKEN / SLACK_APP_TOKEN — see slack/SETUP.md
louis-slack                            # starts the bot
```

`@louis what should we hit for RA?` in a public channel returns trust-ranked leads + community signal; `/remember` files to the shared KB. Full setup (~3 min) + the paste-to-create app manifest: **[`slack/SETUP.md`](slack/SETUP.md)**.

## What makes it more than a lookup

Four things, none of which a literature search can give you — because they live in the assay and in the screen's network structure, not the papers:

- **Mechanistic discovery.** The screen's gene-regulatory clusters carry *both* their regulators and their downstream genes, so `disease_mechanisms` wires a druggable **handle** to the disease's own risk-gene **module**, in a specific state — "perturb DOT1L to move the RA IL21R/PTGER4 program in resting cells." That's a testable hypothesis, and the edge exists in no external database. (Module-level co-cluster — a candidate controller to *test*, not a proven gene-level edge; those need the full `.h5ad`.)
- **Trust flag.** From the screen's own QC — was the CRISPRi **knockdown verified on-target**, and is the guide **off-target**? This is what stops you spending months on a hit that only *looks* good (see IPMK above).
- **Activation state.** A T cell's regulators shift with its state; the screen measured three (Rest / Stim8hr / Stim48hr) and ~87% of hub regulators change ≥2× across them. The server surfaces which state a target acts in — the state-dependence a bench immunologist otherwise needs a whole experiment to read. (The **three measured states**, not modeling unmeasured ones.)
- **A shared, learning knowledge base.** `kb_recall / kb_remember / kb_verdict` maintain a git-tracked markdown KB (a target profile is a reputation record: data facts + novelty + validation + the scientist's verdict, each with provenance). Recall before deriving; file findings back so nothing is re-derived. And it's **two-way and shared**: a labmate can correct Louis in Slack — *"we tested it, the edge didn't hold"* — and he files it **attributed to them**, for the whole lab. Provenance-scoped flags (`--nolab`, `--exclude <tier>`, `--nomem`) dial exactly which knowledge he draws on. Hand the whole thing to a student.
- **The off-allowlist layer — social + conference.** `community_signal` turns the engine's own discoveries into search terms and reads what immunologists are *saying* about each lead — on **X** and on the **conference floor** (ACR/EULAR abstracts). This is the one layer Claude Science structurally can't reach: its sandbox is a strict domain **allowlist** (PubMed, bioRxiv, ChEMBL, Open Targets are on it — Twitter and conference-abstract sites are **not**). So the papers and preprints it already has; what it's missing is what the field is saying *around* them — before, beyond, and sometimes instead of publication. Curated (labs/journals first, wellness vetoed) and baked into the KB, so it ships even inside that sandbox.
- **Provenance-tiered trust + a self-reviewer.** Sources are not equal, and a weaker one can never decide a grade. Louis **weighs every claim by provenance** — the screen/engine facts, peer-reviewed papers, clinical trials and GWAS are *load-bearing*; a **preprint or conference abstract is hypothesis-strength** (it can flag a risk to test, never decide a grade); X/Bluesky chatter is *signal only*. And it **reviews itself**: before committing a verdict it flags any grade resting on weak provenance — *"⚠ Reviewer: this rests on a preprint — verify before an irreversible call"* — the Claude Science reviewer rebuilt for when you're on Slack and lose it. This is why Louis could downgrade its own DOT1L flagship *without over-trusting the preprint that raised the concern*: it weighs the source, it doesn't just cite it. (`evidence_strength` in `louis/kb_index.py`; the reviewer rule in `louis/assistant.py`.)

## What it found — validated across 9 diseases

Louis's own skill was run *inside Claude Science* across **nine autoimmune diseases** — RA, SLE, Crohn's, MS, UC, psoriasis, type-1 diabetes, asthma, atopic eczema — each candidate pressure-tested against Open Targets / ChEMBL / GWAS Catalog / PubMed / ClinicalTrials, graded A–D, and written back to the KB. What came out:

**First — the sanity check.** Before trusting a single *novel* pick, does the engine recover what's already *known*? Told only each disease's GWAS risk-gene modules and **no known targets**, Louis's blind top-3 for the core inflammatory diseases is the textbook **Th17 master-regulator triad — STAT3 · BATF · IRF4** (the validated Th17 network core, Ciofani et al., *Cell* 2012) — and only **1 of 77 regulator clusters clears significance** (the top hit survives a global BH across all 1,309 tests, Crohn's q=0.025; dark in RA/SLE/T1D):

| Disease | Louis's blind top-3 (no known targets given) | |
|---|---|---|
| Crohn's · IBD · atopic eczema | **STAT3 · BATF · IRF4** | ✓ the exact Th17 triad |
| Multiple sclerosis | **STAT3 · BATF** · EGR2 | STAT3 #1 |
| Psoriasis | **STAT3 · IRF4** · IPMK | STAT3 #1 |

The **same unsupervised ranking** that re-derives these known masters is the one that surfaces the novel handles — but recovering the known **calibrates the *method*, not any single pick**: it licenses no novel lead, each still earns its own grade (calibrating the ruler doesn't measure the object). Reproduce every number in one command: `python scripts/positive_control.py`. *(Honest boundary: this is a recovery sanity check, not a held-out predictive AUROC; RA / SLE / UC surface EGR2 — a bona-fide tolerance regulator — at #1, so the control reads cleanest in the Th17-cytokine diseases.)*

**Then — the novel leads** the same engine surfaces, mapped by grade × novelty:

<p align="center">
  <img src="docs/figures/opportunity_map.png" width="94%" alt="The opportunity map — candidate grade vs novelty. The green top-left corner holds the novel, well-founded survivors (HDAC7-UC highlighted, RASA2, HIF1A, DOCK2); DOT1L (RA) sits at C — the stress-tested flagship, not a green-corner win; IL21R/STAT3/ZAP70/AHR sit right as validated-but-crowded.">
</p>

**The whole thesis in one picture:** candidate **grade** (how good a lead) against **novelty** (how understudied this gene is *for this disease, in T cells*). A database hands you the crowded right side; Louis is built for the **green corner** — high-grade *and* barely in the literature: **HDAC7 (the survivor lead), RASA2, HIF1A** land there. **DOT1L is the cautionary tale, not a green-corner win** — Louis stress-tested its own former flagship down to a **C** (the RA wiring is a cross-disease artifact; the direction is an open bench question), and the map plots it there honestly. The known genes (IL21R, STAT3, ZAP70, AHR) sit right, validated but crowded; DOCK2 is real whitespace still maturing; INSR is the screen honestly grading its own artifact a D. Every point traces to a connector-checked verdict — regenerate it with `python scripts/opportunity_map.py`.

- **Novel leads a database wouldn't hand you** — **HDAC7** (Th17-driven colitis, favorable peer-reviewed direction), **DOCK2** (a Rac-GEF whose autoimmune-CD4 role Bluesky independently corroborated the *same week* — the Waggoner Lab's "TCR–SUB1–DOCK2 axis promotes autoimmunity"), **PPM1D** (asthma + eczema, with a tool inhibitor), **RASA2** (eczema — best genetics of the set, honestly flagged as undruggable today). And the one Louis **stress-tested off the board**: **DOT1L** (RA) — genuinely novel, but its wiring is a cross-disease artifact and its direction an open bench question, so Louis downgraded *its own flagship* A→C.
- **It refuses to overclaim.** Asked whether the recurring "epigenetic axis" (DOT1L/HDAC7/MEN1) is one pan-autoimmune *mechanism*, Louis says **no** — the recurrence is *module-conservation* on shared GWAS hubs (ETS1/IRF8/BACH2/CD28/PTPN22…), not convergent regulation. Refusing the flashy overclaim is the credible answer.
- **Two disjoint conserved axes.** The Th1/Th17 diseases share one module-set; the Th2/allergic diseases (asthma + eczema) share a *different* one — a PPM1D/METAP2 type-2-cytokine hub — with metabolic GLS the only cross-over.

<p align="center">
  <img src="docs/figures/pan_autoimmune_synthesis.png" width="47%" alt="Pan-autoimmune synthesis — recurrence is module-conserved, not one mechanism">
  &nbsp;
  <img src="docs/figures/th2_conserved_hub.png" width="47%" alt="A Th2-conserved hub (PPM1D/METAP2) across asthma and eczema; GLS is the lone Th1/Th17 bridge">
</p>

And it designs the bench experiment. Ask Louis to *test* a lead and it returns a real two-arm protocol — CRISPRi knockdown + a selective inhibitor, sgRNA-resistant/catalytic-dead rescue controls, a mandatory direction-of-effect gate — on the screen's own activation-state axis:

<p align="center">
  <img src="docs/figures/hdac7_experiment_schematic.png" width="80%" alt="HDAC7 UC experiment: two-arm design + cheap-gate-first go/no-go">
</p>

## Extending Louis — connect your lab's stack

Louis is a lab *assistant*, not a closed tool. Because he's an **MCP server + a tool-using agent**, teaching him a new capability is teaching him a new *tool* — the same way he already composes with Claude Science's Open Targets / ChEMBL / GWAS connectors. Two paths:

**1. Compose via MCP — zero code.** Point Claude at any MCP server your lab runs — an ELN, a LIMS, an inventory or results DB — and it reasons over that data *and* Louis's screen in one conversation. The validation layer already works exactly this way (Louis's discovery + Claude Science's scientific-web connectors).

**2. Add a tool to Louis — ~20 lines.** Give him a new endpoint with one entry in `TOOLS` (`louis/assistant.py`) and a case in `_dispatch`. That's literally how the shared-memory writes were added — the whole pattern:

```python
# louis/assistant.py — 1) declare the tool
{
  "name": "lab_inventory",
  "description": "Check whether a reagent/antibody is in the lab's stock.",
  "input_schema": {"type": "object", "properties": {"item": {"type": "string"}}, "required": ["item"]},
},
# 2) dispatch it — your endpoint; key in .secrets/, like the Slack/Anthropic ones
if name == "lab_inventory":
    return _clean(requests.get(f"{LAB_API}/stock", params={"q": args["item"]},
                               headers={"Authorization": os.environ["LAB_API_KEY"]}).json())
```

Now *"is our anti-DOT1L antibody in stock, and is it still worth ordering?"* composes the lab's inventory with the screen data, the KB, and the field signal — one assistant over your whole lab stack.

## Optional: local visual browser

A Streamlit UI (disease dropdown → ranked table → evidence panel → per-state chart → CSV) is included for a visual, click-through view of the same data:

```bash
pip install -e ".[app]" && streamlit run app.py   # → http://localhost:8501
```

![The optional Streamlit browser — Crohn's → STAT3 with the evidence panel and activation-state layer](docs/screenshot.png)

## Data

Uses the authors' **precomputed** supplementary tables (auto-downloaded): cluster↔disease enrichment, per-perturbation DE stats (with `n_downstream` = GRN out-degree, per `culture_condition`), guide knockdown efficiency, sgRNA off-target library, Th1/Th2 signature. The full ~22M-cell AnnData is **not** required. Those tables are distributed by the study authors under the MIT License via their public analysis repo; this project re-uses them and does not redistribute the underlying single-cell data.

## Scope / honesty

17 autoimmune diseases, 185 significant disease↔program links. This surfaces and *trust-ranks* candidate targets from a published dataset — hypothesis generation and prioritization for a bench scientist, **not** a validated clinical claim. Confidence flags reflect experimental QC of the CRISPRi perturbation, not therapeutic efficacy.

*License: [MIT](LICENSE). New code written for the hackathon; public dataset.*
