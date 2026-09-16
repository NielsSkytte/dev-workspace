Walk the project's resume card with its owner, one item at a time, and write the answers back —
into the task files' `## Progress` blocks and the card's hand-written sections. An **interview**, not
a summariser: you ask, Niels answers, nothing is inferred from the session.

Usage:
  /checkin           <- the whole card: every open task, blocked on others, open threads, where we stand
  /checkin quick     <- only what the day brief flags: stalled, due back, ask unsent, blocked
  /checkin convert   <- one-time: move a project from the old CONTEXT.md shape onto the card

This is what Today's **Check-in** and **Convert to the card** buttons and the overview drawer's
**Status check-in** launch (`AGENTS.md` > *Dashboard* > *Check-in*). Card shape:
`_templates/CONTEXT.md`; task shape: `ops/tasks/_TEMPLATE.md`.

## When to use which

- **`/checkin`** — you arrived at a project cold (from Today, after days away) and its recorded state
  should match reality. The **owner** is the source.
- **`/handoff`** — a real working session just happened and the record should reflect *what you did*.
  The **session** is the source.

They write the same files. Never run both on one sitting.

## Instructions

1. **Resolve the project** as `/handoff` does (this session's active task, else the cwd). Read its
   card and run `python C:\Dev\ops\bin\daybrief.py --text --scope <project>` — that lists every
   open task with its DevOps id, progress age, next step and ask status without reading the files.
   No card: say so and stop. A card without `## Active tasks — progress` is the old shape: offer
   *"Convert now"* (the `convert` routine below) / *"Skip"*, and stop unless converting.

2. **Interview, one item at a time, in this order.** **One `AskUserQuestion` card per item. Never
   batch, never send a list of questions** (memory record `feedback-interview-one-question`). Put
   the recorded state in the question text so the answer is about something concrete.

   a. **Tasks, most stale first** — stalled, then due back, then the rest by progress age; parked
      tasks last and only in the full mode. Question text: `slug — DevOps <id|none>. Now (<date>):
      <text>. Next: <step 1>. Ask: <status, first line>`. Options: *"Still accurate"* /
      *"Changed — I'll describe"* / *"Done"* / *"Skip"*. A typed answer is the new state: rewrite
      `**Now (today):**` and `**Next:**` from the owner's words; "sent 09-15" or "answered" updates
      `customer_ask:` and `## Needs from customer`; "wait on customer" or "postpone to <date>" parks
      it as `/task wait|postpone` does; "done" moves the file as `/task done` does.
   b. **Blocked on others**, per line: *"Still owed"* / *"Received / resolved"* / *"Changed — I'll
      describe"* / *"Skip"*. Empty section: ask whether anyone owes anything, *"Nobody"* first.
   c. **Open threads**, per line: *"Still open"* / *"Resolved — drop it"* / *"Changed — I'll
      describe"* / *"Skip"*. Empty: ask whether anything is pending, *"Nothing"* first.
   d. **Where we stand**, one card for the section: *"Still accurate — date it today"* /
      *"Changed — I'll describe"* / *"Skip"*. A typed answer replaces the lines (at most six).
   e. **Done when**, only while it is marked *(proposed, confirm)*: *"Confirmed — drop the marker"* /
      *"Changed — I'll describe"* / *"Skip"*.

   `/checkin quick` asks (a) only for tasks the brief flags (stalled, due back, ask unsent) and (b).

3. **Never block on the whole interview.** Every card carries a skip. If everything is skipped, say
   so plainly and write nothing.

4. **Show the full proposed change before writing** — per task the new Progress block, per card
   section added / changed / dropped lines, any file moves. One confirmation: *"Write it" / "Let me
   adjust" / "Discard"*.

5. **On confirmation, write**: the task files (Progress dated today in the owner's words, a dated Log
   line `check-in: …`, field changes, moves), the card sections, then

   ```
   python C:\Dev\ops\bin\daybrief.py --write-cards --project <project>
   ```

   Keep line endings; leave skipped items byte-identical.

6. **Close with one line** naming what changed and what the next action now is.

## `/checkin convert` — old CONTEXT.md onto the card (one time per project)

1. Confirm the card is the old shape (no `## Active tasks — progress`). Already a card: say so, stop.
2. Read the old `CONTEXT.md` (in slices if large), the project's recent sections in
   `ops/log/sessions.md`, the brief for its tasks, and `CLAUDE.md` > Identity.
3. Draft the card from `_templates/CONTEXT.md`: the header blockquote; **Goal** in the customer's
   terms with **Done when (proposed, confirm)**; **Where we stand — <date of the latest evidence,
   not today>**, at most six lines; the `## Active tasks — progress` heading alone (generated);
   **Blocked on others**; **Open threads** (live ones only, at most eight); **Where the detail
   lives**. A paused, delivered or planned project gets the minimal card: Goal, one standing line
   saying the status and why, the rest `-`.
4. A *Decisions Log* table moves verbatim into `CONTEXT_DECISIONS.md` (header as Carl Ras's:
   append-only, date / decision / rationale).
5. **Tasks without a `## Progress` block** (the brief shows "no Progress block"): insert `## Progress`
   and `## Needs from customer` after `## What` — *Now* dated from the last dated Log line, in its
   words; *Next* from *What* and the Log; set `fno_task:` to the DevOps id or `none` and add
   `customer_ask: none`; a dated Log line "brought onto the Progress shape; no facts changed".
6. Show the draft card and the task inserts. One confirmation: *"Write it" / "Let me adjust" /
   *"Discard"*.
7. On confirmation: `git mv CONTEXT.md CONTEXT_ARCHIVE.md` in the project's repo (plain rename if it
   is not one), write `CONTEXT.md` and `CONTEXT_DECISIONS.md`, write the task files, then run
   `--write-cards --project <project>`. Commit the unit repo at wrap-up with `/log`, or now if asked.

## Guardrails

- **Only the owner's answers go in.** Do not infer status from the repo, git or the transcript —
  that is `/handoff`'s job, and mixing them puts unverified claims into the record. `convert`
  drafts from the written record and is confirmed before it is written.
- **Skipped means untouched**, not "still accurate" — never rewrite a skipped item, never restate it
  as confirmed. *Where we stand* is re-dated only when the owner confirmed it today.
- **Never remove a line** the owner did not resolve. **Rewrite, never append** — no history in the
  card.
- **Decisions are append-only.** A check-in rarely produces one; if it does, add it dated and say so.
- Facts only. If an answer is ambiguous, ask one more card rather than guessing.
