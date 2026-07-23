---
id: atomic-lineage-engine
ts: 2026-07-23T07:30:00Z
type: reference
scope: workspace
source: session:14457941
tags: [atomic, lineage, fabric, reusable-asset, elementlogic]
status: distilled
description: "Reusable Atomic lineage engine lives in customers/ElementLogic/LineageDocumentation - static repo parse (sqlglot) + online Fabric enrichment, column-grain, HTML viewer + query CLI; portable rules in atomic_rules.py"
---

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
Next phase parked: semantic-model node type + business-language column metadata
distilled from the store into TMDL descriptions.
