---
title: DataCompare compare engine and app
status: done
created: 2026-09-08
project: customers/Matas/DataCompare
owner: self
priority: normal
blocked_by:
activity: 111953        # the activity for 212-01; both tasks book to it (owner, 2026-09-08)
fno_task: Task-65904
customer_ask: none
waiting_on:
resume_on:
source: session
---

## What
Build and run the DataCompare comparison engine and the app on top of it: the compare and load
pipeline, the daily run, the findings UI, the acceptance-rule mechanism and its register.

## Progress

**Now (2026-09-21):** done. The PoC was first demoed on 2026-09-10 and demoed with the deck and the
app on 2026-09-14, when Matas approved it. `NB_DataCompare_Daily` is on `origin/main` of
`GFOERPDataAnalysis` (last commit 2026-09-08). Master is MFO until 2026-11-01, then GFO, as agreed
with Matas. The work continues under `2026-09-21-matas-datacompare-production` (Task-72114).

**Tried and dropped:** the local Windows scheduled run (`run_daily.ps1`) -> the Fabric notebook run,
kept as disabled fallback; "source" as the word for the non-master side -> "compared" (source read as
where the data comes from); label tables (PaymTerm, PaymMode) as compared entities -> joined for
context only, because MFO Danish against GFO English reports a translation as a data error.

**Next:** -

## Needs from customer

- **Matas:** `CustTable` + `CustBankAccount` on both Link-to-Fabric scopes (email 05). **Resolved:**
  synced (owner, 2026-09-21).
- **Matas:** app registration, Fabric Apps tenant setting, capacity region (email 06). **Resolved:**
  old; the region is West Europe (owner, 2026-09-21).
- **Matas:** "Buy from creditor" in GFO: unresolved, out of scope for now. `PaymTerm`/`PaymMode`:
  joined the scope (owner, 2026-09-21).

## Why
This is the delivery itself. It was being tracked against `2026-07-06-matas-enhance-user-stories`,
which is a different piece of work (the DevOps user stories).

## Context
- F&O: project 212-01, activity 111953, task **65904** = the engine and the app; **65905** = the
  configuration work (Link to Fabric, access, setup). Both use activity 111953. The earlier note in
  `2026-07-06-matas-enhance-user-stories` claimed 65904 was never created - wrong, corrected by the
  owner 2026-09-08.
- The daily run is `NB_DataCompare_Daily` in `GFO_DataCompare_ETL_Dev`, 05:00 UTC.
- Code: `customers/Matas/DataCompare/prototype/` (source of truth), deployed to the lakehouse by
  `deploy_fabric.py`. Notebook item lives in the Matas DevOps repo.

## Log
- 2026-09-08 - opened when the owner confirmed 65904 covers the engine and app work; session re-tagged
  from `2026-07-06-matas-enhance-user-stories`. Heartbeats before the switch carry the old slug and are
  corrected in the timesheet at /log, never in the heartbeats themselves.
- 2026-09-16 — brought onto the Progress shape (Progress + Needs from customer, fno_task Task-65904, customer_ask open); no facts changed. Card: CONTEXT.md converted to the resume card.
- 2026-09-21 - check-in: done. PoC demoed 2026-09-10 and 2026-09-14, approved 2026-09-14; emails 05/06 resolved; master MFO until 2026-11-01 then GFO. All Matas work up to and including 2026-09-14 books here (Task-65904); after that to Task-72114.
