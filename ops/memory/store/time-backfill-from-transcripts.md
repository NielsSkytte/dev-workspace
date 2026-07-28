---
id: time-backfill-from-transcripts
ts: 2026-07-28T12:52:00Z
type: semantic
scope: workspace
source: session:carlras-merge-task-first-attribution
tags: [project, reference]
status: distilled
description: "Recovering untracked hours from Claude Code transcripts: POINT-events not turns, and NEVER re-roll a timesheet (regeneration destroys hand-entered rows with no heartbeat backing)"
---

Method for reconstructing time that the hooks never captured, and the two ways it goes wrong. Both were
hit for real on 2026-07-28 while recovering the pre-hook-fix gap (`hooks-subdir-session-gap`).

**The source works.** `~\.claude\projects\<encoded-cwd>\<session-id>.jsonl` carries a `timestamp` and the
real `cwd` on most records — enough to rebuild heartbeats with the *same* attribution
(`track_time.project_from_cwd`) and the *same* 15+5 model (`rollup.stretch_hours`).

**TRAP 1 — reconstruct POINT events, never turns.** Building a turn as "user message -> last record before
the next user message" lets an idle-then-resumed session collapse into one multi-day interval: the first
attempt produced 42.50 h in a single day for one project, 19.00 h for another. Feed each record as a
zero-length point and let the 15-min merge rebuild the stretches — the idle gaps then discard themselves.
Sanity-gate the output: no reconstructed stretch should exceed ~12 h (the corrected run's longest was 1.52 h).

**TRAP 2 — NEVER regenerate a timesheet.** `rollup.py` finalize builds a day purely from heartbeats, but
finalized timesheets contain **hand-entered rows with no heartbeat backing at all**. Deleting the files and
re-rolling destroyed 8 dates and 28 reviewed rows (Melbye 2.00 h, Tystofte 3.50 h, `carl-ras/marketo`
3.00 h, `Carl-Ras/datahub` 2.00 h) before rollback. This is exactly what `ops/time/README.md` means by
"the timesheet is the reviewed truth" — corrections live there and only there. **Backfill must be
ADDITIVE**: append only rows whose key is absent; report (never overwrite) rows where the computed hours
exceed what is on the sheet.

**TRAP 3 — dedupe on work identity, not Proj ID.** Matching existing rows on `(project, proj_id, activity,
task)` double-counts whenever a project's `fno_code` was filled in since the row was written
(`UNSET` -> `230-02`) or the project key has a case variant (`own/CapacityManager` vs `own/capacitymanager`).
Match on `(project.lower(), activity, fno_task)`. This alone was 4.75 h of phantom hours.

**Coverage is a floor, not truth.** Six dates had heartbeats proving `Dev` work with zero surviving
transcript records, so transcripts are incomplete and any backfill from them UNDERSTATES the gap. Cause
not determined.

**Result of the corrected run:** +32.75 h billable, +1.50 h internal, 41 rows added across 24 dates
(5 new files), all 51 pre-existing rows byte-identical, no dates lost. Every backfilled heartbeat is
tagged `"source": "backfill"` so the whole operation is reversible by filtering on that key. Script kept
in the session scratchpad, not promoted — one-off.
