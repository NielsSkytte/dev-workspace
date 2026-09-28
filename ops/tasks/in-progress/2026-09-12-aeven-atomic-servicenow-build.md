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

**Now (2026-09-21):** POC value chain complete in Pingala's `NielsWorkspace_Dev`:
`PL_Ingest_ServiceNow` (25 tables, 186,727 rows, 0 failures), Raw shortcuts, Enriched (24 tables),
Curated star (12 dims, 6 facts), `Model_ServiceNow` Direct Lake verified by DAX, and
`Report_ServiceNow` (PBIR, Incident Overview) deployed; commits through `3378408`. Reporting polish
is Aeven's responsibility. Nothing at Aeven, nothing raised.

**Tried and dropped:** Direct Lake on SQL -> Direct Lake on OneLake (SQL refuses the calculated
measures table); a `paginationRules` block holding only `supportRFC5988` -> no rules on the count copy
(it looped 6,955 requests in 23 min); plain `TRY_CAST` -> `TRY_CAST(NULLIF(col,''))` ('' casts to
1900-01-01 / 0 in a Fabric warehouse).

**Next:**
1. One master pipeline landing -> enriched -> curated -> model refresh, on a schedule (delta hourly,
   full weekly per config).
2. Raise the Aeven prerequisites (design §10), get the DEV workspace on their capacity, deploy by
   connection swap.
3. Cold path (SCD2 history) once the Atomic hot/cold-path code lands.

## Needs from customer

- **Aeven:** gateway server with outbound 443 to the instance; an integration user with read on the
  table list and role `snc_basic_auth_api_access`; a git-connected DEV workspace on their capacity
  (design §10). **Not asked.**

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
