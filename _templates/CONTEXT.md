# CONTEXT — [Project Name]

> **Resume card.** Read first in every session. Rewritten, never appended, at every handoff.
> Keep it under ~6 KB plus the task lines: this file says where the work stands today, not how
> it got here. History lives in `ops/log/sessions.md` (this project's sections),
> `CONTEXT_ARCHIVE*.md`, the project's `design/` docs, and memory records scoped `project:<path>`.
> Decisions live in `CONTEXT_DECISIONS.md` (append-only table: date, decision, rationale).

## Goal
<!-- What we are trying to achieve, in the customer's terms. Two to four sentences. -->

**Done when:** <!-- the observable end state, one or two lines -->

## Where we stand — YYYY-MM-DD
<!-- Six lines at most, one per workstream, facts with dates. Replace, do not append. -->
-

## Active tasks — progress
<!-- One line-block per open / in-progress task in ops/tasks whose project: is this project,
     most active first. Derived from each task file's Progress block. Grammar:
       slug — DevOps <work item id | none>. **state.** Last: <what landed, date>.
       Next: <one step>. Customer ask: <what, from whom, sent when | none>. -->
- `<task-slug>` — DevOps `<id>` | none. **in progress | open | blocked.** Last: <..., YYYY-MM-DD>.
  Next: <one step>. Customer ask: <what, who, sent YYYY-MM-DD | not sent | none>.

## Blocked on others
<!-- Who owes what. One line each, by name. Customer asks that are not yet sent are listed here too. -->
-

## Open threads
<!-- Pending decisions and things to watch. One line each, at most eight.
     A resolved thread leaves the file; it is not struck through. -->
-

## Where the detail lives
<!-- Pointers only: design docs, tools, CONTEXT_DECISIONS.md, CONTEXT_ARCHIVE.md, related contexts. -->
-
