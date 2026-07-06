Scaffold a new project in the DEV workspace through a one-question-at-a-time interview.

Usage: /new-project [path]
Example: /new-project own/MyTool
Example: /new-project customers/Acme/DataPlatform

## Core rule

**One question per message. Never more.** Ask, wait for the answer, then ask the next. Do not batch
two questions into a single prompt, ever — not even "quick ones". If you catch yourself writing a
numbered list of questions, stop and send only the first.

Use plain-text conversational questions. Do **not** use the AskUserQuestion multiple-choice tool —
the owner prefers open dialogue. State a sensible default inline in each question so it can be
accepted with one word ("yes", "default", "skip").

Spend most of the interview on **purpose**, little on classification. Classification (type, scale,
focus, language) should mostly be *inferred from the purpose conversation and confirmed*, not asked
cold.

## Step 0 — Path

Parse the path from $ARGUMENTS.
- Must start with `own/` or `customers/`. If missing or invalid, ask where the project should live.
- If the directory already exists, warn and stop.

## Step 1 — Purpose (the heart of the interview)

This is where you spend your questions. Go one at a time, and **adapt** — let each answer shape the
next question. Don't move on until you can write the project's purpose back in 2-3 crisp sentences
and the owner confirms it. Vague answers get a sharpening follow-up, not a pass.

Cover, roughly in this order (adapt to what's already been said — skip what's already clear):

1. What is this project? What are you trying to make exist that doesn't exist yet?
2. Why now — what triggered it? The pain, the opportunity, the deadline.
3. Who is it for? Who reads/uses/consumes the output, and what do they do with it?
4. What does "working" or "done" look like? How will you know it succeeded?
5. What's the smallest version that would already be useful?

Then ask any follow-up needed to remove ambiguity. When you think you have it:

> "Here's the purpose as I understand it: «2-3 sentences». Right, or adjust?"

Only proceed once that's confirmed. The confirmed text becomes the **Purpose** section and the
CONTEXT.md **Current Focus**.

## Step 2 — Classification (infer, then confirm in one message)

From the purpose conversation, infer the four classification fields and confirm them in a **single**
message as one yes/or-correct question. Don't interrogate these — they're metadata.

- **type** — `content` (a body of writing/material) or `function` (something that runs/builds).
- **scale** — `spike` (days, minimal) or `project` (weeks+, structured). Default `project`.
- **focus** — one word. Propose one based on the purpose.
  - content: sales, educational, reference, handover
  - function: architecture, infrastructure, notebook, tooling
- **language** — `da` (default) or `en`.

Example confirm message:
> "Reads to me as: **function / project / focus: tooling / Danish**. Good, or change any?"

If the owner corrects one, accept it and move on — don't re-confirm.

## Step 3 — Logistics (one at a time, skippable)

Brief, low-friction, still one question per message. State the default; "skip" is always allowed.
For `customers/...` paths, lean the defaults toward customer-driven.

1. **fno_code** — "F&O time-entry code for this project? Used by the `/time` rollup. Skip to add later."
2. **owner** — only ask if not obviously Niels; otherwise default to Niels silently.
3. **lineage** — "Did this spin off from another project, or will it feed into one? (skip if neither)"
4. **initiated_by** — "Your idea, a team member's, or customer-driven? (default: your idea / for a
   customer project: customer-driven)"
5. **stack** (function only) — "Core technologies? e.g. Python, Fabric, React. (skip to add later)"
6. **conventions** — "Any rules Claude should follow in this project? e.g. formal tone, no PySpark,
   date-prefix files. (skip — easy to add later)"
7. **out of scope** — "Anything this project explicitly does NOT do? (skip)"

If the owner says skip, move on. Never push.

## After the interview

1. Create the project directory.

2. Copy the matching template files into it:
   - Content: `c:\Dev\_templates\content\CLAUDE.md` + `c:\Dev\_templates\CONTEXT.md`
   - Function: `c:\Dev\_templates\function\CLAUDE.md` + `c:\Dev\_templates\CONTEXT.md`

3. Fill the copied CLAUDE.md from the interview answers:
   - Identity block: `type`, `focus`, `scale`, `status: active`, `owner`, `fno_code`, `lineage`
     (`from`/`to`), `initiated_by`, `language`.
   - `Purpose`: the confirmed 2-3 sentence purpose.
   - `Stack` (function), `Conventions`, `Out of Scope`: fill from answers; **leave empty if skipped —
     never invent content.**

4. Set CONTEXT.md **Current Focus** to the confirmed purpose. Set **Last worked** to today's date.

5. Add a VS Code task to `c:\Dev\.vscode\tasks.json`:
   - Label: `Claude · [path]` (e.g. `Claude · own/MyTool`)
   - Detail: the purpose, shortened to one line
   - cwd: `${workspaceFolder}/[path]`
   - Insert before the "ADD NEW PROJECTS" comment block.

6. Confirm in one block:
   ```
   Project scaffolded: [path]
   Type/scale/focus: [type] / [scale] / [focus]
   Task added: Claude · [path]
   Open via: Ctrl+Shift+P → Run Task → Claude · [path]
   ```
   Note: time for this project is tracked automatically once you open sessions rooted at its folder
   (the rollup reads `fno_code` from its CLAUDE.md). No extra registration needed.
