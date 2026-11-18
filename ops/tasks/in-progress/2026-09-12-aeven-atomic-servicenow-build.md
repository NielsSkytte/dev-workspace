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

**Now (2026-11-18):** Canonical status / priority / resolution codes come from `SQL_Util.servicenow_code_map` (`enriched.CodeMap`), labels from `sys_choice` (readable on both instances: test 17,981 rows, prod 17,144). Aeven `main` at `9b01e26`; DEV and PROD run with the code-map Curated views (PROD: bootstrap `248ee77` altered 6 views 2026-11-17 21:55Z). Case to Resolution removed (room `ebd83cf`, Aeven `9b01e26`), `pi_` dropped DEV + PROD; only `Model_ServiceNow` (Task). DEV and PROD runs started 11-17 evening after the drop, results not read.

**Tried and dropped:** Direct Lake on SQL -> Direct Lake on OneLake (SQL refuses the calculated
measures table); a `paginationRules` block holding only `supportRFC5988` -> no rules on the count copy
(it looped 6,955 requests in 23 min); plain `TRY_CAST` -> `TRY_CAST(NULLIF(col,''))` ('' casts to
1900-01-01 / 0 in a Fabric warehouse).; a run-overlap lock file (`6ca7281`, reverted) -> pipeline Concurrency = 1; warehouse
objects in git on a first sync (`DmsImportDatabaseException`) -> shell warehouses; Pingala ids as
variable-library defaults -> UNSET defaults, one value set per environment; full loads stopping at
the first empty page -> page to the stats count (inference: an ACL-emptied page can have readable rows after it).; Power BI REST from a workspace identity (403 on every `/v1.0/myorg` call, PDI 2026-11-16, tenant setting on) -> Fabric API for the model list, Semantic model refresh activity for the reframe.; deployment-pipeline deploy of the warehouses (SQL71561 on lakehouse refs; MS docs: unsupported) -> `NB_Bootstrap` alters a changed Curated view; commit to a new branch (`temp`) on an Update DataLoss conflict -> the workspace's table DDL to `main`.

**Next:**
1. Read the 11-17 evening DEV and PROD run results (first runs without `pi_`).
2. Send `Aeven_Fabric_Workspace_Identity_email.md`; on the six connection ids per workspace: set them in AevenDev / AevenProd, `run_identity = workspace` on aeven-dev, sync, run in DEV first.
3. When Aeven sends the two OAuth connection ids: set them in the AevenDev value set, `ServiceNow_Auth = oauth`, sync, run.
Older steps (2026-10-23..28, not verified as landed):
0. Send the traffic email; push `42305a8` to MasterDataPlan only after Aeven replies.
1. When Aeven answers: in `ITSM-ETL-Dev` Update from git (`2e0020c`: paging + choice labels in Enriched), run `PL_MainExecution` with
   `full_reload` on, rerun `access_check_cell.py`, compare row gaps and fields with `20261020T080536Z`.
2. Send Aeven the row gaps that remain after that run; check Curated builds.
3. Serving to Aeven (local commit `c0ca888`) once Curated builds; `Incident Activity` waits for sys_audit.
4. Per-environment disabled tables, then sync `dataaidemo`.
6. OAuth test on the PDI: room task `project-room/tasks/2026-11-02-oauth-for-servicenow-extraction.md` (owner Niels, taken 2026-11-03).

## Needs from customer

- **Aeven:** sys_audit / sys_audit_delete read: with Aeven's architecture board. `alm_asset` closed; `sys_choice` and
  `sys_dictionary` readable (2026-11-17). Sent 2026-10-21 (`Aeven_ServiceNow_Query_Access_email.md`).
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
- 2026-11-17 — code map live DEV+PROD (Aeven 709c692, 9cb1a23, 248ee77); Case to Resolution removed (9b01e26), pi_ dropped DEV+PROD; warehouse PROD route = bootstrap; Orca code-block fix
