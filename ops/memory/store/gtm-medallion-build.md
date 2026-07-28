---
id: gtm-medallion-build
ts: 2026-07-28T09:37:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: session:c79aa71b
tags: [project, carl-ras, datahub, fabric, medallion, gtm]
status: distilled
description: "Carl Ras datahub GTM medallion shape: Raw Python lakehouse (full history) → Enriched warehouse (house standard) → shared Warehouse_Curated (13-mo windowed fact) → DirectLake model + freshness report"
---

The GTM (GA4/Stape events) medallion in Fabric, decided + partly built 2026-07-28. Shape
deliberately hybrid — Python where JSON/volume make it better, house SQL-warehouse where
business logic + F&O convergence live:

- **Raw** `Lakehouse_Raw_GTM` (03-Raw/GTM) + `NB_Raw_GTM` (pure Python: polars + deltalake).
  Flattens LZ `dbo.events` GA4/Stape JSON body (46 fields, `str.json_path_match`, bracket
  notation for hyphen keys like `x-ga-measurement_id`) → typed `events`, incremental on
  `sequence_number`, batched per `arrival_date`. Full history kept here (cheap).
- **Enriched** `Warehouse_Enriched_GTM` (02-Enriched/GTM) — house standard: `viewtransform.Events`
  view (business logic: type casts, EventCategory, IsWebVital, segment NULLIF) → `sp_CreateTableAsSelect`
  → `enriched.Events` table.
- **Curated** = shared `Warehouse_Curated` (per owner decision), Gtm-prefixed isolated objects:
  `viewfacttransform.GtmEvents` → `fact.GtmEvents` (13-month window, see [[fabric-directlake-guardrails]]),
  `viewdimtransform.GtmEvent` → `dim.GtmEvent` (natural key EventName), conforming to existing
  shared `dim.Date` (SurrogateKey = yyyymmdd int).
- **Model** DirectLake `Model_GTM` in Semantic-Model-DEV (NOT import, unlike the Atomic F&O
  model — refresh pain drove this). **Report** GTM freshness (events/hour) in Sales-DEV.

Decisions: F16 for now; 13-month window; shared Curated; separate Enriched warehouse. LZ inbound
ingest already live+verified (324M events, hourly). Live task: `2026-07-16-carlras-gtm-inbound-ingest`
(activity TagManager) holds resume facts (IDs, endpoints, DDL mechanism).
