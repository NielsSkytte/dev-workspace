---
id: time-wrapup-attribution
ts: 2026-08-07T08:05:00Z
type: semantic
scope: workspace
source: session:a77891ac
tags: [time-tracking, billing, value-model, log, attribution]
status: distilled
description: "/log wrap-up time bills to whichever customer the session was for, but writes only workspace bookkeeping - three instances found once the value record started reporting Focus"
---

The `Focus:` line added to the value record on 2026-08-06 surfaced this on its first
run, across three separate days and three separate customers:

| Day | Billable line | Hours | Focus |
|---|---|---|---|
| 2026-08-01 | customers/Carl-Ras/datahub | 0.50 | `ops/memory/store/` 100% |
| 2026-08-01 | customers/Matas/DataCompare | 0.75 | `ops/memory/store/` 100% |
| 2026-08-06 | customers/ElementLogic/LineageDocumentation | 0.75 | `ops/memory/store/` 100% |

**The mechanism:** time attribution is task-first and falls back to cwd (ADR-003), so a
`/log` run at the end of a customer session bills to that customer — while the files it
actually writes are `ops/memory/store/` records and `ops/log/sessions.md`, i.e. Pingala's
own continuity substrate. The deliverable-class weights already discount this
(`ops/memory/` at 0.5x, `ops/memory/daily/` and `ops/tasks|time/` at 0) but the weight
scales line counts, not hours, so the hours still land on a **billable customer line**.

Unresolved, and a judgement call rather than a bug: some session-closing documentation is
plausibly part of an engagement, but writing curated memory records about our own tooling
is not. Options considered, none yet adopted: route `/log` time to `Dev` outright; keep it
on the customer but non-billable; or leave it and correct at review using `Focus` as the
prompt.

**Read `Focus: ... 100%` as a prompt, not a verdict** — it is computed from file writes
only, so a stretch of advice, analysis or review contributes hours with no focus at all.
"100% memory store" means those were the only *files written*, not that the whole line was
bookkeeping.

Related: the same review re-attributed 2026-08-04 off Element Logic — see
`lineage-business-descriptions` for the customer-requested-vs-capability split, where the
answer was to split the day rather than move it whole.
