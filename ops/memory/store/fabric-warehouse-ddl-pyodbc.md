---
id: fabric-warehouse-ddl-pyodbc
ts: 2026-07-28T09:36:00Z
type: semantic
scope: workspace
source: session:c79aa71b
tags: [reference, fabric, warehouse, tsql, tooling]
status: distilled
description: "Run T-SQL against a Fabric warehouse from a local machine via pyodbc + ODBC Driver 18 + AAD access-token; workspace-first alternative to hand-authoring the sqlproj"
---

To build/query a Fabric **Warehouse** programmatically from the local machine (instead of
hand-authoring the git sqlproj + templated `xmla.json`), connect with a token:

- Driver: **ODBC Driver 18 for SQL Server** (present on Niels' machine); `pip install pyodbc`.
- Token: `az account get-access-token --resource https://database.windows.net/` (SQL/TDS
  audience — NOT the storage or fabric audience).
- Connect: pass the token via `attrs_before={1256: token_struct}` where
  `token_struct = struct.pack(f"<I{len(t)}s", len(t), t)` and `t = token.encode("utf-16-le")`.
  Server = warehouse `properties.connectionString` (`...datawarehouse.fabric.microsoft.com`,
  one endpoint per workspace), `Database=<warehouse displayName>`, `Encrypt=yes`.
- **Cross-database** queries work within a workspace: a warehouse can read a plain
  lakehouse's tables as `[Lakehouse_X].[dbo].[table]` (plain lakehouse tables surface under
  `dbo` in its SQL endpoint). `CREATE VIEW` needs the referenced object to already exist.
- `autocommit=True`; run `CREATE SCHEMA/VIEW/PROCEDURE` as separate batches (each must be
  first in its batch).

Used to build `Warehouse_Enriched_GTM` (schemas + view + materialization SP) directly.
The warehouse itself is created via `fab mkdir` (then committed to git from the workspace).
