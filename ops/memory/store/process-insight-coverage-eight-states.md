---
id: process-insight-coverage-eight-states
ts: 2026-10-28T19:30:00Z
type: semantic
scope: project:customers/Carl-Ras/process-insight
source: session:80a43015
tags: [process-insight, coverage, ontology]
status: distilled
description: "Coverage has eight states since 2026-10-28 (D36): ETL gap = landed, our pipeline must carry it; Not landed = source holds it, landing does not. Onboarding needs a live landed-tables snapshot, else everything reads as ETL gap"
---

Niels split the old ETL gap state on 2026-10-28 (product brief D36, own/ProcessInsight 931fa72):
**ETL gap** means the data is landed and our pipeline (Enriched, binding, Curated, measure) must
change; **Not landed** means the source system holds it but the table or column is not in landing
(not linked, not exported, not onboarded from an API). Empty is unchanged: landed and built, no rows
or values yet. A BLANK reason carries its category as a prefix (`not-landed:`, `etl:`, `no-data:`,
`other-source:`, `overlay:`) and the prefix wins in `tools/coverage.py`.

Root cause of the inflated ITD ETL gap (131 of 194): the 2026-10-24 onboarding saw only the Enriched
catalogue, which drops landed columns such as createddatetime. Engine fix: `onboard_agent.py` refuses
to run without `--snapshot <catalog>=<landed.json>` for every catalog the data hints name, and
`onboard.py` keeps a "not in the evidence" BLANK open while the snapshot lands its tables.
