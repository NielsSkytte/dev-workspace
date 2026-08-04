---
id: metaatomic-consolidation
ts: 2026-08-03T18:00:00Z
type: semantic
scope: workspace
source: /log
tags: [metaatomic, lineage, elementlogic, tystofte, carlras, reusable-asset, architecture]
status: distilled
description: "own/MetaAtomic becomes the single home for the metadata/lineage capability: the EL lineage engine + Tystofte source extraction move in, customer projects become deployments that import it, Carl Ras is the portability gate"
---

Four projects held pieces of one capability. Consolidated into `own/MetaAtomic` by owner decision
2026-08-03 (ADR `own/MetaAtomic/docs/decisions/0009-metaatomic-is-the-product.md`).

**What each held.** MetaAtomic — the name, the concept, architecture docs and ADRs, and ~1,470 lines
that never executed. `customers/ElementLogic/LineageDocumentation` — a working engine and UI
(19,996 nodes / 18,279 edges, adversarially verified) with no knowledge upstream of
`ingestion_boundary.py`. `customers/Tystofte/Tystofte-Fabric` — working Oracle catalog extraction
(`nb_A_build_metadata`) and data profiling (`nb_C_profile_timestamps`) with no engine or UI on top.
An out-of-Dev third-party project does the same extraction for SQL Server; not yet inventoried.

**Two decisions, in order.** ADR 0008 picked the lineage node/edge model over MetaAtomic's `meta.*`
Delta schema — the lineage model runs at scale and is verified, MetaAtomic's has never executed.
That stands. ADR 0008 also left the code in the customer project and reduced MetaAtomic to a catalog
adapter; ADR 0009 reversed that the same day. Neither customer project can be the product: each is
scoped and billed to one customer.

**The anti-drift mechanism is structural, not procedural.** Customer projects keep config, inputs,
outputs and per-customer overrides, and hold *no engine code*. Forking is impossible because there
is nothing local to fork. Editing engine code in a customer folder has no effect.

**Carl Ras is the portability gate.** One customer never produces generic code. The reusability
claim is not accepted until a second Atomic installation runs with no engine changes — the test of
whether the structural reference-table detection (built portable on purpose, 2026-07-22) held
everywhere else.

**Sequencing (owner, 2026-08-03):** finish the Element Logic build in place → move → then test on a
new customer. Suggested observable trigger: LineageDocumentation `CONTEXT.md` Next Actions 1-3
closed (online enrichment run done, viewer published). Its Next Action 4 — semantic-model
business-language metadata distillation — is *new engine code* and belongs after the move, written
in MetaAtomic rather than built in the customer project and migrated afterwards.

**The move's pass/fail:** re-run Element Logic from the new home and reproduce 19,996 nodes /
18,279 edges / 0 failures. That number is the safety net for restructuring mid-engagement.

**Carried open questions.** `own` and `customers/ElementLogic` are separate local-only git repos, so
the move loses history unless deliberately preserved. How deployments import MetaAtomic (path,
submodule, package) is undecided. Constraints and indexes are multi-column sets that do not fit the
flat Node/Edge model. Field-level reconciliation of the two schemas is in
`own/MetaAtomic/docs/capability-map.md`.

**What not to rebuild.** MetaAtomic's three unbuilt pieces — `helpers.py`, `profile_timestamps.py`,
`generate_handover.py` — already exist working in Tystofte-Fabric. Building them would have been the
third implementation. Marked superseded in MetaAtomic's `CONTEXT.md`.
