---
id: day-brief-derived-view-and-day-start-hook
ts: 2026-09-16T14:45:00Z
type: decision
scope: workspace
source: /log
tags: [continuity, daybrief, hooks, dashboard, today]
description: One derive script (ops/bin/daybrief.py) renders the day brief, the dashboard's Today page and every card's task section from the task files; a hook prints the brief on the first turn of a working day (05:00 boundary) and opens the dashboard once a day.
status: distilled
---

`daybrief.build()` reads CLAUDE.md identity, the card, the task files, the 90 newest heartbeat files
and the memory store, in about 130 ms; `render_text(scope)` gives the project brief or the workspace
table (ASCII), `render_section` + `write_cards` regenerate the `## Active tasks - progress` section,
`--json` feeds `/api/today`. Flags: `--text --json --write-cards --check --scope --project`.

Day start: day key = (local now - 5 h).date(); `daybrief_hook.maybe_brief(session_id, project)` prints
once per session per day key (state in `.claude/hooks/.daybrief_state.json`, gitignored) and, the first
time a day key is seen at all, starts `ops/dashboard.py --no-open` detached if port 8787 is silent and
opens the browser. Called from `session_task.py` (SessionStart startup|resume|compact - compact takes the
progress-nudge path instead) and from `track_time.py` on UserPromptSubmit, so an open idle session gets
the brief on its first prompt after 05:00. The session-start.ps1 workspace walk was removed; the brief
replaced the file-by-file walk, so a session starts with no reads.

Today (served at `/`; since 2026-09-21 `ops/web/today.js`, with Projects and Time beside it) writes nothing: every button
POSTs `/api/launch` with a command (`/switch-task`, `/task postpone|wait|resume`, `/handoff`,
`/checkin`, `/checkin convert`) so the write happens in a session with the owner in it. Colours: the
warm-neutral ladder for progress age, terracotta only for attention (stalled, ask unsent, DevOps none).
A CLAUDE.md without an Identity block (the wiki mirror) is not a project for the brief.
