---
title: Carl Ras — confirm the Census sync and the source mapping behind the Marketo field push
status: open
created: 2026-08-10
project: customers/Carl-Ras/datahub
owner: fabric-back
priority: normal
blocked_by:
activity: MarketoImport
fno_task:
source: handoff
---

## What
Originally: "find out who computes and pushes the AX09 aggregates into Marketo." **Mostly
answered.** Rescoped 2026-08-12 to the questions that are actually still open.

The chain is now established end to end:

```
AX09 -> Impact's Databricks silver_* -> gold_census_contacts -> Census
     -> Marketo (importLead, ben+carlras@impact.dk, ~07:10 UTC daily)
```

**Priority dropped from high to normal.** It was a blocker because the Store/Online split rule
was unobtainable. We have the SQL; it is no longer a blocker.

## Answered — do not re-ask
1. **Which account writes?** `ben+carlras@impact.dk` — Impact's, 99.8% of API-sourced changes.
2. **How often?** Daily, 2-3 bulk `importLead` batches inside 07:08-07:14 UTC, ~2,948 leads x 25
   fields each.
3. **What tool?** Census, now shipping as "Fivetran Activations" (Fivetran acquired Census
   2025-05-01). Explains why Niels recalled both names.
4. **What is the transformation?** We hold it — four Databricks DLT files in `datahub/data/`,
   delivered 2026-06-22 with the GTM access and never described. See
   `design/MARKETO_WRITEBACK_GOAL.md` sections 3-4.
5. **Store vs Online?** Solved, and it is three different rules: `WebOrderId != '0'` at account
   grain, `len(WebOrderId) > 2` for contact dates, and a 28-value `departmentId` whitelist for
   contact store counts.
6. **`Account Segment1` / `Account Discount Group`?** Master data from `silver_customer`, not
   computed.

## Still open
1. **Is the June SQL snapshot still current?** The files are from 2026-06-22. Partly self-checking
   — a ported rule that reproduces the reference set for June but not August indicates drift
   (goal doc 4.6) — but a direct confirmation is cheaper.
2. **The Census sync itself.** The transformation is the warehouse side; the sync holds the
   mapping to Marketo field names (`LatestOrderDateAccount` -> `Latest Purchase Date Account`),
   the schedule, the matching identifier, and the **sync behaviour** (Update Only / Update or
   Create / Mirror). That last one answers full-vs-delta push, which Marketo cannot tell us
   because it logs no no-ops. Ask for screenshots of the sync's mapping page and schedule —
   Census is dashboard-configured, there is no config file.
3. **`silver_*` -> AX09 mapping.** The SQL reads `silver_order`, `silver_contact`,
   `silver_customer`, `silver_address`, plus `inriver_productdata` and `lookup_tables.cr_segment`.
   Which AX09 tables and columns these correspond to is **not established**, and it is the real
   work in the port. `LineAmountMST`, `InventTransId`, `departmentId`, `WebOrderId` and `Status`
   are the load-bearing columns.
4. **`HasWebLogin` needs Microsoft Graph** — `prod.msgraph.users__identities`, not AX09. Is that
   source available to us, or does the field get dropped?
5. **Who writes the custom objects** (`purchase_c`, `orderLine_c`)? Their activities carry no
   `Modifying User`, so it cannot be derived. Their write pattern spreads across the working day
   rather than batching, which points at the webshop or a middleware rather than Impact's
   warehouse — **if so it is out of scope for the takeover.**
6. **Are we replacing the incumbent or running alongside first, and who agrees the cutover date?**
7. **`lookup_tables.cr_segment` and `inriver_productdata`** are referenced but not supplied. Only
   `cr_segment` matters for the segment flags; `inriver_productdata` feeds brand fields that never
   reach Marketo.
8. **Nine defects need a reproduce-or-fix decision** (goal doc section 7). Three are real bugs:
   store order count counts distinct dates instead of order ids; account-grain counts and dates
   ignore the `Status = 'Delivered'` filter that the sums apply; email dedupe is
   nondeterministic. Raising these with Impact is also a courtesy — they are live defects in a
   system Impact still owns.

Kasper (Impact) is the contact. Simon internally may know which side owns the order feed.

## Why it still matters
Retiring Databricks stops those Marketo fields updating. Nothing errors — segmentation just starts
targeting stale numbers. The transformation being in hand removes the largest unknown, but the
`silver_*` -> AX09 mapping (item 3) is now the critical path.

## Log
- 2026-08-10 — created (handoff from the Marketo activity-data exploration)
- 2026-08-12 — Census/Fivetran identified; Impact's gold SQL found in `datahub/data/`; rescoped,
  priority high -> normal, six questions closed and the source-mapping gap opened
