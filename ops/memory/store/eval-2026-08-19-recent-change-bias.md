---
id: eval-2026-08-19-recent-change-bias
ts: 2026-08-19T10:30:00Z
type: evaluative
scope: workspace
source: session:3582ea00-1223-4496-8acc-d74e4a5b233d
tags: [evaluation, diagnosis, own-output]
status: distilled
description: "Asked 'did we touch currency?', I reached first for the most recent currency-adjacent commit; it was wrong, and measuring all 66 candidate columns found the real cause in one query"
---

## What happened

Niels asked whether we had touched currency. My first hypothesis was **GEN-007** (`7944b67`),
which had just retyped enriched CVR `EmployeesFte` from `varchar(8000)` to `decimal(28,12)` — the
most recent commit anywhere near a decimal type. Plausible, recent, in the right layer, and wrong.

What actually found it: enumerating **every** column the model types as Fixed Decimal Number (66,
by grepping `dataType: decimal` in the TMDL and reading each `sourceColumn`), then one query for
`MAX(ABS(col))` and a count over the Currency ceiling across all of them. Exactly one violation,
in a table nobody had touched — `fact.CampaignForecasts.ForecastQuantity`.

## The lesson

"What changed recently?" is a good question for a regression and a **bad** one for a failure whose
trigger is data. The AX09 row arrived 24 h earlier; no commit was involved. Recency felt like
evidence because the recent change was in the right neighbourhood.

**Rule:** when the error names a *class* of value rather than an object — a type ceiling, an
overflow, a conversion — enumerate the whole class and measure it before reading commit history.
The sweep cost one query and settled it; the commit archaeology would not have, at any depth.

## Related

- `carlras-currency-ceiling-one-row` — the finding itself.
- Same shape as `eval-2026-08-18-predicted-one-emptied-table`: reasoning from a plausible partial
  view instead of measuring the full set.
