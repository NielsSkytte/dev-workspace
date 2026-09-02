---
title: Verify the August bonus payout against the predicted tiers — settles whether ferie is deducted
status: open
created: 2026-09-02
project:              # workspace-level (time / finance)
owner: self           # needs the payslip, which only Niels sees
priority: normal
blocked_by: August bonus not yet paid out
activity:
fno_task:
source: session
---

## What
When the August 2026 bonus is paid, compare the amount against the predictions below and record
which scenario it matches. That settles the open question — **does the bonus rule deduct vacation,
even though the F&O utilisation page does not?**

## Why the prediction is written down first
There is no HR department to ask (Niels, 2026-09-02), so the rule can only be recovered by
observation. A single observation is only informative if the prediction precedes it — otherwise
whatever number appears gets rationalised after the fact. These are locked as of 2026-09-02, before
any payout.

## The predictions

August 2026: **145,00 fakturerbare timer**, basis **155,50 h**, one week of vacation taken.

| Scenario | Basis | pct | Tier | Bonus | Payout |
|---|---|---|---|---|---|
| **A1** ferie not deducted, grundlag = actual hours | 155,50 | 93,25% | 90% | 20% | **34.800 kr** |
| **A2** ferie not deducted, grundlag = tier floor | 155,50 | 93,25% | 90% | 20% | 33.588 kr |
| **A3** the sheet's flat 160 basis | 160,00 | 90,63% | 90% | 20% | 34.560 kr |
| **B1** ferie **deducted** (basis − 37,00 h) | 118,50 | 122,4% | 100% | 24% | **41.760 kr** |

**The discriminator is A vs B, and the gap is 6.960 kr — not a rounding question.**
Roughly 33–35 t.kr means vacation is **not** deducted, confirming what the F&O page shows.
Roughly 41,8 t.kr means it **is**, and every month containing holiday is better than it looks.

A1 vs A2 vs A3 is the secondary question (does Grundlag use actual hours or step with the tier);
those three sit within 1.212 kr of each other and may not be separable from the payout alone.

## Caveat that matters
**1.200 kr is the *assumed* gennemsnitsats from Niels's sheet, not a verified rate.** If the real
average rate differs, every kroner figure above moves proportionally while the **tier** does not. So
capture from the payslip, in order of usefulness:

1. the **bonus percentage** applied (settles it outright, rate-independent),
2. the **grundlag** figure (gives the effective rate and the basis),
3. the payout amount alone (only conclusive if it lands near 41,8 t.kr with a plausible rate).

If only the amount is visible and it sits in the 33–35 t.kr band, that is scenario A at a 1.200 kr
rate — but the same amount could be scenario B at a lower rate. Say so rather than concluding.

## Context
- Model, tiers and the per-month rule: `ops/memory/store/bonus-model-faktureringsprocent`.
- Tool: `python ops/time/bonus.py 145 --basis 155.5`.
- The F&O page does **not** deduct vacation from `Timer per måned` — August shows the full 155,50 h
  against 21 arbejdsdage despite a week off. `Normtimer` (141,00) *is* absence-adjusted but feeds
  `Nytte til stede`, which the bonus does not use.

## Log
- 2026-09-02 — created. Niels: *"vi har ikke en hr afdeling, det nemmest er ok at se hvad der reelt
  kommer til udbetaling os så tage den der fra."* Predictions locked before payout.
