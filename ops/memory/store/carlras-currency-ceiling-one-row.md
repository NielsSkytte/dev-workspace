---
id: carlras-currency-ceiling-one-row
ts: 2026-08-19T10:30:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: session:3582ea00-1223-4496-8acc-d74e4a5b233d
tags: [project, fabric, semantic-model, refresh, data-quality]
status: distilled
description: "Carl Ras: one mistyped AX09 value killed the whole TEST model refresh - a Fixed Decimal Number column is Currency, ceiling 922,337,203,685,477.5807, and nothing in Atomic checks a value's range"
---

Hand-written from the session.

## The mechanic

A semantic-model column typed **Fixed Decimal Number** is stored as **Currency**: max magnitude
`922,337,203,685,477.5807`. One source row above that fails the import with

```
0xC112001A  Value was either too large or too small for a Currency.
            The exception was raised by the IDataReader interface.
```

and, because a refresh is one transaction, **every table rolls back** — `0xC11C0006` on the rest.
The message names no table and no column, which is what makes it expensive to diagnose.

In TMDL the type is written `dataType: decimal` (= Fixed Decimal / Currency);
`dataType: double` is Decimal Number and has no such ceiling.

## What it was here (2026-08-19)

`fact.CampaignForecasts.ForecastQuantity` = **2222222222222222** — sixteen 2s, a stuck key.
Entered in AX09 by user `SOUR` on 2026-08-18 09:03; campaign 848150 *"2026 09 Festool Roadshow
Aarhus"*, item `44011068`, `crcampaignforecast.RecId` 5638443880. Ingested into TEST 04:25, killed
the 04:45 refresh. DEV was clean only because its snapshot predates the entry.

**Not caused by any change of ours.** `Campaign Forecasts.tmdl` had not been touched since
`144c901`; the first hypothesis (GEN-007 retyping CVR `EmployeesFte` to `decimal(28,12)`) was
wrong — see `eval-2026-08-19-recent-change-bias`.

## How to find it

Sweep every Currency-typed curated column for `MAX(ABS(col))` and a count over the ceiling — 66
columns here, exactly one violation.
`customers/Carl-Ras/datahub/tools/find_out_of_range_currency.sql` holds both the AX09 record lookup
and the full sweep. Map the columns by grepping the model for `dataType: decimal` and reading each
one's `sourceColumn`.

**Already close to the same ceiling:** `fact.InventoryTransactions.CostAmountPostedMST` at
4.85e14 — 53% of it.

## Atomic checks cardinality, nothing else

The only quality gate is `rowcheck.<Table>` -> `transform.sp_RowCheck` -> `transform.RowCheckLog`,
and it compares one number: expected `COUNT(*)` vs actual. No value domain, no range, no
nullability, no notification. The value cleared raw, enriched and curated untouched and stopped
only at Analysis Services, by accident. Spun out as task
`2026-08-19-carlras-atomic-dataquality-gate`.

## Fix applied

`Campaign Forecasts[Forecast Quantity]` retyped to Decimal Number — in place on the TEST model via
`updateDefinition`, and in `Semantic-Model` (landed in `503b5d4`, live in Semantic-Model-DEV), so a
DEV->TEST deployment no longer reverts it. TEST refresh green at 08:11: 14 min, one memory-ceiling
probe (5090 MB vs 5084 MB limit) then five adaptive batches — that probe is the loader planning
batch size, not a data error.

Retyping only stops bad input from killing the refresh; the AX09 record still has to be corrected
at source.
