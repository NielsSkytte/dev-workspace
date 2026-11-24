---
title: Carl Ras — Marketo inbound ingest (Bulk Extract -> landing -> Raw -> Enriched in PROD)
status: in-progress
created: 2026-11-24
project: customers/Carl-Ras/datahub
owner: fabric-back
priority: normal
blocked_by:
activity:
fno_task: CarlRData-496
customer_ask: none
waiting_on:
resume_on:
source: direct
---

## What
Get Marketo lead and activity data into the Fabric platform in PROD: `PL_Ingest_Marketo` (Landingzone-Code) ->
`Lakehouse_Landingzone_Marketo` -> `PL_Ingest_Lakehouse_Raw_Marketo` -> `PL_Transform_Enriched_Marketo`, with the
daily Bulk Extract quota (500 MB, shared with Impact's Fivetran) logged and monitored. Done when: a scheduled daily
landing ingest runs in PROD as the SPN, the 08-20 to 11-14 gap is backfilled within the agreed cap, and the quota
ledger shows what each run spent.

## Why
Marketo data stopped landing after 2026-08-20. The write-back thread (CarlRData-553) needs fresh leads.

## Progress
**Now (2026-11-24):** Ingest deployed DEV->TEST->PROD (Landingzone-ETL a04ce3c, 842d343). Sample load 11-15..11-18 plus
11-19 changes verified landing -> Raw -> Enriched in PROD (enriched.Leads 55,612; enriched.Activities 8,230,893). Spent
about 60 MB of the shared 500 MB on 11-19. Per-run ledger in `ops.run_ledger`, per-job in `dbo.export_log`.
Leads (updatedAt) drive the cost; one Monday window was 39 MB.
**Tried and dropped:** ledger table in `dbo` (Raw tried to ingest it); moved to schema `ops`.
**Next:** (1) Niels decides the daily cap (proposal 60 MB, 2-day lookback) and enabling the daily landing schedule;
(2) re-stamp PROD Marketo items to the SPN (tools/fabric_identity.py), enable schedule; (3) plan the 08-20..11-14
backfill, and tell Impact (Benno) when it starts; (4) commit design/MARKETO_INGEST_DESIGN.md section 10 update.

## Needs from customer
- none (Impact is informed when the backfill starts, per Niels 2026-11-19).

## Context
`datahub/design/MARKETO_INGEST_DESIGN.md`, `datahub/CONTEXT.md`, related task `2026-08-12-carlras-marketo-writeback`.

## Log
- 2026-11-24 — created (the inbound thread had no task file; work started 2026-11-18, session 37e0bc8a)
