---
id: eval-20261025-review-and-capture
ts: 2026-10-25T12:00:00Z
type: evaluative
scope: workspace
source: /log session eae86d9b (sentinel review)
tags: [evaluation, skills, memory-capture, heredoc]
status: distilled
description: "2026-10-25: no skill fired or was missed in the review-step work; Python patches through Bash heredocs lose backslash escapes (use Edit); capture mojibake and harness boilerplate in User lines persist"
---

- No skill fired during the review-step and synthetic-check work; none was missed (the work was
  own/Ontology product code, which no skill covers).
- Repeat defect: Python string patches sent through a Bash heredoc lost `\n`/`\t` escapes three
  times (literal newlines in the file). Edit tool for any replacement holding a backslash.
- Sentinel 2026-10-25: daily capture still writes mojibake (`â†’` etc.), stores harness boilerplate
  and skill bodies as User lines, and scoped a process-insight turn as datahub. capture_turn.py needs a fix.
