---
id: link-to-fabric-late-tables-and-endpoint-lag
ts: 2026-10-16T12:00:00Z
type: procedural
scope: workspace
source: /log session a007db1c
tags: [dataverse, link-to-fabric, onelake, sql-endpoint, fabric]
status: distilled
description: "Link to Fabric: tables that get change tracking after the link exists are listed but not selected (Manage tables), shortcuts appear only after 'Refresh Fabric tables', and the lakehouse SQL endpoint can lag OneLake by hundreds of tables until refreshMetadata runs"
---

Observed 2026-10-16 on two leita.dk trials (process-insight test source):

- **Change tracking enabled after the link was created** does not add the table to the link. It
  shows up in **Manage tables** unselected (Sales: 739 of 754 selected). Select it, save, wait for
  the initial sync, then **Refresh Fabric tables** creates the OneLake shortcut (MS Learn:
  fabric-link-to-data-platform, "Use the Refresh Fabric tables option to add the newly enabled table").
  Power Apps showing a table "Active / Created" did not mean it was in OneLake yet: the 10 tables
  were still absent from `Tables/` an hour later.
- **Check OneLake, not the SQL endpoint.** The CS lakehouse had 778 entries in `Tables/` (DFS list
  `?resource=filesystem&directory=<lh>/Tables`) while `sys.tables` showed 67. `POST
  /v1/workspaces/{ws}/sqlEndpoints/{id}/refreshMetadata` brought it to 778 in ~5 minutes; a second
  call while one runs returns 409 `LockConflict`.
- **Long OneLake copies outlive the token** (~60-75 min): renew both storage tokens every 30 min
  and retry once on `authenticati|unauthorized` (`own/ProcessInsight/tools/testsource_copy.py`). DuckDB
  `delta_scan` reads Link tables (deletion vectors); `deltalake.write_deltalake` writes the copy
  with `{'bearer_token', 'use_fabric_endpoint': 'true'}`. Set DuckDB `TimeZone='UTC'` or timestamps
  come back in local time.
