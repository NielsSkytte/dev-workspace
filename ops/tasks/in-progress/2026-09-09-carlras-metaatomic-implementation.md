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

**Now (2026-10-20):** DEV runs daily and is level with Fabric-ETL main at `f627fb6` (10-19). Lineage is whole: the
10-18 DEV store has raw -> enriched 2,528 and enriched -> curated 881 column edges (the "all views partial" finding was a
stale 10-12 snapshot). `NB_DataQuality` profiles entry, enriched and curated with the AX09 pack, reconciles row counts from
the Delta log, and the run mail arrives (Niels, 10-20). Weighted score made the headline with the mean over tables beside
it (Niels's yes, 10-20): own repo `816661e`, pyz `0.7.0+20261020.816661e` uploaded to Lakehouse_Util and written to the
Fabric-ETL clone, not committed.

**Fabric App (2026-10-20):** tests 1-2 pass in Pingala `NielsWorkspace_Dev` (`own/MetaAtomic` `88ea59f`, findings in
`docs/app-hosting-pattern.md` section 7a): static MetaAtomic page + Fabric SSO; delegated `fabric-sqldatabase` connector
to a separate store, actor = the user's UPN by column default; views read keyless only. Sizing (estimate, inference):
1 page delivery from the daily run into the app (unknown, spike first); 2 one app shell over portal, lineage, stream
matrix, DQ, packs (~1 d); 3 DQ editor writes through the connector, store reshaped to single-row appends, `checkPack`
ported to TypeScript (~2-4 d); 4 Carl Ras store DB + an Entra group with SELECT/INSERT (~0.5 d plus their admin);
5 Carl Ras gates: "Fabric Apps (preview)" tenant setting, sharing "Run and interact". Total ~5-8 days.
Test 3 passes (10-20): a function reads the run's pages from `Files/MetaAtomic/out/` as the app identity, up to 25.9 MB in
6.5 s, so page delivery needs no redeploy and item 1 drops to ~0.5 d (inference); total ~4-7 days.

**Tried and dropped:** cloning as the `Fabric_Datahub` service principal -> `TF401444`, not an org member
(needs a paid Basic seat, org admin required); Graph for the SharePoint publish -> a Copy activity under
Niels's account (09-09); the pyz in the lakehouse plus an upload script -> the pyz travels in the
`Fabric-ETL` repo and comes with the clone (09-09 afternoon); DevOps Basic seat for `Fabric_Datahub` ->
staying on PAT (09-21); the engine path for `NB_DataQuality` through the `/lakehouse/default` mount (`8d41e79`, 10-12) ->
the notebook has no default lakehouse, replaced by an `abfss://` copy (`d7f2424`).

**Next:**
1. Commit and push the pyz to Fabric-ETL (Niels's go); no Update from git needed (`NB_MetaAtomic` reads the pyz from its
   clone, `NB_DataQuality` from Lakehouse_Util; the notebook diff is a comment). Then check the next run's page and mail
   show the weighted headline and compare with the previous run's weighted score.
2. **Copy Lineage** is parked: Niels will replace it with something else once the main work is implemented (10-20).
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
- **Hosting (2026-10-20): at Carl Ras MetaAtomic incl. DQ and lineage is hosted as a Fabric App** (Niels). MetaAtomic
  stays deployable to either host, chosen per deployment (Matas: SWA). Design base:
  `own/MetaAtomic/docs/app-hosting-pattern.md` (SWA vs Fabric App, the module schema is the API, tested facts),
  `customers/Matas/DataCompare` (the SWA build and Matas Dev GraphQL/SSO tests), `datahub/INBOX.md` 2026-10-17 note.
  Test app: `own/MetaAtomic/fabric-app` (Rayfin `dataapp` template). Carl Ras capacity is West Europe (Fabric Apps
  available there per the pattern doc); whether the "Fabric Apps (preview)" tenant setting is on at Carl Ras is unknown.

## Log
- 2026-09-09 — created, in progress: deployed, first run by hand completed, schedule set
- 2026-09-09 — time: 39 min of session f0ca3d4e (05:40-08:00 UTC, rooted in own/MetaAtomic) attributed here by Niels; the remaining 52 min of that session go to 2026-08-11-carlras-operation-hardening. Apply when 2026-09-09 is rolled up: the heartbeats carry own/MetaAtomic.
- 2026-09-16 — brought onto the Progress shape (Progress + Needs from customer, `fno_task` / `customer_ask` set, `activity` blanked per CLAUDE.md task-always rule); no facts changed. Card: `customers/Carl-Ras/datahub/CONTEXT.md`.
- 2026-09-21 — check-in: staying on PAT; DevOps seat ask dropped. Engine 0.7.0 available locally (2026-09-18). Next: upload to Lakehouse_Util.
- 2026-10-13 — engine 0.7.0 deployed (`3069ba9`); `NB_DataQuality` made to run in Fabric (`8d41e79`, `d7f2424`, `e371d83`); run `a1d06a51` Completed, 92 tables, score 95.0; sqlglot 30.22 regression found (fixed in the own repo, not deployed).
- 2026-10-20 — Progress brought up to date (lineage whole, DQ over three layers, mail works); weighted score made the headline (`816661e`), engine uploaded to Lakehouse_Util; Copy Lineage parked.
