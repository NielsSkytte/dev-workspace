---
title: Assisted triage — promote TODO.md captures into routed tasks
status: open
created: 2026-06-15
project:                # workspace-level (the ops substrate itself)
owner: Q                # refines the /task + /todo commands and the triage routine
priority: normal
blocked_by:
source: todo            # promoted from a TODO.md capture (see naming-gap note in Context)
---

## What
Enhance `/task` with assisted triage: pull the unprocessed `- [ ]` items from `ops/TODO.md` and help promote them into routed tasks — instead of triage being a fully manual, on-request act.

## Why
This is the missing half of the capture pipe. `/todo` makes capture frictionless on purpose, but frictionless capture only pays off if triage *reliably happens*. Without a dependable trigger, raw todos rot into an un-triageable graveyard and the Input→Control handoff silently breaks. The goal is to make triage reliable without re-adding friction to capture.

## Context
- `ops/TODO.md` — the capture store these items come from.
- `.claude/commands/todo.md` — capture + one-beat sharpen (just revised).
- `.claude/commands/task.md` — this command; the create step is where routing judgment lives.
- `.claude/hooks/session-start.ps1` — already counts unprocessed todos and surfaces them; a triage trigger could build on this.
- `AGENTS.md` > Continuity loop — **Guardrail 7**: the triage *routine* must be documented here (tool-neutral); the command/hook is only a dumb executor.
- Open design question (from this session): trigger = **threshold** (nudge at N+ unprocessed) vs **daily schedule**. Decide before building.
- **Naming gap found during triage**: `_TEMPLATE.md`'s `source:` enum is `inbox | direct`, and `task.md` step 3 says to check off `ops/INBOX.md` — but captures actually live in `ops/TODO.md`, which the workspace explicitly distinguishes from a project's `INBOX.md`. Reconcile: add `todo` to the enum and fix the command wording to point at `TODO.md`.

## Log
- 2026-06-15 — created (triaged from TODO.md)
