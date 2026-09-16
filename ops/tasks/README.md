# Task Store

The workspace-level queue of **business work in flight** — across every project, in one place. This is the **Output** stage of the ICOR pipeline (Input → Control → Output → Refine):

- **Input** — `/todo` drops raw items into `ops/TODO.md` (capture, zero friction).
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

## Progress, DevOps id, customer ask, parked (added 2026-09-16)

The task file is the unit of progress. Its `## Progress` block carries **Now (YYYY-MM-DD)**, **Tried and
dropped** and **Next**; the Now date is what "progress age" is measured from. `fno_task` names the Azure
DevOps work item or says `none` (customer projects bill task-always, so `none` means the time cannot be
registered at task level yet). `customer_ask` says whether we need something from the customer and whether it
has been sent; the `## Needs from customer` section says what and from whom.

A task can be **parked** without changing folder: `waiting_on: customer|<name>` or `resume_on: YYYY-MM-DD`
(`/task wait`, `/task postpone`, `/task resume`). Parked tasks leave the day brief and the project card's active
list until the date passes (then **due back**) or the wait is cleared.

`ops/bin/daybrief.py` derives the day brief, the dashboard model and each project card's *Active tasks*
section from these files; nothing is typed twice.

## Relationship to projects

A task is tagged with its `project` (e.g. `customers/Matas/...` or `own/AtomicCortex`), or left blank for workspace-level work. Deep, project-specific context still lives in that project's `CONTEXT.md`; this store is the cross-project view of *what is open everywhere*.
