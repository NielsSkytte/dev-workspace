Scaffold a new project in the DEV workspace.

Usage: /new-project [path]
Example: /new-project own/MyTool
Example: /new-project customers/Acme/DataPlatform

## Instructions

1. Parse the project path from $ARGUMENTS.
   - Must start with `own/` or `customers/`
   - If missing or invalid, ask the user where the project should live.
   - If the directory already exists, warn and stop.

## Interview

Run through these rounds. Use AskUserQuestion ONLY for actual multiple-choice questions (type, scale, language). For everything else, ask in plain text and let the user respond naturally.

### Round 1

Use AskUserQuestion for type (content vs function). Then ask in plain text:

"What does this project do and why? One or two sentences."

### Round 2

Use AskUserQuestion for these three together:
- **Scale** — spike (days, minimal) or project (weeks+, structured). Default: project.
- **Focus** — one-word sub-type. Offer 3-4 relevant examples based on the type chosen in Round 1:
  - Content examples: sales, educational, reference, handover
  - Function examples: architecture, infrastructure, notebook code, tooling
- **Language** — Danish (default) or English.

### Round 3

Ask in plain text, in a single message. Make it clear all three are skippable:

"A few quick context questions — skip any that don't apply:
1. Did this spin off from another project, or will it feed into one?
2. Your idea, team member's, or customer-driven?
3. [Function only] Core technologies? (e.g., Python, Fabric, React)"

### Round 4

Ask in plain text, in a single message. Explicitly say these can be added later:

"Last two — totally fine to skip and add later:
1. Any rules Claude should follow in this project? (e.g., 'formal tone', 'no PySpark', 'date-prefix all files')
2. Anything this project explicitly does NOT do?"

If the user says skip, move on. Don't push.

## After the interview

1. Create the project directory.

2. Copy the matching template files:
   - Content: `c:\Dev\_templates\content\CLAUDE.md` and `c:\Dev\_templates\CONTEXT.md`
   - Function: `c:\Dev\_templates\function\CLAUDE.md` and `c:\Dev\_templates\CONTEXT.md`

3. Fill in the copied CLAUDE.md with the interview answers. Leave sections empty if the user skipped them — don't invent content.

4. Set the Current Focus in CONTEXT.md to the project's purpose.

5. Add a VS Code task entry to `c:\Dev\.vscode\tasks.json`:
   - Label: `Claude · [path]` (e.g., `Claude · own/MyTool`)
   - Detail: purpose, shortened to one line
   - cwd: `${workspaceFolder}/[path]`
   - Insert before the "ADD NEW PROJECTS" comment block

6. Confirm to the user in one block:
   ```
   Project scaffolded: [path]
   Task added: Claude · [path]
   Open via: Ctrl+Shift+P → Run Task → Claude · [path]
   ```
