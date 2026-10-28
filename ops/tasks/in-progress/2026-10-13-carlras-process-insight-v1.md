---
title: Carl Ras — process-insight v1 (Dataverse → ontology → Direct Lake models + coverage report, three metric libraries)
status: in-progress
created: 2026-10-13
project: customers/Carl-Ras/process-insight
owner: architect
priority: normal
blocked_by:
activity:
fno_task: none        # new Proj ID not yet agreed with Carl Ras
customer_ask: none
waiting_on:
resume_on:
source: direct
---

## What
Build v1 of process-insight at Carl Ras as agreed in `customers/Carl-Ras/process-insight/CONTEXT_DECISIONS.md`
(D1–D12, P1–P7). Done when: on DEV, one Pingala-side command builds everything for the Case to
Resolution, Sales and Customer Insight libraries, and every metric shows one of the seven coverage
states with evidence; TEST/PROD run the same command per stage.

## Why
Process first: Carl Ras gets the full picture of its business in numbers from day one, and the
coverage report says what to fix next. It is also the Ontology accelerator's Dataverse slice.

## Progress
**Now (2026-10-28):** Inventory to deliver (ITD) runs in NielsWorkspace (48deed5a) from `tools/atomic_install.py`, which now also has snapshot, models and coverage steps, Util from AtomicBase notebooks when no reference platform, model names from the library title (own/Ontology eb4db16). ITD coverage of 194: Working 50, Empty 7, ETL gap 9, Not landed 69, Other source not ingested 27, No data 32. Case to Resolution (CTR) redeployed in NielsWorkspace_Dev (pi_ schemas, compat 1708): Working 16, Empty 35, ETL gap 23, Not landed 52, not ingested 21, No data 8.
Atomic Vision - Dev (4e7cb5f8, repo pingalaglobal/atomicvision, main) holds both models and Process Insight Coverage (one run, both libraries, 349 metrics, Atomic Vision theme, State slicer on Metric detail), merged as PRs 913-916; Direct Lake on OneLake reads the data in NielsWorkspace / NielsWorkspace_Dev. Engine: ETL gap split into ETL gap / Not landed (brief D36, own 931fa72); onboarding needs a live snapshot (e9a0edc); architecture `own/Ontology/docs/09-architecture.md`, client page `docs/pitch/process-insight-engine.html` (f03ba54).
A full installer rerun (snapshot + all default steps) was started 2026-10-28 ~20:00 in the background: result not verified.
**Tried and dropped:** TREATAS for role filters (SQLBI: USERELATIONSHIP far faster); a new workspace `Ontology-Test-LZ` (Niels: use `NielsWorkspace_Dev`); `CDCreader` for the Raw read (source tables have no change feed; watermark read instead). Option A for Atomic Vision (own data chain there): Niels chose B, the data stays in NielsWorkspace. `COL_LENGTH` in warehouse DDL: not supported by Fabric Warehouse; INFORMATION_SCHEMA instead.
**Next:**
1. Read the rerun log `C:\Users\NielsSkytteChristens\AppData\Local\Temp\claude\C--Dev-customers-Carl-Ras-process-insight\80a43015-cb40-4a7e-b41c-88471b5340ec\scratchpad\full-install.log`; the snapshot step counts as proven only if it is clean (landed.json before the run is saved as landed-before.json beside it).
2. Remaining deploy gaps (review 2026-10-28): coverage as the last step of PL_PI_Main in Fabric; a models-only deploy tool for git workspaces (the Atomic Vision deploy was manual: clone, copy, PR, sync, refresh); the git path end to end with an F&O extension; an ITD golden test.
3. F&O enum notebook (`util.enums`) untested with real credentials: needs a client Key Vault and an SPN that reads F&O.
4. Regenerate `Case to Resolution Synthetic` and `ITD_Synthetic_Model` at 1708; drop the old cold/enriched schemas in NielsWorkspace_Dev; decide the PL_PI_Main schedule.
5. Niels sends `note-atomicbase-jesper-lars.md` (deferred 2026-10-28).
6. ITD review gaps: a daily on-hand snapshot in Curated; the synthetic input gives no column meanings.
7. R5: exclude parent-propagated child resolutions from M20-001/002/104 (measure change).
8. When the author returns a new library export: re-import, apply accepted L-changes.
9. ServiceNow 6b: wake PDI dev443926 (Niels), then check login and land metadata.
10. Sales and Customer Insight libraries through `05-library-onboarding.md` when exported.
11. Later: spike 0g (graph directly on Warehouse).

## Needs from customer
- New Proj ID for this work — not sent.

## Context
- `own/Ontology/docs/01-product-plan.md` — product plan and build phases
- `customers/Carl-Ras/process-insight/design/PLAN.md` — Carl Ras configuration and deployment
- `customers/Carl-Ras/process-insight/CONTEXT.md`, `CONTEXT_DECISIONS.md`, `input/`
- `own/Ontology/docs/00-project-brief.md` (D26-D32, section 3h)
- `own/MetaAtomic/CONTEXT.md` — lineage and verification capabilities this needs

## Log
- 2026-10-13 — created
- 2026-10-15 — started (session task)
- 2026-10-15 — plan split: product half to own/Ontology/docs/01-product-plan.md (own 2446dd7, AAI e03f529); existing-source binding decided (D13 / brief D32)
- 2026-10-16 — phase 1 closed (config/overlay schema, deploy_check.py, Carl Ras config); test source copied into Pingala NielsWorkspace_Dev (Service 778, Sales 744 tables + metadata snapshot)
- 2026-10-18 — phase 3 done (binding corrections, stored.yaml, 66 of 175 measures valued); R1-R5 decided; library change request sent
- 2026-10-25 — Atomic installer built; core Atomic F&O + ITD extension installed in NielsWorkspace (run 1); run 2 interrupted by restart
- 2026-10-28 — ETL gap split (D36); ITD + CTR models and one coverage model in Atomic Vision - Dev (PRs 913-916); installer gets snapshot/models/coverage steps; architecture doc and client page
