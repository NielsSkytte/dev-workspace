---
title: DataCompare after PoC approval (production)
status: in-progress
created: 2026-09-21
project: customers/Matas/DataCompare
owner: self
priority: normal
blocked_by:
activity: 110383        # consultant activity on Task-72114 -- F&O derives it from the task (owner, 2026-09-29; was 111953)
fno_task: Task-72114
customer_ask: open
waiting_on:
resume_on:
source: checkin
---

## What
All DataCompare work after the PoC approval on 2026-09-14: move to production, the customer entity,
the master switch to GFO, and getting Matas's people onto the app.

## Progress

**Now (2026-09-21):** the PoC was demoed (deck and app) and approved on 2026-09-14. `CustTable` and
`CustBankAccount` are synced into Link to Fabric. `GFO_DataCompare_ETL_Prod` is ready. Master is MFO
until 2026-11-01, then GFO, as agreed with Matas.

**Tried and dropped:** -

**Next:**
1. Move to production: all data used is already production data; only the database that stores the
   rules etc. is kept as separate Dev and Prod.
2. Master flag MFO -> GFO on 2026-11-01; people at Matas reach the app by 2026-11-01.
3. Customers: match evidence first, then the adapter.
4. Configurable match keys (point to an existing primary key, or create a composite key) and a
   first-seen date on every unhandled finding.

## Needs from customer

- **Matas:** rulings on the big buckets (on-hold All->No 2,497; the `%1` address placeholder; bank
  accounts and person names not migrated; 90 vendors without a GFO address; 38 on-hold vendors not
  migrated). Each ruling becomes an acceptance rule. **Owed.**

## Why
Task-72114 is the F&O task for all Matas work after 2026-09-14 (owner, 2026-09-21). Work up to and
including 2026-09-14 books to Task-65904.

## Context
- F&O: project 212-01, activity 110383 (consultant), Task-72114. Task-65904 books to 111953.
- Before this: `2026-09-08-matas-datacompare-engine-app` (Task-65904), closed 2026-09-21.

## Log
- 2026-09-21 - created at check-in; the owner named Task-72114 for all work after 2026-09-14.
  Matas heartbeats on 2026-09-18 and 2026-09-21 before the re-tag carry the engine-app slug and are
  corrected to Task-72114 in the timesheet at /log, never in the heartbeats.
