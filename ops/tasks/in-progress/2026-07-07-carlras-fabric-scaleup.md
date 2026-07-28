---
title: Carl Ras — implement Fabric scale-up + semantic model processing (existing python script)
status: in-progress
created: 2026-07-07
project: customers/Carl-Ras/datahub
owner: fabric-back
priority: normal
blocked_by:
activity:
fno_task:
source: todo
---

## What
Implement scale-up of the Fabric capacity and processing of the semantic model at Carl Ras,
using the existing python script.

## Why
Standing TODO from 2026-07-06; the platform work the Datahub implementation needs.

## Context
- Project: `customers/Carl-Ras/datahub` (`230-02`). This task was previously its own project
  folder `Carl-Ras/fabric`; merged into `datahub` on 2026-07-28 — it was a second repo
  (`Fabric-ETL`), not a second project. State carried over into `datahub/CONTEXT.md`
  > *Workstream — Fabric scale-up & model processing*.
- Code lives in `datahub/Fabric-ETL` (`NB_CapacityManager_Bootstrap`, `PL_ScaleProcess_SP`).

## Log
- 2026-07-07 — created (promoted from TODO 2026-07-06 at the day-start routing pass)
- 2026-07-23 — open → in-progress (work ran 07-17): CapacityManager deployed to the Carl Ras workspace; auth chain (WI → AKV → SP → ARM) verified end-to-end through three debug iterations (KV firewall disabled by customer, wrong app id in `scale-sp-id` fixed, error-body surfacing added to the notebook). Scale-up now blocked on the subscription's regional Fabric CU quota (16/16 used, F32 requested) — quota increase with the Carl Ras admin is the next step. Note: the "existing python script" became the CapacityManager asset (own/CapacityManager); session forgot /switch-task at start — time for 07-17 attributed by the hooks but not task-tagged.
