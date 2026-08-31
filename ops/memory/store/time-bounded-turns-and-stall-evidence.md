---
id: time-bounded-turns-and-stall-evidence
ts: 2026-08-31T10:15:00Z
type: semantic
scope: workspace
source: session:7ee7dd73
tags: [workspace, time, rollup, hooks, defect, heartbeats, transcripts]
status: distilled
description: "Four separate ways a heartbeat records waiting as work - an unbounded span, midnight bucketing, a Stop with no UserPromptSubmit, and an unanswered AskUserQuestion - plus why the bound must never truncate silently and why stall evidence expires in ~30 days"
---

Found 2026-08-31 auditing the rollup after 2026-08-27 finalized at 22.75 h. **Four defects, four
different mechanisms.** They are listed together because the shared symptom - one huge heartbeat -
hides the fact that no single fix covers them.

| # | Mechanism | Fixed in | Evidence |
|---|---|---|---|
| 1 | Unbounded span: one heartbeat is one turn, and `Stop` does not always fire at its end | `rollup.py` `MAX_SPAN = 60 min` | all 8 spans >60 min of 1,422 held <=20 min of transcript activity around a 5-13 h hole |
| 2 | Bucketed by `ts_start` only, so a midnight-crossing span landed wholly on its start date | `rollup.py` `split_local_days()` | 08-27 read 22.75 h, 08-28 read empty |
| 3 | A `Stop` with no `UserPromptSubmit` reused the stale `start` of an earlier turn | `track_time.py` per-session `last_stop` | 08-03 session `5bbffdc6`: two heartbeats, identical `ts_start`, the real turn 0.9 min and a duplicate ending 5.5 h later |
| 4 | An `AskUserQuestion` keeps the turn open until answered | `track_time.py` on `PreToolUse`/`PostToolUse`, matcher `AskUserQuestion` | 08-20 session `45041831`: question 09:15:55, answered 14:25:44 - 310 of a 325 min heartbeat |

**A `!`-prefixed bash-input fires `Stop` without a `UserPromptSubmit`** (defect 3). The guard is not
"is the start old" - it is whether a *previous* `Stop` for this session landed within the 15 min idle
timeout. Inside it, the later `Stop` legitimately extends the turn (a turn that yields on background
work); beyond it the heartbeat becomes a point at `ts_end`.

**The bound cannot tell a stalled turn from a long one.** It sees only the span, and a genuinely
long turn normally writes a single heartbeat - **only 30 of 1,391 turns ever emitted a second
`Stop`, and those share the same `ts_start`**, so they extend the same interval rather than adding
another. A first attempt at this claimed further heartbeats would cover the overflow; that was
wrong. So the bound names every turn it touches, in that day's timesheet file and on stdout, and the
decision belongs to the review gate.

**Rollup corrections are derive-side; capture is only fixed where it writes something false.**
Defects 1 and 2 are computed in `rollup.py`, so the JSONL stays the immutable record and past days
heal on any re-read. Defects 3 and 4 are hook fixes because the hook was writing a *wrong*
`ts_start` / covering a wait - not to make raw data smaller.

**Stall evidence expires.** `value.py --stalls` reads transcripts, and Claude Code keeps roughly
**30 days** of them (35 files on disk, oldest 2026-07-31). Five of the eight bounded turns on record
already have no transcript and read `no transcript` in `ops/time/stalls.md`. Hence: run it at every
`/log`, unconditionally, and `stalls.md` is tracked in git so the finding outlives its source.
A month-end-only pass loses the early weeks.

**The error alone is not a trigger.** 32 error events are on record since 2026-07-31 (classifier
timeouts, API errors, connection drops, overloads) and most sit inside perfectly normal turns. The
span triggers the check; the error at the gap explains it.

**Also fixed:** `DAY_CAP = 12.0` only ever bound the `--merge` path, so a 22.75 h day finalized
silently. A day over the cap is now flagged in its own timesheet file.

Net effect of the rules across all history: **-34.00 h on six dates**. Corrected by hand and
recorded in `stalls.md`: 2026-08-03 14.25 -> 8.75 h, 2026-08-20 12.25 -> 7.25 h.

Not covered by any capture fix: a permission prompt and the auto-mode classifier are not tools, so
the hook cannot see those waits. The 60 min bound plus the `stalls.md` review is the only guard
there - that is the 2026-08-27 case.
