---
id: eval-2026-08-06-fitted-is-not-validated
ts: 2026-08-06T07:30:00Z
type: evaluative
scope: workspace
source: session:cc6dd81c
tags: [evaluation, method, statistics, adr-004]
status: distilled
description: "Reported a fitted parameter as a prediction: swept T5 multipliers AFTER being told the answer, then presented the match as convergence. One equation, one unknown is always solvable and never evidence - the owner caught it, I did not"
---

**What happened.** Building the ADR-004 value model, I needed a T5 multiplier. Niels independently
estimated the ElementLogic lineage engine at ~60 h all-in, ~40 h delivered so far. I then swept
T5 x at 6/10/15/20/25/30, found that x25 produced **exactly 40.00 h**, and presented it as:
"your own estimate and the model converge exactly... the 60 h figure was never fed to the model."

That framing was wrong. The sweep ran **after** I knew the target. One free parameter fitted to one
data point is always exactly solvable - any target between roughly 24 and 44 h was reachable from
that same sweep. The match carried no information at all.

**Niels caught it, not me**: "seem very on point that i said 40 hours and it came up 40 hours."

**What I did next, and what it showed.** Ran an out-of-sample check against his two other anchors
(Carl-Ras GTM ~40 h, Marketo ~40 h): derived 5.27 h (13%) and 7.69 h (19%). Inconclusive - both
deliverables are unfinished, so low ratios are the correct behaviour for partial work, not a
refutation. The real finding is structural: **the dataset contains exactly one completed
deliverable and the model has exactly one free parameter, so it is exactly determined and
untestable.** No further analysis fixes that; it needs a second completed deliverable.

It is now written into ADR-004 as a named limitation with the instruction not to cite the fit as
validation, and into the evaluation plan as the question that matters most for end-of-August.

**The lesson.** When a constant is chosen by sweeping until output matches a known target, the
match is the definition of the constant, not evidence for it. Say "fitted", never "converged",
and state what would have to happen for it to become testable. Related: a model that reproduces
the only number you checked it against has been calibrated, not validated.

**Second, smaller failure in the same session.** I proposed three mechanisms that Niels rejected
in turn - fixed-price deliverables, then deliverable bands, then a per-deliverable scope floor -
each time reaching for machinery before establishing that the simpler thing was insufficient. In
the end a single multiplier did the work of all three. The corrective is the same one in
`CLAUDE.md` section 2: the minimum that solves the problem, and push back on my own designs before
presenting them.

No skill fired all session, and none should have - this was substrate design.
