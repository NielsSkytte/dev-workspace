---
id: eval-20261019-lavish-and-capture
ts: 2026-10-19T12:00:00Z
type: evaluative
scope: workspace
source: /log
tags: [eval, lavish, capture-hook, sentinel]
status: distilled
description: "2026-10-19: lavish skill fired on 'show me the lavish' and the review loop worked (two notes applied via poll). Sentinel: capture mojibake persists (19 lines 10-18/19, first logged 10-16) and harness markup/compaction summaries land in User bodies."
---

- **lavish:** "show me the lavish" with no artifact named; the newest `.lavish/overview.html` was the right
  pick. Background poll returned feedback; reply + re-poll worked.
- **capture_turn.py (open defect):** cp1252 mojibake (`â†’`, `â–¶`) still in 10-18/10-19 daily files,
  same as eval-20261016-capture-assistant-mojibake. Also captured verbatim: `<bash-input>` /
  `<local-command-caveat>` markup and a compaction summary as a User body (10-18.md:745). Filter both.
- 10-19.md:28 claims `/log` was not run for 10-18; 10-18.md:629 shows it was. Not distilled.
