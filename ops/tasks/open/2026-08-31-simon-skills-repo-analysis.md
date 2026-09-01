---
title: Analyse Simon's skills repo vs our skills — and author Atomic's semantic network into the pingala skills
status: open
created: 2026-08-31
project:              # workspace-level (capability layer)
owner: Q
priority: normal
blocked_by: Repo URL not obtained from Simon; Simon is on maternity leave (memory `carlras-viewtransform-workspace-drift`, 2026-08-13)
activity:
fno_task:
source: todo
---

## What
Clone Simon's new skills repo and analyse the skills in it — overlap/fit against the workspace
skills (`.claude/skills/`) and against `pingala/psi-context-library`. Get the repo URL from Simon.

In the same pass: update our pingala skills with **Atomic's semantic-network feature**. That is
*not* among Simon's skills — it needs authoring from the Atomic side.

## Why
The capability layer has three sources now (workspace skills, `psi-context-library`, Simon's repo).
Without the comparison we either duplicate what Simon already wrote or keep a pingala skill set that
is silently behind Atomic.

## Context
- Original capture: `ops/TODO.md` 2026-06-18 (folds in the 2026-06-19 semantic-network item at the
  2026-07-06 triage).
- Workspace skills: `C:\Dev\.claude\skills\` — the `pingala-*` and `fabric-*` families are the
  overlap surface.
- `pingala/psi-context-library` — the team-side context/skill store.
- Related task: `tasks/open/2026-06-10-migrate-dev-skills-to-atomiccortex.md` — same question from the
  AtomicCortex angle (which capabilities are team-scoped). Decide these together, not separately.
- Atomic (Simon's generator) background: memory `carlras-viewtransform-workspace-drift`,
  `tasks/open/2026-08-18-carlras-atomic-ctas-merge.md`.

## Log
- 2026-08-31 — promoted from TODO (captured 2026-06-18); routed workspace-level / Q. Blocked on the
  repo URL; Simon is on maternity leave, so the analysis half may have to wait while the
  semantic-network authoring half can proceed from the Atomic repo.
