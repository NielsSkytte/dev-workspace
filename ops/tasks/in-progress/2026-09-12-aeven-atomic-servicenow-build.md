---
title: Aeven — AtomicServiceNow build (ServiceNow add-on to Atomic, POC)
status: in-progress
created: 2026-09-12
project: customers/Aeven/AtomicServiceNow
owner: fabric-back
priority: normal
blocked_by:
activity: 1
fno_task:
source: session
---

## What
Build the Aeven Fabric POC as a ServiceNow add-on to Pingala Atomic — REST API extract (Zurich)
to raw, then curated layer and semantic model. Single activity for all project work (F&O 4058-1).

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
