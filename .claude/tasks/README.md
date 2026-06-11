# Task Store

The workspace-level queue of **business work in flight** — across every project, in one place. This is the **Output** stage of the ICOR pipeline (Input → Control → Output → Refine):

- **Input** — `/park` drops raw items into `.claude/INBOX.md` (capture, zero friction).
- **Control** — triage promotes an inbox item into a structured task here (the deciding/routing step).
- **Output** — *this store*: tracked, actionable tasks with state and context.
- **Refine** — review / session log / automation (later).

Scope is **business, all kinds** — the BPM (Business Project Management) quadrant of ICOR. Personal-life tasks do not belong here.

## Why a store and not a checklist

A parked line can't carry *why it matters*, *what context it needs*, or *who owns it*, can't be referenced, and doesn't track state. A task is a file so it can.

## Lifecycle — state is the folder

```
tasks/
├── open/         ← created, not started
├── in-progress/  ← actively being worked
├── done/         ← completed (outcome noted in the Log)
└── cancelled/    ← won't do (reason noted in the Log)
```

A task moves between folders as its state changes. The file *is* the record; moving it *is* the state transition.

## Task file

- **Filename**: `YYYY-MM-DD-short-slug.md` (date created + a slug). This is the task's reference handle.
- **Schema**: see `_TEMPLATE.md`. Frontmatter holds structured fields; the body holds the work in plain language plus a running Log.

## Working with tasks

Use the `/task` command (`.claude/commands/task.md`):

- `/task <description>` — create a task (the LLM structures it from context)
- `/task` — list open + in-progress work
- `/task start|done|cancel <slug>` — move it through its lifecycle

## Relationship to projects

A task is tagged with its `project` (e.g. `customers/Matas/...` or `own/AtomicCortex`), or left blank for workspace-level work. Deep, project-specific context still lives in that project's `CONTEXT.md`; this store is the cross-project view of *what is open everywhere*.
