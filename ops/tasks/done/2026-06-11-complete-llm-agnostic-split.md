---
title: Complete the LLM-agnostic substrate/harness split
status: in-progress
created: 2026-06-11
project:
owner: architect
priority: normal
blocked_by:
source: direct
---

## What
Bring the workspace into full compliance with the LLM-agnostic principle (AGENTS.md / Guardrail 7). Two parts:
1. ✅ **Relocate substrate out of the Claude harness folder.** Done 2026-06-11 — `INBOX.md` and `tasks/` moved to `ops/`; `/park` and `/task` command paths and the `CLAUDE.md` workspace map updated.
2. **Migrate workspace conventions from `CLAUDE.md` into `AGENTS.md`.** Reduce `CLAUDE.md` to a thin bootstrap pointer; make `AGENTS.md` the full operational doc that any LLM can run from.

## Why
The content is already portable, but the *structure* leaks into Claude-specific homes — a bare non-Claude LLM pointed at the folder wouldn't find the inbox/tasks, and the conventions live only in `CLAUDE.md`. That fails the acid test (delete the harness → lose capability). Fixing it is the tool-portability half of the AtomicCortex charter.

## Context
- `AGENTS.md` — the principle this satisfies
- `CLAUDE.md` Guardrail 7
- ADR-0001 (`own/AtomicCortex/docs/decisions/0001-...`) — "one spec" shared across instances; this principle is part of that shared spec
- Location decided: `ops/` (sibling to `customers/` / `own/`).

## Log
- 2026-06-11 — created after a Claude-specificity audit flagged the inbox/tasks nesting and CLAUDE.md-bound conventions
- 2026-06-11 — chose `ops/` as the neutral location; relocated inbox + task store there and repointed commands/docs (part 1 done). Part 2 (migrate conventions `CLAUDE.md` → `AGENTS.md`) remains. Moved to in-progress.
