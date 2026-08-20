---
id: eval-2026-08-19-t4-gate-too-cheap
ts: 2026-08-20T00:00:00Z
type: evaluative
scope: workspace
source: session:45041831
tags: [adr-004, value-model, evaluation, time, tiers]
status: distilled
description: "Niels judged 2026-08-19's 5.5x weighted factor TOO HIGH; the whole day was carried by T4 at 6.0x, whose gate is only 20 changed lines in a turn, and one line billed memory bookkeeping to a customer task at 7.1x"
---

**The verdict.** At the 2026-08-20 `/log` review gate Niels was asked whether 2026-08-19's
**2.19 h keyboard → 12.00 h weighted billable (5.5×)** matched his gut. Answer: **too high.**
Evidence for the end-of-August ADR-004 re-evaluation.

**Where the day's weight came from — T4, not T5.** There were **no T5 events on 08-19**. Every
block was carried by T4 at 6.0×:

| Line | Keyboard | Weighted | T4 share of weighted |
|---|---|---|---|
| Carl-Ras (untagged) | 0h 44m | 3.50 h | 2.32 h (66%) |
| Carl-Ras `fabric-scaleup` | 0h 35m | 3.75 h | 1.79 h (48%) |
| Carl-Ras `operation-hardening` | 0h 08m | 1.00 h | 0.54 h (54%) |
| own/MetaAtomic | 0h 36m | 3.00 h | 0.97 h (32%) |

**T4's gate is `>= 20 weighted changed lines in a turn` (`T4_MIN_LINES`).** That is a low bar —
a 20-line SQL edit doubles the rate from T3's 3.0× to 6.0×. The step from T3 to T4 is the largest
proportional jump below T5 (2×) and the easiest to trip. On a day of ordinary editing, most turns
that touch a file at all clear it, so the day converges on 6.0× rather than sitting between tiers.

**A second, separate inflation.** The `operation-hardening` line scored **7.1× effective on 0h 08m**
with `Focus: ops/memory/store/ (4 files) 60%, context.md 40%` — memory bookkeeping and a context
update, billed against a customer task. `ops/memory/` is weighted 0.50× and `ops/tasks/`,
`ops/time/`, `ops/memory/daily/` are 0.00×, but `ops/memory/store/` at 0.50× still counts, and the
0.5 h per-line floor then rounds a fragment up. See the README's own warning that `Focus:` is a
prompt, not a verdict — here it was the verdict, and it was right.

**Two candidate fixes to weigh at the re-evaluation** (neither applied — ADR-004 is not amended by
a memory record):

1. **Raise `T4_MIN_LINES`, or lower the T4 multiplier.** 20 lines is an edit; a *senior consultant*
   turn should be a subsystem decision. The 6.0× may be right for what T4 is meant to name and
   wrong for what actually trips it.
2. **Exclude `ops/` entirely from customer-attributed weight.** `ops/memory/store/` is the
   workspace's own bookkeeping whatever task it happened under; 0.50× is a discount, not an
   exclusion.

Related: [[timesheet-period-not-day]] (measured is the claim, weighted is the evidence — so an
inflated weighted figure does not overbill by itself, it just stops justifying a lift),
ADR-004 > Evaluation plan.
