---
id: bonus-model-faktureringsprocent
ts: 2026-09-02T09:00:00Z
type: semantic
scope: workspace
source: session:e15b57a5
tags: [time, bonus, fno, utilisation, money, close]
status: distilled
description: "Niels's bonus is a step function on faktureringsprocent evaluated PER MONTH, the denominator is calendar workdays and is not reduced by vacation, and the 50% tier pays nothing"
---

The bonus runs on **faktureringsprocent = Fakturerbare timer / Timer per måned**, read off
`https://pingprod.operations.dynamics.com/?cmp=ping&mi=HRMUtalizationEmplTrans_PIN`
("Beregnet nytte per medarbejder per periode"). `ops/time/bonus.py` implements it; `/fno` runs it as
a gate before entry.

| faktureringsprocent | bonus |
|---|---|
| 50% | **0%** |
| 60% | 2% |
| 70% | 10% |
| 80% | 16% |
| 90% | 20% |
| 100% and above | 24% (capped) |

**It is a step function, so the boundary is what matters.** 89.8% pays the 80% rate. A fraction of an
hour on the wrong side of a whole-10% mark is worth thousands of kroner — at 143.68 h against a
160 h basis you are 0.32 h short of 90% and about 7,000 kr poorer for it. At every close, report the
tier, the margin above the line, and the distance to the next boundary.

**Per month, never accumulated** (Niels, 2026-09-02). Each month stands alone — a weak month cannot
be rescued by a later strong one. May–Aug 2026 taken together is 46.10% and would pay nothing;
taken monthly, August pays 20%.

**The denominator changes every month — never assume one.** May 140.00, Jun 163.00, Jul 170.00,
Aug 155.50, Sep 163.00. It tracks calendar workdays at roughly 7.4 h/day, but not by an exact
constant, so **read it, don't compute it**. Assuming a flat 160 put August at 90.6% when it is
93.25% — a whole tier of error.

**Vacation does not lower the target.** August has 21 arbejdsdage and Niels took a week off; a
reduced basis would read ~118 h, but F&O shows the full 155.50. A vacation week therefore costs
~37 h of billing capacity against an unmoved target: **a month containing holiday is structurally
harder, and that should be known going in, not at the close.** Not confirmed with HR whether the
bonus rule adjusts separately — the page does not.

**Two percentages on that page, and only one pays.** *Nytte til stede* uses **Normtimer** (141.00 in
August), which **is** absence-adjusted, giving a flattering 102.84%. The bonus does not use it. The
workspace's own coverage check behaves like Normtimer — `absence.md` removes vacation from its
denominator, which is why August reads **104% internally and 93.25% for bonus**. Both are right;
they answer different questions.

**The 50% tier pays 0%, so reaching it is worth nothing** — the first paying boundary is 60%. July
2026 landed 1.00 h short of 50% and lost nothing by it.

**What a near boundary licenses.** Going *looking* for hours genuinely worked and never registered —
an unlogged meeting, a day the value model supports and the timesheet undercounts, customer work
sitting in internal. **Never** entering hours that were not worked. The evidence rule is unchanged:
`time-shortfall-can-be-in-the-target`.

**Timing vacation: there is no general rule, and the direction flips.** Since the target is not
reduced, it looks as though concentrating vacation in one month beats spreading it. Tested over two
months with ten vacation days, the winner depends entirely on how much is billed per working day:

| billable h / working day | 10 days in one month | 5 + 5 split | winner |
|---|---|---|---|
| 9.06 (Aug 2026's actual) | 57,187 kr | 69,581 kr | split, +12,394 |
| 8.00 | 48,384 kr | 49,152 kr | split, +768 |
| 7.40 | 37,296 kr | 28,416 kr | concentrate, +8,880 |

The question is never "concentrate or spread" but **which arrangement puts more months just above a
boundary instead of just below one**. The asymmetry runs against concentrating: the top is capped at
24%, so a month at 122% pays no more than one at 105%, while the bottom collapses — 65% pays 2% and
55% pays nothing. **A month falling below ~70% is the thing to avoid**, and that is exactly what
piling all the vacation into one month risks.

**A caveat that may dissolve the whole question.** August billed 145.00 h across 16 working days =
9.06 h/day, well above the 7.4 h/day the basis assumes. That is evidence the work is demand-limited
and gets *compressed* rather than lost — in which case vacation costs no billable hours and its
timing is irrelevant to the bonus. The truth is likely between the two models; 9.06 h/day is
probably not sustainable across a full month.
