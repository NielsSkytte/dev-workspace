---
id: eval-2026-08-07-convenient-sample
ts: 2026-08-07T08:10:00Z
type: evaluative
scope: workspace
source: session:a77891ac
tags: [evaluation, method, sampling, memory-fidelity]
status: distilled
description: "Scoped a query to one month, then generalised from it - 'these modes have never been used' was false, Fable ran 3,263 turns the month before. Second day running of concluding from a conveniently-bounded sample"
---

**The miss.** Asked to think about pricing Fable and ultracode sessions, I measured
usage with a script scoped to `MONTH = "2026-08"`, found `{'claude-opus-5': 2962}`
and two Agent calls, and wrote: *"the modes you want to price have never been used"*.
The owner replied *"look at last month"*. July had **3,263 Fable turns — more than
any other model that month — and four Workflow runs.** The claim was flatly wrong,
and it was wrong because I chose the window and then forgot I had chosen it.

Worse, I had built an argument on top of it: that the 5-minute gap cap was not
discarding meaningful processing time (12% in August). July's figure is **34%**, and
the single 89.6-minute gap ADR-004 already flagged sits inside it. The conclusion
survived — the tier model does already price ultracode via T5 — but it survived by
luck, having been reached from the one month where the phenomenon was absent.

**This is the second consecutive day of the same failure shape.** Yesterday:
a causal claim from four observations with two variables moving
(`eval-2026-08-06-sample-of-four`). Today: a factual claim from one month of three
available. Both were cheap to avoid and both were caught by someone other than the
check I should have run.

**Rule earned:** when a script bounds its own input — a month constant, a `--limit`,
a directory glob — the bound is an assumption, and it must be stated in the finding
or removed before generalising. "In August" is a different sentence from "ever", and
only one of them was true.

**Also this session, from the summarizer rather than me:** a daily record reported
three items I had explicitly listed as *deliberately not done* — "Fixed mismatch
between focus and spill population, resolved timesheet/value disagreement, and
addressed task `requested_by:`" — as completed, and reported a timesheet change of
"9.00 to 0.75" when the change was 1.75 to 0.75 (9.00 is the weighted figure in a
different artifact, unchanged). Deferred work recorded as done is the most damaging
possible error for a continuity substrate: the next session reads it and skips the
work. Seventh consecutive `/log` carrying a fabricated completed action.
