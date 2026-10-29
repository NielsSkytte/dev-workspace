---
id: metaatomic-dq-run-time-20261029
ts: 2026-10-29T00:50:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: session:38b6cca4
tags: [metaatomic, data-quality, fabric-notebook, performance]
status: distilled
description: "NB_DataQuality on Pingala base 150 -> 23 min: lineage graph once per run, 8 tables in parallel, date guess on date-shaped values only, ODBC cursor instead of query() for store inserts, publish 16 files at a time"
---

Causes found 2026-10-28/29 on base (690 tables): the lineage lookup rebuilt the store graph per column
(~50 min); tables ran one at a time; the date guess ran on every value; the notebook connection's
`query()` slowed sharply with batch size (100 rows 8 s, 300 rows 75 s) while its ODBC cursor wrote 300 rows
in 0.03 s (store load 31 min -> 19 s); results were published one file at a time (10.5 -> 1.5 min). Result
unchanged (13,946 issues, score 56.6). NB_MetaAtomic (lineage) still takes ~1 h 45 min per run.
Stored failing-row examples were dropped for a live drill-down query (Niels 2026-10-28: no stored examples).
