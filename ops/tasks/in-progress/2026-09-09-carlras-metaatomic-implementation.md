---
title: Carl Ras — MetaAtomic implementation (lineage, stream matrix and portal running on a schedule in Fabric)
status: in-progress
created: 2026-09-09
project: customers/Carl-Ras/datahub
owner: self
priority: normal
blocked_by:
activity:
fno_task: CarlRData-666
customer_ask: none
source: direct
---

## What
Run MetaAtomic for Carl Ras inside their Fabric tenant, on a schedule, with nothing depending
on a workstation: `NB_MetaAtomic` clones the three DevOps repos, builds lineage, the stream matrix
and the portal from `metaatomic.pyz` in `Lakehouse_Util`, and publishes the pages to
`Files/MetaAtomic/out/`. `PL_UpdateLineage` triggers it daily at 05:30. The stream matrix
document lives in `Fabric-ETL/MetaAtomic/design/`.

## Progress

**Now (2026-10-13):** engine `0.7.0+20261012.a50dcc5` is in Fabric-ETL main (`3069ba9`) and Lakehouse_Util; DEV updated
by Update from git on Niels's go. Manual `PL_UpdateLineage` run `a1d06a51` Completed 07:09-08:09 UTC: `NB_DataQuality` ran,
92 tables (91 landing, 1 raw), 661M rows, sample 20,000, score 95.0. The scheduled runs 10-08 to 10-13 had failed at
`NB_DataQuality` (engine not found, then no lineage store); fixed in `8d41e79`, `d7f2424`, `e371d83`. The `0.7.0` file in
Fabric has a regression: it vendors sqlglot 30.22, which dropped `infer_schema`, so all 94 view lineages are partial (10-13).
Fixed in `own/MetaAtomic` (`376d4dd`); not deployed.

**Tried and dropped:** cloning as the `Fabric_Datahub` service principal -> `TF401444`, not an org member
(needs a paid Basic seat, org admin required); Graph for the SharePoint publish -> a Copy activity under
Niels's account (09-09); the pyz in the lakehouse plus an upload script -> the pyz travels in the
`Fabric-ETL` repo and comes with the clone (09-09 afternoon); DevOps Basic seat for `Fabric_Datahub` ->
staying on PAT (09-21); the engine path for `NB_DataQuality` through the `/lakehouse/default` mount (`8d41e79`, 10-12) ->
the notebook has no default lakehouse, replaced by an `abfss://` copy (`d7f2424`).

**Next:**
1. Rebuild the engine (lineage fix, quarantine), push the file and the `NB_DataQuality` change to Fabric-ETL, upload it to
   Lakehouse_Util, Update from git in DEV on Niels's go, run once, check the lineage coverage has no `infer_schema` errors.
2. Widen the inactive **Copy Lineage** activity to `MetaAtomic/out/metaAtomic` before activating it.
3. `Landingzone-ETL` contributes 0 nodes — engine work, tracked in `own/MetaAtomic`.

## Needs from customer

- None.


## Why
The pages are the customer-facing record of what the platform holds and how far each stream has
come. A copy that ages on a laptop is not that record.

## Context
- `customers/Carl-Ras/datahub/CONTEXT.md` > MetaAtomic section (prerequisites, blockers, the GTM gap)
- `own/MetaAtomic/README.md` > Running it in Fabric
- Engine work that this deployment drove is R&D and is logged in `own/MetaAtomic/CONTEXT.md`
- Related: 2026-08-11-carlras-operation-hardening (the daily run must stay green)

## Log
- 2026-09-09 — created, in progress: deployed, first run by hand completed, schedule set
- 2026-09-09 — time: 39 min of session f0ca3d4e (05:40-08:00 UTC, rooted in own/MetaAtomic) attributed here by Niels; the remaining 52 min of that session go to 2026-08-11-carlras-operation-hardening. Apply when 2026-09-09 is rolled up: the heartbeats carry own/MetaAtomic.
- 2026-09-16 — brought onto the Progress shape (Progress + Needs from customer, `fno_task` / `customer_ask` set, `activity` blanked per CLAUDE.md task-always rule); no facts changed. Card: `customers/Carl-Ras/datahub/CONTEXT.md`.
- 2026-09-21 — check-in: staying on PAT; DevOps seat ask dropped. Engine 0.7.0 available locally (2026-09-18). Next: upload to Lakehouse_Util.
- 2026-10-13 — engine 0.7.0 deployed (`3069ba9`); `NB_DataQuality` made to run in Fabric (`8d41e79`, `d7f2424`, `e371d83`); run `a1d06a51` Completed, 92 tables, score 95.0; sqlglot 30.22 regression found (fixed in the own repo, not deployed).
