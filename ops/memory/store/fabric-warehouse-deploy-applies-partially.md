---
id: fabric-warehouse-deploy-applies-partially
ts: 2026-08-27T10:15:00Z
type: semantic
scope: global
source: session:50082637-f235-4ee7-be0d-fd881b292a68
tags: [fabric, warehouse, deployment, git]
status: distilled
description: "A failed warehouse GIT import rolls back whole; a failed warehouse DEPLOYMENT does not - it leaves the objects it managed to create behind in the target"
---

Hand-written from the session. Corrects an assumption carried from `fabric-warehouse-git`
failure 4, which is about the git path only.

## Two mechanisms, two behaviours

| | On failure |
|---|---|
| **Update from git** | rolls back whole - verified 2026-08-21, neither warehouse gained an object after a cross-warehouse failure |
| **Deployment pipeline** | **applies partially** - the same class of failure left `enriched.BudgetLedger` created (empty) in TEST while both views were rejected |

## Why it matters

A failed deployment is not a no-op. Inspect the target before retrying: the objects that landed
may make the retry look like a different problem, and per `fabric-deployment` failure 2 an orphan
item can make the retry fail with "already exists" instead.

In this case the leftover table matched what the source would send, so the retry was clean once
the underlying syntax defect was fixed.

## Ordering, both mechanisms

A new cross-warehouse entity needs **two commits and two syncs, producer first** - Fabric imports
warehouse items independently and does not order them. The same applies to promotion: deploy the
producing warehouse, then the consuming one, never both in one selection.
