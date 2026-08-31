---
id: tmdl-calculated-tables-serialize-as-import
ts: 2026-08-31T10:30:00Z
type: semantic
scope: workspace
source: session:f17772e8-6514-4c38-b590-03daab4595e6
tags: [fabric, semantic-model, direct-lake, tmdl, verification]
status: distilled
description: "TMDL always serializes a calculated table as `mode: import`, so grepping a Direct Lake model for import partitions overcounts - check the data sources, not the partition modes"
---

Settled 2026-08-31 on Carl Ras `Model_OneLake`.

## The trap

Two task files disagreed for ten days on whether `Model_OneLake` was pure Direct Lake. One said
"pure"; the other said "not pure - 7 partitions are still `mode: import`". Both had read the same
TMDL.

**A calculated table has no storage mode of its own.** Its partition is
`partition … = calculated` with a DAX `source`, and TMDL writes `mode: import` for it regardless of
what the rest of the model does. Field-parameter tables, measure-holder tables and
`GENERATESERIES` helpers all land in that bucket.

Counting `mode: import` therefore reports every calculated table as an Import table.

## The reliable test

Read `expressions.tmdl` and the model's data sources:

- `Model_OneLake`: **one** source, `AzureStorage.DataLake` on the curated warehouse's OneLake path.
  No `Sql.Database` anywhere. => genuinely pure Direct Lake, 28 directLake tables + 7 calculated +
  3 calculation groups.
- The Import `Model` beside it: a real `Sql.Database("<endpoint>", "Warehouse_Curated")`. => Import.

So the question "is this model Import or Direct Lake" is answered by **which connections it holds**,
never by tallying partition modes.

## Confirming behaviour separately

A Direct Lake table that has never appeared in a `DirectLakeFraming` event can still answer a query —
automatic framing picks it up. `Budget Ledger` returned 842,590 rows / -517,770,124.91 via
`executeQueries` with no framing event of its own in the refresh history. Absence of a framing event
is not evidence the table is unusable; run the query.

## Related

- `carlras-directlake-conversion`
- `directlake-drop-create-window`
