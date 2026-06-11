Park anything in the workspace inbox so it doesn't get forgotten — a task, an idea, a question, a plain to-do. Frictionless capture: no classifying, no routing, no formatting. That's triage's job later.

Usage:
  /park [whatever you want to remember]     ← capture an item
  /park                                     ← show the current inbox

Examples:
  /park look into whether Fabric mirroring works for the Tystofte D365 source
  /park idea: a skill that auto-generates the Purpose cell for notebooks
  /park ask Niels about the PKA renewal date

## Instructions

The global inbox lives at `C:\Dev\.claude\INBOX.md`.

### If $ARGUMENTS is empty

Read `C:\Dev\.claude\INBOX.md` and show the current parked items. Don't append anything. Keep it brief — just the list.

### If $ARGUMENTS has content

This is a **capture** action. Optimise for zero friction — do NOT interview, classify, route to a project, or reformat the user's words. Capture is sacred; thinking happens at triage.

1. Read `C:\Dev\.claude\INBOX.md` (create it from the template below if it somehow doesn't exist).
2. Append a single line under the `## Parked` section, using today's date:
   ```markdown
   - [ ] YYYY-MM-DD — <the user's text, verbatim>
   ```
   - Use the real current date. Keep the user's wording — only trim a leading filler word like "remember to" or "todo:" if it's pure noise.
   - Append at the end of the existing list (most recent at the bottom).
3. Confirm in one short line, e.g. `Parked: <first few words…>`. Nothing more — don't summarise the inbox or suggest next steps.

### File template (only if the file is missing)

```markdown
# Workspace Inbox

A single, low-friction place to park anything before it gets forgotten.
Capture with `/park <whatever>`. Triaged later.

Each item: `- [ ] YYYY-MM-DD — the thing`.

---

## Parked

<!-- new items append below this line -->
```
