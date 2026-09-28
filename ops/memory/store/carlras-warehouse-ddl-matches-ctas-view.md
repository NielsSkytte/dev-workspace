---
id: carlras-warehouse-ddl-matches-ctas-view
ts: 2026-09-25T06:55:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: /log
tags: [carl-ras, fabric, warehouse, ctas, git, cvr, decision]
status: distilled
description: "Carl Ras datahub rules from 2026-09-24/25: a warehouse table's .sql file must match the CTAS view that builds it, changed in the same commit (4 of 65 pairs had drifted); Marketo (and GTM after Part 3) warehouses are never committed from the workspace; the CVR employee band is decoded in Enriched with blank = NULL"
---

- **Table file = view.** 65 CTAS pairs checked 2026-09-24: 61 clean, 4 drifting
  (`dim.AlternativeChartOfAccount` missing `Linje`, `dim.Date` missing `MonthSelector`,
  `fact.InventoryOnHand` types). The drift made Update from git offer to delete the tables. Fixed
  in `3d3c70d`; the `InventoryOnHand` type change in that commit was wrong and went back to
  `decimal(28,12)` in `f0ca063`. Rule written into the datahub `CLAUDE.md` Conventions (`d52c6dc`).
- **Never commit from the workspace:** `Warehouse_Enriched_Marketo`; `Warehouse_Enriched_GTM`
  joins it once its views are generated (Part 3 of the GTM ingest task).
- **CVR employee band (GEN-012).** CVR's API sends interval codes (`ANTAL_10_19`); the ingest
  stores them unchanged. The decode to `Antal ...` labels sits in Enriched
  `viewtransform.CentralCompanyRegister` (the Atomic layer for uniform values). Owner decision:
  blank is NULL, not an authored `Unknown` word; Power BI labels it. Whether readable labels
  ever existed in DEV before 2026-08-16 is not proven - one internal note is the only trace.
