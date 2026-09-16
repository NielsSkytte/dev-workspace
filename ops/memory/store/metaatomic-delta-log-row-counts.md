---
id: metaatomic-delta-log-row-counts
ts: 2026-09-16T09:10:00Z
type: fact
scope: own/MetaAtomic
source: /log
tags: [metaatomic, fabric, onelake, delta, row-counts, stream-matrix, carl-ras]
description: Engine 0.6.0 reads row counts from each table's Delta log in OneLake (active files at latest version, checkpoint + commits, deletion vectors subtracted); no SQL endpoint; proven to the row against Carl Ras PROD
status: distilled
---

`lineage_engine/delta_counts.py` (0.6.0, `own` b4cd8ee + bf48fda). A Fabric lakehouse or warehouse table is
a Delta table under `<item>/Tables/[<schema>/]<table>/_delta_log/`; the row count is the sum of
`stats.numRecords` over files active at the latest version (checkpoint parquet via pyarrow, then later
JSON commits; deletion-vector cardinality subtracted; a file without stats -> `partial`, lower bound).
Needs a storage token (`https://storage.azure.com`) and read on the item. Schema-less lakehouse tables
are keyed `dbo.<table>` so they compare by name with INFORMATION_SCHEMA. `COUNT_BIG(*)` over the SQL
endpoint remains only as fallback for a store whose log cannot be read.

Motive: every Carl Ras PROD lakehouse endpoint (Raw_AX09, Raw_CVR, Util) refuses every query with
"Retrieval of MWC token used for accessing storage failed" - on record (sessions 09-13) as a stale owner
credential on the item; fix is an item takeover, not done. Proven live 2026-09-16, read-only, all 14
PROD stores: on the 11 whose endpoint answers, Delta and SQL agree to the row on every table (a first
pass showed SQL lower on two landing lakehouses; minutes later equal - inference: endpoint sync lag). The
3 refusing stores are counted anyway: AX09 raw 90 tables / 471.9M rows in 124 s.
