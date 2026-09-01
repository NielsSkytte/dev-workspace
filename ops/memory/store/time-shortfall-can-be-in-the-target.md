---
id: time-shortfall-can-be-in-the-target
ts: 2026-09-01T15:15:00Z
type: semantic
scope: workspace
source: session:e15b57a5
tags: [time, topup, absence, adr-005, value-model, decision]
status: distilled
description: "A period reading short against target is a question about the target as often as about the measurement - August's -9,50 h gap was a vacation week, and marking it dropped the target instead of inflating the hours"
---

August 2026 read **125,00 of 142,50 h (88%)** against a 155 h ambition. The instinct — and the
instruction, *"luk hullet"* — was to top up. The gap was in the **target**.

**The topup was refused on evidence.** `--topup` proposed **+17,50 h** across 24., 25. and 27.
August. The value model supported roughly 1,50 / 0,50 / 1,50 h on those days against 0,75 / 0,50 /
0,50 registered — nowhere near the proposal. Rather than apply it, the discrepancy was put back to
Niels, who answered: *"der var jeg på ferie men arbejde lidt"*.

**The correct move was `absence.md`, not `--topup`.** Marking 24, 25 and 27 August as `vacation`
(note: *"ferie; lidt arbejde registreret"*) removed three workdays from the denominator. August went
from **125,00 of 142,50 (88%)** to **125,00 of 120,00 (104%)** — over target, with not one hour
added. The small amounts actually worked on those days stay registered; a vacation day with some
work on it is normal and needs no reconciliation.

**The rule this confirms (ADR-005 v2, measured-not-floored).** When a period reads short, ask *why
the target is what it is* before asking how to reach it. The coverage check compares against
7.5 h × workdays, and it has no way to know a workday was not one. A topup whose per-day evidence
does not stand up is a signal that `absence.md` is incomplete — not a number to apply anyway.
**Never apply a topup whose weighted evidence does not support the proposed lift**, even under an
instruction to close the gap; surface the conflict instead.
