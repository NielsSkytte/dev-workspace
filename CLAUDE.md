# CLAUDE.md — Claude Code Bootstrap

> **Read [`AGENTS.md`](AGENTS.md) first — it is the complete, tool-neutral source of truth** for how this workspace operates (structure, projects, agents, knowledge flow, continuity loop, conventions, guardrails). This file is a Claude Code *bootstrap* only: it points there and maps the Claude-specific harness onto it. Nothing load-bearing lives here (Guardrail 7 — deleting `.claude/` + this file must lose no knowledge or capability).

## Behaviour

Be short and to the point, /s

**Facts only — never imply.** State what the evidence shows; label inference explicitly as
inference. Word choices must not suggest more than the evidence supports (see memory record
`feedback-fact-only-language`). Before asserting a defect, cite the record (file + line).

**If you can do it, do it — then report.** The ask line is blast radius, not difficulty: changes
that stay on this machine and that you can undo (reading, authoring, internal commits) are done and
reported; a customer-facing push, a customer-tenant mutation, anything destructive, and any costly
or long run are asked first. A proven fix is a reason to act, not to ask. Ladder in `AGENTS.md` >
Conventions; memory record `feedback-act-then-report`.

**Ask closed.** When a question IS warranted: recommendation first, two or three named options
carrying their concrete values, and state what a bare "yes" triggers. No "your call", no open
either/or without a recommendation (see memory record `feedback-closed-questions`).

## Claude harness map

The harness *accelerates* routines that are fully described in `AGENTS.md`. Where the pieces live:

| Harness piece | Location | Wraps (neutral routine in AGENTS.md) |
|---|---|---|
| Agents (`fabric-back`, `semantic`, `fabric-front`, `content`, `architect`, `M`, `Q`) | `.claude/agents/` | *Agents — the roster* |
| Slash commands (`/todo`, `/task`, `/log`, `/time`, `/dashboard`, `/brief`, `/handoff`, `/new-project`, …) | `.claude/commands/` | *Continuity loop*, *Knowledge flow*, *Working with projects*, *Time tracking*, *Dashboard* |
| Agent Skills (auto-invoked by context) | `.claude/skills/` | *Building new capabilities* |
| Memory hooks (`capture_turn.py` = per-turn capture; `build_snapshot.py` = session-start injection) | `.claude/hooks/` | *Memory* (substrate lives at `ops/memory/`) |
| Time hooks (`track_time.py` = per-turn heartbeat on `UserPromptSubmit`+`Stop`; `session_task.py` = active-task resolution on `SessionStart`) | `.claude/hooks/` | *Time tracking* (substrate lives at `ops/time/`) |

**Reach for a slash command** for a short recipe you trigger on demand; **reach for an Agent Skill** when it carries domain knowledge or files and should fire automatically by context. Before creating any skill/command/agent, apply the justification rubric in `AGENTS.md` > *Building new capabilities*.

## Continuity loop — Claude triggers

The routine and its knowledge live in `AGENTS.md` > *Continuity loop*. Claude's two triggers:

- **Workspace walk (root):** a `SessionStart` hook in `C:\Dev\.claude` fires it automatically at `C:\Dev` and emits the capped **memory snapshot**. Hooks inject context and do not auto-generate a reply — the walk runs on the first reply of the session.
- **Customer walk (at a customer root):** `customers/` is two-tier — a customer node wraps its projects. **When a session starts at `customers/<client>/` with no project selected, read the customer node's `CONTEXT.md` + the project index in its `CLAUDE.md`, surface the projects and their statuses, and prompt which project this session is for** (one project → name and confirm). Then run that project's project walk. The customer node is a map and time normally bills to the chosen project — but a session that stays at the customer node (no project selected) is tracked at the **customer level** (`customers/<client>`, Proj ID `UNSET`, resolved at the review gate; decided 2026-07-28). Tasks still attach only to projects.
- **Project walk (inside a project):** hooks don't cascade, so this rule rides this cascading `CLAUDE.md` into project sessions — **when a session starts inside `customers/…/<project>` or `own/…`, read that project's `CONTEXT.md` (and any "Related contexts" it names) and surface unread `INBOX.md` before the first request.**
  - **Customer projects — pick the session's task:** if the project is `customers/…` and has any open/in-progress task (a task whose `project:` matches), run the `/switch-task` selection before the first request — list its tasks and ask which one this session's time bills to, then set the active task from the answer. If it has exactly one, name it and confirm rather than listing. `own/…` projects skip this (no task-level tracking).

At session end / when wrapping up, offer to append a session-log entry (`/log`), which also distills the day's memory.

## Memory — Claude accelerators

The memory substrate lives at `ops/memory/` (see `AGENTS.md` > *Memory*). Claude accelerates it: a `Stop` hook (`.claude/hooks/capture_turn.py`) captures each turn to `ops/memory/daily/`; the `SessionStart` hook injects the snapshot (`build_snapshot.py`); native Claude auto-memory is **disabled** (`autoMemoryEnabled: false` in `.claude/settings.json`) so `ops/memory/` is the only home.

## Reminders

- **Hook registration is dual (fixed 2026-07-28):** `track_time.py`, `capture_turn.py` + `session_task.py` are registered in both `.claude/settings.json` (workspace) **and** the user-level `~/.claude/settings.json` — settings don't cascade, so only the user-level registration reaches sessions rooted below `C:\Dev` (project/customer sessions). The scripts self-guard to cwds under `C:\Dev`; Claude Code deduplicates the identical command strings, so **keep them byte-identical (load-bearing)**. The `SessionStart` *snapshot* hook (`session-start.ps1`) stays workspace-root-only by design; the `SessionStart` *task* hook (`session_task.py`) is dual-registered, since it must fire in project sessions.
- **Time attribution is task-first (ADR-003, 2026-07-28):** the active task decides the project, cwd is the fallback, capped to the same customer, with a session-scoped marker. Don't reintroduce cwd-first logic. Hook output is ASCII-sanitised on purpose — task titles carry non-cp1252 characters and a Windows encode error would be swallowed by the fail-silent guard.
- **Scripts are ASCII-only** under Windows PowerShell 5.1 (hooks, `.ps1`). See `AGENTS.md` > *Conventions* for the why.
- **Project context chain:** open sessions rooted at the project folder so the chain resolves project → workspace root. Use the per-project VS Code Task (`Ctrl+Shift+P` → `Tasks: Run Task`).
- **Harness dirs are junctioned into every project root (fixed 2026-07-31):** only `CLAUDE.md` cascades — `commands/`, `skills/` and `agents/` do **not**. `ops/bin/heal-repos.ps1` > `Link-Harness` therefore junctions all three from each project root's `.claude/` back to `C:\Dev\.claude\`, and hard-links `settings.json`. A project root is any dir holding a `CLAUDE.md`. Before this, project-rooted sessions had no slash commands, no domain skills and no agent roster (`M`/`Q`/`sentinel` unspawnable — 5 logged occurrences; memory `hooks-subdir-session-gap`). Two guarantees keep it true: `/new-project` links on creation, and `/log` re-runs the healer every wrap-up, so a hand-made project self-heals. **Never delete a `.claude/` subfolder with `Remove-Item -Recurse`** — PowerShell 5.1 can follow the junction and empty the workspace original; use `cmd /c rmdir <link>`.
- **Switching to / starting projects, guardrails, identity block, all conventions:** see `AGENTS.md`.
