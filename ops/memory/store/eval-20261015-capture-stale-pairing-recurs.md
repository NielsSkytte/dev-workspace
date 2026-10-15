---
id: eval-20261015-capture-stale-pairing-recurs
ts: 2026-10-15T13:00:00Z
type: evaluative
scope: workspace
source: /log
tags: [sentinel, capture_turn, memory, pairing]
status: distilled
description: "Sentinel on daily 2026-10-13/14: capture_turn.py stale pairing recurred (about 40 records, 4 inverted); hook fixed 2026-10-15 (turn-anchored reader, per-session state)"
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
- Fixed 2026-10-15 in `.claude/hooks/capture_turn.py`: the reader takes the last real user prompt
  (skips isMeta, compact summary, tool results, non-human origin, harness prefixes) and only the
  assistant text after it; re-reads up to 2 s for `end_turn`; uses `last_assistant_message` from the
  hook input if present; writes "(answer not yet in transcript)" instead of an older answer.
  State is per session, and an in-place replace happens only while the record is still last
  (parallel sessions caused the duplicates). Replay of this session's transcript: 14th:195 now
  pairs with "Yes. Microsoft provides two ways ...".
- Records before 2026-10-15 keep the defect; 10-13/14 carry a warning header.
