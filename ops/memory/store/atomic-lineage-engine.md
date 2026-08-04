---
id: atomic-lineage-engine
ts: 2026-07-23T07:30:00Z
type: reference
scope: workspace
source: session:14457941
tags: [atomic, lineage, fabric, reusable-asset, elementlogic, metaatomic]
status: distilled
description: "Reusable Atomic lineage engine - static repo parse (sqlglot) + online Fabric enrichment, column-grain, HTML viewer + query CLI; portable rules in atomic_rules.py. Home moving to own/MetaAtomic (ADR 0009, 2026-08-03) - still in customers/ElementLogic/LineageDocumentation until the EL build finishes"
---

> **Home change pending (2026-08-03).** The engine becomes `own/MetaAtomic` — see
> `metaatomic-consolidation`. Until the initial Element Logic build finishes it still lives at the
> path below; after the move, customer projects hold no engine code.

A reusable **Atomic lineage engine** exists at
`customers/ElementLogic/LineageDocumentation/lineage_engine/` — parses any
Git-serialized Atomic Fabric repo (no Fabric access needed) into a column-grain
nodes/edges store, with an online Fabric-notebook enrichment mode, a
self-contained interactive HTML viewer, and `python -m lineage_engine.query`
(`--json`) for terminal/agent lineage questions.

**Why it matters beyond Element Logic:** Atomic conventions are encoded as
explicit config (`atomic_rules.py` — layer rules, CTAS materialization pairs,
structural reference-table detection), so pointing it at another Atomic
customer repo is expected to work. First stop for "where does column X come
from / where is it used" at any Atomic customer — query the store instead of
parsing views by hand. Adversarially verified 2026-07-21 (zero fabricated edges).

**Semantic layer added 2026-08-03** (`tmdl_semantic.py`): TMDL parsed into semantic tables,
columns, measures and calculation items; measures are `grain: column` + `node_type: measure`
so column-grain trace walks measure → measure → column with no second mechanism; model
relationships are a separate `edge_kind` that is never traversed as lineage. The parked
business-language metadata is now `lineage_engine.describe` — see
`lineage-business-descriptions`. Still parked: writing those descriptions back into the
model's own TMDL `description` field (round-trip ownership unresolved).
