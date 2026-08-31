---
id: time-capture-defects
ts: 2026-08-06T07:30:00Z
type: semantic
scope: workspace
source: session:cc6dd81c
tags: [workspace, time, hooks, defect, heartbeats]
status: distilled
description: "Two heartbeat capture defects that inflate the CURRENT timesheet independently of any value model: a Stop hook that does not always fire (340-min heartbeat for a 1-min turn) and intra-turn dead time (131-min turn containing 8.8 min of activity); plus the unbounded fallback attribution"
---

Found 2026-08-06 while measuring the substrate for ADR-004. **These inflate today's timesheet, not
just the value model** - they are defects in `ops/time/` capture as it stands.

**1. The `Stop` hook does not always fire at the end of a turn.** On 2026-08-03, session
`5bbffdc6`, `customers/Carl-Ras/datahub`: `UserPromptSubmit` stamped 10:23:46, the last assistant
reply landed 10:24:39, the last system event 10:27:57 - and then **nothing until the next user
prompt at 16:03:22**, when `Stop` finally fired and wrote `ts_end` 16:03:33. A ~1-minute turn
recorded a **340-minute heartbeat**. `ops/time/README.md:49` documents the *many heartbeats per
turn* case ("harmless: they collapse into one stretch") but not this one, which is the reverse and
is not harmless. Under the live 15-minute model this single artifact is most of 2026-08-03's
13.25 billable hours.

The mirror case also occurs: **one heartbeat spanning several turns**. On 2026-07-16,
`customers/Vestforbraending`, a single 40-minute heartbeat covered three separate user prompts
(11:05, 11:12, 11:20) with idle between them. So heartbeat intervals are unreliable as turn
boundaries in *both* directions.

**Fix used in `value.py`:** take turn boundaries from the transcript, **intersected with** the
heartbeat. The transcript ends a turn whose `Stop` never fired; the heartbeat bounds a turn whose
segmentation broke on a resumed session (an unbounded transcript walk produced a 3,137-minute
"turn"). Neither source alone is sufficient.

> **Superseded 2026-08-31 for `rollup.py`.** This record said "`rollup.py` still uses raw heartbeats
> - the live timesheet still carries this defect." It no longer does: `rollup.py` bounds a heartbeat
> at 60 min and splits it at local midnight, and two further capture defects were found and fixed
> (a `!`-bash-input `Stop` inheriting a stale turn start, and an unanswered `AskUserQuestion`).
> See `time-bounded-turns-and-stall-evidence`.

**2. Intra-turn dead time is invisible to the between-turn idle rule.** On 2026-07-23, session
`36359848`, `customers/Carl-Ras/fabric`: a **131.3-minute** turn containing **8.8 minutes** of
activity across 130 events - an **89.6-minute gap before a tool result** (a pending permission
prompt or a long-running call) and a **33.0-minute gap** before the next assistant message. The
section 3 idle rule only measures gaps *between* turns, so it cannot see either.

**Fix:** sum inter-event intervals inside a turn, each capped at the same 5 minutes used between
turns. Across 2026-05 to 2026-08 this removed **16%** of measured production time (1,485 -> 1,245
minutes) and dropped the longest turn from 132 to 23.8 minutes. Distribution afterwards: p50 1.1,
p90 5.6, p95 7.6, p99 16.9 min.

**3. Fallback attribution was unbounded.** 37 turns (5.5%) had no covering heartbeat at all - the
`Stop` hook is fail-silent, so its heartbeat can simply be missing. `value.py` originally borrowed
the project from the nearest heartbeat in the same session **at any distance**. Now capped at 30
minutes (beyond that the turn is dropped rather than guessed at) and the count is printed per row
in the audit record. Effect: Matas fell **32.75 -> 28.00 weighted hours**, the difference being
`.claude/hooks/track_time.py` and `AGENTS.md` edits sitting on a customer line.

**Incidental correction:** transcript *content* reaches back to 2026-05-26, not 2026-07-07 - the
earlier date was file mtime, not content. Relevant whenever scoping a backtest window.
