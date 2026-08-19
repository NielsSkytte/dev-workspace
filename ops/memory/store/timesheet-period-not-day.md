---
id: timesheet-period-not-day
ts: 2026-08-19T19:30:00Z
type: semantic
scope: workspace
source: session:metaatomic-fabric-host
tags: [time-tracking, billing, adr-005, adr-004, rollup, decision]
status: distilled
description: "The billable unit is the WEEK, not the day: the timesheet records measured time, closing a short period to 100% is a deliberate --topup with the value model as evidence, and 12 h per customer per date is a hard cap that spills"
---

ADR-005 was accepted on 2026-08-17 and amended twice on 2026-08-19, before v1 had written a single
day. What changed is the *unit* and the *agency*, not the goal.

## The goal, unchanged

A normal working week should end up billed in full. Elapsed keyboard time measures how long work
took, not what it was worth, and the value model (ADR-004) usually justifies the full day on its own.

## What was wrong with v1

v1 floored **every worked day** to 7.5 h automatically at finalize. Two things are wrong with that:

- **The day is the wrong unit.** 2026-W33 measured 39.75 h against a 37.50 h target — 106% — while
  containing three days under 7.5 h. v1 would have lifted all three and taken an already-full week
  to roughly 46 h. A 3 h Tuesday next to an 11 h Wednesday is one full week.
- **The tooling was deciding.** A timesheet that claims something nobody chose is the same failure
  mode as a page asserting a number nobody read.

## The rule now

| | |
|---|---|
| Default | finalize writes **measured** hours. Nothing is topped up automatically. |
| Closing a gap | `rollup.py --topup <week\|month>` — dry run; `--apply` writes |
| Evidence | the weighted hours from `value/<date>.md` print beside every proposed lift, and any lift that exceeds them is flagged |
| Ceiling | no day is lifted above 7.5 h; weekends never; shortest days fill first |
| Cap | **12 h per customer per date**, hard. Over it, hours **spill** to another date for the same customer — moved, never dropped, every move printed |

The cap's grain is deliberate. "You billed me 18 hours in one day" is a statement about a *customer*,
not a folder; 12 h across two customers is unremarkable because neither can see the other. A day that
**measured** long stays long — the cap exists so that *combining* days cannot manufacture one.

**The evidence check paid for itself immediately:** a dry run over 2026-W31 proposes lifts on two days
whose weighted hours sit *below* the claim (3.25 h weighted against a 7.25 h claim). Under v1 both
would have been written silently.

**Pattern worth keeping.** Both amendments moved the same way: from a rule the tooling applies to a
decision a person makes, with the evidence printed next to it. That is the third time in two days
(the others: never overwrite an authored document; refresh a derived block but never a judgement one).

Related: [[time-wrapup-attribution]], [[value-model-mode-pricing]]
