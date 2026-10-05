---
id: fno-entry-day-rule-7-5-max-9
ts: 2026-09-29T12:00:00Z
type: semantic
scope: workspace
source: session:a110c294
tags: [fno, time, registration, day-cap, entry]
status: distilled
description: "F&O entry lines per customer per date: 7.5 h a normal day, 9 h cap, 12 h allowed when the tracked data supports it, no total limit per day (owner, revised 2026-10-05), within the ISO week on weekdays (owner, 2026-09-29). Enforced by packDays in ops/web/time.js on consolidated rows; the timesheet cap (rollup DAY_CAP 12 h per customer per date, ADR-005) is unchanged"
---

**The rule (owner, 2026-09-29):** what goes into F&O is laid out per customer as normal days --
7.5 h, never more than 9 h on one date -- *"distributed across the week normally in 7,5 max 9
hours per day"*. Per customer, not per day across all companies. Weekends only when a week has no
weekday in range.

**Revised 2026-10-05 (owner):** 9 h per customer/project per day, with an option of 12 h when the
tracked data supports it; no limit in total per day. `packDays` does not yet implement the 12 h
exception (owner chose to leave the code as is). Skill: `time-tracking-to-fno` > `references/fno-entry.md`.

**Where it lives.** `packDays` in `ops/web/time.js`, applied to consolidated entry rows AFTER
`scaleRows`: each line keeps its own weekday up to 7.5 h, the excess fills other weekdays of the
same ISO week (and range) to 7.5, then to 9. Totals per dimension unchanged. A day that still
cannot fit is marked "over 9 h" on the row. Scaling up to the F&O entry figure was what pushed
lines past the old cap -- consolidation capped, scaling then inflated.

**Not changed:** `rollup.DAY_CAP = 12.0` (h per customer per date, ADR-005) still governs
finalized timesheets -- that is the record of work, not of registration. The Consolidated chip
used to say "max 9 h a day" while the code said 12 per customer; the text now describes packDays.

**September 2026 was registered before the rule was encoded** and went out with Carl Ras 02-09
9.50 and 09-09 12.75, Matas 07-09 11.25 / 08-09 10.75, Aeven 12-09 / 13-09 12.00 each. The
journals were posted before they could be corrected; owner chose to leave them (a correction
journal would add reversal entries to the project ledger).

**Also observed 2026-09-29:** journals approved (Godkendelse -> Finished) were posted by someone
else the same day -- not by this session. Approved is not a resting state to count on for later
edits; make every correction before approving.
