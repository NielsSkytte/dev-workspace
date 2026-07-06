---
id: time-tracking-system
ts: 2026-06-22T14:00:00Z
type: semantic
scope: workspace
source: session:per-project-time-tracking
tags: [project]
status: distilled
description: "Per-project time tracking at ops/time/ — heartbeat+idle-timeout (15+5) model, deterministic rollup, F&O codes, data not in git (ADR-002)"
---

The workspace tracks **active working time per project** (the level that has its own `CLAUDE.md`):
`Dev` (the setup itself; absorbs `ops/` work), each `customers/<client>/<project>`, each `own/<project>`.
Substrate at `ops/time/`, a peer to `ops/memory/` with the same raw->reviewed split: **heartbeats**
(raw, append-only) distil into **timesheets** (reviewed, F&O-ready). Decision record: **ADR-002**.

**Model (the 15+5 rule).** Each turn emits a heartbeat `{ts_start, ts_end, project, session, task}`
(`ts_start` at `UserPromptSubmit`, `ts_end` at `Stop`). Per (local day, project, task): merge heartbeats
into active *stretches*, splitting wherever an idle gap exceeds **15 min** (stale gaps discarded — a
session left open for days costs nothing); each stretch = its span **+ 5 min** tail buffer; sum, round
to **0.25 h**. **Attribution is strictly by session cwd** — whatever folder the session is rooted in gets
the time, regardless of files touched.

**Determinism is the point.** No LLM goes near the numbers (billing must be auditable/reproducible). The
only LLM-suitable piece is the optional F&O work *description*, sourceable from existing `ops/memory/daily/`
summaries with zero new inference — **deferred, not built**.

**F&O codes** live in each project's `CLAUDE.md` `## Identity` (`fno_code:`); a task can override via its own
`fno_code:`. `Dev` -> `INTERNAL-RND` (non-billable); missing -> `UNSET`. All 10 projects backfilled with a
blank field to fill in.

**Cadence.** `/time` = live tally (writes nothing); `/log` finalizes complete past days (catch-up for
missed days) into `timesheet/<YYYY-MM>/<date>.md` (daily files grouped by month). The **daily file is the
F&O entry unit** (entered per day) — no weekly aggregate file; `/time week` / `/time month` print a by-date
report on demand. Hours round to 0.25 h with a **0.5 h floor** (any logged work on a project that day).
Corrections edit the timesheet, never the heartbeats. (Revised 2026-06-30: dropped weekly rollup, month
folders, 0.5 h floor.)

**Not version-controlled** (user's call): `heartbeats/`, `timesheet/`, `active-task` are gitignored —
operational output regenerable from heartbeats; the want is the current per-day timesheet to enter into F&O,
not a git history of hour-by-hour changes. Only `ops/time/README.md` + `rollup.py` (the system) are tracked.

Harness accelerators (non-load-bearing, per [[memory-arch-three-jobs]]'s substrate/harness split):
`.claude/hooks/track_time.py` captures; `ops/time/rollup.py` computes; `/time`, `/log`, `/task` wrap it.
Full spec + by-hand recipe in `ops/time/README.md`.
