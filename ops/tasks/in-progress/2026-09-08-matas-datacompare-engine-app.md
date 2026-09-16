---
title: DataCompare compare engine and app
status: in-progress
created: 2026-09-08
project: customers/Matas/DataCompare
owner: self
priority: normal
blocked_by:
activity: 111953        # the activity for 212-01; both tasks book to it (owner, 2026-09-08)
fno_task: Task-65904
customer_ask: open
waiting_on:
resume_on:
source: session
---

## What
Build and run the DataCompare comparison engine and the app on top of it: the compare and load
pipeline, the daily run, the findings UI, the acceptance-rule mechanism and its register.

## Progress

**Now (2026-09-10):** the compare engine runs daily 05:00 UTC as `NB_DataCompare_Daily` in
`GFO_DataCompare_ETL_Dev` against `SQLDB_DataCompare` (first unattended run 09-08: agreement 92.0 %,
11,502 matched); it is entity-keyed (`FIELDS`, `ADAPTERS`, `dc.compare_pair.entity`) and verified
against the vendor output (333,442 compared values, 42,998 findings). The app (findings, value pairs,
vendors, rules register, method card) runs on the local relay only. The overview deck
(`design/presentation/`) was revised with the owner 09-10 and not yet shown to Matas. Customer data is
the gate for the next entity, not the code.

**Tried and dropped:** the local Windows scheduled run (`run_daily.ps1`) -> the Fabric notebook run,
kept as disabled fallback; "source" as the word for the non-master side -> "compared" (source read as
where the data comes from); label tables (PaymTerm, PaymMode) as compared entities -> joined for
context only, because MFO Danish against GFO English reports a translation as a data error.

**Next:**
1. Verify `NB_DataCompare_Daily` is committed in the Matas repo (the record contradicts itself);
   settle `seed_static.sql` GFO-master vs the prototype's MFO.
2. Show Matas the deck, then the app; each ruling on the big buckets becomes an acceptance rule.
3. Send email 06 (app registration, Fabric Apps tenant setting, capacity region) and email 05
   (`CustTable` + `CustBankAccount`); the day the client id arrives: `adapter-graphql.js`, the Azure
   Static Web App, and `load_sql.py` + `appinsights.py` into a scheduled Fabric Python notebook.
4. Customers, the day the tables land: overlap check on `CustAccount` across the legal-entity map,
   row counts per legal entity both sides, is GFO `CustBankAccount` populated, then the adapter.
5. Deploy the config store (`src/config-store/`); move `COMPANY_MAP` and the derived recode maps
   into `cfg.*`.

## Needs from customer

- **Matas:** `CustTable` + `CustBankAccount` on both Link-to-Fabric scopes (email 05). **Not sent.**
- **Matas:** app registration for the static track, Fabric Apps tenant setting, capacity region
  (email 06). **Not sent.**
- **Matas:** which table/field is "Buy from creditor" in GFO; whether `PaymTerm`/`PaymMode` should
  join the scope. **Not asked.**

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
