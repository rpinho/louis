# KB conventions — the tool's memory

A cumulative, shareable knowledge base so the agent stops re-deriving the same thing
every session. Structure adapted from a mature personal-wiki PKM.

## Structure

- **`raw/`** — immutable evidence, by source (provenance). Fetched PubMed abstracts,
  Claude Science outputs, dataset extracts. Never edited; only appended to.
- **`wiki/`** — synthesized knowledge, by domain. One-to-many (a page compiles many sources):
  - `wiki/targets/<GENE>.md` — the **target profile**: data facts (trust / GRN / activation
    state), novelty assessment (literature-graded), mechanism (which disease modules /
    risk genes it's wired to), and the **scientist's verdicts** — each with provenance.
    A target profile is a reputation record: it accrues a track record over time.
  - `wiki/diseases/<disease>.md` — the compiled target landscape for a disease.
  - `wiki/modules/cluster-<id>.md` — GRN module profiles.
- **`index.md`** — master index (read this first when recalling).
- **`log.md`** — append-only record of derivations, findings, verdicts.
- **`state.md`** — open hypotheses under investigation, the current shortlist.

## Rules (carried over verbatim from the source PKM)

- **Full routing, no lazy dumping.** Every finding goes to its own *specific* profile — the
  specific gene, the specific disease — never a catch-all monitoring section.
- **Provenance is sacred.** Every claim cites its source (dataset table, PMID, Claude Science
  session, or the scientist) and its date.
- **Recall before derive.** Read the KB (`kb_recall`) before re-computing. File every new
  synthesis back (`kb_remember`) so it's never re-derived.
- **Filename hygiene.** ASCII only — no unicode, emoji, arrows, or em dashes in filenames.
- **The KB is the novelty layer's memory.** "STAT3 is obvious / GLS is emerging / RIPK1 is a
  known drug-target class" are facts that live here, so novelty isn't re-assessed each time.

## Why markdown + git

It's shareable and auditable: hand the KB to a student or a lab, diff what changed, and the
accumulated knowledge (what's known, what's novel, what the scientist judged) travels with it.
