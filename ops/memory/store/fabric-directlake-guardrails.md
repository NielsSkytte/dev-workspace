---
id: fabric-directlake-guardrails
ts: 2026-07-28T09:35:00Z
type: semantic
scope: workspace
source: session:c79aa71b
tags: [reference, fabric, directlake, semantic-model, capacity]
status: distilled
description: "Fabric DirectLake per-table guardrails by SKU (F16 = 300M rows/table, 20GB model) and the materialized-table-not-view rule; drives fact windowing"
---

DirectLake semantic-model guardrails, confirmed against MS Learn (direct-lake-overview
#fabric-capacity-requirements) during the Carl Ras GTM build:

- **Rows per table is the binding limit and is per-table, per-query.** One table over
  the limit drops the WHOLE model to DirectQuery (Direct Lake on SQL) or errors
  (Direct Lake on OneLake, no fallback).
- **Rows/table by SKU:** F2–F32 = **300 M**; F64 = 1,500 M; F128 = 3,000 M; scales up.
  So **the 300M ceiling holds all the way from F2 to F32** — scaling F16→F32 does NOT
  raise it; only F64+ does. Model size on OneLake: F16 = 20 GB, F32 = 40 GB. Max
  memory: F16 = 5 GB.
- **DirectLake must read a MATERIALIZED delta table, never a SQL view** — a table
  "based on a SQL view" forces DirectQuery fallback; fix = materialize the view to a
  table. This validates the house `viewtransform → CTAS → table` discipline.
- RLS/OLS/DDM defined at the SQL endpoint also forces fallback — keep security in the
  model, not the endpoint.

**Consequence for high-volume sources:** window the fact table. GA4 events ~12M/month;
Carl Ras GTM fact capped to a **13-month rolling window** (~155M rows, ~55% of the F16
300M ceiling) with full history kept in the Raw lakehouse. See [[gtm-medallion-build]].
