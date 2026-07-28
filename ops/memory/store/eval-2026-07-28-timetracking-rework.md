---
id: eval-2026-07-28-timetracking-rework
ts: 2026-07-28T12:54:00Z
type: evaluative
scope: workspace
source: session:carlras-merge-task-first-attribution
tags: [evaluative, skills]
status: distilled
description: "Time-tracking rework session: no skill fired (correctly — workspace-internal work has no skill); the misses were mine, and two were caught only by verifying my own output"
---

**Did a skill fire?** No — and correctly so. The session was workspace-internal (time substrate, hooks,
ADR, project merge); no skill covers it and none should. `update-config` arguably borders on the settings
edit but the change was hook registration inside an established dual-registration pattern already
documented in `CLAUDE.md`, which the guidance covers better than a skill would.

**Should one have fired and didn't?** No gap identified.

**Corrections a skill should have prevented:** none — but three self-inflicted errors are worth recording,
because the pattern is the lesson.

1. **Destroyed reviewed data by re-rolling timesheets** (rolled back from backup within the same turn).
   Cause: treating heartbeats as the superset of the timesheet. `ops/time/README.md` states the opposite in
   plain language — the timesheet is the reviewed truth — and I had read that file earlier in the session.
   Reading a rule is not the same as applying it to the operation in front of me.
2. **Turn-based reconstruction produced 42.50 h in a day.** Caught only because I printed the diff before
   writing. The number was absurd on sight; had I written first and checked after, it would have entered
   billing records.
3. **Dedupe key included Proj ID**, which would have double-counted 4.75 h. Caught in the dry-run diff, in
   the *same* dry run I had promised the user I would show. The promise to show a diff is what caught it.

**The transferable lesson:** on operations that touch billing records, the dry-run-then-diff step is not
ceremony — it caught two of three errors here. The one it did not catch (1) was the one where I skipped it
and wrote directly. Worth making a habit for any script that mutates `ops/time/` or customer-facing data.

**Process note:** the `sentinel` agent was not dispatched (standing instruction: no subagents unless the
user asks). Daily records hand-vetted per the README recipe instead — 3 fidelity flags found in the local
summarizer's output (a fix attributed to this session that predated it, a figure relabelled as a different
quantity, one garbled finding), so hand-vetting is holding up as the fallback. Third consecutive /log
where the local summarizer overstated. Pattern worth watching.
