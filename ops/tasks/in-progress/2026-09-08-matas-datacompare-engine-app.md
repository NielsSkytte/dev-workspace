---
title: DataCompare compare engine and app
status: in-progress
created: 2026-09-08
project: customers/Matas/DataCompare
owner: self
priority: normal
blocked_by:
activity: 111953        # the activity for 212-01; both tasks book to it (owner, 2026-09-08)
fno_task: Task-65904    # opgave for the compare engine and the app (owner, 2026-09-08)
source: session
---

## What
Build and run the DataCompare comparison engine and the app on top of it: the compare and load
pipeline, the daily run, the findings UI, the acceptance-rule mechanism and its register.

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
