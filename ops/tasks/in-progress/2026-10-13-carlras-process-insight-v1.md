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
**Now (2026-10-16):** phase 1 done. Spec (54 entities), 155 metrics linked, 175 measures (162 defined, 13 BLANK by reason, all 162 run on a synthetic Direct Lake model in leita.dk), config + overlay schema (`03-spec-schema.md` 3.8) with `own/Ontology/tools/deploy_check.py` -> `spec.lock.yaml`; Carl Ras `config.yaml` (8 values open) + empty `overlay.yaml`. Test source copied as real Delta into Pingala `NielsWorkspace_Dev` (F8, `tools/testsource_copy.py`, D15 revised 2026-10-16): `Lakehouse_Landingzone_DataverseService` 778 tables (incident 17), `Lakehouse_Landingzone_DataverseSales` 744 tables, metadata snapshot + manifest in `Files/metadata/`. The 10 change-tracked tables (SLA, resolutions, live work items, swarms, routing) are selected in Link to Fabric but not yet in OneLake in either trial. own/Ontology uncommitted until this handoff.
**Tried and dropped:** TREATAS for role filters (SQLBI: USERELATIONSHIP far faster); a new workspace `Ontology-Test-LZ` (Niels: use `NielsWorkspace_Dev`).
**Next:**
1. Phase 2: metadata reader on `Files/metadata/` (entities, attributes, relationships, option sets), then the Raw (SCD2) + Enriched generator for the Case to Resolution tables, in `NielsWorkspace_Dev` beside the ServiceNow chain.
2. When the 10 change-tracked tables reach OneLake: rerun `python tools/testsource_copy.py service|sales run` (overwrites). Deadline 2026-11-14 (trial expiry).
3. Decide test data before phase 4 (17 real cases is too thin to check numbers): sample data or a generator with known answers.
4. ServiceNow 6b: wake PDI dev443926 (Niels), then check login and land metadata; Aeven docs and Fabric connection `CON_ServiceNow_PDI_dev225547` still name the old instance.
5. Sales and Customer Insight libraries through `05-library-onboarding.md` when exported.
6. Later: spike 0g (graph directly on Warehouse) when preview adds Warehouse as a graph source.

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
