---
id: eval-2026-08-01-harness-cascade
ts: 2026-08-01T12:40:00Z
type: evaluative
scope: workspace
source: session:972e353e
tags: [evaluative, skills, hooks-subdir-session-gap, dashboard, time-tracking, fact-only-language]
status: distilled
description: "evaluative: the 07-30 'skills never fired' mystery was never a trigger problem in project sessions - those roots had no .claude at all; plus two self-inflicted errors caught by dry-run and by the period-total invariant"
---

Session 972e353e, 2026-07-31 -> 08-01. Dashboard layout, the harness cascade fix, the internal-hours
triage panel, and applying a 22-move time reassignment.

## Skills

**No workspace skill fired, and none should have.** The subject matter was the harness itself
(dashboard, `heal-repos.ps1`, `rollup.py`, timesheets) -- outside every domain skill's scope. Slash
commands `/dashboard` and `/log` fired on invocation. Recording it because a day of real work with
zero evaluative content is itself worth noting (per [[skill-usage-evaluation]]).

**The standing "no subagents unless requested" instruction now binds where it did not before.**
`sentinel` was again not dispatched (6th consecutive `/log`, hand-vetted instead). Note the change
in *why*: it used to be unspawnable from project-rooted sessions -- that is now fixed -- so from
here the only obstacle is the instruction, not the harness.

**The 07-30 open question is answered, and the answer was not "trigger tuning".**
[[eval-2026-07-30-env-discovery]] left two undistinguished causes for `pingala-fabric-platform`
never firing across ~70 turns. Cause (1) is confirmed: `own/EnvDiscovery` had **no `.claude/`
directory at all**, so no skill could load there. 16 of 26 project roots were in that state, and
`agents/` was absent from all 26. Every hour spent theorising about trigger phrasing for
project-rooted sessions was spent on the wrong layer. The workspace-level leg
([[eval-2026-07-31-skills-available-not-firing]]) remains a genuine trigger miss -- two different
faults that looked like one.

**Lesson worth keeping:** when a capability "doesn't fire", check it is *present* before tuning how
it is *described*. The cheap test proposed on 07-30 (ask at a project root and see what loads) would
have found this in one turn.

## Own-output failures

1. **Shipped the panel behind an invisible control.** The entry point was a text link in a tile
   footer whose hover state painted light-on-light; the owner reported not being able to find the
   panel at all, and read the alert rows as the panel. Caught only because they said so. A review
   surface has to be a named section, not a hover target.

2. **A dict that overwrote instead of aggregating.** The reassignment analysis keyed rows by
   `(project.lower(), activity, fno_task)` but built it with `{key(r): r for r in rows}`, so the two
   casing variants of `own/CapacityManager` collapsed and one was lost. It produced billable +18.50
   / internal -15.00 -- a 3.50 h phantom. **Caught by the invariant, not by reading the code**: the
   period total must not change when time only moves sides. This is the same hazard already written
   down as TRAP 3 in [[time-backfill-from-transcripts]], hit again in new code.

**What worked:** dry-run-then-diff before writing to billing data, for the second time
([[eval-2026-07-28-timetracking-rework]] records the first). It surfaced three rows that would have
gone negative and one move with no destination, all before anything was written. Combined with the
period-total invariant, it is the pattern that keeps timesheet edits safe -- verify against a
conserved quantity, not against expectations.

## Local summarizer

Two fidelity flags in `daily/2026-08-01.md`, both the same class flagged on 07-30 and 07-31:
`20260801T121330Z` says "adjusted the hours for specific rows" for a turn that was a **dry run**
(nothing written but one finalized day), and `20260801T120445Z` conflates cause, reporting that
copying the plan is what makes allocations survive a reload. Three consecutive `/log`s with the
summarizer asserting completed actions that had not happened -- the model or prompt needs revision,
not just per-day vetting.
