# ADR-005: Full Working Periods + Weekly Coverage Check

| Field       | Value                        |
|-------------|------------------------------|
| Status      | Accepted (v2, amended 2026-08-19 before v1 had written a day) |
| Date        | 2026-08-17, amended 2026-08-19 |
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

## Decision (v2, 2026-08-19)

**1. The goal is a full *period*, not a full day.** A normal working week should end up billed in
full. Days vary — 3 h next to 11 h is one full week — so the day is the wrong unit and the period
(week or month) is the right one.

**2. The timesheet records MEASURED time. Nothing is topped up automatically.** The value model
(ADR-004) is what justifies billing a full day, and it usually gets there on its own. When a period
still comes out short, closing it is an explicit act:

```
python ops/time/rollup.py --topup 2026-W33          # dry run
python ops/time/rollup.py --topup 2026-08 --apply   # write it
```

**2b. A top-up is bounded and evidenced.** No day is lifted above 7.5 h; weekends are never lifted;
the shortest days fill first; within a day the lift goes proportionally onto the **billable** lines
only. The weighted hours from `value/<date>.md` print beside every proposed lift and any lift that
exceeds them is flagged — a claim past its evidence is a decision and has to look like one. Every
file written records `measured -> claimed` and the period it was closing.

**2c. A short period is not automatically a rounding problem.** If the shortfall cannot be placed
because a workday has no time at all, it stays unplaced and is reported. That is a question for
`absence.md`.

**3. Empty workdays must be answered.**
`ops/time/absence.md` records why: `vacation` / `holiday` / `sick` (removed from the target, no
timesheet) or `offline` (worked away from this keyboard — kept in the target, claimed as a full
day on a named project).

**4. A coverage check runs per ISO week, with every rollup.**
`rollup.py --check` reports the week against 7.5 h x workdays, the month to date against the same
guarantee, every unaccounted workday, and every day under a full day with the weighted
hours beside it.

### What v1 said, and why it changed

v1 (2026-08-17) floored **every worked day** to 7.5 h automatically at finalize. It was replaced two
days later having written no day: an automatic per-day lift makes the timesheet claim something the
tooling decided, and the intent was always that the *multipliers* justify the full week, with a
manual lift for whatever they leave short. The mechanism moved; the goal did not.

## Consequences

- The timesheet is a **measurement** again, and becomes a **claim** only where someone lifted it —
  in which case the file says so. Both numbers survive either way.
- **The check is the workflow.** Every rollup prints, per week and per month, measured vs target,
  and for each day under 7.5 h what the value model supports. Acting on it is a `/log` decision.
- **Weeks are often already full.** 2026-W33 measured 39.75 h against a 37.50 h target (106%) with
  three individual days under 7.5 h. Under v1 those three would each have been lifted, taking a week
  that was already over target to roughly 46 h. That is the concrete reason the day is the wrong
  unit.
- **The evidence check earns its place immediately.** A dry run over 2026-W31 proposes lifts on two
  days whose weighted hours sit *below* the claim (3.25 h weighted against a 7.25 h claim). Under v1
  both would have been written silently.
- Backfilling stays a manual decision. Days finalized before this rule keep their measured hours;
  `--topup <period>` is how they get closed, and only if someone runs it.
- Risk moved rather than removed: a thin day no longer inflates itself, but a thin *period* can
  still be lifted to full. The difference is that someone chooses it, with the weighted hours in
  front of them, and the file records the choice.
- ADR-004's re-evaluation at the end of 2026-08 should ask whether weighted hours should *become*
  the timesheet basis rather than only its justification. Under v2 they are no longer redundant —
  measured is the number, weighted is the evidence, and the gap between them is exactly what a
  top-up closes.

## Amendment 2026-08-19: the per-customer day cap is 12 h, and it spills

A day that is genuinely long for one customer is fine — that is what a long day looks like. What is
not fine is several days stacking onto one date and producing a number nobody can defend. So:

- **12 h per customer per date** (`DAY_CAP` in `rollup.py`, `CUSTOMER_CAP` in `value.py` — one
  concept, one number). The grain is the customer, because that is the only view a customer has.
- **Over it, hours spill to another date** for the same customer inside the same week, largest line
  first, and every move is printed. Hours are moved, never dropped; period totals are unchanged.
- If the week has no room, the excess stays where it was measured and is reported. An honest
  over-cap day beats a fabricated date.
- The all-customers `FLAG_CAP` (15 h) is unchanged: soft, a review flag, never moves hours.

## Implementation

`ops/time/rollup.py` (`topup`, `distribute_hours`, `weighted_hours`, `load_absence`, `check`),
`ops/time/absence.md`, `ops/time/README.md` section 8, `/time check`, `/log` step 4.
