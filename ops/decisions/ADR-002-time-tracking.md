# ADR-002: Per-Project Time Tracking

| Field       | Value                        |
|-------------|------------------------------|
| Status      | Accepted                     |
| Date        | 2026-06-22                   |
| Author      | Niels                        |
| Reviewers   | -                            |

---

## Context

Working time needs to be tracked per project for billing (Dynamics F&O time entry) and for visibility
into where effort goes. The constraints that shape the design:

- **Sessions go stale.** A session can sit idle for hours or days; wall-clock between interactions is not
  working time. Naive "session open duration" massively overcounts.
- **The unit is the project**, defined as the level that has its own `CLAUDE.md` init: `Dev` (the workspace
  setup itself), each `customers/<client>/<project>`, each `own/<project>`. `ops/` is not a billable project.
- **Some work is task-specific** within a project and should be separable.
- **Billing needs F&O codes** at the project level, occasionally overridden at the task level.
- **Guardrail 7** (governing principle): durable knowledge and data live as plain markdown/data under `ops/`
  (LLM-agnostic substrate); `.claude/` is a non-load-bearing accelerator. Acid test: deleting `.claude/`
  must lose no knowledge or capability.

## Decision

Adopt a **heartbeat + idle-timeout** model (the approach WakaTime/RescueTime use), implemented as a peer
substrate at `ops/time/` mirroring `ops/memory/` (raw stream distils into a reviewed artifact).

- **Heartbeats (raw).** Every turn appends `{ts_start, ts_end, project, session, task}` to
  `ops/time/heartbeats/<utc-date>.jsonl`. `ts_start` is stamped at prompt submit, `ts_end` at turn end, so
  the heartbeat carries the actual time spent on the turn.
- **Attribution by working directory.** The project is the session's cwd, regardless of which files are
  touched. Predictable and free; cross-edits wash out.
- **The 15+5 rollup model.** Per (local day, project, task): merge heartbeats into active stretches,
  splitting wherever an idle gap exceeds **15 min** (idle gaps discarded — solves the stale-session problem);
  each stretch counts as its span **+ 5 min** tail buffer (reading/thinking after the last reply); sum and
  round to the nearest **0.25 h**, then floor to a **0.5 h** minimum (any logged work on a project that day).
- **F&O dimensions.** A time line is Project ID → Activity → Task (Task fed from Azure DevOps). Project ID =
  the project `CLAUDE.md` `## Identity` `fno_code:` (`Dev` → `INTERNAL-RND`; missing → `UNSET`). A tagged task
  **adds** its `activity:` and `fno_task:` beneath the project id — additive, not an override; some projects
  register at activity level only, some down to task. Rows group by the finest dimension present; billable =
  `customers/…`. (Amended 2026-07-02: three-dimension model replacing the single task-override code.)
- **Daily review gate + cadence.** `/log` finalizes every complete past day with no timesheet yet
  (catch-up for missed days). Finalized daily timesheets are the reviewed truth and the unit of F&O entry
  (entered per day); corrections edit `ops/time/timesheet/<YYYY-MM>/<date>.md`, never the heartbeats. There is
  no weekly aggregate file — `/time week` / `/time month` print a by-date report on demand. `/time` shows the
  live tally without writing. (Amended 2026-06-30: dropped the weekly rollup; daily files grouped into
  `timesheet/<YYYY-MM>/`; added the 0.5 h floor.)
- **Task tagging is opt-in.** `/task start <slug>` writes `ops/time/active-task`; heartbeats bill to that
  task until `/task done|cancel` clears it. Untagged time is project-level.

### Substrate vs harness

| Substrate (`ops/time/`, survives `.claude/` deletion) | Harness (`.claude/`, accelerator only) |
|---|---|
| `README.md` — spec + by-hand recipe (source of truth) | `track_time.py` hook — appends heartbeats |
| `rollup.py` — tool-neutral python implementing the spec | `/time`, `/log` — wrap the rollup |
| `heartbeats/`, `timesheet/` — the data | `/task` — sets the active-task marker |

The algorithm and codes live in the substrate; the hook carries no decision logic (it only stamps and
appends). Acid test holds: with `.claude/` gone, `ops/time/README.md` + `rollup.py` + the data still
produce timesheets by hand.

## Consequences

### Positive
- Stale sessions cost nothing; reported time reflects actual active work.
- One predictable attribution rule, no per-turn classification.
- Billing-ready: per project+code per day, rounded to F&O increments; pull a week or month by date on demand.
- Fully recoverable from plain data; no harness lock-in.

### Negative / Risks
- **Approximation.** The 15+5 model is a heuristic; bouncing between projects within 15 min can overcount,
  and a stretch crossing local midnight is double-buffered. Mitigated by the daily review gate.
- **Capture depends on the hook firing.** If `track_time.py` doesn't run (hook misconfig), days have no
  heartbeats; the rollup simply reports nothing for them. Same failure mode and visibility as the memory hook.
- **Codes must be filled in.** Projects show `UNSET` until `fno_code:` is added to their `CLAUDE.md`.

## Alternatives Considered
- **Session-duration tracking** (open→close). Rejected — overcounts stale sessions by orders of magnitude.
- **Manual time entry.** Rejected as the primary path — defeats the point; the review gate already allows
  manual correction on top of automatic capture.
- **F&O codes in a central mapping file.** Rejected in favour of per-project `CLAUDE.md` — keeps the code
  next to the project it belongs to (the same init file that defines the project), with a task-level override.

## Related
- `ops/time/README.md` — the operational spec and by-hand recipe.
- `AGENTS.md` > Time tracking — the tool-neutral routine.
- ADR-001 — agent/skill routing (sibling decision record).
