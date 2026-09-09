---
title: Move the DataCompare daily run from this machine into Fabric
status: done
created: 2026-09-08
project: customers/Matas/DataCompare
owner: fabric-back
completed: 2026-09-08
priority: normal
blocked_by:
activity: 111953        # F&O activity for 212-01
fno_task: Task-65905
source: session
---

## What
Port `pull.py` -> `compare.py` -> `load_sql.py` into notebooks in `GFO_DataCompare_ETL_Dev`,
orchestrate them in a Data pipeline and schedule it daily, replacing the Windows scheduled task
`DataCompare daily run` that runs the same three steps on Niels's machine.

## Why
The local task authenticated as Niels through the fab CLI token cache, so it stopped the moment the
token lapsed or the machine was off, and it copied Matas vendor data to a laptop every morning.

## Context
- Local runner: `prototype/run_daily.ps1`, logs to `prototype/logs/daily-<date>.log`, Windows task
  `DataCompare daily run`, daily 07:00, StartWhenAvailable, runs only while Niels is logged on.
- `DC_NONINTERACTIVE=1` makes `fabric_sql.connect` fail rather than open a sign-in dialog. The Fabric
  version needs no such guard - it needs an identity.
- What to request from Matas: an identity for the pipeline with read on the two managed lakehouses
  (`dataverse_matas_...` = MFO, `dataverse_matasgroup_...` = GFO) and write on the DataCompare Fabric
  SQL database.
- A run must stay decoupled from accepting a rule: accepting, retiring and reactivating change the
  latest run's numbers in place and must not trigger a run (owner, 2026-09-08).
- The rule set a run was judged under is recorded in `dc.run_rule`; the Fabric loader must write it
  the way `load_sql.py` does.

## Log
- 2026-09-08 - raised when the local daily schedule was wired; owner deferred the Fabric build
- 2026-09-08 - owner reversed the same day: built and done. `NB_DataCompare_Daily` in
  GFO_DataCompare_ETL_Dev, scheduled daily 05:00 UTC, verified by a real run (2026-09-08 09:31,
  agreement 91.0%, 4 rules recorded) that matches the local run of the same morning. The notebook is
  thin: `prototype/deploy_fabric.py` uploads compare/load_sql/fabric_sql/fabric_run to
  `LH_DataCompare/Files/code`, so local and Fabric run the same code. No extract step in Fabric -
  DuckDB's delta reader reads the lakehouses in place, so `pull.py` has no Fabric counterpart and no
  Matas data lands on a disk. The Windows task is disabled, not deleted.
- 2026-09-08 - probe NB_Probe_DailyRun (deleted after use) settled the runtime questions: python
  3.12.12, duckdb 1.4.4 with azure + delta, ODBC Driver 18, and pyodbc read AND write to the
  DataCompare SQL database with a notebookutils token for audience
  https://database.windows.net/.default.
- Remaining, optional: the schedule runs under the user who created it (Microsoft: a scheduled
  notebook runs as the schedule's creator). A service principal as the pipeline's last-modified user
  is the upgrade that survives that account being unavailable - not needed while developing.
