---
title: Carl Ras — Dataverse write-back (outbound.Dataverse_Account, filtered subset of accounts)
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
Write selected curated dimensions back to Dataverse, starting with **accounts** and only a
**subset** (a "current account" definition — accounts with recent orders), because writing all
accounts is neither wanted nor cheap. The filter must be easy to change, and adding a second
outbound table must be cheap. Built for Carl Ras now, intended to become part of Atomic.

Reuses the outbound layer decided 2026-08-13 for Marketo (`CLAUDE.md` > Conventions > Outbound):
`outbound` schema in `Warehouse_Curated`, `viewoutboundtransform` holds the logic,
`PL_Transform_Curated_Outbound` materialises every view in that schema automatically.

## Done
- Research: the write paths from Fabric to Dataverse, their limits, and the Atomic fit
  (2026-09-02 session).

## Next
1. **Answer the two blocking questions** — which Dataverse environment (and why: D365 CE / a
   Power App / dual-write), and whether the push may CREATE accounts or must be update-only.
2. **Test whether `account` supports `UpsertMultiple`** — one GET on `sdkmessagefilters`. Decides
   between the bulk action and `$batch` / parallel single upserts.
3. Confirm or create the **alternate key** on `account` (candidate: `accountnumber` = AX09
   `CustAccount`); without one there is no key from our side into Dataverse.
4. Settle the **"current account" filter** — the `AccountWindow` CTE already in
   `viewoutboundtransform.Marketo_Lead` (any order in the last 365 days) is the existing precedent.
5. Build `viewoutboundtransform.Dataverse_Account` + `NB_Outbound_Dataverse` + `PL_Outbound_Dataverse`,
   with a `Lakehouse_Util.DataverseOutboundLog` mirroring `MarketoOutboundLog`.

## Notes
- Entitlement (Power Platform request) limits count **every row**, batched or not — the subset
  filter is a cost decision, not only a performance one.
- Service protection limits: 6,000 requests / 20 min execution / 52 concurrent, per user per web
  server, 5-minute sliding window; honour `Retry-After`.
- The three-state rule (value / factual 0 / unknown-omitted) applies here too, but Dataverse
  coercion has not been measured — do not assume Marketo's behaviour.
