---
id: servicenow-landed-mode-full-load-traffic
ts: 2026-10-28T19:10:00Z
type: semantic
scope: project:customers/Aeven/AtomicServiceNow
source: session:0d50bc3e
tags: [servicenow, ingestion, delta, aeven]
status: distilled
description: "catalogue_source 'landed' forced full_reload on every run, so the daily schedule copied all 23 tables daily (~410k rows, 0.44 GB); fix: deltas on sys_updated_on, Saturday full, load_weekday for sys_dictionary/sys_db_object; config in SQL_Util only"
---

Aeven reported heavy traffic ("1TB of transactions") after the daily schedule was enabled. ingest_log
10-20..10-28 showed 10 runs, each a full read (~0.44 GB, 3-5 min); 1 TB is not explained by these runs.
Cause: `catalogue_source: "landed"` forced `full_reload` (`tools/build_notebooks.py`, `3723b21`), meant for
the access-testing phase. Fix `42305a8`; weekly full load stays as a safety net for deletes, access
changes, silent updates and new fields. Config one copy in `SQL_Util.dbo.servicenow_tables`/`servicenow_columns`
(`e257a81`, Niels: nothing repo-based). Before enabling a schedule on a source, check that it runs deltas.
