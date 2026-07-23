---
id: hooks-subdir-session-gap
ts: 2026-07-23T07:30:00Z
type: project
scope: workspace
source: session:14457941
tags: [infrastructure, hooks, time-tracking, memory-capture]
status: distilled
description: "Sessions rooted BELOW C:\\Dev (e.g. C:\\Dev\\customers) get NO capture/time hooks - Element Logic session 07-20..23 has zero heartbeats and zero daily records; hours need manual timesheet entry"
---

Sessions rooted below `C:\Dev` do not get the workspace hooks. The Element Logic
lineage session (07-20 → 07-23, session `14457941`, rooted at `C:\Dev\customers`)
produced **no time heartbeats and no memory daily records** — Claude treats
`C:\Dev\customers` as its own project (`projects\C--Dev-customers\`), and the
`Stop`/`UserPromptSubmit`/`SessionStart` hooks registered in `C:\Dev\.claude\settings.json`
do not cascade to sub-rooted projects (CLAUDE.md content cascades; hooks do not).

**Why:** hook registration is per project root; only sessions launched at `C:\Dev`
load `C:\Dev\.claude\settings.json` hooks.

**How to apply:**
- Element Logic hours 07-20..23 (fno 6001-01, task 45394) must be entered
  manually in `ops/time/timesheet/` — the substrate has nothing to roll up.
- Fix direction to evaluate: register the three hooks in user-level settings
  (`~/.claude/settings.json`) with cwd-guards, or per-project settings stubs.
  Until fixed, per-project VS Code task sessions are ALSO untracked — the
  "time is captured automatically once you open sessions rooted at its folder"
  claim in /new-project's confirmation is currently FALSE.
- Related: [[claude-auto-memory-disable]]
