---
title: Carl Ras — register GTM in PL_Execute_Raw / PL_Execute_Enriched
status: cancelled
created: 2026-08-07
project: customers/Carl-Ras/datahub
owner: self
priority: normal
blocked_by:
activity: MarketoImport
fno_task:
source: handoff
---

## What
Bring the GTM source into the orchestrated chain the way AX09, CVR and now MARKETO are.

## Why
Measured 2026-08-07 while building the Marketo source. GTM Raw **runs** —
`Lakehouse_Raw_GTM/Tables/events` exists and is populated in `Fabric-ETL-DEV` — but it runs by
hand. `NB_Raw_GTM`'s logicalId `89dfee8d-beed-4297-afc7-9e251ceff128` is referenced by **zero**
files in the repo.

Niels, 2026-08-07: "ideally we should have all in pl_execute_raw also gtm, but do a handoff to
that activity for resolving that, dont do it now."

## Context
What GTM is missing relative to a registered source:

- no `PL_Ingest_Lakehouse_Raw_GTM` pipeline — `NB_Raw_GTM` is a bespoke polars notebook with its
  own `max(sequence_number)` watermark, not the AutoLoader/SCDMerger shell
- no entry in `03 - Raw/PL_Execute_Raw.DataPipeline`
- no `PL_Transform_Enriched_GTM`, and no entry in `02 - Enriched/PL_Execute_Enriched.DataPipeline`
  (`02 - Enriched/GTM/` holds only `Warehouse_Enriched_GTM.Warehouse`)
- no `NB_Table_PrimaryKeyMap_GTM`, so no `rawtablekeymap_gtm`
- no entries in any variable library (`VL_DatastoreId`, `VL_ConnectionId` have no GTM names)
- `Warehouse_Enriched_GTM` exists in git but **not** in the `Fabric-ETL-DEV` workspace

The decision to make first: does GTM keep its bespoke Raw notebook (it flattens the GA4 JSON
body, which the shared ingest notebook does not do) and get a pipeline wrapper, or does it move
to the AutoLoader shell with the flattening pushed into a separate step — the shape Marketo now
uses for `activity_attributes`. See `design/MARKETO_INGEST_DESIGN.md` §2.2 and §4.

## Log
- 2026-08-07 — created (handoff from the Marketo ingest build)

- 2026-08-17 — MERGED into `2026-07-16-carlras-gtm-inbound-ingest` and closed as a separate task. Its content was folded into that task verbatim; nothing dropped.
