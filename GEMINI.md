# GEMINI.md — Gemini / Antigravity Bootstrap

> **Read [`AGENTS.md`](AGENTS.md) first — it is the complete, tool-neutral source of truth** for how this workspace operates (structure, projects, agents, knowledge flow, continuity loop, conventions, guardrails). This file is a Gemini / Antigravity *bootstrap* pointer: it maps Antigravity capabilities onto the neutral operational substrate. Nothing load-bearing lives here (Guardrail 7 — deleting tool harness files must lose no knowledge or capability).

## Behaviour

Be short and to the point.

**Facts only — never imply.** State what the evidence shows; label inference explicitly as inference. Word choices must not suggest more than the evidence supports (see memory record `ops/memory/store/feedback-fact-only-language.md`). Before asserting a defect, cite the record (file + line).

## Antigravity Harness Map

The harness accelerates routines fully described in [`AGENTS.md`](AGENTS.md).

| Harness piece | Location / Tool | Wraps (neutral routine in AGENTS.md) |
|---|---|---|
| Agents roster (`fabric-back`, `semantic`, `fabric-front`, `content`, `architect`, `M`, `Q`, `sentinel`) | Antigravity Personas / Subagents | *Agents — the roster* |
| Agent Skills | `.agents/skills/` (junctioned to `.claude/skills/`) | *Building new capabilities* |
| Memory & Time Substrate | `ops/memory/`, `ops/time/` | *Memory*, *Time tracking* |
| Dashboard | `ops/dashboard.py` | *Dashboard* (`http://127.0.0.1:8787/`) |
| Action & Log capture | `ops/TODO.md`, `ops/tasks/`, `ops/log/sessions.md` | *Continuity loop* |
| Workspace Custom Commands | `.claude/commands/*.md` | *Command routines (`/log`, `/todo`, `/task`, `/brief`, `/checkin`, `/dashboard`, `/handoff`, `/switch-task`, `/new-project`, `/time`, `/update-skills`)* |

## Workspace Custom Commands (`.claude/commands/`)

Whenever the user invokes or references a slash command (e.g. `/log`, `/todo`, `/task`, `/brief`, `/checkin`, `/dashboard`, `/handoff`, `/switch-task`, `/new-project`, `/time`, `/update-skills`), **immediately inspect and execute the instructions** in its corresponding file under `file:///C:/Dev/.claude/commands/<command>.md`:

- **`/log`** (`.claude/commands/log.md`) — Session log, memory distillation, time rollup, backup & git commit.
- **`/todo`** (`.claude/commands/todo.md`) — Quick action/idea capture to `ops/TODO.md`.
- **`/task`** (`.claude/commands/task.md`) — Create or triage a workspace task in `ops/tasks/`.
- **`/brief`** (`.claude/commands/brief.md`) — Workspace/project morning briefing & task walk.
- **`/checkin`** (`.claude/commands/checkin.md`) — Mid-session status check & task review.
- **`/dashboard`** (`.claude/commands/dashboard.md`) — Workspace status dashboard & metrics.
- **`/handoff`** (`.claude/commands/handoff.md`) — Generate structured handover notes.
- **`/switch-task`** (`.claude/commands/switch-task.md`) — Switch active task context & set active task.
- **`/new-project`** (`.claude/commands/new-project.md`) — Scaffold a new customer or internal project.
- **`/time`** (`.claude/commands/time.md`) — Log or review time heartbeats & timesheet totals.
- **`/update-skills`** (`.claude/commands/update-skills.md`) — Re-index and update skill registry.

When starting or running a session:

- **Workspace Walk (at `C:\Dev`):** Read `ops/tasks/in-progress/` and `ops/tasks/open/`, unchecked items in `ops/TODO.md`, and the latest `ops/log/sessions.md` entry. Surface open work and suggest focus.
- **Customer Walk (at `customers/<client>/`):** Read customer node `CONTEXT.md` + project index in `CLAUDE.md`. Surface projects and prompt for project selection before starting work.
- **Project Walk (inside `customers/.../<project>` or `own/...`):** Read project `CONTEXT.md` (and related contexts), surface unread `INBOX.md` entries, and resolve active task (`/switch-task` routine).
- **Session Wrap-Up:** Append a dated entry to `ops/log/sessions.md`, update project `CONTEXT.md`, offer wrap-up commits according to commit policy, and distill daily memory into `ops/memory/store/`.

## Key Reminders & Guardrails

- **ASCII-only Scripts (Guardrail 9):** Any `.ps1` script executed under Windows PowerShell 5.1 must use ASCII punctuation.
- **Tenant Isolation (Guardrail 11):** Never call `fab` bare. Always use `ops\bin\fab-as.ps1 <Customer> <args>`. Validate `tenant_id:` on customer node before running tenant-bound CLI.
- **Commit Policy:** Personal/internal repos (`C:\Dev`, unit repos) are auto-offered at wrap-up. Customer-facing / DevOps repos are **never auto-committed** without explicit user permission.
- **Provider-Neutral Substrate:** All durable state (tasks, memory, decisions, context) must remain plain markdown/JSONL in tool-neutral locations. Harness files must contain zero proprietary decision logic or unbacked business rules.
