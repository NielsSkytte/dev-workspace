---
id: eval-20261009-capture-stale-pairing
ts: 2026-10-09T12:30:00Z
type: evaluative
scope: workspace
source: /log
tags: [memory, capture-hook, sentinel, evaluative]
status: distilled
description: "Sentinel on daily/2026-10-09: 13 flags, 9 records pair a user line with a stale or earlier assistant body (repeat or previous turn's answer), recurring after 2026-10-05; inference: capture_turn.py takes the last assistant message when a turn ends on tool calls or a background notification"
---

- Same class as 2026-10-05 (3 pairing mismatches, session a78914e1). On 10-09 in session f17eef0c, one
  inverted the meaning ("push" paired with "not committed or pushed"). None of the flagged records were
  distilled.
- Also: harness `<task-notification>` XML and expanded /handoff help text landed as User lines
  (see `capture-turn-records-expanded-help`).
- Needs its own check in `.claude/hooks/capture_turn.py`; not changed this session.
