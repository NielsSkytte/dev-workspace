---
id: fabric-warehouse-deploy-bootstrap
ts: 2026-11-17T22:00:00Z
type: semantic
scope: project:customers/Aeven/AtomicServiceNow
source: session cf6eaca2
tags: [fabric, warehouse, deployment, git, decision]
status: distilled
description: "Fabric deployment pipeline cannot deploy warehouse views over a lakehouse SQL endpoint (SQL71561, MS docs: unsupported); Aeven PROD route is NB_Bootstrap CREATE OR ALTER on text diff (248ee77); notebook DDL needs a manual Source control refresh"
---

- Deploying `Warehouse_Enriched_ServiceNow` DEV->PROD (2026-11-17) failed with ~150 SQL71561/SQL71501 errors on lakehouse
  references. An agent with the Microsoft docs skills confirmed: no supported route; warehouse CI/CD is preview.
- Rule: warehouses are never deployed. `NB_Bootstrap_Warehouse_ServiceNow` creates missing objects and runs
  `CREATE OR ALTER VIEW` for Curated views (`itsm_curated_view`, `viewdimtransform`, `viewfacttransform`) whose
  normalised text differs. Never alters tables, never drops. Enriched views are written by the transform notebook each run.
- Fabric Source control does not show warehouse DDL a notebook ran until a manual refresh of the panel (cost real time 11-17).
- Update from git is blocked (BlockOnPossibleDataLoss) when the repo changes a column type on a table with rows: commit the
  workspace's table DDL to main; committing to a new branch did not help.
- Skill: `fabric-warehouse-git` failures #7 and #8.
