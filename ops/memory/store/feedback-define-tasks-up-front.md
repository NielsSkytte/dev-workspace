---
id: feedback-define-tasks-up-front
ts: 2026-08-20T00:00:00Z
type: semantic
scope: workspace
source: session:carlras-datahub-2026-08-17-to-19
tags: [feedback, time]
status: distilled
description: "Single out the task being worked on and define it up front where possible - a session's time tag must follow the work, and when the work changes shape, say so and re-tag before continuing"
---

**"In general we need to be better at singling out the tasks we work on and have them defined up
front if possible."** Niels, 2026-08-20, at the `/log` review gate.

The failure that prompted it: session `b436423e` ran 2026-08-17 to 08-19 tagged
`2026-08-17-carlras-curated-data-loss-windows`, the task it opened with. Within a few hours the work
had become a full Direct Lake conversion — a different deliverable, later its own task — and the tag
never moved. Two days of billable time landed under the wrong task and, because the timesheet
aggregates by activity, could not be split back out afterwards without guessing at a ratio.

**What follows:**

- **Name the task before the work, not after it.** If a request does not map to an existing task,
  create one first and tag the session, rather than working first and reconstructing it at wrap-up.
- **When the work changes shape mid-session, say so and re-tag.** The signal is a new deliverable or
  a new question, not a new file. Do not let a session tag drift because the conversation is
  continuous.
- **Time tags are not retro-fixable in aggregate.** `ops/time/timesheet/<month>/<date>.md` groups by
  project + activity; once a day is finalized the per-task detail is gone. The correction has to be
  made while the day is live, or not at all.
- **Corrections are made in the timesheet file, never the heartbeats** — the file says so in its own
  header, and heartbeats are the raw record. (Learned by doing it wrong in the same session: I
  retagged heartbeats for two already-finalized days, then restored them from backup.)

Related: `timesheet-period-not-day` (the billable unit is the week), ADR-003 (the active task decides
the project, cwd is the fallback).
