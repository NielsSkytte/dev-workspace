---
title: Carl Ras — implement Fabric scale-up + semantic model processing (existing python script)
status: in-progress
created: 2026-07-07
project: customers/Carl-Ras/fabric
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
Standing TODO from 2026-07-06; also the concrete work that fleshes out the `Carl-Ras/fabric`
placeholder project (v1-review Next item).

## Context
- Project: `customers/Carl-Ras/fabric` (PLACEHOLDER — confirm scope and locate the existing
  python script as the first step; see its CONTEXT.md).
- Carl-Ras node: shared infra picture; fno_code for datahub is 230-02, fabric placeholder has
  none on file yet.

## Log
- 2026-07-07 — created (promoted from TODO 2026-07-06 at the day-start routing pass)
- 2026-07-23 — open → in-progress (work ran 07-17): CapacityManager deployed to the Carl Ras workspace; auth chain (WI → AKV → SP → ARM) verified end-to-end through three debug iterations (KV firewall disabled by customer, wrong app id in `scale-sp-id` fixed, error-body surfacing added to the notebook). Scale-up now blocked on the subscription's regional Fabric CU quota (16/16 used, F32 requested) — quota increase with the Carl Ras admin is the next step. Note: the "existing python script" became the CapacityManager asset (own/CapacityManager); session forgot /switch-task at start — time for 07-17 attributed by the hooks but not task-tagged.
