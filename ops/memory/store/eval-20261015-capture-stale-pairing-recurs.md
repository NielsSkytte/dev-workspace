---
id: eval-20261015-capture-stale-pairing-recurs
ts: 2026-10-15T13:00:00Z
type: evaluative
scope: workspace
source: /log
tags: [sentinel, capture_turn, memory, pairing]
status: distilled
description: "Sentinel on daily 2026-10-13/14: capture_turn.py stale pairing recurs (about 40 records); 4 records read as the opposite answer; distillation done from session context instead"
---

- Skill/agent: sentinel at /log, on `daily/2026-10-13.md` (63 records), `2026-10-14.md` (21),
  `2026-10-15.md` (2, clean).
- Same defect as [[eval-20261009-capture-stale-pairing]]: in session 06541b4e the assistant body
  often answers the previous User line. Four records invert the answer (e.g. 14th:195 "test CS
  data?" paired with "No."; the real answer was yes).
- Also: unneutralised `<task-notification>` / `<agent-message>` frames and expanded slash-command
  text in User lines; duplicate bodies.
- Action taken: a stored destructive git command (13th:876) and a mispaired bare directive
  (14th:129) were truncated. The day's store records were written from session context, not from
  the daily stream.
- Open: fix the pairing in `capture_turn.py`; until then, never distill a daily record without
  checking its pair.
