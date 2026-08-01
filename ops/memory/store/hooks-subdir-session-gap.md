---
id: hooks-subdir-session-gap
ts: 2026-07-23T07:30:00Z
type: project
scope: workspace
source: session:14457941
tags: [infrastructure, hooks, time-tracking, memory-capture]
status: distilled
description: "FIXED 2026-07-28 for time/capture (user-level registration + in-script guard) and FIXED 2026-08-01 for the agent roster (+ skills/commands, which were missing from most project roots entirely - heal-repos.ps1 keyed on git repos, not projects). Sessions below C:\\Dev previously got NO hooks (Element Logic 07-20..23, DataCompare 07-16..28 untracked). Only the SessionStart snapshot stays root-only, by design"
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
- **FIXED 2026-08-01** (session 972e353e) — and the roster was only the visible half. The real
  finding: `ops/bin/heal-repos.ps1` > `Link-Harness` junctioned **`commands` and `skills` but never
  `agents`**, and it was applied only to *unit roots and nested git repos*. A project that is a
  plain folder (`Matas/DataCompare`, `own/EnvDiscovery`) matched neither and had **no `.claude/`
  at all** — no slash commands, no domain skills, no roster, no settings. Only 10 of 26 project
  roots were provisioned, none with `agents`. The provisioner keyed on **repos**; the sessions key
  on **projects** (`CLAUDE.md` > Reminders says to root sessions at the project folder), and the
  two never lined up. Fix: `agents` added to `Link-Harness`, plus `Get-ProjectRoots` (any dir with
  a `CLAUDE.md`, both storage-standard depths) linked in a link-only pass. All 26 roots now carry
  `agents`/`skills`/`commands` junctions + a hard-linked `settings.json`; verified end-to-end on a
  throwaway project. Held by two guarantees: `/new-project` links on creation (new step 6) and
  `/log` re-runs the healer every wrap-up, so a hand-made project self-heals.
- **This resolves the open question in [[eval-2026-07-30-env-discovery]]**: cause (1) holds.
  `own/EnvDiscovery` had no `.claude/` whatsoever, so no skill *could* have fired there — the
  ~70-turn session that prompted the trigger-tuning theory was never a trigger problem at all.
  The workspace-level leg is separate and still a genuine trigger miss (see
  [[eval-2026-07-31-skills-available-not-firing]]).
- **Trap when unpicking this:** never `Remove-Item -Recurse` a `.claude/` subfolder — PowerShell
  5.1 can follow the junction and empty the workspace original. Use `cmd /c rmdir <link>`.
- **STILL OPEN (by design):** only the `SessionStart` *snapshot* hook stays root-only.
- Related: [[claude-auto-memory-disable]]
