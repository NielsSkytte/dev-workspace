---
title: Aeven — AtomicServiceNow build (ServiceNow add-on to Atomic, POC)
status: in-progress
created: 2026-09-12
project: customers/Aeven/AtomicServiceNow
owner: fabric-back
priority: normal
blocked_by:
activity: 400760
fno_task: none
customer_ask: open (workspace identity, drafted 2026-11-16)
waiting_on:
resume_on:
source: session
---

## What
Build the Aeven Fabric POC as a ServiceNow add-on to Pingala Atomic — REST API extract (Zurich)
to raw, then curated layer and semantic model. Single activity for all project work (F&O 4058 / 400760).

## Progress

**Now (2026-11-17):** Aeven PROD live since the first delta run 2026-11-14 (Completed, 37 min); `52fdfe3` (system tables in Lakehouse_Util) and `a689974` (Process Insight fix) not deployed to PROD. Aeven DEV on MasterDataPlan `a689974`: the 11-16 18:34Z run (`system_full = sys_dictionary`) passed Ingest, so DEV has its one full `sys_dictionary` load, and failed at Enriched (LSROBOTokenFailure / AADSTS53000) and ran after a re-save; a full default `PL_MainExecution` was started 2026-11-16 evening, result not read. Workspace-identity run mode built (room `b50a34f`): PDI `PL_MainExecution` job `7d6a2eca` Completed fully as the workspace identity; Aeven set to `wi_model_step: user`, not switched on, waits for Aeven's connections.

**Tried and dropped:** Direct Lake on SQL -> Direct Lake on OneLake (SQL refuses the calculated
measures table); a `paginationRules` block holding only `supportRFC5988` -> no rules on the count copy
(it looped 6,955 requests in 23 min); plain `TRY_CAST` -> `TRY_CAST(NULLIF(col,''))` ('' casts to
1900-01-01 / 0 in a Fabric warehouse).; a run-overlap lock file (`6ca7281`, reverted) -> pipeline Concurrency = 1; warehouse
objects in git on a first sync (`DmsImportDatabaseException`) -> shell warehouses; Pingala ids as
variable-library defaults -> UNSET defaults, one value set per environment; full loads stopping at
the first empty page -> page to the stats count (inference: an ACL-emptied page can have readable rows after it).; Power BI REST from a workspace identity (403 on every `/v1.0/myorg` call, PDI 2026-11-16, tenant setting on) -> Fabric API for the model list, Semantic model refresh activity for the reframe.

**Next:**
1. Read the DEV run result (`ingest_log`, `pipeline_activity_log`).
2. Deploy `52fdfe3` + `a689974` DEV -> PROD; run PROD once with `tables = none`, `system_full = sys_dictionary`.
3. Send `Aeven_Fabric_Workspace_Identity_email.md`; on the six connection ids per workspace: set them in AevenDev / AevenProd, `run_identity = workspace` on aeven-dev, sync, run in DEV first.
4. When Aeven sends the two OAuth connection ids: set them in the AevenDev value set, `ServiceNow_Auth = oauth`, sync, run.
5. When Aeven grants the sys_choice role: rerun, check ChoiceLabel and the sys_dictionary catalogue.
Older steps (2026-10-23..28, not verified as landed):
0. Send the traffic email; push `42305a8` to MasterDataPlan only after Aeven replies.
1. When Aeven answers: in `ITSM-ETL-Dev` Update from git (`2e0020c`: paging + choice labels in Enriched), run `PL_MainExecution` with
   `full_reload` on, rerun `access_check_cell.py`, compare row gaps and fields with `20261020T080536Z`.
2. Send Aeven the row gaps that remain after that run; check Curated builds.
3. Serving to Aeven (local commit `c0ca888`) once Curated builds; `Incident Activity` waits for sys_audit.
4. Per-environment disabled tables, then sync `dataaidemo`.
6. OAuth test on the PDI: room task `project-room/tasks/2026-11-02-oauth-for-servicenow-extraction.md` (owner Niels, taken 2026-11-03).

## Needs from customer

- **Aeven:** read on `sys_dictionary.internal_type`, query rights on `sys_updated_on`, `alm_asset`,
  sys_audit / sys_audit_delete (`Aeven_ServiceNow_Query_Access_email.md`). Sent 2026-10-21.
- **Aeven:** say which empty fields on 13 tables are unreadable vs unused in test
  (`Aeven_ServiceNow_Field_Access_email.md`). Sent; first reply by 2026-10-23: many may be unused in test.
- **Aeven:** production list. Answered: workspace `ITSM-ETL-Prod` and connection `ServiceNow_Prod_BasicAuth_http_v2` (`9d0cd0a3-...`), PROD live 2026-11-14.
- **Aeven:** workspace-identity setup: "Service principals can call Fabric public APIs" for a group with the two identities, Contributor for each identity on its workspace, six connections per workspace (`Aeven_Fabric_Workspace_Identity_email.md`). Drafted 2026-11-16, **not sent**.

## Why
Signed Q3 POC engagement (project 4058). First gate: ServiceNow data landed in raw, deployable to
a landing-zone workspace or directly into fabric-etl.

## Context
- Project: `customers/Aeven/AtomicServiceNow` (scaffolded 2026-09-12).
- Reference: proven ADF extractor in `customers/Aeven/ServiceNowPOC/adf` — review first.
- Off limits: `customers/Aeven/ServiceNowPOC/fabric` (do not read / reuse).
- Dev/test: Zurich PDI https://dev225547.service-now.com/ — no access to Aeven's instance.

## Log
- 2026-09-12 — created at project scaffold; started (session task)
- 2026-09-13 — POC value chain complete in NielsWorkspace_Dev (landing -> raw shortcuts -> enriched -> curated -> Direct Lake model) and a first PBIR report deployed; commits through 3378408
- 2026-09-16 — brought onto the Progress shape (Progress + Needs from customer, fno_task none, customer_ask open); no facts changed. Card: CONTEXT.md converted to the resume card.
- 2026-09-21 — check-in: fno_task 400760; reporting polish descoped (Aeven's responsibility); threads 3 and 6 dropped
- 2026-10-02 — Aeven repo MasterDataPlan and ITSM-ETL-Dev connected; first git deploy (shell warehouses after DmsImportDatabaseException); PL_Ingest folds per table, count.json as copy-complete marker
- 2026-10-03 — PL_MainExecution (concurrency 1), variable libraries as value sets (UNSET defaults), catalogue fallback with inferred types, 4 tables in parallel, production design + decisions Q1-Q7; access and production emails drafted
- 2026-10-20 — access read-out of run 20261020T080536Z; full-load paging bounded by the stats count (e499775 / MasterDataPlan c783d94); field-access follow-up drafted
- 2026-10-23 — waiting on Aeven for permissions; first reply: many empty fields may be unused in test
- 2026-10-28 — Aeven traffic complaint: measured 0.44 GB/run; deltas + weekly full built (42305a8); traffic email drafted
- 2026-11-03 — project shared with Kresten via project-room/ (atompower4us/aeven-atomicservicenow-room, CI green); originals moved; OAuth room task taken by Niels
- 2026-11-11 — aeven-dev connection named in environments.json (room 35eb6e7).
- 2026-11-16 — workspace-identity run mode; PDI full run as WI (7d6a2eca); room b50a34f; WI email drafted (Aeven 46a97ac)
