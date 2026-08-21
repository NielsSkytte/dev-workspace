---
id: marketo-write-precision-and-offset
ts: 2026-08-20T15:05:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: session:508d3307-4a64-434b-9dfe-a5ebf6eba693
tags: [project, marketo, write-back, reverse-etl, timezone, precision, data-quality]
status: distilled
description: "Marketo write path measured live: a null on a numeric field becomes 0 (so NULL-not-zero is unimplementable and only omitting the key works), a bare date into a datetime field displays a day early, and float fields keep six significant digits"
---

Measured against the live Carl Ras instance `569-TGK-793` on 2026-08-20, on one synthetic lead
(`pingala.writeback.test01@example.invalid`, id 9578783), via
`customers/Carl-Ras/datahub/tools/marketo_write_test.py`. Raw request/response pairs are in
`customers/Carl-Ras/datahub/out/marketo_calls/`.

## 0. A null on a numeric field becomes 0 — so "emit NULL, never a coalesced 0" cannot be done

The single most important finding. Measured field by field on lead 9578783, sending an explicit
JSON `null` (and, for one field, `""`) and reading the value back:

| Marketo type | fields here | sent `null` | result |
|---|---|---|---|
| integer | the six `OrderCount*` | `null` | **`0`** |
| integer | `OrderCountAccountStore` | `""` | **`0`** |
| float | the three `totalSales*` | `null` | **`0.0`** |
| boolean | `HasWebLogin` | `null` | **`false`** |
| string | `title`, `accountName`, `accountSegment1`, `accountDiscountGroup` | `null` | `null` — clears correctly |
| date | `latestPurchaseDateAccount` | `null` | `null` — clears correctly |
| datetime | the five `Latest*Date*` | `null` | `null` — clears correctly |

**Marketo has no null for a numeric or boolean field on this API path.** Both `null` and `""`
coerce to `0` / `false`. So writing NULL to express "this account has no invoiced orders" produces
**exactly the zero the whole policy exists to prevent** — the same value Impact's
`coalesce(...,0)` writes, arrived at by a different route.

The only way to express "no value" on those ten fields is to **omit the key from the payload**.
But omission means *leave whatever is there*, not *unknown* — so a lead whose account join misses
keeps Marketo's prior value, which may be Impact's stale zero. There is no third option.

Consequence for the project convention in `customers/Carl-Ras/datahub/CLAUDE.md`
("Outbound emits `NULL`, never a coalesced `0`"): **it is unimplementable as written for the nine
numeric fields plus `HasWebLogin`.** The rule has to become "omit the key", and the difference
matters — omitting is not neutral, it is a decision to leave a possibly-wrong value in place.
Strings, dates and datetimes are unaffected and can genuinely be cleared.

## 1. The date offset — a bare date lands on the previous day

Marketo has two distinct field types and they behave differently:

| Marketo type | sent | stored (REST read-back) | shown in activity log / UI |
|---|---|---|---|
| `date` | `"2026-08-20"` | `2026-08-20` | `2026-08-20` |
| `datetime` | `"2026-08-19"` | `2026-08-19T00:00:00Z` | **`2026-08-18 19:00:00`** |

**The API is not lying and nothing is lost.** A bare date is taken as **UTC midnight**; the
instance renders in **UTC-5**, so the displayed date is the day before at 19:00. The REST
read-back returns exactly what was sent, which is why this is invisible to an integration that
only ever reads back through the API.

Where it bites: the **activity log, the Marketo UI, and any smart-list date filter a marketer
builds** all use the local rendering. So segmentation on "purchased in the last 7 days" evaluates
against a date one day early.

Of Carl Ras's six outbound date columns, **five are `datetime`** and only
`latestPurchaseDateAccount` is a true `date`. So five of six shift.

**Fix:** send an explicit offset that puts the intended day at local midnight —
`"2026-08-19T00:00:00-05:00"` — not a bare date.

**This reproduces the incumbent exactly.** Impact's values carry a time component of 18:00 or
19:00 (the two CST/CDT offsets) on 100% of records, which is the same mechanism: they send UTC
midnight too. So Carl Ras's marketers have been segmenting a day early all along. Ask Impact how
they handle it rather than silently matching it — and note that fixing it on our side makes our
values differ from theirs by a day during any parallel run.

## 2. Float fields keep six significant digits

| sent | stored |
|---|---|
| `123456.78` | `123457.0` |
| `23456.78` | `23456.8` |
| `40646631.78` | `40646600.0` |

Six significant digits, consistently. The third row is the **actual maximum**
`totalSalesAccount` in Carl Ras's data — **31.78 DKK lost**. Above ~1M DKK the rounding is whole
kroner; at the top of the range it is hundreds.

Integer fields (`OrderCount*`) are exact. Only the three `totalSales*` floats are affected.

Two consequences:
- `decimal(38,6)` in `outbound.Marketo_Lead` is pointless past six significant digits.
- **A cutover diff cannot be an equality test.** Marketo's own stored value will not equal
  curated's, so the comparison needs a relative tolerance or it reports false mismatches.

## 3. Two mechanics worth keeping

- **`requestId` is the reconciliation key.** It is returned in the POST response and *stamped onto
  every resulting Change Data Value activity* (`Request Id = 11d16#1a01fa3ccdb`). No endpoint
  accepts it as a parameter, so it is not queryable — but it is recoverable by reading activities,
  which is how a push gets audited field-by-field after the fact.
- **An unchanged value logs nothing.** A 20-field update produced 19 activities because one field
  already held the target value. Re-pushing unchanged data costs API calls but no activity volume
  and fires no triggers.

## 4. Campaigns do fire, and creation is the riskier half

Creating the test lead triggered a smart campaign five seconds later — `Call Webhook` /
`DM-Raptor ID update.01-Request REAID`, an outbound call to the Raptor personalisation vendor
(returned 400 on a synthetic address). The 20-field **update** fired nothing: all 19 activities
were type 13.

So on this instance the live trigger is on person creation, which an `updateOnly` write-back never
does. Not proof that no field carries a data-value trigger — only that none of these 20 do today.
No API exposes campaign trigger definitions; reading the lead's activity log after a write is the
only way to find out.
