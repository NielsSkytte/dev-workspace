Update the current project's CONTEXT.md based on what happened this session — automating the end-of-session handoff to your future self.

Usage: /handoff
Example: /handoff (use at end of a meaningful session)

## When to invoke

- End of a working session in a project
- Before context-switching to another project
- Whenever significant progress, decisions, or new threads emerged
- When the user explicitly says "handoff", "wrap up", or "end of session"

Skip if the session was trivial (just questions, no real work done).

## Instructions

1. **Locate CONTEXT.md.** It should be in the current working directory (the project root). If not found, tell the user and stop — they may not be in a project, or the project lacks CONTEXT.md.

2. **Read the current CONTEXT.md** to understand the existing state.

3. **Analyze the session.** Review what happened — what the user asked for, what was built, decisions made, blockers hit, new threads that emerged. Be honest: distinguish what's done from what's in progress.

4. **Draft updates** to these CONTEXT.md sections:
   - **Current Focus** — Update to reflect where you actually are now. One sentence.
   - **Last worked** — Today's date (YYYY-MM-DD).
   - **Completed since last update** — Concrete things finished this session. Bullet points, factual.
   - **In progress** — Things started but not finished. Be specific.
   - **Blocked on** — Anything genuinely blocked. Don't invent blockers.
   - **Open Threads** — Add new threads that surfaced. Don't remove existing ones unless they were resolved this session.
   - **Next Actions** — Refresh the ordered list. Put the immediate next thing first.
   - **Decisions Log** — Add any key decisions made this session with date and rationale.

5. **Present the proposed update.** Show what you're about to change — what's added, what's modified, what's left alone. Use a compact diff-style summary so the user can scan it.

6. **Confirm with the user before writing.** Use AskUserQuestion or a direct yes/no question. Options: "Looks good, write it" / "Let me adjust" / "Skip handoff".

7. **Write the updated CONTEXT.md** only after confirmation. Preserve the file structure — don't reformat sections that don't need changes.

8. **Confirm completion** with a one-line summary: "CONTEXT.md updated. Next session resumes at: [first next action]."

## Guardrails

- **Never invent progress.** If you're not sure something was completed, mark it in progress.
- **Don't remove user-written content** unless it's clearly resolved.
- **Don't overwrite the Decisions Log** — append new entries, never modify old ones.
- **Stay factual.** Don't add aspirational next actions that weren't actually discussed.
