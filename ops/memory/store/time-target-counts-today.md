---
id: time-target-counts-today
ts: 2026-08-20T00:00:00Z
type: semantic
scope: workspace
source: session:45041831
tags: [time, rollup, dashboard, adr-005]
status: distilled
description: "rollup.py --check counts the running day in the week target, so a mid-week check always reads short; the dashboard's Week audit page excludes it - two views of the same rule, deliberately different"
---

`rollup.py --check` adds a full 7.5 h to the week target for **every** workday that is not an
absence day, including **today**. Mid-week that guarantees a shortfall: on 2026-08-20 (Thu) it
printed W34 as *24.50 h of 30.00 h (82%), short by 5.50 h* while the week had in fact billed
8.00 h a day on every day that was over.

The dashboard's **Week audit** page (`#timesheet/audit`, added 2026-08-20) takes the other view:
a day still running is given a target of 0 and shown as `today`, so the same week reads
**24.00 h of 22.50 h (107%)**. A day that cannot yet be complete cannot be judged short.

**Both are on purpose, and they answer different questions.** The check is a *nag* — it should
overstate the gap while there is still time to close it. The page is a *verdict* — it is read
when deciding whether to `--topup`, and an inflated shortfall there would invite a lift that the
week does not need.

**What follows:** never quote the check's mid-week "short by X" as the number to close. Wait for
the week to complete, or read the audit page. The two only agree once the last day is finalized.

Related: [[timesheet-period-not-day]] (the billable unit is the week), ADR-005 v2.
