---
id: carlras-record-drift-twelve-task-sweep
ts: 2026-08-31T10:30:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: session:f17772e8-6514-4c38-b590-03daab4595e6
tags: [project, continuity, task-store, verification, process]
status: distilled
description: "Carl Ras: 8 of 12 open tasks were STALE-BEHIND - the record lags the service, not the other way round, and two recorded blockers had cleared days earlier unnoticed"
---

Measured 2026-08-31: one read-only agent per open task, each checking DEV, TEST and PROD against the
three repos. Verdicts: **8 stale-behind, 4 accurate. Zero stale-ahead.**

## The pattern

The drift runs one way. Nothing was recorded as done that wasn't; plenty was done and never written
back. Parallel sessions and hand-fixes in the service outrun the task files, and a task file left
alone for a week understates progress rather than overstating it.

Two blockers had cleared with nobody noticing:

- The Fabric regional CU quota was raised **16 -> 32** between 08-12 and 08-19. Scale-up had been
  succeeding since, and runs inline in `PL_MainExecution` in DEV and TEST. The task still read
  "blocked on quota" from 07-23.
- The Marketo inbound chain (dedupe fix `a106aec`) completed in **both** environments on 08-21 —
  33,315 leads at one row per id. The task still read "blocked, fix ready and unproven".

Both had been true for ten days. Neither cost anything except the work not restarting.

## What the record over-stated

- "TEST is down" — TEST had been building data every weekday; only the terminal `Fail Scale Up`
  marker failed, and the model refreshed. A `Failed` run status is not "no data": read the stage.
- "`Warehouse_Enriched_GTM` is not in the workspace" — it is, in DEV and TEST.
- "TEST is not ready for Direct Lake" — deploy steps 1-3 were already done.
- "`dim.Date` rebuilds EMPTY" — populated in both environments, and the mechanism was misattributed
  to the routine drop-create rather than to `Update from git` / DacFx.

## The finding that was worse than recorded

`fact.GeneralLedgerTransactions` in **PROD holds 353 rows, 2026-07-01 to 07-31** — frozen from a
July rebuild. The current-month-window defect is no longer a prediction; it has fired in production.
TEST holds August only. Enriched retains full history (113M rows to 2001) everywhere.

## Process consequence

A verification sweep of this shape is cheap relative to what it corrects, and the value is
concentrated in the *contradictions*: three separate agents measured `dim.Date`, and two contradicted
measurements taken earlier the same session. Both contradictions were resolved by re-measuring
directly, not by preferring the newer report — one of them (the Graph group membership) was the agent
being wrong. See `graph-guest-group-member-enumeration`.
