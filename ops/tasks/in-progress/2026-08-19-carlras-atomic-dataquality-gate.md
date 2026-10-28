---
title: Carl Ras — Atomic data-quality gate: rule-based row checks, quarantine, stakeholder notification
status: in-progress
created: 2026-08-19
project: customers/Carl-Ras/datahub
owner: fabric-back
priority: normal
blocked_by:
activity:
fno_task: CarlRData-555
customer_ask: dropped
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

## Progress

**Now (2026-10-28):** the DQ mail names its environment (released to Carl Ras DEV + TEST, engine `c055c15`). The app
now shows every page in its own bundled UI, and the menu shows the UI and engine versions. The TEST mail still fails:
the Outlook connection is Niels's and Fabric refuses to share it (403). Mail route A/B/C is waiting for Niels. Built in
own `823f5ba` and changed in `d673ab3` (Niels: no stored examples, live query only). Live on base only: a side panel per
issue that reads the failing rows live through the app's `drill` function (mssql, app identity). The run stores only
the query (`drill/<id>.json`), never the rows. Run time (`8e45433`): NB_DataQuality took 150 min on base on 10-25; the
lineage lookup rebuilt the store graph per column (~50 min), now built once; tables run 8 at a time (`workers`), each
with its own SQL hook; every table records its time per step (`timing`, summary in dq.json). Base test run of
NB_DataQuality alone started 18:55 UTC (job `1770250a`). NB_MetaAtomic (lineage, ~105 min) not yet looked at. Also new: expectation kind `except`, which accepts a
group of rows (a column and its values, covers later rows) or single rows (key plus failing value), with a review
date. The run counts the rows it takes out and accepts an issue left with none. Carl Ras redeploy waits for Niels's
MFA sign-in.

**Earlier (2026-10-26):** the 10-13 block below is overtaken by the Fabric App build (own/MetaAtomic
`docs/fabric-app-build-plan.md`; task `2026-09-09-carlras-metaatomic-implementation`). The store exists:
`MetaAtomic_Store` in Fabric-ETL-DEV (schema 4, loaded by `PL_UpdateLineage` since 10-21) and a TEST store. The DQ page
runs in the Fabric App at Carl Ras DEV + TEST: ax09 check set 1.1 with local adjustments, the check builder,
engine-suggested exceptions. Quarantine has still not run in Fabric.

**Earlier (2026-10-13):** quarantine is built in MetaAtomic (ADR 0018, `54d9f95`, 136 tests pass). It reverses the 09-18
deferral for exact row-level rules, on Niels's 10-13 instruction: rules `validity.value_range` and
`validity.allowed_values`, a scan that copies failing rows to a fix area (`quarantine.row`), a filter the load adds to its
read, an alert per owner per run (Teams, e-mail, structured event) and `NB_DataQuality` MODE `quarantine`. It has not run in
Fabric. It needs a Fabric SQL database for the store (none at Carl Ras), a Teams webhook, Key Vault secrets, and the rule
declared with an owner and a key. Data quality itself runs in Fabric since 10-13 (run `a1d06a51`). Worker findings for an AX
data-quality package are in `customers/Carl-Ras/datahub/design/ax_dq/` (not re-run by me). The triggering AX09 row was
last measured uncorrected on 08-31; not re-checked.

**Tried and dropped:** nothing yet.

**Scope history.** 2026-09-18 (Niels): reporting only, quarantine deferred. 2026-10-13 (Niels): quarantine is wanted, with
an alert to the source owner every time it happens. Part 2 is built; part 3 (notification) is built as part of it.

**Next:**
1. ~~Provision the Fabric SQL database for the store~~ done: `MetaAtomic_Store` (10-21).
2. Pick the Teams webhook and the Key Vault; name the owner of the AX09 source for the alert.
3. Declare the Forecast Quantity rule in `dq_expectations.json` (value range, `RECID` as key, owner), then run
   `quarantine scan` in DEV before a load.
4. Fix `Model_OneLake`'s `Forecast Quantity` type before promotion.

## Needs from customer

- **Carl Ras: correct `crcampaignforecast.RecId 5638443880`** (`FORECASTQTY = 2222222222222222`, user
  `SOUR`, 2026-08-18). Correction initiated by Niels 08-19; still uncorrected 08-31; follow-up not recorded.
- **Carl Ras: a plausibility limit on forecast quantity in AX09** — the right place for the check.
  **Not raised.**


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
- 2026-10-21 — Customer ask dropped: no longer relevant
- 2026-08-31 — **VERIFIED ACCURATE; premises hold and the evidence for them got stronger.** Nothing
  described here has been built: no reject/quarantine schema in `Warehouse_Enriched_AX09` or
  `Warehouse_Curated` in either environment, no rule table among `Lakehouse_Util`'s 26 tables, and no
  `WebActivity`/Office365/Teams activity in any of the seven transform pipelines.
  `transform.sp_RowCheck` is live-confirmed **logging only** — the `THROW 50001` block exists in the
  header comment, not in the body.
  - **"A log nobody watches" is now measurable.** DEV's row check has not run since **2026-08-21**
    (11 days) with two failures outstanding the whole time — `GeneralLedgerTransactions` +4 and
    `SalesInvoiceTransactions` **-1,871**, the latter a regression against the diff-0 result recorded
    on 08-14/16. TEST's runs daily and shows **six** tables red as of today's 08:44 run. Nobody is
    acting on either.
  - **The triggering source record was never corrected.** `crcampaignforecast.RecId 5638443880` still
    holds `FORECASTQTY = 2222222222222222`, `MODIFIEDDATETIME` unchanged at 2026-08-18 09:03:49 —
    13 days after the correction was initiated. The platform survives only because the model column
    was retyped.
  - **The model-side fix is live where it matters:** `Campaign Forecasts[Forecast Quantity]` is
    `dataType: double` in both DEV's and TEST's `Model`, which is what `VL_ModelId` resolves to.
    **Footnote:** `Model_OneLake`'s copy of that column is still `decimal` — harmless while that model
    is out of the refresh path, but it must be fixed before `Model_OneLake` is ever promoted.
  - Currency sweep across 65 curated columns, both environments: exactly **one** violation, the known
    row. `fact.InventoryTransactions.CostAmountPostedMST` sits at 484,633,785,324,405 = **52.5%** of
    the ceiling — unchanged, no new risk.
- 2026-09-18 — **reporting only, by decision.** Niels: data quality observes and publishes, it never stops
  or alters a data load. Quarantine deferred (see Progress). Recorded in
  `customers/Carl-Ras/datahub/CONTEXT_DECISIONS.md` and `own/MetaAtomic/CONTEXT_DECISIONS.md`.
- 2026-08-19 — created after the Currency overflow took down the TEST model refresh.
- 2026-09-16 — brought onto the Progress shape (Progress + Needs from customer, `fno_task` / `customer_ask` set, `activity` blanked per CLAUDE.md task-always rule); no facts changed. Card: `customers/Carl-Ras/datahub/CONTEXT.md`.
- 2026-10-13 — started: quarantine built in MetaAtomic (ADR 0018, `54d9f95`), not run in Fabric; moved to in-progress.
