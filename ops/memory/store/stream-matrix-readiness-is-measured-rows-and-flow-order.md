---
id: stream-matrix-readiness-is-measured-rows-and-flow-order
ts: 2026-09-09T20:30:00Z
type: semantic
scope: workspace
source: /log
tags: [metaatomic, stream-matrix, readiness, medallion, environments, niels-rule, derived-vs-asserted]
status: distilled
description: "Niels's rule for the stream matrix (2026-09-09): a stage is ready in an environment only when its rows are counted there, above zero, and every stage before it in the flow is ready; deployed without a count is deployed, not ready; an outbound track is ready only when the inbound streams it reads from are ready through curated; a source is proven by its landing. MetaAtomic 0.4.0 measures all of it per run, and the asserted done is only a claim against it"
---

**The rule, in Niels's words.** "Prod can never be okay if the preceding stages are not ready for
prod. Data must be ready in source, then landing, then raw, enriched and finally curated. Something
can only be ready if we can actually measure rows in that environment. Lakehouse_Raw_CVR with an
unknown number of rows can never be production ready: prod can be deployed, but is not ready until
we count rows. Outbound uses the inbound data, so AX must be ready first."

**What the engine measures on the schedule, per stage and environment** (`stream_matrix/deployments.py`,
inventory in `lineage_engine/online_local.py`): item presence, rows of the stage's store or of one
named `Store.table`, the latest run of its pipelines and notebooks, the flow order (source first
inbound, curated first outbound), and `outbound_depends_on`. A stage that measures nothing, the
source system or an outbound target, is proven by its neighbour in the flow. A store whose workspace
belongs to every environment is one shared store. The verdict decides the chip; "done" adds the tick
when backed and a red cross when not; the banner's "live" is ready and validated together. Nothing is
corrected automatically: which of two disagreeing states is wrong is a judgement.

**What it did on its first reading at Carl Ras.** Three of the day's own claims fell: raw in PROD for
AX09 and CVR had completed loads but their lakehouse SQL endpoints refuse every query, so no count,
so not ready, so everything after them in PROD blocked. Marketo raw in PROD stood on a measured 25 M
rows. `sys.partitions.rows` reads zero on Fabric endpoints; one batched `COUNT_BIG(*)` per store is
the real count, 90 tables and 470 M rows in 27 s.
