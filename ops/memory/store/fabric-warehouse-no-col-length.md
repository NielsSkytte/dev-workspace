---
id: fabric-warehouse-no-col-length
ts: 2026-10-28T19:30:00Z
type: semantic
scope: workspace
source: session:80a43015
tags: [fabric, warehouse, sql]
status: distilled
description: "Fabric Warehouse rejects COL_LENGTH ('FUNCTION COL_LENGTH is not supported', 15871); check a column with INFORMATION_SCHEMA.COLUMNS before ALTER TABLE ADD"
---

Seen 2026-10-28 in `tools/coverage_model.py` DDL against NielsWorkspace Warehouse_Curated:
`[SQL Server]FUNCTION 'COL_LENGTH' is not supported. (15871)`. Working form:
`IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = N'<s>' AND TABLE_NAME = N'<t>' AND COLUMN_NAME = N'<c>') ALTER TABLE [<s>].[<t>] ADD [<c>] <type> NULL;`
Adding a nullable column with ALTER TABLE ADD works.
