---
id: dashboard-fno-entry-measure
ts: 2026-09-01T15:15:00Z
type: semantic
scope: workspace
source: session:e15b57a5
tags: [dashboard, time, value-model, fno, adr-004, measure]
status: distilled
description: "The dashboard's four time measures and the F&O entry figure that sits between work time and value time - entry = work + (1 - e^-x)(value - work), where x is turns and files per work hour"
---

The week/audit page is now the **primary time-entry surface** (Month is the overview) and carries
four measures per line, in this order, each with a percentage:

1. **keyboard** — raw measured keyboard time.
2. **measured** — the 15+5 active-time model (`rollup.py`).
3. **work time** — what the 15+5 model claims, with measured folded in as a % control. Divergence
   between the two means the model has drifted from what is observed; it is a check, not a bill.
4. **F&O entry** — what actually gets registered. **This is the source of truth for entry.**
5. **value time** — the ADR-004 weighted figure. The **ceiling**: the most that could defensibly be
   billed, never exceeded.

**The F&O entry formula.**

```
entry = work + (1 - e^-x) * (value - work)      x = turns/(10*work) + files/(8*work)
```

rounded to 0.25 h, with `work` as the floor and `value` as the ceiling. The constants 10 and 8 are
p90 turn- and file-densities per work hour. The reasoning: **density of work, not duration, is what
moves a line from measured time toward its value.** A short prompt written quickly should not count
for much; a long response over many files should. When turns and files per hour are ordinary, the
entry sits near work time; when they are dense, it approaches the value ceiling.

Why an intermediate figure exists at all — week 32 measured 32,75 h of work against 82,5 h of value.
Billing either end is wrong: work time throws away delivered value, value time bills a ceiling.
Niels: *"i want to bill the customer something in between."*

**Distribution.** The entry total is spread across the consolidated rows of a block so the block sums
to it exactly. Section 1 groups by `customer/<name>` then date, which is the order F&O is entered in.
The month filter (current / last, default current) clips the *whole page* before anything is derived,
splitting a straddling ISO week at the month boundary — an early version clipped only the entry
blocks and leaked July hours into August.

**Related:** `TURN_GAP = 15.0` in `value.py`, split from `IDLE_GAP`, caps the gap credited between
turns and splits stretches at 15 min to match `rollup.py`. Measured over the 25 days whose
transcripts survive: billable value time **155.25 → 167.50 h (+7.9%)**, stretches 421 → 243,
keyboard unchanged. Forward only.
