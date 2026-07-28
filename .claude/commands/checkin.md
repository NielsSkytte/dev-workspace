Walk the current project's status one category at a time and write the answers back to its `CONTEXT.md`. An **interview**, not a summariser — you ask, Niels answers, nothing is inferred from the session.

Usage:
  /checkin           <- interview the project you are sitting in
  /checkin quick     <- only the categories that currently hold something

This is the routine the dashboard's **Status check-in** button launches (`AGENTS.md` > *Dashboard*).

## When to use which

- **`/checkin`** — you arrived at a project cold (e.g. from the dashboard) and want its recorded state
  to match reality. The **user** is the source.
- **`/handoff`** — a real working session just happened and CONTEXT.md should reflect *what you did*.
  The **session** is the source.

They write the same sections. Never run both on one sitting: run `/checkin` when you have nothing to
report from the session, `/handoff` when you do.

## Instructions

1. **Locate and read `CONTEXT.md`** in the current working directory. If there is none, say so and stop
   — the session is not rooted in a project. Also read the project's open/in-progress tasks from
   `C:\Dev\ops\tasks\` (matched on the task's `project:` field).

2. **Interview, one category at a time, in this order.** Blocked on → In progress → Next Actions →
   Open Threads → Tasks.

   **One `AskUserQuestion` card per category. Never batch them, never send a list of questions**
   (memory record `feedback-interview-one-question`). For each category:

   - Put the **current recorded items in the question text**, numbered, so the answer is about
     something concrete rather than a blank page.
   - Offer options shaped to that category. Good defaults:
     - *"Still accurate"* — carry it forward untouched.
     - *"Resolved / done"* — drop it, and note the resolution in the write-up.
     - *"Changed — I'll describe it"* — the user types the new state in Other.
     - *"Skip this category"* — leave it exactly as it is.
   - When a category holds several items and they have moved differently, ask about the **item**, not
     the category — one card each — rather than forcing one answer onto all of them.
   - Empty category: ask whether anything belongs there now, with *"Nothing"* as the first option.
   - `/checkin quick`: skip categories that are currently empty.

3. **Never block on the whole interview.** Every card carries a skip. If the user skips everything,
   say so plainly and write nothing.

4. **For Tasks**, ask per open/in-progress task whether it is still open, now in progress, done, or
   blocked. A state change means **moving the file** between `ops/tasks/<state>/` and appending a dated
   Log line — do that only after the confirmation step below.

5. **Show the full proposed change before writing** — a compact per-section diff of what is added,
   changed, dropped and left alone, including any task moves. Then one confirmation:
   *"Write it" / "Let me adjust" / "Discard"*.

6. **On confirmation, write**: update `CONTEXT.md` (`**Last worked:**` to today, plus the answered
   sections), move any task files, append their Log lines. Preserve file structure and leave untouched
   sections byte-identical.

7. **Close with one line** naming what changed and what the next action now is.

## Guardrails

- **Only the user's answers go in.** Do not infer status from the repo, from git, or from the
  transcript — that is `/handoff`'s job, and mixing them puts unverified claims into the record.
- **Skipped means untouched**, not "still accurate" — never rewrite a section the user skipped, and
  never restate a skipped section as confirmed.
- **Never remove a user-written line** unless the user said it is resolved.
- **Append to the Decisions Log, never edit it.** A check-in rarely produces decisions; if one comes up
  in conversation, add it dated, and say you did.
- Facts only. If an answer is ambiguous, ask one more card rather than guessing.
