---
title: DataCompare events into Matas's Application Insights
status: open
created: 2026-10-06
project: customers/Matas/DataCompare
owner: fabric-back
priority: normal
blocked_by: Application Insights resource access + SPN (not yet requested)
activity: 110383        # same as Task-72114: all work after 2026-09-14 books there
fno_task: Task-72114
customer_ask: open
waiting_on:
resume_on:
source: direct
---

## What
The daily DataCompare run (Dev and Prod) sends its events to Matas's Application Insights, grouped so
a reader can tell where an event came from. Matas will log F&O information to the same Application
Insights later, so the grouping must hold for more sources than DataCompare.

Done when: a Prod run posts RunSummary / FindingNew / FindingResolved / FindingAccepted to Matas's
Application Insights under a service principal, events carry a source and environment grouping, and
the Matas colleague who asked has been shown it.

## Why
Matas asked (Teams chat, 2026-10-06) whether we have worked with Application Insights: they also need
to log information from F&O and are unsure how it should be shown, expecting a grouping by origin.
They asked to be shown once we have it working, and will say when they start on the F&O side.

## Progress
**Now (2026-10-06):** `prototype/appinsights.py` computes the four events from the two latest runs of
every active pair (each carries `pair`) and posts to the track endpoint; it dry-runs without
`DC_APPINSIGHTS_CONNECTION_STRING`. It is not called by the daily notebook (`fabric_run.main` only loads).
**Tried and dropped:** -
**Next:**
1. Request from Matas: which Application Insights resource (connection string), and an SPN with access
   (owner said he would order it).
2. Grouping: set `cloud_RoleName` = `DataCompare` (source system) and a custom dimension `environment`
   (dev/prod) on every event, so F&O can use its own role name in the same resource. Agree the
   convention with Matas before they start on F&O.
3. Call `appinsights.py` from `fabric_run.main()` after the load; connection string per environment
   (Key Vault or `fabric_sql.ENVIRONMENTS`), never in code.
4. Show it to the Matas colleague: a saved query / workbook per source.

## Needs from customer
- **Matas:** Application Insights resource (connection string) and an SPN with access to it. Not sent.

## Context
- `prototype/appinsights.py`, `prototype/fabric_run.py`, `prototype/README.md` (Dev and Prod).
- CONTEXT_DECISIONS 2026-09-07 "Headline status lives in the data" (every figure must exist as data for
  Application Insights).
- Related: `2026-09-21-matas-datacompare-production` (Prod went live 2026-10-06).

## Log
- 2026-10-06 — created from the Teams chat with Matas about Application Insights and F&O logging
