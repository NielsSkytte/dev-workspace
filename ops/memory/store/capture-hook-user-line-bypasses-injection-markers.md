---
id: capture-hook-user-line-bypasses-injection-markers
ts: 2026-09-10T00:00:00Z
type: evaluative
scope: workspace
source: /log
tags: [memory, hooks, capture_turn, sentinel, injection-markers, snapshot]
description: With summarization off, capture_turn.py writes the User line verbatim, so the injection-marker filter never sees it and harness markup lands in daily/ again.
status: distilled
---

Sentinel pass on `daily/2026-09-10.md` (5 records) returned 2 flags and one mechanism finding that
matters more than either flag.

`.claude/hooks/capture_turn.py` applies `_INJECTION_MARKERS` only inside `sanitize_summary`, which
runs on model summary text. `MEMORY_SUMMARIZE` is off, so the User line is written verbatim and
passes no marker check at all. Result: raw `<task-notification>` / `<task-id>` / `<status>` markup
is back in the daily file, unbalanced (opened, truncated before its close) - the same class of
record a previous sentinel pass added to that marker list after 8 occurrences in
`daily/2026-08-31.md`. Unbalanced harness markup must not reach snapshot injection.

Second gap in the same file: `command_invocation()` collapses a `<command-name>` turn to
`/name args`, but there is no equivalent for a **skill-preamble** turn. So the turn that carried
today's actual request stored two screens of `writing-voice` skill text as the User line, and the
request itself ("build the overview deck") is nowhere in the record - that turn cannot be
fidelity-checked from its own text.

Both are hook gaps, not model behaviour. The fix is two edits in `capture_turn.py`: run the marker
filter over the verbatim User line as well as over summary text, and collapse a skill-preamble turn
the way a command turn is collapsed. Not applied - raised at the 2026-09-10 wrap-up.
