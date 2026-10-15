---
title: Carl Ras — process-insight v1 (Dataverse → ontology → Direct Lake models + coverage report, three metric libraries)
status: open
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
**Now:** 2026-10-15 — product plan in `own/Ontology/docs/01-product-plan.md`, Carl Ras half in `design/PLAN.md`; existing-source binding decided (D13 / brief D32). Nothing built.
**Next:**
1. Phase 1a: library-to-source concept mapping (product plan section 5b), then spec format and the Case to Resolution process ontology.
2. Phase 0 in parallel: Direct Lake role-dim spike (P3) in a Pingala workspace; Dataverse test source (proposed).

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
