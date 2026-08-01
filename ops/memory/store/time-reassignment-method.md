---
id: time-reassignment-method
ts: 2026-08-01T12:30:00Z
type: semantic
scope: workspace
source: session:972e353e
tags: [project, reference, time-tracking]
status: distilled
description: "Moving tracked time between projects: relabel heartbeats and re-run the 15+5 model for the hours, apply the DELTA to existing timesheet rows (never regenerate), cap at zero rather than negative"
---

How to reassign already-tracked time (`Dev` -> a project, or the deviation case project -> project)
without corrupting the reviewed timesheet. Applied for real 2026-08-01: 22 moves across 15 July
days, 18.50 h internal -> billable.

**The per-session figure is NOT the hours to write.** Any UI that splits a day per session (the
dashboard's internal-hours triage) fragments the stretches, and each fragment then earns its own
5 min tail buffer and 0.5 h floor. July showed 38.25 h that way against 31.50 h on the tile. Writing
those figures into a timesheet inflates it.

**The correct computation — relabel, then re-run the model:**

1. Relabel the matching heartbeats in memory: `project` -> target, `task` -> target task slug (the
   slug is what makes `task_dims` resolve `activity` + `fno_task`).
2. Run `rollup.rows_for()` over the day **with** and **without** the relabelling.
3. The **difference** is what to apply. Both sides then come from the same 15+5 model that built
   the sheet, so nothing is invented.

Integrity check that catches most mistakes: the period total must be **unchanged**. July went
81.50 h -> 81.50 h with 18.50 h crossing sides. A first run showed billable +18.50 / internal
-15.00 -- a 3.50 h phantom -- caused by `{key(r): r for r in rows}` collapsing two casing variants
(`own/CapacityManager` / `own/capacitymanager`) onto one key so one silently overwrote the other.
**Aggregate by key, never build a dict that overwrites** (this is [[time-backfill-from-transcripts]]
TRAP 3 wearing a different hat).

**Apply the delta to the EXISTING rows; never regenerate the file** (TRAP 2 -- finalized days hold
hand-entered rows with no heartbeat backing). Splice: keep everything before the table header and
after the totals, rewrite only the rows + the two total lines, append an audit block. Match rows on
`(project.lower(), activity, fno_task)`.

**Cap at zero, never write a negative.** Three of 15 days held *less* than the model computed
(hand-adjusted earlier), so the removal overshot: 07-07 `own/CapacityManager` 4.00 vs 4.75 wanted.
Cap and record the shortfall in the audit block with a `!` marker -- do not silently absorb it.

**Expect some moves to vanish, correctly.** 07-21's 0.50 h `Dev` had nowhere to land: relabelled to
`ElementLogic/LineageDocumentation`, the heartbeats merged into that day's existing stretch and
changed no rounded total. Those 0.50 h were a floor artifact (one stray turn given the minimum), not
real time. Say so rather than forcing a row.

**Prerequisites:** a day with no timesheet cannot be edited -- run `rollup.py` first (finalize skips
existing files, so it is additive-only). Back up before writing: `ops/time/` is gitignored and the
OneDrive mirror is the only rollback point.

**Rule boundary:** `ops/time/README.md` sec.2 sanctions `Dev` -> project only; `own/` -> customer is
project-to-project and excluded. The owner overrode this deliberately (own/CapacityManager work
billed to Carl-Ras, own/EnvDiscovery to Matas). Surface such moves as deviations, flag them in the
export, and let the owner decide -- do not block, and do not apply silently.
