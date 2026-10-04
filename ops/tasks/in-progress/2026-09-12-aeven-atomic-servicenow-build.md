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
customer_ask: open
waiting_on:
resume_on:
source: session
---

## What
Build the Aeven Fabric POC as a ServiceNow add-on to Pingala Atomic — REST API extract (Zurich)
to raw, then curated layer and semantic model. Single activity for all project work (F&O 4058 / 400760).

## Progress

**Now (2026-10-04):** Deployed by git to Aeven DEV `ITSM-ETL-Dev` (`1fd1bd43`), repo `MasterDataPlan`
main at `66ea2c2`: 15 Atomic items, `PL_MainExecution` (concurrency 1, schedule off), variable libraries
with UNSET defaults and value set AevenDev active. Last `PL_MainExecution` run 2026-10-03: Ingest,
Metadata (catalogue fallback from mirrors) and Enriched succeeded; Curated failed 16 views because 8
tables return 0 rows to the integration user (sys_dictionary, core_company, change_request, problem,
sc_req_item, sc_request, sc_task, alm_asset) and sys_choice lacks name/element/value/language.
Pingala `dataaidemo` at `1ab2a5f`.

**Tried and dropped:** Direct Lake on SQL -> Direct Lake on OneLake (SQL refuses the calculated
measures table); a `paginationRules` block holding only `supportRFC5988` -> no rules on the count copy
(it looped 6,955 requests in 23 min); plain `TRY_CAST` -> `TRY_CAST(NULLIF(col,''))` ('' casts to
1900-01-01 / 0 in a Fabric warehouse).; a run-overlap lock file (`6ca7281`, reverted) -> pipeline Concurrency = 1; warehouse
objects in git on a first sync (`DmsImportDatabaseException`) -> shell warehouses; Pingala ids as
variable-library defaults -> UNSET defaults, one value set per environment.

**Next:**
1. Send `Aeven_ServiceNow_Read_Access_email.md`; on access, rerun `PL_MainExecution` and check Curated builds.
2. Check the Ingest duration on the first run with 4 tables in parallel (pushed in `66ea2c2`).
3. Serving to Aeven (local commit `c0ca888`) once Curated builds; `Incident Activity` waits for sys_audit.
4. Per-environment disabled tables, then sync `dataaidemo`.
5. Production per `docs/production-deployment.md` (Q1-Q7 decided 2026-10-03).

## Needs from customer

- **Aeven:** read access on the test instance for the 8 tables above, all sys_choice fields, and
  sys_audit / sys_audit_delete. Drafted 2026-10-03 (`Aeven_ServiceNow_Read_Access_email.md`), **not sent**.
- **Aeven:** production list (instance URL, integration user and roles, gateway and connection,
  ITSM-ETL-Prod workspace, run account). Drafted 2026-10-03 (`Aeven_Production_Requirements_email.md`), **not sent**.

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
