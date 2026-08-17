---
title: Carl Ras — GTM to the house pattern (inbound ingest, execute-chain registration, generated viewtransform)
status: in-progress
created: 2026-07-16
project: customers/Carl-Ras/datahub
owner: fabric-back
priority: normal
blocked_by:
activity: TagManager
fno_task:
source: session
---

## What
Build the inbound import of the GA4/Stape event data from the Carl Ras-owned landing
storage account (`stcrdatabricksweprod/landing`, Event Hubs Capture Avro) into the
Fabric platform: new GTM source in the LandingZone (shortcut + ingest notebook →
`Lakehouse_Landingzone_GTM`), then the Raw layer per the house pattern.

## Why
The decided inbound architecture (2026-07-03): OneLake shortcut on the landing
container, rebuild the medallion in Fabric, retire Databricks. This is the first
build step of the datahub project.

## Context
- Project: `customers/Carl-Ras/datahub` (fno_code 230-02); CONTEXT.md holds the decided
  architecture; sample Avro in `datahub/data/`.
- Repos: `Landingzone-ETL` (LZ workspace; GTM folder goes here, alongside AX09/CVR) and
  `Fabric-ETL` (`03 - Raw\GTM` later). Both dev.azure.com/CarlRas/Datahub.
- Auth for now: Niels' guest account (prove it works), then switch to WI/SPN.

## Resume facts (medallion build, 2026-07-28)
- Workspace Fabric-ETL-DEV = `fe4c7544-750c-4e23-812f-8260f15cbabd`. WH SQL endpoint (all warehouses in ws) = `fvov2azruplupjattgq3vftqma-ir2uz7qmouru5ajpqjqpcxf2xu.datawarehouse.fabric.microsoft.com`.
- Items: `Lakehouse_Raw_GTM` = `c3688d18-d847-4217-bf22-53e6250b9742` (folder 03-Raw/GTM `c9f47eac-889e-4255-a098-5c0a97506ef5`); `Warehouse_Enriched_GTM` = `3c95ab07-7091-4bb0-93f8-d1aa72af625a` (folder 02-Enriched/GTM `36a70ee7-34de-46a0-ac42-e186e282fde3`); LZ src `Lakehouse_Landingzone_GTM` = `ccd0a488...` in ws `5ec283c4-9f90-4ea9-a056-9faceb84ce25`.
- DDL mechanism: pyodbc + `ODBC Driver 18`, token via `az account get-access-token --resource https://database.windows.net/`, attrs_before {1256: token_struct}; Database=<warehouse displayName>. Cross-db `[Lakehouse_Raw_GTM].[dbo].[events]` works (plain LH→dbo).
- Curated (next): shared `Warehouse_Curated` (01-Curated), reuse `dim.Date` (SurrogateKey=yyyymmdd int) + `sp_CreateFactTableAsSelect`/`sp_CreateDimTableAsSelect`. Add Gtm-prefixed `viewfacttransform.GtmEvents`→`fact.GtmEvents` (WHERE EventDate>=DATEADD(MONTH,-13,...)), `viewdimtransform.GtmEvent`→`dim.GtmEvent` (natural key EventName). Model_GTM DirectLake in Semantic-Model-DEV; report in Sales-DEV (existing reports live there).
- Not yet in git: Enriched WH objects + folder relocation of Raw LH — capture via workspace→git commit next session.

## Part 2 — register GTM in `PL_Execute_Raw` / `PL_Execute_Enriched`

*(merged 2026-08-17 from `2026-08-07-carlras-gtm-register-in-execute-chain`)*

Measured 2026-08-07 while building the Marketo source. GTM Raw **runs** —
`Lakehouse_Raw_GTM/Tables/events` exists and is populated in `Fabric-ETL-DEV` — but it runs by
hand. `NB_Raw_GTM`'s logicalId `89dfee8d-beed-4297-afc7-9e251ceff128` is referenced by **zero**
files in the repo. Niels, 2026-08-07: *"ideally we should have all in pl_execute_raw also gtm."*

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

## Part 3 — move GTM's Enriched views to the generated (metadata-driven) pattern

*(merged 2026-08-17 from `2026-08-07-carlras-gtm-generated-viewtransform`)*

Apply the generated-`viewtransform` mechanism built for Marketo to GTM as well. Niels, 2026-08-07:
*"the handwritten views are another thing we are looking into … in the way you say generated."*

Marketo now has `NB_Generate_ViewTransform_MARKETO` (`02 - Enriched/MARKETO/`), which reads
`Lakehouse_Util.marketo_columns` and issues `CREATE OR ALTER VIEW` into
`Warehouse_Enriched_MARKETO.viewtransform`, then drops any view the metadata no longer asks for.
Everything downstream is unchanged — `PL_Transform_Enriched_*` still discovers views with
`SELECT TABLE_NAME FROM INFORMATION_SCHEMA.VIEWS` and `sp_CreateTableAsSelect` still CTASes them.

To do the same for GTM: a `gtm_columns` equivalent (GTM's Raw `events` table has 21 flattened
columns, currently fixed in a `BODY_FIELDS` literal inside `NB_Raw_GTM`), and a generator
notebook. Note `Warehouse_Enriched_GTM` already carries a hand-written
`viewtransform/Views/Events.sql`, which the generator would replace.

**Sequencing:** do not start part 3 before the Marketo generator has run for real — the DDL path
through `notebookutils.data.connect_to_artifact` is undocumented and unproven
(`design/MARKETO_INGEST_DESIGN.md` §5, open item 2).

## Log
- 2026-07-16 — created + started (session task); scoped to the LZ ingest first
- 2026-07-27 — LZ ingest DONE and live: notebook + hourly pipeline in Landingzone-ETL/GTM (green), full backfill 2024-03→today verified exact (324,355,033 events, zero gaps/dups). Remaining in task scope: Raw layer (03 - Raw\GTM in Fabric-ETL), WI/SPN connection swap. Details in datahub/CONTEXT.md.
- 2026-07-28 — Medallion scaffold started (goal: DirectLake model + hourly-freshness PBI report). Decisions: Raw=Python Lakehouse (full history); Enriched=Warehouse per house standard; Curated=shared Warehouse_Curated + GTM fact/dims; fact windowed to **13 months** (F16 DirectLake guardrail = 300M rows/table, ~155M at 13mo); DirectLake model (not import, unlike Atomic builds). BUILT: `Lakehouse_Raw_GTM` + `NB_Raw_GTM` (flatten LZ dbo.events→typed events, incremental on sequence_number) — pushed to Fabric-ETL main, smoke-tested green (1.03M rows, flatten verified). `Warehouse_Enriched_GTM` created; `viewtransform.Events` view + `transform.sp_CreateTableAsSelect` built via direct T-SQL (pyodbc+token). 14-month Raw load (full_reload, backfill_from=2025-06-01) running server-side at wrap. Folder bug found+fixed: fab mkdir creates at workspace root; moved LH→03-Raw/GTM, WH→02-Enriched/GTM via REST API; prevention noted in pingala-fabric skill. NEXT: materialize enriched.Events (EXEC sp after load done) → Curated fact/dims → DirectLake Model_GTM → freshness report; commit Enriched+Curated to git.
- 2026-08-17 — MERGED: `2026-08-07-carlras-gtm-register-in-execute-chain` (part 2) and
  `2026-08-07-carlras-gtm-generated-viewtransform` (part 3). One GTM workstream: land it, register
  it, then generate its views. Both were handoffs from the Marketo ingest build and neither has
  been started.
