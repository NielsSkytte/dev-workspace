Write this session into the record: the task files it moved (their `## Progress` blocks) and the
project's resume card (`CONTEXT.md`), rewritten, not appended. The session is the source.

Usage: /handoff
Example: /handoff (end of a working session, or before switching project)

The routine is `AGENTS.md` > *Continuity loop* > *Handoff — the card rewrite*. Card shape:
`_templates/CONTEXT.md`. Task shape: `ops/tasks/_TEMPLATE.md` and `ops/tasks/README.md`.

## When to invoke

- End of a working session in a project, or before context-switching to another project
- Whenever real progress, a decision, a new customer ask or a new thread emerged
- After a context compaction in a long session — write the task's Progress then, not at the end
- When the user says "handoff", "wrap up", or "end of session" (`/exit` offers it)

Skip if the session was trivial (questions only, nothing moved). Say so in one line.

## Instructions

1. **Resolve the project and the card.** The project is the one this session's active task belongs
   to (`C:\Dev\ops\time\active-task`, this session's entry) or, without one, the project the cwd is
   in. The card is `<project>/CONTEXT.md`. No card (workspace root, or a customer node with no task
   chosen): say which project you would hand off and stop. A card without the heading
   `## Active tasks — progress` is the old shape: run `/checkin convert` first, then continue here.

2. **Tasks first — they are the unit of progress.** For the active task and any other open or
   in-progress task this session worked on (matched on the task's `project:`), rewrite its
   `## Progress` block in place:
   - `**Now (YYYY-MM-DD):**` — today's date; where the work stands, one to three lines, facts with
     dates and ids. Replace the old text, do not stack dated paragraphs.
   - `**Tried and dropped:**` — keep what is there; add only what this session dropped and only
     where it changes the next step.
   - `**Next:**` — ordered, the immediate step first. Remove steps that landed; do not add steps
     that were not discussed.
   - `## Needs from customer` and the `customer_ask:` field when an ask arose, was sent (`sent
     YYYY-MM-DD`) or was answered this session. `fno_task:` stays `none` or the id — never blank.
   - A dated `## Log` line naming what landed.
   - A state change is a folder move: `done` and `start` as in `/task`, parking as in
     `/task postpone|wait|resume`. Do it in the write step, not before.
   - **Work with no task**, on a customer project: create the task first (`/task <description>`,
     with its DevOps id or `none`) and put the progress there. Progress never lives only in the
     card. `own/` projects may carry it in *Where we stand* alone.
   Keep each file's line endings (several are CRLF).

3. **Then the card's hand-written sections, rewritten.**
   - `## Where we stand — YYYY-MM-DD` — today's date in the heading; at most six lines, one per
     workstream, each a fact with a date. Replace; the old lines are not history, the session log is.
   - `## Blocked on others` — who owes what, by name; an ask this session sent gets its date, one
     answered leaves; unsent asks from step 2 appear here too.
   - `## Open threads` — add what surfaced, delete what resolved (not struck through), at most eight.
   - `## Goal` / `**Done when**` — only if the session changed the goal, or the owner confirmed a
     done-when marked *(proposed, confirm)*: then drop the marker.
   - `## Where the detail lives` — pointers for new design docs or tools only.
   - `## Active tasks — progress` is **never edited by hand**; step 6 regenerates it.

4. **Decisions** made this session become rows in `CONTEXT_DECISIONS.md` (`| date | decision |
   rationale |`), appended at the bottom. Create the file from the Carl Ras header if missing.
   Never edit an old row.

5. **Show before writing.** For each task, the new Progress block in full (it is short); for the
   card, a compact per-section list of added / changed / dropped lines; any file moves and decision
   rows. Then one confirmation: *"Write it" / "Let me adjust" / "Skip handoff"*.

6. **On confirmation, write** the task files, the card sections and the decisions, then run

   ```
   python C:\Dev\ops\bin\daybrief.py --write-cards --project <project>
   ```

   which regenerates the task section from the files. If the hand-written part of the card is over
   about 6 KB, trim *Where we stand* and *Open threads* to the rule above before writing.

7. **Close with one line:** what was rewritten and *"Next session resumes at: <Next 1 of the active
   task>."* Then offer `/log` if it has not run today (history goes there, not in the card).

## Guardrails

- **Never invent progress.** Not sure it landed: it stays in *Next*. Not verified: say "not verified".
- **Rewrite, never append.** No "Completed since last update", no dated paragraphs stacking up in
  *Now*, no struck-through threads. How it got here belongs in `ops/log/sessions.md` and memory.
- **Facts only, dated.** Ids, run ids, counts and dates over adjectives; label inference as inference.
- **The generated section is not yours.** Change the task file and regenerate.
- **Decisions are append-only.** Old rows are never edited.
