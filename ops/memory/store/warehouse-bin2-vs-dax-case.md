---
id: warehouse-bin2-vs-dax-case
type: semantic
status: distilled
created: 2026-08-19
source: ops/memory/daily/2026-08-19.md
project: customers/Carl-Ras/datahub
---

# Moving DAX logic into a Fabric Warehouse: two traps SQL alone will pass

**1. BIN2 versus DAX case-folding.** `Warehouse_Curated` is `Latin1_General_100_BIN2_UTF8` -
case-sensitive. DAX compares strings case-insensitively. A uniqueness column built with
`ROW_NUMBER() OVER (PARTITION BY [Txt] ...)` gave **1,320 distinct in SQL but 1,316 in the model**,
because four `Txt` values differed only by case: each pair was partitioned separately, both got index
0, and they collided once DAX folded the case. Four report rows would still have merged - the exact
thing the column existed to prevent. `PARTITION BY UPPER([Txt])` fixes it.

**Rule: SQL agreeing with itself is not evidence that the model agrees.** Verify a moved calculation
in the model, not only in the warehouse.

**2. A Fabric Warehouse CTAS rejects `nvarchar`.** `NCHAR(8203)` yields nvarchar and
`sp_CreateDimTableAsSelect` fails with "The data type nvarchar(4000) in column ... is not supported
in this edition of SQL Server." Cast to `VARCHAR(n)`. And because the procedure **drops before it
creates**, that failure left `dim.AlternativeChartOfAccount` missing until the cast was added - the
same failure mode that removed `enriched.SalesLineTransactions` for 47 minutes on 2026-08-16.
