---
title: Carl Ras — raw AX09 keeps two SCDcurrent rows per key on sqldictionary (bad key map), audit the other tables
status: open
created: 2026-08-14
project: customers/Carl-Ras/datahub
owner: fabric-back
priority: normal
blocked_by:
activity: AX09Import
fno_task:
source: direct
---

## What

`Lakehouse_Raw_AX09.sqldictionary` holds **more than one row flagged `SCDcurrent = 'true'` for the
same business key**. Measured 2026-08-14: **549 `(TABLEID, FIELDID)` keys across 1,427 rows.**

**Cause.** `Lakehouse_Util.rawtablekeymap_ax09` keys this table on `RECID` alone:

| COLUMN | SCDType | TABLE |
|---|---|---|
| `RECID,DATAAREAID` | 2 | DEFAULT |
| `Dataareaid,Itemid,Inventlocationid` | 2 | Inventsumdim |
| `RECID` | 2 | DATAAREA |
| **`RECID`** | 2 | **SQLDICTIONARY** |

`RECID` is not the business key of `sqldictionary` — `(TABLEID, FIELDID)` is. When AX re-creates a
dictionary entry it gets a **new `RECID`**, so the SCD2 load sees a brand-new record rather than an
update to an existing one, and never closes the old row. Both stay current, forever.

Concrete: `SALESLINE`, `FIELDID` 0, `TABLEID` 359 — two rows, `RECID` 5637429721 (effective
2026-04-21) and 5637466263 (effective **2026-08-14 07:09:33**). `CRREPORTINGGROUPS` has been in the
same state since 2026-05-07.

## Why it matters

Every enriched view that joins `sqldictionary` for `PIN_PrimaryTable` / `PIN_PrimaryTableId` gets
one output row per duplicate. It already caused a real defect: it doubled **8,544 rows** in
`enriched.SalesLineTransactions` — every line with no `inventtrans` match — which is the entire
unexplained remainder of that table's row-count failure.

That symptom is patched defensively in the view (GEN-005, `Fabric-ETL` `3a72fca`), **but the raw
data is still wrong** and anything else joining `sqldictionary` inherits it. It is also growing: a
new duplicate appeared the morning of 2026-08-14.

**Latent, not yet firing:** `viewtransform.SalesInvoiceTransactions` has the same unguarded
dictionary join, resolving to `custinvoicetrans` / `inventtrans`. Both have exactly one current row
today so that view is correct — it doubles the day AX re-creates either entry.

## To do

1. **Re-key `SQLDICTIONARY` to `TABLEID,FIELDID`** in `NB_Table_PrimaryKeyMap_AX09` (the notebook
   that populates `rawtablekeymap_ax09`; `PL_IaC_PopulateLakehouseUtil` runs it). Ship it in git,
   then re-seed each environment.
2. **Repair the existing raw rows** — the key-map change fixes future loads, not the 549 keys
   already duplicated. Needs a re-ingest or a targeted close-out of the superseded rows.
3. **Audit every other table for the same class of error.** `DATAAREA` also keys on bare `RECID`,
   and the `DEFAULT` is `RECID,DATAAREAID`. The general test: for each raw table, does any business
   key carry more than one `SCDcurrent = 'true'` row? Anything that answers yes is silently
   fanning out every view that joins it.
4. Once raw is clean, decide whether GEN-005's defensive `TOP (1)` stays or is reverted.

## How to see it

```sql
SELECT TABLEID, FIELDID, COUNT(*) AS current_rows
FROM [Lakehouse_Raw_AX09].[dbo].[sqldictionary]
WHERE SCDcurrent = 'true'
GROUP BY TABLEID, FIELDID
HAVING COUNT(*) > 1;
```

Run it with `tools/wh_query.py` against `Warehouse_Enriched_AX09` (cross-database) — the
`Lakehouse_Raw_AX09` SQL endpoint still cannot serve data itself.

## Notes

- Found while diagnosing `2026-08-14-carlras-enriched-rowcount-failures`. Full write-up:
  `design/ATOMIC_GENERATOR_CHANGES.md` > GEN-005.
- This is **not** an Atomic generator issue. The generated view is reasonable; the raw layer is
  breaking the one-current-row-per-key contract the view assumes. Do not hand it to Simon.

## Log
2026-08-14 — created; cause identified and measured, nothing fixed in raw yet.
