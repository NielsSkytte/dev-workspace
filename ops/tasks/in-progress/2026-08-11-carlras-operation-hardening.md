---
title: Carl Ras — operation_hardening (keep PL_MainExecution running green across DEV/TEST/PROD)
status: in-progress
created: 2026-08-11
project: customers/Carl-Ras/datahub
owner: fabric-back
priority: normal
blocked_by:
activity:
fno_task:
source: direct
---

## What
operation_hardening — make the daily `PL_MainExecution` chain run green and keep it that way.
Covers the run-failure work that follows the SPN-auth migration and the key-map/join fixes:
diagnosing and closing each remaining failure in the chain, and removing the classes of
fragility that produce them.

Open at creation (measured 2026-08-11):
- **TEST**: scheduled runs 08-10 and 08-11 fail at the last stage only — `Semantic Model` →
  `PL_Update_SemanticModel` → `Notebook1` (`NB_Refresh_SemanticModel`), `403 Forbidden` on the
  refresh POST. Raw/Enriched/Curated pass. TEST `Model` last refreshed 2026-08-07 06:54 UTC.
- **DEV**: no run since 2026-08-07 12:09 (Failed on `VL_ConnectionId|CON-SQLFabric-ETL_Lakehouse_Util`
  → `VariableNotFound`); that run predates commits `0d2dc5b` and `9153a8e`. Both DEV schedules disabled.
- **PROD**: no job instances; schedule disabled, owner is a user account.

## Why
The chain is the platform's daily heartbeat. Raw/Enriched/Curated are current but the TEST
semantic model has been stale since 2026-08-07, and PROD has never been exercised. Every failure
so far has been an identity, variable-library or key-map issue rather than data logic — the same
classes will keep recurring until they are closed deliberately.

## Context
- `customers/Carl-Ras/datahub/CONTEXT.md` — project state; the semantic-model refresh/memory work.
- `customers/Carl-Ras/datahub/CLAUDE.md` — the 2026-08-11 conventions: nothing per-environment
  hardcoded; variable libraries are the environment contract; `Lakehouse_Util` must be seeded.
- `Fabric-ETL/Orchestration/Schedule/PL_MainExecution.DataPipeline` → Raw / Enriched / Curated /
  Semantic Model; the last stage is `PL_Update_SemanticModel` → notebook logicalId
  `33e45f7b-5e2d-86e7-48fb-e834b0d9a6f2` (`NB_Refresh_SemanticModel`, the old per-table plan).
  `NB_Refresh_SemanticModel_Full` exists but the pipeline does not point at it.
- `tools/fabric_identity.py` — the SPN identity migration; it has no semantic-model takeover.
- Measured on the 403: the SPN (`aa462763…` / object `f05f446a…`, the TEST schedule owner) reads
  the dataset and its refresh history over the Power BI API (200), and the dataset's
  `configuredBy` is `EXT_NSKC@carl-ras.dk`. Model ownership as the cause is inference, untested.
- Related tasks: `2026-07-07-carlras-fabric-scaleup` (capacity/model processing),
  `2026-08-07-carlras-gtm-register-in-execute-chain`.

## Log
- 2026-08-11 — created; started (session task)
