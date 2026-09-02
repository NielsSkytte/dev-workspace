---
title: Carl Ras — Dataverse write-back (outbound.Dataverse_Account/_Contact, feeding a new app)
status: in-progress
created: 2026-09-02
project: customers/Carl-Ras/datahub
owner: fabric-back
priority: medium
blocked_by:
fno_task:
source: session
---

## What
Feed a **new app being developed on Dataverse** with accounts and contacts from curated — into
**new custom tables**, not the F&O-backed `account`/`contact`. Only a **subset**: a "current
account" definition (accounts with recent orders), because pushing all of them is neither wanted
nor cheap. The filter must be easy to change, and adding a further outbound table must be cheap.
Built for Carl Ras now, intended to become part of Atomic.

Because the tables are ours: bulk messages are available (any custom table supports
`CreateMultiple`/`UpdateMultiple`, hence `UpsertMultiple`), we define the alternate keys, and
nothing else writes the rows — so the never-create rule and the three-state null policy from the
Marketo push do not carry over. The table is a projection of curated.

Reuses the outbound layer decided 2026-08-13 for Marketo (`CLAUDE.md` > Conventions > Outbound):
`outbound` schema in `Warehouse_Curated`, `viewoutboundtransform` holds the logic,
`PL_Transform_Curated_Outbound` materialises every view in that schema automatically.

## Done
- Research complete and written up: `design/DATAVERSE_WRITEBACK_DESIGN.md` (2026-09-02) — the write
  paths and why `$batch` wins, the filter, the alternate keys, ordering, limits, retirement, the
  environment/credential shape, and the five open questions.
- Settled with Niels: standard `account`/`contact` (not custom, not F&O), DEV environment
  `https://carl-ras-dev.crm17.dynamics.com/`.

## Next
1. **Decide physical tables vs Fabric-sourced virtual tables** with the app team — the one
   question that changes everything downstream. Test: does the app need to write its own state on
   the row, relate the rows to other Dataverse tables, or use row-level security, auditing,
   dashboards, search or business process flows? Any yes rules out virtual tables.
2. Get the **Dataverse environment URL(s)** and whether DEV/TEST/PROD point at one environment or
   several — decides `VL_ConnectionId` vs a pinned env-invariant URL.
3. Agree the **table and column contract with the app team**, then define the **alternate keys**
   (`accountnumber` = AX09 `CustAccount`; contact keyed on `ContactPersonId`).
4. Settle the **"current account" filter** — the `AccountWindow` CTE already in
   `viewoutboundtransform.Marketo_Lead` (any order in the last 365 days) is the existing precedent.
5. Settle **retirement**: upsert never deletes, so accounts that leave the window persist.
   Proposed: stamp every row with the push's run id / timestamp, and let the app filter on it or a
   `BulkDelete` query remove the unstamped.
6. Build `viewoutboundtransform.Dataverse_Account` + `_Contact`, `NB_Outbound_Dataverse`,
   `PL_Outbound_Dataverse`, and `Lakehouse_Util.DataverseOutboundLog` mirroring `MarketoOutboundLog`.

## Notes
- Entitlement (Power Platform request) limits count **every row**, batched or not — the subset
  filter is a cost decision, not only a performance one.
- Service protection limits: 6,000 requests / 20 min execution / 52 concurrent, per user per web
  server, 5-minute sliding window; honour `Retry-After`.
- `UpsertMultiple` on a standard table rolls the **whole** request back on any one error, and
  returns no per-record result. Batch 100-1,000, be ready to fall back to `$batch`.
- Contacts must be pushed **after** accounts: the lookup to the parent is set with
  `"<lookup>@odata.bind": "cr_accounts(cr_accountnumber='NNNN')"`, which needs the parent to exist.
- Virtual tables require a **GUID primary key** on the source, so an outbound view feeding one
  would have to generate a deterministic GUID column.
