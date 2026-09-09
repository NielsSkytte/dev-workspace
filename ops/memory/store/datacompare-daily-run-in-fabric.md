---
id: datacompare-daily-run-in-fabric
ts: 2026-09-08T12:30:00Z
type: semantic
scope: project:customers/Matas/DataCompare
source: /log
tags: [project, matas, datacompare, fabric, notebook, schedule, duckdb, delta, onelake, pyodbc, git-integration]
status: distilled
description: "The DataCompare daily run lives in Fabric (NB_DataCompare_Daily, 05:00 UTC): DuckDB's delta reader reads the two Link-to-Fabric lakehouses in place with a notebookutils storage token, so there is no extract step and no Matas data on disk, and pyodbc writes to the Fabric SQL database with a notebookutils token for audience https://database.windows.net/.default. The notebook is thin - deploy_fabric.py uploads compare/load_sql/fabric_sql/fabric_run to LH_DataCompare/Files/code - so the local and Fabric runs execute the same code, split at compare.table_ref, compare.connect and fabric_sql.connect(). A scheduled notebook runs as whoever created the schedule"
---

**Why it moved off the laptop.** A daily reconciliation that needs a machine awake and a user signed
in is not daily; the fab CLI token lapses; and the local path copied Matas vendor names, addresses and
bank rows to a local disk every morning. None of that needed anything from Matas: a Fabric schedule
runs under the identity of whoever created or last updated it (MS Learn, Security context of running
notebook), so a service principal is an upgrade, not a prerequisite.

**Runtime facts, from a probe run in the workspace and then deleted.** Python 3.12.12; duckdb 1.4.4
with the azure and delta extensions installable at runtime; pandas and deltalake present; ODBC Driver
18 for SQL Server present and pyodbc importable; notebookutils.credentials.getToken serves `storage`
and `https://database.windows.net/.default`; pyodbc could read the dc schema and create, insert into
and drop a table. notebookutils.data.connect_to_artifact also works but is unsuited to loading tens of
thousands of rows.

**The git-integration trap.** The workspace is connected to the Matas DevOps repo. `fab import` writes
an item behind git's back, and the workspace then reads permanently "Modified" against the branch even
when the content is byte-identical - the logicalId association is what differs. Worse: deleting the
item to clear it does not recover, because updateFromGit does nothing when the workspace head already
equals the remote commit, and a portal Commit at that moment commits the deletion. Author the notebook
in git, let the workspace update from it, and keep deploy_fabric.py to the code modules only.
