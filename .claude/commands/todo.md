Capture anything into the workspace TODO list so it doesn't get forgotten — a task, an idea, a question, a plain to-do. Capture is fast and never blocked. If a capture is too thin to triage later, you get **one** optional sharpening beat — never an interview.

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

A **capture** action with a frictionless front door and a quality safety net. The two beats below are sequential and the first is unconditional — **the verbatim line always lands before anything else**, so nothing is ever lost even if the user walks away mid-thought.

#### Beat 1 — Capture verbatim (always, immediately)

1. Read `C:\Dev\ops\TODO.md` (create it from the template below if it somehow doesn't exist).
2. Append a single line under the `## Todos` section, using today's real date:
   ```markdown
   - [ ] YYYY-MM-DD — <the user's text, verbatim>
   ```
   - Keep the user's wording. Only trim a leading filler word like "remember to" or "todo:" if it's pure noise.
   - Append at the end of the existing list (most recent at the bottom).
3. Confirm in one short line, e.g. `Added: <first few words…>`.

#### Beat 2 — Sharpen, only if thin (optional, one beat, never blocking)

After capturing, apply the **thinness test** to the line:

> Does it name a **specific object** *and* carry an implied **why / for-what**?

- **Passes → stop.** Do nothing more. Most captures pass (e.g. "look into whether Fabric mirroring works for the Tystofte D365 source" — specific object, clear purpose). Do not nag a good capture.
- **Fails → one sharpening beat.** The line is vague enough that triage-you, a week later with the context gone, couldn't reconstruct the intent (e.g. "create tool for fabric" — vague object, no why). Fire **exactly one** `AskUserQuestion` prompt, framed as optional. Populate it with your **2–4 best-guess interpretations** of what the user likely meant, inferred from the wording and the current conversation/project context — each a one-click answer. The auto-provided "Other" option lets the user type detailed free input in the same prompt. So one interaction serves both a busy user (click a guess) and a precise one (write a sentence). Example shape:

  > **What about X should change?** — [best guess 1] / [best guess 2] / [best guess 3] / (Other for detail)

  - When the user picks a guess or types detail, **edit the existing line in place** to the sharper version (e.g. `create tool for fabric` → `create a Fabric pipeline-review skill`). Keep their phrasing; just fold in the specificity.
  - If the user dismisses the prompt or says "leave it" — **do nothing**. The raw verbatim line stays exactly as captured. Never re-ask, never escalate to a second question.

  This is the **one** place `/todo` is allowed to use `AskUserQuestion` — a single optional quick-pick, never a chain.

The reason this beat exists at capture time and not triage time: the context behind a thin capture is alive *now* and gone later, so one cheap question now prevents an un-triageable line later. The reason it's a single optional beat and not an interview: capture must stay frictionless — sharpening is a courtesy, not a gate.

### Guardrails

- **Beat 1 is unconditional.** Never withhold the verbatim capture pending an answer to Beat 2. The line is on disk before you ask anything.
- **One question, max.** Beat 2 is a single beat. No follow-ups, no classifying, no routing to a project, no priority — that is triage's job (`/task`), done later.
- **Bias toward silence.** When unsure whether a line is thin, treat it as passing. A missed sharpen is cheap; nagging a good capture erodes the frictionless front door.

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
