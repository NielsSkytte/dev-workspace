Brief another project — send a cross-project note to its INBOX.md without switching context. Supports both quick one-liners and richer structured briefs.

Usage:
  /brief [ProjectPath] [message]              ← quick one-liner
  /brief [ProjectPath]                        ← structured brief (interview)
  /brief [ProjectPath] --rich [message]       ← structured brief starting from a message

Examples:
  /brief own/MetaAtomic "Oracle needs DBMS_METADATA fallback for limited-privilege scenarios"
  /brief own/MetaAtomic
  /brief own/MetaAtomic --rich "Oracle DBMS_METADATA fallback"

## Instructions

### Step 1 — Parse and validate the path

Parse the target project path from $ARGUMENTS.
- Must resolve to a directory under `c:\Dev\` (e.g., `own/MetaAtomic` or `customers/Tystofte/PowerPortal`)
- If the path doesn't exist, list matching project names and ask the user to clarify.

### Step 2 — Determine the mode

- **Quick mode** — if a message was provided and `--rich` was not specified, use quick mode.
- **Structured mode** — if no message was provided, or `--rich` was specified.

### Step 3 — Read the target project's CLAUDE.md

Understand the target project's purpose, focus, and scope. This is needed for validation in both modes.

### Step 4 (quick mode) — Validate and append

Validate the note:
- Is it relevant to the target project's declared purpose and focus?
- Is it actionable (specific enough to act on later)?
- If off-scope, push back: explain why and suggest a better target if one exists.

If valid, format and append to the target project's INBOX.md (create the file if needed):

```markdown
### YYYY-MM-DD — from [source project path]
- [the note content]
```

If INBOX.md already has an entry for the same date and source, append under that heading instead of creating a duplicate.

Confirm to the user: "Briefed [project name]: [brief summary]" — keep it short.

### Step 4 (structured mode) — Interview and append

Ask the user, in plain text (all skippable except the insight itself):

1. **Insight** (required) — "What's the insight or update?"
2. **Context** (optional) — "Why does this matter for [target project]? Skip if obvious."
3. **References** (optional) — "Any specific files, sections, or commits to point to? (e.g., `framework/normalize_staging.py:45` or a doc path)"
4. **Suggested agent** (optional) — "Which agent should process this when the project picks it up? (fabric / content / architect / skip)"

After the interview, format and append to INBOX.md:

```markdown
### YYYY-MM-DD — from [source project path]

**[insight headline]**

[context paragraph if provided]

References:
- [file path or section]
- [file path or section]

Suggested agent: [agent name]
```

Omit sections that were skipped — don't include empty headings or "N/A".

Confirm to the user: "Briefed [project name] with structured note: [insight headline]"

### Step 5 — Stay in context

After the brief lands, you remain in the source project. Don't switch context. Don't read the target project's other files unless the user asks.

## Guardrails

- **INBOX.md only.** Never modify the target project's CONTEXT.md, CLAUDE.md, or any other file.
- **Scope validation matters.** If a note is off-scope, push back before writing. A bad inbox entry creates noise the user has to clean up later.
- **One brief per insight.** Don't bundle unrelated insights into one brief — encourage separate calls if the user tries to.
- **Don't read source project files** to enrich the brief unless the user provided specific references.
