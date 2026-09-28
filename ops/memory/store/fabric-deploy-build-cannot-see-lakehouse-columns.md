---
id: fabric-deploy-build-cannot-see-lakehouse-columns
ts: 2026-09-25T14:40:00Z
type: semantic
scope: workspace
source: /log
tags: [fabric, deployment-pipeline, warehouse, sqlproj, dacfx, lakehouse, carl-ras, operation-hardening]
status: distilled
description: "Fabric's deployment-pipeline build of a warehouse cannot see a lakehouse's columns and guesses them from how the views use them, so unprefixed columns in multi-table queries and SELECT * over Raw fail with SQL71501/71508/71561; fix is prefix every column and name every Raw column list, enforced by tools/wh_rules.py in pre-push; why 09-09 passed and 09-14 failed is not established"
---

Carl Ras `Fabric-ETL Deployment`, DEV->TEST, 2026-09-24/25.

- **Proven:** the deploy builds each warehouse as a standalone SQL project that cannot see the
  columns of `Lakehouse_Raw_*`. Rebuilt locally against the real DEV Raw schema (94 tables,
  4,095 columns), the same SQL builds with 0 errors.
- Failing shapes: a column without a table prefix in a query joining two or more tables; `*`
  over a Raw table in combination with such a reference. Fixes: GEN-013 (Curated), GEN-014
  (7 prefixes, `ed158d6`), GEN-015 (4 Raw `*` -> named lists, `8ed2333`). AX09 deployed to TEST
  2026-09-25 15:05 UTC.
- Guard: `tools/wh_rules.py` runs in the datahub pre-push. The skill `fabric-warehouse-git`
  carries it as failure 8 (commit `cccfde6`).
- **Not established:** why the same SQL passed on 2026-09-09. The error class changed between
  09-09 (import-time `Invalid object name`) and 09-14 (`SQL Project build failed`, SQL715xx).
  Inference: Fabric added a SQL-project build before import in that window.
- Deploy order to a stage that lacks the tables: Enriched before Curated. PROD Curated failed
  2026-09-25 because `viewdimtransform.Customer` reads
  `Warehouse_Enriched_CVR.enriched.CentralCompanyRegister`, which CVR's deploy had not created
  yet; a second Curated deploy went through.
