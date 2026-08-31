---
id: fabric-git-status-misses-warehouse-drift
ts: 2026-08-31T10:30:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: session:f17772e8-6514-4c38-b590-03daab4595e6
tags: [fabric, git, warehouse, drift, release, guardrail]
status: distilled
description: "Fabric's own git/status reports a warehouse CLEAN while its view bodies differ from git - so a git-status drift gate is necessary but not sufficient"
---

Measured 2026-08-31 on `Fabric-ETL-DEV`.

## The finding

`GET /v1/workspaces/{id}/git/status` listed exactly two changed items —
`Warehouse_Enriched_AX09` (workspace-modified) and `VL_ConnectionId` (remote-modified). It reported
`Warehouse_Curated` as **clean**.

`Warehouse_Curated` was not clean. Three of its views carried an uncommitted hand-patch applied
directly in the service on 2026-08-21:

```sql
-- live in DEV
TransDate >= DATEADD(MONTH, -12, DATEFROMPARTS(YEAR(GETDATE()), MONTH(GETDATE()), 1))
-- in git
TransDate >= DATEFROMPARTS(YEAR(GETDATE()), MONTH(GETDATE()), 1)
```

Verified by reading `OBJECT_DEFINITION(OBJECT_ID('viewfacttransform.GeneralLedgerTransactions'))`
against the repo file. `viewfacttransform.SalesTransactions` and `.InventoryTransactions` carried the
same divergence.

## Why it matters

`2026-08-19-carlras-landingzone-dev-drift` item 4 proposes a release gate that refuses to deploy
while a source workspace has uncommitted changes, driven by `git/status`. **That gate would have
passed this workspace.** Build it — it catches the item-level case, which is how the 40-vs-88 table
drift was found — but do not treat a clean `git/status` as proof a workspace matches git.

The reliable check for warehouse internals is to read `OBJECT_DEFINITION` (or
`INFORMATION_SCHEMA.VIEWS`) per object and diff against the repo `.sql` files. `SET PARSEONLY ON`
validates syntax but says nothing about drift.

## Corollary

The same DEV view had **lost its `-- Auto Generated (Do not modify)` header**, replaced by a bare
`CREATE VIEW`. So the project's usual drift marker was gone on that object too — two independent
signals absent on the same change.

## Related

- `carlras-viewtransform-workspace-drift` — the earlier, item-level case.
- Task `2026-08-17-carlras-curated-data-loss-windows` holds the window itself.
