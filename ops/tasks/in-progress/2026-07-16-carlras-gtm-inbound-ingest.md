---
title: Carl Ras — GTM inbound ingest (Event Hub landing storage → Fabric LZ/Raw)
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

## Log
- 2026-07-16 — created + started (session task); scoped to the LZ ingest first
- 2026-07-27 — LZ ingest DONE and live: notebook + hourly pipeline in Landingzone-ETL/GTM (green), full backfill 2024-03→today verified exact (324,355,033 events, zero gaps/dups). Remaining in task scope: Raw layer (03 - Raw\GTM in Fabric-ETL), WI/SPN connection swap. Details in datahub/CONTEXT.md.
- 2026-07-28 — Medallion scaffold started (goal: DirectLake model + hourly-freshness PBI report). Decisions: Raw=Python Lakehouse (full history); Enriched=Warehouse per house standard; Curated=shared Warehouse_Curated + GTM fact/dims; fact windowed to **13 months** (F16 DirectLake guardrail = 300M rows/table, ~155M at 13mo); DirectLake model (not import, unlike Atomic builds). BUILT: `Lakehouse_Raw_GTM` + `NB_Raw_GTM` (flatten LZ dbo.events→typed events, incremental on sequence_number) — pushed to Fabric-ETL main, smoke-tested green (1.03M rows, flatten verified). `Warehouse_Enriched_GTM` created; `viewtransform.Events` view + `transform.sp_CreateTableAsSelect` built via direct T-SQL (pyodbc+token). 14-month Raw load (full_reload, backfill_from=2025-06-01) running server-side at wrap. Folder bug found+fixed: fab mkdir creates at workspace root; moved LH→03-Raw/GTM, WH→02-Enriched/GTM via REST API; prevention noted in pingala-fabric skill. NEXT: materialize enriched.Events (EXEC sp after load done) → Curated fact/dims → DirectLake Model_GTM → freshness report; commit Enriched+Curated to git.
