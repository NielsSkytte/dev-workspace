Gracefully close a session — always prompts whether to run /handoff and /log before ending.

Usage: /exit

## Instructions

1. Check if the current session involved meaningful work in a project (under `customers/` or `own/`).
2. Ask the user two questions (can answer together):
   - "Want to run /handoff to update CONTEXT.md for this project?"
   - "Want to run /log to append a session-log entry (this also distills today's memory stream into the store)?"
3. If yes to /handoff — run the /handoff routine.
4. If yes to /log — run the /log routine.
5. If no to both — confirm the session is closed with no updates.

The goal is to make sure no meaningful session ends without the user actively choosing to skip continuity updates.
