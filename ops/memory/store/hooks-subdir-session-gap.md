---
id: hooks-subdir-session-gap
ts: 2026-07-23T07:30:00Z
type: project
scope: workspace
source: session:14457941
tags: [infrastructure, hooks, time-tracking, memory-capture]
status: distilled
description: "FIXED 2026-07-28 for time/capture (user-level registration + in-script guard); sessions below C:\\Dev previously got NO hooks (Element Logic 07-20..23, DataCompare 07-16..28 untracked - manual timesheet entry). STILL OPEN: agent roster + SessionStart snapshot don't cascade"
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
- **Second confirmed instance (2026-07-28):** DataCompare session `1f323a74` (rooted at
  `C:\Dev\customers\Matas\DataCompare\src\config-store`, ran 07-16 → 07-28) — zero
  heartbeats, zero daily records; DataCompare hours 07-16..28 (fno 212-01) need manual
  timesheet entry. **Extension:** the workspace *agent roster* doesn't cascade either —
  the `sentinel` agent was not an available agent type at /log; its review must be done
  by hand (README recipe) in sub-rooted sessions.
- **FIXED 2026-07-28** (session 1f323a74): `track_time.py` + `capture_turn.py` are now
  registered in the user-level `~/.claude/settings.json` (identical command strings to the
  workspace registration) with an **in-script guard** — any cwd outside `C:\Dev` is ignored,
  any depth inside rolls up (project / customer-node `customers/<client>` / `Dev`; depth-3
  folders without a `CLAUDE.md` fall to the customer, `realpath` canonicalizes casing).
  Claude Code dedupes the identical command strings (docs-verified) — keep them
  byte-identical, that identity is load-bearing. Verified by execute-and-assert tests +
  a 3-lens adversarial workflow (which killed an initial Stop-dedup guard as a regression:
  a turn legitimately Stops several times; every Stop must write). The /new-project
  "time is captured automatically" claim is TRUE again.
- **STILL OPEN:** the workspace *agent roster* (e.g. `sentinel`) and the `SessionStart`
  snapshot hook do not reach sub-rooted sessions (snapshot deliberately root-only; the
  roster gap is real — /log sentinel review must be done by hand in project sessions).
- Related: [[claude-auto-memory-disable]]
