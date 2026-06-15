Capture anything into the workspace TODO list so it doesn't get forgotten — a task, an idea, a question, a plain to-do. Frictionless capture: no classifying, no routing, no formatting. That's triage's job later.

Usage:
  /todo [whatever you want to remember]     ← capture an item
  /todo                                     ← show the current TODO list

Examples:
  /todo look into whether Fabric mirroring works for the Tystofte D365 source
  /todo idea: a skill that auto-generates the Purpose cell for notebooks
  /todo ask Niels about the PKA renewal date

## Instructions

The workspace TODO lives at `C:\Dev\ops\TODO.md`.

### If $ARGUMENTS is empty

Read `C:\Dev\ops\TODO.md` and show the current open items. Don't append anything. Keep it brief — just the list.

### If $ARGUMENTS has content

This is a **capture** action. Optimise for zero friction — do NOT interview, classify, route to a project, or reformat the user's words. Capture is sacred; thinking happens at triage.

1. Read `C:\Dev\ops\TODO.md` (create it from the template below if it somehow doesn't exist).
2. Append a single line under the `## Todos` section, using today's date:
   ```markdown
   - [ ] YYYY-MM-DD — <the user's text, verbatim>
   ```
   - Use the real current date. Keep the user's wording — only trim a leading filler word like "remember to" or "todo:" if it's pure noise.
   - Append at the end of the existing list (most recent at the bottom).
3. Confirm in one short line, e.g. `Added: <first few words…>`. Nothing more — don't summarise the list or suggest next steps.

### File template (only if the file is missing)

```markdown
# Workspace TODO

The workspace's low-friction action capture (ICOR Input).
Capture with `/todo <whatever>`. Triaged into `ops/tasks/` later.

Each item: `- [ ] YYYY-MM-DD — the thing`.

---

## Todos

<!-- new items append below this line -->
```
