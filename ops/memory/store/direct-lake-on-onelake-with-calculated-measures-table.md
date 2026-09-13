---
id: direct-lake-on-onelake-with-calculated-measures-table
ts: 2026-09-13T21:00:00Z
type: semantic
scope: project:customers/Aeven/AtomicServiceNow
source: /log
tags: [power-bi, semantic-model, direct-lake, tmdl, measures-table, fabric]
description: A Direct Lake model that also holds a calculated {0} measures table must be Direct Lake on OneLake (AzureStorage.DataLake expression); Direct Lake on SQL refuses it as a composite model, and the model first answers after one refresh
status: distilled
---

`tools/build_model.py` (Aeven) generates TMDL: entity partitions `mode: directLake` with
`expressionSource: DatabaseQuery`, and `DatabaseQuery = AzureStorage.DataLake("https://onelake.dfs.fabric.microsoft.com/<ws>/<warehouse>")`,
compatibilityLevel 1702. The measures table is `partition = calculated`, `source = {0}`. Importing
the same model with a SQL-endpoint expression failed with "composite model does not support
Direct Lake on SQL mode". After import the model says "Cannot find table" until the first
refresh (framing). Relationships derived from `SurrogateKey_Dim<Dim>[_<Role>]` columns, first role
active, further roles inactive. Verified by DAX against the warehouse counts.
