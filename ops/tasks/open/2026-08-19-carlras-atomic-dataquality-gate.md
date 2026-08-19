---
title: Carl Ras — Atomic data-quality gate: rule-based row checks, quarantine, stakeholder notification
status: open
created: 2026-08-19
project: customers/Carl-Ras/datahub
owner: fabric-back
priority: normal
blocked_by:
activity:
fno_task:
source: session
---

## What

A new Atomic capability: **check data against quality rules as it moves through the layers, hold
back the rows that fail, and notify the people who can fix them at source.**

Three parts, in the order they matter:

1. **Rules.** Declarative, per table/column — range, domain, nullability, referential, format.
   Evaluated during the load, not after it.
2. **Quarantine, not failure.** A failing row is diverted (rejected table / flagged column), the
   load completes with the rows that pass. **A curated load or a model refresh must never die
   because one source row is wrong.**
3. **Notification.** The rows that were held back go to a named stakeholder — the person who owns
   the data in the source system — with enough identity to find and correct the record.

## Why — the incident that triggered it (2026-08-19)

TEST `PL_MainExecution` failed at the semantic-model step:

```
0xC112001A  Value was either too large or too small for a Currency.
            The exception was raised by the IDataReader interface.
```

One row. AX09 user `SOUR`, 2026-08-18 09:03, campaign 848150 *"2026 09 Festool Roadshow Aarhus"*,
item `44011068`, `crcampaignforecast.RecId` 5638443880, `ForecastQuantity = 2222222222222222` —
sixteen 2s, a stuck key. The model column `Campaign Forecasts[Forecast Quantity]` is Fixed Decimal
Number, whose ceiling is 922,337,203,685,477.5807. The value cleared raw, cleared enriched, cleared
curated, and stopped the refresh transaction dead — **the entire nightly model rebuild lost to one
typo, ~24 h after it was entered.**

Two things that incident proves:

- **The value was never checked anywhere.** It failed by accident, at the last possible layer,
  because Analysis Services happens to have a numeric ceiling. Nothing in the chain asked whether
  a forecast of 2.2 quadrillion units is plausible.
- **The failure mode is the worst available.** Not "one campaign forecast is wrong" but "no data
  at all today", and nothing routed to whoever could correct the AX09 record.

## What Atomic has today

Exactly one quality gate, and it counts rows:

```sql
-- rowcheck.CampaignForecasts
SELECT 'ExpectedRowCount' = (SELECT COUNT(*) FROM [Lakehouse_Raw_AX09].[dbo].[crcampaignforecast]
                             WHERE [SCDcurrent] = 'true');
```

`transform.sp_RowCheck` compares that against the built table and writes a verdict to
`transform.RowCheckLog`. Cardinality only — no value domain, no range, no nullability, no
referential check, no notification. (And `RowCheckLog` itself went unread for a week in August
while three tables were red — see `carlras-pin-rowcheck-replacement`, so a log nobody watches is
not the answer here either. Notification is part of the feature, not a follow-up.)

## Shape to work out

- **Where the rule is evaluated** — in the `viewtransform` layer alongside the row-count
  expectation, or a separate rule table in `Lakehouse_Util` the load reads. The second keeps rules
  out of generated SQL, which matters while Atomic's views are machine-generated.
- **What "held back" means per layer.** Raw should probably keep everything (it is the source of
  record); enriched or curated is where a row gets diverted. Decide once, apply everywhere.
- **How a rejected row is surfaced.** A `reject.<Table>` table per layer with the rule id and the
  offending value, so the notification writes itself.
- **Who gets told, and how.** Owner per source table; delivery via the existing orchestration
  (pipeline mail activity / Teams webhook). One digest per run, not one message per row.
- **Interaction with `sp_CreateTableAsSelect`.** Drop-create means a rejected row simply is not in
  the new table; there is no incremental "still rejected since yesterday" state unless the reject
  table is append-only. Related: `2026-08-18-carlras-atomic-ctas-merge`.

## Not this

- Not a fix for the Currency ceiling specifically. That was closed on 2026-08-19 by typing the
  model column as Decimal Number; a range rule would have caught it earlier and told someone, which
  is the point.
- Not input validation in AX09. That is the customer's ERP and the right place for a plausibility
  limit on a forecast quantity — worth raising with Carl Ras separately, but it does not remove the
  need for the platform to survive bad input.

## Context

- Incident and the fix: session 2026-08-19, task `2026-08-11-carlras-operation-hardening`.
- `customers/Carl-Ras/datahub/tools/find_out_of_range_currency.sql` — finds the offending record
  and sweeps every Currency-typed curated column.
- Atomic changes are framework changes. Since 2026-08-19 we edit the generated files ourselves and
  git is the record — log any change as a GEN-xxx entry in
  `customers/Carl-Ras/datahub/design/ATOMIC_GENERATOR_CHANGES.md`.

## Log
- 2026-08-19 — created after the Currency overflow took down the TEST model refresh.
