---
id: aeven-prod-first-run-20261114
ts: 2026-11-14T12:00:00Z
type: semantic
scope: project:customers/Aeven/AtomicServiceNow
source: session 9b6af283
tags: [aeven, production, deploy]
status: distilled
description: "Aeven ITSM-ETL-Prod first run: rebuild action in NB_Setup_Prod; PROD models repointed to PROD warehouse (ee91c38); 70,391 tasks; duplicate DimTasks key fixed a32b981; ModelFrameMode=pipeline 1ee9d9e"
---

- Deployment pipeline copied the models still pointing at DEV's `Warehouse_Curated`; a rebuild now
  repoints them to PROD (`ee91c38`). After that the report showed 70,391 tasks, 15,873 incidents.
- `ITSM-ETL-Prod` is not git-connected; Claude cannot see PROD runs. DEV run data is readable via
  the MasterDataPlan repo after a Source control commit.
- Model load failure: duplicate `DimTasks` key. Cause: `count.json`/`total.json` were folded as
  pages, each adding a row without `sys_id`. Fixed `a32b981`; Enriched skips rows without sys_id.
- AevenProd `ModelFrameMode = pipeline` (`1ee9d9e`): PL_MainExecution reframes the model once after
  Process Insight.
- Aeven data: 2,305 of 13,790 resolved incidents have `resolved_at` before `opened_at`; asked in
  the first-run email draft. Case to Resolution switched off to shorten Process Insight.
