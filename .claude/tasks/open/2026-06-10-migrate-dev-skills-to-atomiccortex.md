---
title: Migrate team-scoped DEV skills into AtomicCortex
status: open
created: 2026-06-10
project: own/AtomicCortex
owner: architect
priority: normal
blocked_by: AtomicCortex graduating from project to system (ADR-0001)
source: inbox
---

## What
Decide which of the capabilities currently living in the DEV workspace (notably certain skills) are genuinely team/business-scoped and belong in AtomicCortex, versus which are personal-PKA capabilities that stay in DEV. Migrate the team-scoped ones.

## Why
Keeps the personal PKA and AtomicCortex cleanly separated per ADR-0001 ("one spec, many instances, federated at seams"). Generic, team-scoped skills written to the shared spec belong in the team system, not welded into the personal workspace.

## Context
- ADR-0001 — `own/AtomicCortex/docs/decisions/0001-atomiccortex-is-a-system-not-a-project.md`
- Memory: `atomiccortex-vision`
- Blocked until AtomicCortex is reframed from a `type: content` wiki project into a system (its `CLAUDE.md` still describes the narrow wiki scope).

## Log
- 2026-06-10 — parked in inbox
- 2026-06-11 — promoted to task (Control step); routed to AtomicCortex / architect, marked blocked
