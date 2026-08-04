---
id: lineage-business-descriptions
ts: 2026-08-04T00:30:00Z
type: procedural
scope: workspace
source: session:a77891ac
tags: [atomic, lineage, elementlogic, metaatomic, semantic-model, llm, ollama, documentation]
status: distilled
description: "lineage_engine.describe - derives business descriptions for semantic columns/measures FROM the lineage (not names); fingerprinted store so scheduled re-runs regenerate only what changed; local Ollama backend by default so customer metadata never leaves the network"
---

`lineage_engine/describe.py` turns the lineage store into plain-English
`business_description` text for every **non-hidden** semantic column and measure.
Built for Element Logic; portable to any Atomic customer (moves with the engine to
`own/MetaAtomic`, ADR 0009).

**Evidence, never the name.** A column contributes its whole chain back to source with
only *non-trivial* transformations named (92.5% of column hops in this store are `direct`
pass-through and carry no information). A measure contributes its full DAX, the DAX of
every measure it builds on **transitively**, and the chains of the columns those read.
The transitive closure is load-bearing: without it a measure shows its fiscal filter but
not where its amount comes from, because the base aggregation is often two hops up.
The authored TMDL description is passed only as `authored_hint` and labelled unreliable —
in this model it is a mechanical restatement of the DAX.

**Re-runnable by design** (this is a scheduled feature, not a one-off). The engine rebuilds
`lineage.json` from the repo every run, so descriptions live in their own store
(`descriptions/descriptions.json`, committed to the repo), keyed by node id, each carrying a
**fingerprint over the exact evidence that produced it**. A re-run regenerates only what
actually changed; when richer source-system metadata lands later, exactly the affected
fingerprints change. `"source": "reviewed"` marks human-owned entries that are never
regenerated. The store is checkpointed after every group, so a long run is interruptible
and resumes where it stopped. Run order is **engine → describe**; `--merge-only` re-applies
the store after an engine run with zero model calls.

**Backend is local by default** (`--backend ollama`, ADR-001 Local Model Offload) — the
decisive reason is not cost but that no customer metadata leaves the network. It sends
table/column names, data types, DAX and SQL view expressions; **no row data**.
`--backend anthropic` (Message Batches, `claude-opus-5`, structured outputs, cached system
prompt) remains available and needs credentials.

**Measured quality of a 12B local model on this evidence:** it genuinely reads the lineage —
surfaced a source field four layers upstream, read `ALL('DimDates'[CalendarDate])` as
"ignoring all date filters", and picked a `DaysPastDueDate > 0` filter out of the DAX. It
is weak at *business meaning* (describes mechanics: "filtered by the FactCommittedCosts
exchange rate conversion type"), restates the object's own name when evidence is thin
despite an explicit prompt rule against it, and is inconsistent between related measures.
Prompt tuning is the open work, and local inference being free is what makes iterating on
it affordable.
