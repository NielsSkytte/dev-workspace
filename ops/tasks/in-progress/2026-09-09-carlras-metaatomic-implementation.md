---
title: Carl Ras — MetaAtomic implementation (lineage, stream matrix and portal running on a schedule in Fabric)
status: in-progress
created: 2026-09-09
project: customers/Carl-Ras/datahub
owner: self
priority: normal
blocked_by:
activity:
fno_task:             # needs an ADO task id under CarlRData before the next work session (CLAUDE.md > Time registration)
source: direct
---

## What
Run MetaAtomic for Carl Ras inside their Fabric tenant, on a schedule, with nothing depending
on a workstation: `NB_MetaAtomic` clones the three DevOps repos, builds lineage, the stream matrix
and the portal from `metaatomic.pyz` in `Lakehouse_Util`, and publishes the pages to
`Files/MetaAtomic/out/`. `PL_UpdateLineage` triggers it daily at 05:30. The stream matrix
document lives in `Fabric-ETL/MetaAtomic/design/`.

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
