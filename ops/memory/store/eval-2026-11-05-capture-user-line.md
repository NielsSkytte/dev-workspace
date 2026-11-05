---
id: eval-2026-11-05-capture-user-line
ts: 2026-11-05T18:30:00Z
type: evaluative
scope: workspace
source: /log
tags: [memory, capture_turn, sentinel, skills]
status: distilled
description: "Sentinel 2026-11-05: daily stream has no local-model output; capture defects: double-encoded characters, skill bodies and harness text in the User line; nothing filters them while summarization is off"
---

- Sentinel on `daily/2026-11-04.md` and `2026-11-05.md`: no local-model output, shape clean. Fidelity flags came from contradictions inside verbatim turns, so those claims stayed out of `store/`.
- Capture defects: double-encoded characters (also 11-03, 10-20; the cause at `capture_turn.py:313` is Sentinel's inference, not proven); expanded skill bodies, harness text and "Tool loaded." in the User line. README rule 4 covers only command turns and rules 1-2 run only on summaries.
- Sentinel also caught "the database is up" for Tystofte as resting on the owner's "i believe"; the 11-04 line description was reworded.
- Skills this session: `switch-task` and `log` fired on request and did what they say. None missing.
