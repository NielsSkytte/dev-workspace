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

**Now (2026-10-09):** Prod live since 2026-10-06 (own SQL DB, release = pipeline `DataCompare` only).
Dev on branch `dev` at 21fdd13: rule kinds (mapping, normalise, on-hold condition; `rules.py`), rule
builder with value list + preview, Excel mapping import (one mapping rule per field), match keys in
`compare.MATCH_KEYS` recorded in `dc.match_key`; schema migrate_v4 (add-only) committed ad966e8.
Dev run 2026-10-09 11:47-11:50 UTC Completed: Vendor 11,591 matched, 232 open, 40,625 accepted;
Customer 0 matched (GFO holds only 5 GFO-RCM placeholders). Prod still runs the 2026-10-06 notebook.

**Tried and dropped:** pushing to `main` (Matas policy needs a PR) -> branch `dev`. `deploy_fabric.py`
upload -> code generated into the notebook. One accept rule per Excel line -> one mapping rule per field.

**Next:**
1. Release to Prod through the pipeline (SQLDB first, then notebook) when the owner says so.
2. Customer page with 0 matched: show the missing lists first and say why (offered 2026-10-09, not answered).
3. Rule builder slice 2: missing-record rules, conditions on other fields (DESIGN-custom-rules.md).
4. Hosting at Matas: SPN connection in `fabric_sql.connect`, API package, resource group + SPN.
5. Master flag MFO -> GFO and people at Matas in the app, both by 2026-11-01.

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
- 2026-10-09 - rule kinds, builder, mapping import and match keys released to Dev (21fdd13); Dev run Completed.
