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
customer_ask: sent 2026-10-21
waiting_on:
resume_on:
source: session
---

## What
Build the Aeven Fabric POC as a ServiceNow add-on to Pingala Atomic — REST API extract (Zurich)
to raw, then curated layer and semantic model. Single activity for all project work (F&O 4058 / 400760).

## Progress

**Now (2026-11-12):** Aeven PROD exists: workspace `ITSM-ETL-Prod` (`a9483211-...`, empty), connection `ServiceNow_Prod_BasicAuth_http_v2` (`9d0cd0a3-...`), in `_aeven-prod` (room). Built and run on the PDI: stage guard + model bind, `PL_Preflight_ServiceNow`, `NB_Bootstrap_Warehouse_ServiceNow` (room `8d8906e`, local; dataaidemo `8da559d`). Rehearsal DEV -> PROD (`ServiceNow_Rehearsal_Prod`, pipeline `nsc test`): from empty through Curated; Process Insight fails where `sys_audit` never landed (`enriched.Audit` missing). Rehearsal workspace still up. Nothing synced to Aeven.

**Earlier (2026-11-11):** Aeven DEV connection is `ServiceNow_Test_BasicAuth_http_v2` (`494578c4-…`, WebForPipeline, Basic, Aeven gateway), verified by Niels and named in `environments.json` (room `35eb6e7`). `CON_Fabric_SQL` (`d7263d88-…`) reads the plan config from SQL_Util (Kresten). Niels asked Aeven for a production Web v2 connection (he cannot create it).

**Earlier (2026-11-04, late):** Metadata-driven views (decision 2026-11-04 rewritten): Enriched views generated at runtime from SQL_Util by MetaAtomic `atomic_views` 0.2 (own `b85353d`), house formatting, ownership via `servicenow_tables.view_mode`, breaking-change guard, persist in dependency waves, repo copy via DevOps API (waits for a dataaidemo PAT in Key Vault). Dev: dataaidemo `fd05db3`, flag test passed (blocked + free change). Room commits `d703c29`, `1244fb4` local, not pushed. Task - ServiceNow (ITSM) phase-1 model deployed in dev. AtomicSQL / AtomicInstructionSets reviewed, findings sent to the process-insight session. Not synced to Aeven: needs `Warehouse_SqlEndpoint` for aeven-dev. Curated persist still in its notebook.

**Earlier (2026-11-04):** OAuth (client credentials) built and proven on PDI dev443926 + NielsWorkspace_Dev; `ServiceNow_Auth` (VL_RunSettings) switches basic/oauth per value set; basic rerun on the same pipeline passes. On MasterDataPlan main `3b8ab2e` with Aeven = basic. OAuth email sent to Aeven (client, property, 2 gateway connections); waiting for their connection ids. Aeven run 2026-11-03 (`20261103T144624Z`) clean, 23 tables / 43,273 rows; `enriched.ChoiceLabel` 0 rows because sys_choice returns only label, sys_id, sys_domain, sys_domain_path (on 10-20 it returned all fields: access changed at Aeven). On the PDI `personalize_choices` opens all sys_choice fields plus full sys_dictionary / sys_db_object; email sent asking for it or a read-only role. Kresten moved the SQL_Util config to schema `config` (done at Aeven); room rule added for who syncs to Aeven (`499c458`).

**Earlier (2026-10-28):** Aeven reported heavy traffic ("1TB of transactions") after the daily schedule; schedule is UserDisabled at Aeven. ingest_log 10-20..10-28: 10 runs, each a full read of 23 tables, ~410k rows, 0.44 GB, 3-5 min; 1 TB not explained by these runs. Fix committed locally `42305a8` (deltas in landed mode, Saturday full, sys_dictionary/sys_db_object Saturdays only via `load_weekday`), not pushed. Reply drafted: `Aeven_ServiceNow_Traffic_email.md`.

**Earlier (2026-10-23):** Waiting on Aeven for permissions. Full `PL_MainExecution` run `20261020T080536Z`
at Aeven ran without errors: sys_choice returns all fields (17,979 rows); still blocked are
`sys_dictionary.internal_type` (empty in all 204,762 rows), `alm_asset` (count 0), and empty fields on 13
tables; sys_audit / sys_audit_delete are not tested (`enabled: false`). 13 tables land fewer rows than
the stats count (e.g. sys_user 3,061 / 175,296). Aeven's first reply: many of the empty fields may just
be unfilled in test; that does not explain internal_type, alm_asset or the audit tables. Full-load
paging to the stats count is pushed (local `e499775`, `MasterDataPlan` main `c783d94`), not run yet.
Pingala `dataaidemo` at `1ab2a5f`.

**Tried and dropped:** Direct Lake on SQL -> Direct Lake on OneLake (SQL refuses the calculated
measures table); a `paginationRules` block holding only `supportRFC5988` -> no rules on the count copy
(it looped 6,955 requests in 23 min); plain `TRY_CAST` -> `TRY_CAST(NULLIF(col,''))` ('' casts to
1900-01-01 / 0 in a Fabric warehouse).; a run-overlap lock file (`6ca7281`, reverted) -> pipeline Concurrency = 1; warehouse
objects in git on a first sync (`DmsImportDatabaseException`) -> shell warehouses; Pingala ids as
variable-library defaults -> UNSET defaults, one value set per environment; full loads stopping at
the first empty page -> page to the stats count (inference: an ACL-emptied page can have readable rows after it).

**Next:**
- When Aeven sends the two OAuth connection ids: set them in the AevenDev value set, `ServiceNow_Auth = oauth`, sync, run.
- When Aeven grants the sys_choice role: rerun, check ChoiceLabel and the sys_dictionary catalogue.
0. Send the traffic email; push `42305a8` to MasterDataPlan only after Aeven replies.
1. When Aeven answers: in `ITSM-ETL-Dev` Update from git (`2e0020c`: paging + choice labels in Enriched), run `PL_MainExecution` with
   `full_reload` on, rerun `access_check_cell.py`, compare row gaps and fields with `20261020T080536Z`.
2. Send Aeven the row gaps that remain after that run; check Curated builds.
3. Serving to Aeven (local commit `c0ca888`) once Curated builds; `Incident Activity` waits for sys_audit.
4. Per-environment disabled tables, then sync `dataaidemo`.
5. Production per `project-room/docs/production-deployment.md` (Q1-Q7 decided 2026-10-03).
6. OAuth test on the PDI: room task `project-room/tasks/2026-11-02-oauth-for-servicenow-extraction.md` (owner Niels, taken 2026-11-03).

## Needs from customer

- **Aeven:** read on `sys_dictionary.internal_type`, query rights on `sys_updated_on`, `alm_asset`,
  sys_audit / sys_audit_delete (`Aeven_ServiceNow_Query_Access_email.md`). Sent 2026-10-21.
- **Aeven:** say which empty fields on 13 tables are unreadable vs unused in test
  (`Aeven_ServiceNow_Field_Access_email.md`). Sent; first reply by 2026-10-23: many may be unused in test.
- **Aeven:** production list (instance URL, integration user and roles, gateway and connection,
  ITSM-ETL-Prod workspace, run account). Production connection asked 2026-11-11; rest of the list drafted 2026-10-03 (`Aeven_Production_Requirements_email.md`), **not sent**.

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
