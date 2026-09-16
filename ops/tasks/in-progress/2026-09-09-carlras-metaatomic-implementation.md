---
title: Carl Ras — MetaAtomic implementation (lineage, stream matrix and portal running on a schedule in Fabric)
status: in-progress
created: 2026-09-09
project: customers/Carl-Ras/datahub
owner: self
priority: normal
blocked_by:
activity:
fno_task: none        # no Azure DevOps work item yet; Carl Ras bills task-always (CLAUDE.md), so time here cannot be registered until one exists
customer_ask: open
source: direct
---

## What
Run MetaAtomic for Carl Ras inside their Fabric tenant, on a schedule, with nothing depending
on a workstation: `NB_MetaAtomic` clones the three DevOps repos, builds lineage, the stream matrix
and the portal from `metaatomic.pyz` in `Lakehouse_Util`, and publishes the pages to
`Files/MetaAtomic/out/`. `PL_UpdateLineage` triggers it daily at 05:30. The stream matrix
document lives in `Fabric-ETL/MetaAtomic/design/`.

## Progress

**Now (2026-09-15):** `PL_UpdateLineage` runs `NB_MetaAtomic` daily 05:30 since 2026-09-09; engine
0.5.1+20260915 verified in the store 09-15 (13,505 nodes, online). The notebook is generic since 09-15 —
every Carl Ras value is a pipeline parameter. The clone runs on Niels's read-only PAT
(`metaatomic-ado-pat`, expires in a year) because `Fabric_Datahub` is not in the DevOps organization.

**Tried and dropped:** cloning as the `Fabric_Datahub` service principal -> `TF401444`, not an org member
(needs a paid Basic seat, org admin required); Graph for the SharePoint publish -> a Copy activity under
Niels's account (09-09); the pyz in the lakehouse plus an upload script -> the pyz travels in the
`Fabric-ETL` repo and comes with the clone (09-09 afternoon).

**Next:**
1. DevOps Basic seat for `Fabric_Datahub` (Carl Ras org admin), then flip the notebook off the PAT.
2. Widen the inactive **Copy Lineage** activity to `MetaAtomic/out/metaAtomic` before activating it.
3. `Landingzone-ETL` contributes 0 nodes — engine work, tracked in `own/MetaAtomic`.
4. Get a CarlRData work item id for this task (time on 09-09/09-10 carries no Task dimension).

## Needs from customer

- **Carl Ras (DevOps organization admin): add `Fabric_Datahub` (object id `f05f446a-1951-466a-bf82-287c77906c5e`)
  to the CarlRas DevOps organization** — Basic access, project Datahub, Readers. One more paid seat
  (10 assigned, 5 included on 09-09). Status not recorded.


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
