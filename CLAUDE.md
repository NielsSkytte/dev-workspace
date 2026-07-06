# CLAUDE.md — Claude Code Bootstrap

> **Read [`AGENTS.md`](AGENTS.md) first — it is the complete, tool-neutral source of truth** for how this workspace operates (structure, projects, agents, knowledge flow, continuity loop, conventions, guardrails). This file is a Claude Code *bootstrap* only: it points there and maps the Claude-specific harness onto it. Nothing load-bearing lives here (Guardrail 7 — deleting `.claude/` + this file must lose no knowledge or capability).

## Behaviour

Be short and to the point, /s
## Claude harness map

The harness *accelerates* routines that are fully described in `AGENTS.md`. Where the pieces live:

| Harness piece | Location | Wraps (neutral routine in AGENTS.md) |
|---|---|---|
| Agents (`fabric-back`, `semantic`, `fabric-front`, `content`, `architect`, `M`, `Q`) | `.claude/agents/` | *Agents — the roster* |
| Slash commands (`/todo`, `/task`, `/log`, `/time`, `/brief`, `/handoff`, `/new-project`, …) | `.claude/commands/` | *Continuity loop*, *Knowledge flow*, *Working with projects*, *Time tracking* |
| Agent Skills (auto-invoked by context) | `.claude/skills/` | *Building new capabilities* |
| Memory hooks (`capture_turn.py` = per-turn capture; `build_snapshot.py` = session-start injection) | `.claude/hooks/` | *Memory* (substrate lives at `ops/memory/`) |
| Time hook (`track_time.py` = per-turn heartbeat on `UserPromptSubmit`+`Stop`) | `.claude/hooks/` | *Time tracking* (substrate lives at `ops/time/`) |

**Reach for a slash command** for a short recipe you trigger on demand; **reach for an Agent Skill** when it carries domain knowledge or files and should fire automatically by context. Before creating any skill/command/agent, apply the justification rubric in `AGENTS.md` > *Building new capabilities*.

## Continuity loop — Claude triggers

The routine and its knowledge live in `AGENTS.md` > *Continuity loop*. Claude's two triggers:

- **Workspace walk (root):** a `SessionStart` hook in `C:\Dev\.claude` fires it automatically at `C:\Dev` and emits the capped **memory snapshot**. Hooks inject context and do not auto-generate a reply — the walk runs on the first reply of the session.
- **Customer walk (at a customer root):** `customers/` is two-tier — a customer node wraps its projects. **When a session starts at `customers/<client>/` with no project selected, read the customer node's `CONTEXT.md` + the project index in its `CLAUDE.md`, surface the projects and their statuses, and prompt which project this session is for** (one project → name and confirm). Then run that project's project walk. The customer node is a map, never a billing target — time/tasks attach only to the chosen project.
- **Project walk (inside a project):** hooks don't cascade, so this rule rides this cascading `CLAUDE.md` into project sessions — **when a session starts inside `customers/…/<project>` or `own/…`, read that project's `CONTEXT.md` (and any "Related contexts" it names) and surface unread `INBOX.md` before the first request.**
  - **Customer projects — pick the session's task:** if the project is `customers/…` and has any open/in-progress task (a task whose `project:` matches), run the `/switch-task` selection before the first request — list its tasks and ask which one this session's time bills to, then set the active task from the answer. If it has exactly one, name it and confirm rather than listing. `own/…` projects skip this (no task-level tracking).

At session end / when wrapping up, offer to append a session-log entry (`/log`), which also distills the day's memory.

## Memory — Claude accelerators

The memory substrate lives at `ops/memory/` (see `AGENTS.md` > *Memory*). Claude accelerates it: a `Stop` hook (`.claude/hooks/capture_turn.py`) captures each turn to `ops/memory/daily/`; the `SessionStart` hook injects the snapshot (`build_snapshot.py`); native Claude auto-memory is **disabled** (`autoMemoryEnabled: false` in `.claude/settings.json`) so `ops/memory/` is the only home.

## Reminders

- **Scripts are ASCII-only** under Windows PowerShell 5.1 (hooks, `.ps1`). See `AGENTS.md` > *Conventions* for the why.
- **Project context chain:** open sessions rooted at the project folder so the chain resolves project → workspace root. Use the per-project VS Code Task (`Ctrl+Shift+P` → `Tasks: Run Task`).
- **Switching to / starting projects, guardrails, identity block, all conventions:** see `AGENTS.md`.
