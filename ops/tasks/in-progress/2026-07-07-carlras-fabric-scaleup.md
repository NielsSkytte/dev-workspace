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
- 2026-08-31 — **VERIFIED against the live service: the recorded blocker is GONE and was never
  written back.** The regional CU quota was raised 16 -> 32 between 2026-08-12 and 2026-08-19. A
  scale-up that failed 08-12 with `TotalCapacityUnits:16, RegionalQuota:16, RequestedSku:32`
  succeeded repeatedly on 08-19 and 08-21 (last 16:24:38-16:42:17, Completed), and the scale now
  runs inline inside `PL_MainExecution` in DEV and TEST. **This task is no longer blocked on quota.**
  - **New, undocumented blocker:** a run on 08-19 18:25 requested **F64** and hit the raised ceiling
    (`RegionalQuota:32, RequestedSku:64`). Nothing records whether F64 is a goal or a one-off probe.
  - **PROD has none of the capacity items** — no `PL_ScaleProcess_SP`, no
    `NB_CapacityManager_Bootstrap`, no `VL_Capacity`. PROD's `PL_MainExecution` is a 3-activity stub
    (Raw / Enriched / Curated) with no scale activities and no `VL_Capacity` reference, so the
    standing worry that "missing `VL_Capacity` fails PROD at submit" is **wrong** — PROD never binds
    it. This is a promotion gap, not a latent failure.
  - `PL_ScaleProcess_SP` still carries its Refresh Semantic Model step in DEV; the "now redundant,
    strip it" recommendation was never actioned.
  - The capacity object `f54ce0e2…` itself is unreadable by this account (no role) — SKU state is
    taken from job telemetry, not a direct read.
  - **Inference, not measurement:** Direct Lake removes the refresh memory pressure that motivated
    this task, but only in DEV, where it is built. TEST and PROD still run the Import model, so the
    rationale survives there until Direct Lake is promoted.
- 2026-07-07 — created (promoted from TODO 2026-07-06 at the day-start routing pass)
- 2026-07-23 — open → in-progress (work ran 07-17): CapacityManager deployed to the Carl Ras workspace; auth chain (WI → AKV → SP → ARM) verified end-to-end through three debug iterations (KV firewall disabled by customer, wrong app id in `scale-sp-id` fixed, error-body surfacing added to the notebook). Scale-up now blocked on the subscription's regional Fabric CU quota (16/16 used, F32 requested) — quota increase with the Carl Ras admin is the next step. Note: the "existing python script" became the CapacityManager asset (own/CapacityManager); session forgot /switch-task at start — time for 07-17 attributed by the hooks but not task-tagged.
