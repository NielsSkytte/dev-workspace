# ADR-005: Full-Day Floor + Weekly Coverage Check

| Field       | Value                        |
|-------------|------------------------------|
| Status      | Accepted                     |
| Date        | 2026-08-17                   |
| Author      | Niels                        |
| Reviewers   | -                            |

Extends ADR-002 (*Per-Project Time Tracking*) and ADR-004 (*Value-Based Billing*).
Attribution (ADR-003) and the F&O dimensions are unchanged. This ADR changes **what number
lands in the timesheet** for a day that was worked.

---

## Context

ADR-004 established that elapsed time and delivered value have come apart: 13.8 h of measured
keyboard time on billable work produced 58.00 h on the timesheet, and the ElementLogic lineage
engine was built in 4.14 h of keyboard time. ADR-004 derived the second number (weighted hours)
but deliberately stopped short of the timesheet — nothing was invoiced from it.

That left the timesheet still driven by elapsed time, with two consequences:

- A month of full working days produces a month of **partial** timesheets. Measured over
  2026-07-06 to 2026-08-13, most workdays landed between 1.5 h and 6 h; the monthly total was
  well under 7.5 h x working days even though every one of those days was worked.
- A day with **no** keyboard time is indistinguishable from a day that never got asked about.
  Vacation, a public holiday, a customer workshop and a forgotten day all look identical: absent.

## Decision

**1. A workday that saw real work is claimed as a full day (7.5 h).**
"Real work" = total active time (the 15+5 model, all projects merged) of at least 0.5 h on a
Mon–Fri date. The deficit to 7.5 h is split proportionally across the day's **billable** lines;
internal lines stay exactly as measured. Weekends are never floored — weekend hours are claimed
as measured, on top of the target.

**2. The floor is applied at finalize, never retroactively.**
`rollup.py` floors a day as it writes `timesheet/<date>.md`, and stamps the raw and claimed
totals into the file. A finalized day is never rewritten — a past month may already be invoiced.

**3. Empty workdays must be answered.**
`ops/time/absence.md` records why: `vacation` / `holiday` / `sick` (removed from the target, no
timesheet) or `offline` (worked away from this keyboard — kept in the target, claimed as a full
day on a named project).

**4. A coverage check runs per ISO week, with every rollup.**
`rollup.py --check` reports the week against 7.5 h x workdays, the month to date against the same
guarantee, every unaccounted workday, and every finalized day sitting below the floor.

## Consequences

- The timesheet is now a **claim**, not a measurement. `value/<date>.md` (ADR-004) is the evidence
  on file behind it, and every floored daily file names the raw figure it was lifted from. Nothing
  is hidden; both numbers survive.
- Backfilling is a manual decision. Days finalized before 2026-08-17 keep their measured hours;
  the check lists them with the top-up needed.
- The floor is conservative against the value model. On 2026-08-13 the timesheet read 5.00 h and
  the value record justified 9.00 h weighted; the floor would have claimed 7.50 h.
- Risk accepted: a workday with 35 minutes of genuine activity and no other work is claimed at
  7.5 h. This is the intended behaviour — the day was worked, and the 0.5 h trigger only excludes
  noise. It is visible in the daily file's floor line, so an over-claim is reviewable, not silent.
- ADR-004's re-evaluation at the end of 2026-08 should now also ask whether the floor or the
  weighted hours is the better basis for the timesheet. They are currently redundant: the floor is
  the claim, weighted hours the justification.

## Implementation

`ops/time/rollup.py` (`apply_floor`, `load_absence`, `check`), `ops/time/absence.md`,
`ops/time/README.md` section 8, `/time check`, `/log` step 4.
