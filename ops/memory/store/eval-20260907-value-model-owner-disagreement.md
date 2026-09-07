---
id: eval-20260907-value-model-owner-disagreement
ts: 2026-09-07T13:00:00Z
type: evaluative
scope: workspace
source: /log
tags: [eval, time-tracking, value-model, adr-004, matas]
status: distilled
description: "ADR-004 evidence (2026-09-07): the owner puts the day that built the DataCompare prototype, Fabric backend and app at about 8 h against 3.00 h measured, and asks why the July/August backend days (match engine etc.) show so little; the weighted numbers for those days (0.44 h keyboard -> 7.50 h weighted on 08-03) already sit near his gut, the measured ones do not"
---

Asked at /log: "Did any weighted number disagree with your gut?" Owner: today's 3.00 h is too low
for what was done, should be more like 8 h; and what about all the time spent on the backend
(NB_Match_Engine and the rest)?

Facts. Today's heartbeats run 08:41 to 14:11 local, 26 turns, 3.00 h measured active time (the
session also lost a stretch to a disconnect). The backend days, keyboard vs weighted for Matas:
07-28 0.38 -> 2.50, 07-29 0.91 -> 7.75, 07-30 0.70 -> 4.00, 07-31 0.39 -> 3.00, 08-01 0.09 -> 0.75,
08-03 0.44 -> 7.50 (match engine built and verified). The measured timesheets carry the small
numbers; the weighted numbers are the derived evidence column.

Reading: on days where an agent builds a subsystem from a few owner turns, measured keyboard time
undercounts by 5-17x and the T5 weighting lands where the owner would land by judgement. The
owner's 8 h for today is above today's measured 3.00 h by 2.7x, in the same band. Action taken: a
TODO to set 2026-09-07 Matas to 8.00 h at finalization; the August lines were already sent to F&O
as entered, so the backend days stay as the ADR-004 comparison, not as corrections.
