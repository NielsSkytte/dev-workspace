---
title: Pingala — decide how to bill value delivered above the timesheet floor (rate / fixed price / component licensing)
status: open
created: 2026-08-14
project:                # workspace-level - a Pingala commercial decision, not a customer project
owner: architect
priority: normal
blocked_by: needs a pricing owner; feeds the end-of-August ADR-004 re-evaluation
activity:
fno_task:
source: direct
---

## What

Decide how Pingala captures the value it delivers when AI-augmented work produces far more than
the hours suggest. Carl Ras is the first engagement to hit it in practice; the question is general.

Concrete case (Carl Ras, 2026-08-11/12/13):

| measure | hours |
|---|---|
| Keyboard (interaction) | 6.97 |
| **Timesheet (tracked, the floor)** | **19.75** |
| Weighted (provisional model) | 31.50 |

Niels wants to bill nearer 31 than 20, with 20 as the minimum.

**Already decided, do not relitigate** (ADR-004 amendment 2026-08-14): the timesheet is always the
floor, and keyboard time is never a billing basis. The timesheet is heartbeat-derived elapsed time
with no multipliers — `rollup.py` and `value.py` are independent pipelines — so the floor is a real
measurement, not a modelled one.

## The constraint that shapes the answer

You cannot put 31 in the hours column of a time-and-materials agreement that counts hours. It
misstates the measure, and it fails on its own terms: if the agreement caps hours, inflating them
exhausts the cap sooner and the problem returns in weeks. **The number being sought is a price,
not a better hours figure.**

## Three routes to evaluate

1. **Rate, not hours.** Bill tracked hours at a higher rate. The only route that fits *inside* an
   existing hours ceiling, since it adds no hours. Frame as capability, not speed — customers pay
   more for seniority and resist paying more for velocity.
2. **Fixed price on outcome.** Stop selling hours; the agreement holds scope and price. The
   structural answer, because the ceiling only binds while the unit of sale is the hour.
3. **Component licensing.** Charge for the asset, not the time to apply it.

## The finding that matters most

**Reuse breaks the multiplier model structurally, not just quantitatively.** Reusing a built
component can deliver in 2 h what would otherwise take 200. No multiplier on 2 h reaches 200 —
that needs 100x and the tier table tops out an order of magnitude below.

Two problems wear the same coat:

- **Acceleration** — hours understate effort. A multiplier is a plausible instrument.
- **Reuse** — hours are near zero *regardless* of value. A multiplier cannot express it, because
  it scales hours and there are barely any.

ADR-004 contemplates only the first. The first is also the weaker long-term position: acceleration
is a commodity every competitor acquires with the next model generation. Reuse is Pingala's own IP
and is exactly what an hours frame can never price.

## Evidence discipline

The weighted number is evidence at negotiation, not an invoice line. Caution already on record in
`eval-2026-08-06-fitted-is-not-validated`: the multipliers are self-derived and untested against a
customer's own counterfactual, so 4.52x is a sound internal instrument and a thin argument to
someone who did not build the model.

Concrete outcomes argue better. The same session produced a measured 2.57x speedup on the enriched
build and surfaced three tables that had been silently inflating their row counts since at least
2026-08-07 with nobody told — customer-legible value with no reference to hours at all.

## Next

- Needs a **pricing owner**. Above the scope of the time-tracking system and not Niels's call alone.
- Feeds **ADR-004 evaluation question 5** at end of August: does the weighted model have anything
  useful to say about reuse, or does that case need a separate instrument entirely? The answer
  decides whether tier multipliers are the right long-term shape at all.
- Check what existing customer agreements actually permit before designing anything — the hours
  ceiling is the binding constraint and its wording will differ per contract.

## Log
2026-08-14 — created from the Carl Ras PIN_RowCheck session, where the gap between 19.75 tracked
and 31.50 weighted hours first became concrete. Written up in
`ops/decisions/ADR-004-value-based-billing.md` > Amendment 2026-08-14.
