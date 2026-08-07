---
id: value-model-mode-pricing
ts: 2026-08-07T08:00:00Z
type: semantic
scope: workspace
source: session:a77891ac
tags: [value-model, adr-004, billing, ultracode, fable, workflow, time-tracking]
status: distilled
description: "Ultracode is already priced by the value model through T5, so a mode multiplier would double-count; Fable is a model default not a value signal. The real unpriced case is orchestration used for research rather than construction"
---

Settled 2026-08-07 against real July usage, after the idea of factoring value up
~6x when Fable or ultracode is enabled.

**Usage, measured:** Fable ran on **16 of ~18 July working days** (3,263 turns, more
than opus-5's 2,470); ultracode ran on **four** — 07-21 (x2), 07-27, 07-28. August
had neither (opus-5 only, two Agent calls).

**A mode multiplier would double-count.** On 07-21, the heaviest ultracode day, the
value record reads `T5 Principal Consultant | 1 turn | 21 keyboard min | 25.0x |
8.90 h` — **one T5 turn produced 8.90 of that day's 9.00 weighted hours**, and the
day was already capped, so the raw figure was higher. 07-28's workflow fired T5 too
(7.54 of 15.50 h). The tier model already prices orchestration, just indirectly: a
workflow builds a subsystem, files land, T5 fires at 25x. Multiplying by 6 on top
takes 40 minutes of typing past 50 raw hours for a signal counted once already.

**Fable is a poor trigger.** It ran on nearly every July day *including* 07-24, which
produced 0.50 weighted hours from 26 Fable turns. It was the month's default model,
not a value signal, so a Fable multiplier inflates indiscriminately.

**The genuinely unpriced case is narrower.** Compare 07-21 with 07-23: both used
orchestration, only one fired T5. 07-23 discarded 84.6 minutes of processing time,
fired no T5 anywhere, and gave the Element Logic line 0.75 h from a single 7-minute
turn — those agents were *reading*, not writing, and the model scores file output.
So the gap is **orchestration used for research rather than construction**, which is
the same gap ADR-004 already names ("14% of billable weighted hours sit in stretches
that wrote no file", "high-value/low-line work reads too cheap"). The targeted fix is
to count processing time, a measured quantity that can be checked rather than fitted
— unlike a mode flag, which would repeat the T5 mistake at zero observations.

**The floor rule** (billable never below keyboard + processing, stated 2026-08-06)
**holds on every measured day.** Worst case is 07-23 at **2.4x** once discarded
processing is added back to actual (0.82 h keyboard + 1.41 h lost = 2.23 h actual vs
5.25 h weighted). It holds structurally because every multiplier is >= 2.0x, and
capped hours that cannot spill stay on the record as `UNPLACED` rather than being
dropped.

**Caveat on the processing figure:** "processing" was inferred from any gap ending in
a `tool_result`, which also captures a tool sitting unanswered awaiting permission.
An 89-minute tool is more plausibly an unapproved prompt than 89 minutes of compute,
so 116 min/July is an **upper bound** until that is separated.
