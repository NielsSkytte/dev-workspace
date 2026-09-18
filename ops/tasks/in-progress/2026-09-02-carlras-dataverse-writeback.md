---
title: Carl Ras — Dataverse write-back (outbound.Dataverse_Account/_Contact, feeding a new app)
status: in-progress
created: 2026-09-02
project: customers/Carl-Ras/datahub
owner: fabric-back
priority: medium
blocked_by:
fno_task: CarlRData-557
customer_ask: none
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

## Progress

**Now (2026-09-14):** population complete in `org8a074fed.crm4` on 2026-09-14 (34,913 accounts /
44,526 contacts, every contact parent-bound); the delta push is proven (50 sent, immediate rerun 0);
token-expiry (`e852ac4`) and percent-encoded parent key (`54ffbda`) fixes are in git and await one sync.

**Tried and dropped:** `TOP (5000)` as the selection cap -> a 365-day window on the contact's own order
(`c23022f`, 09-14); `UpsertMultiple` and the Copy activity -> Web API `$batch`, which returns per-record
status (09-02); custom tables -> the standard `account` / `contact` (Niels, 09-02).

**Next:**
1. `dataverse_url` into a variable library with per-stage value sets (today a run-time parameter, no default).
2. Least-privilege application-user role (design section 10) before any TEST/PROD environment.
3. Schedule `PL_Outbound_Dataverse` after `PL_Transform_Curated_Outbound` in `PL_MainExecution` once
   Patrick confirms the app takes a daily delta.

## Needs from customer

- **Carl Ras:** none.
- **Patrick (Pingala, internal):** confirm the app is ready for a daily delta and whether push failures
  should land in his `cr_processerrorlog` — status not recorded.


## Done
- Research complete and written up: `design/DATAVERSE_WRITEBACK_DESIGN.md` (2026-09-02) — the write
  paths and why `$batch` wins, the filter, the alternate keys, ordering, limits, retirement, the
  environment/credential shape, and the five open questions.
- Settled with Niels: standard `account`/`contact` (not custom, not F&O), DEV environment
  `https://carl-ras-dev.crm17.dynamics.com/`.

## Next
0. ~~Delta push~~ **shipped and proven 2026-09-14** (`22c157e`): rerun of 50 accounts sent 0.
   New environment `org8a074fed.crm4` fully loaded (3,831 / 5,000, 0 failed). Tables serialised
   in git (`abf775a`). Window shipped (`c23022f`) and fully pushed 2026-09-14: 34,913 accounts /
   44,526 contacts in `org8a074fed.crm4`, all parent-bound. Two defects found and fixed on the way:
   token expiry mid-run (`e852ac4`), percent-encoded parent key in the bind body (`54ffbda`).
   Remaining: `dataverse_url` to a variable library, least-privilege role, schedule the daily delta.
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

## Log
- 2026-09-17 — scope: Customer Insights - Data segmentation (CI trial env) is part of the same app delivery and billed here for now, per Niels; may be split out later (Niels will say). Set up 2026-09-16/17: lakehouse view `dbo.CI_SalesInvoice` over shortcuts to TEST `enriched.SalesInvoiceTransactions` + `dim.Customer` (invoice-journal grain, key `DataArea|RecId_CustInvoiceJour`, verified unique in DEV and TEST), loaded via Power Query; Customer via OneLake; SalesOrder activity; RFM + measure-based suggestions. Not in any repo by choice.
- 2026-09-16 — brought onto the Progress shape (Progress + Needs from customer, `fno_task` / `customer_ask` set, `activity` blanked per CLAUDE.md task-always rule); no facts changed. Card: `customers/Carl-Ras/datahub/CONTEXT.md`.
