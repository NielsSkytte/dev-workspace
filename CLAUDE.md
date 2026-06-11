# DEV — Global Workspace

## Owner
Solo workspace. All work is business-oriented — development, content, strategy, and customer delivery.
Default audience: Danish, unless overridden in project CLAUDE.md.

---

## Folder Structure

```
DEV/
├── CLAUDE.md              ← you are here (global rules)
├── _templates/            ← project scaffolding (content/, function/)
├── .vscode/               ← tasks.json for project switching
├── .claude/
│   ├── agents/            ← agent definitions (fabric, content, architect, M, Q)
│   ├── commands/          ← slash commands (/brief, /handoff, /park, /task, etc.)
│   ├── skills/            ← Agent Skills (folder per skill, SKILL.md + assets)
│   ├── INBOX.md           ← workspace capture inbox (/park) — ICOR Input
│   └── tasks/             ← workspace task store (/task) — ICOR Output; open/in-progress/done/cancelled
├── customers/
│   └── [client]/
│       └── [project]/
└── own/
    └── [project]/
```

**Two buckets — the only rule is delivery obligation:**
- `customers/` — someone external is waiting for output
- `own/` — discretionary work, no external obligation

---

## Every Project Must Have

| File | Purpose |
|---|---|
| `CLAUDE.md` | Project identity, type, rules, lineage |
| `CONTEXT.md` | Live state — current focus, open threads, next actions |

These two files are the context-switching primitive. Always keep CONTEXT.md current.

Optional:
| File | Purpose |
|---|---|
| `INBOX.md` | Cross-project knowledge feed — written by `/brief` from other sessions |

---

## Project Types

Two primary types, declared as `type:` in project CLAUDE.md:

| Type | What it produces |
|---|---|
| `content` | Documents — wiki, slides, Word, markdown, presentations |
| `function` | Executable things — pipelines, notebooks, scripts, APIs, tools |

The `focus:` field in the Identity block provides the sub-classification (e.g., `sales`, `educational`, `architecture`, `notebook code`). The Purpose section elaborates.

### Scale

| Scale | Use |
|---|---|
| `spike` | Days. Quick experiment or exploration. Minimal docs. |
| `project` | Weeks+. Structured work. Full CLAUDE.md + CONTEXT.md. |

Spike graduation rule: if a spike spans multiple sessions or develops significant structure, prompt to upgrade to project scale.

---

## Identity Block

Every project CLAUDE.md starts with:

```yaml
## Identity
type: content | function
focus:
scale: spike | project
status: active | paused | delivered | archived
owner: own | customers/[client]
lineage:
  - from:
  - to:
initiated_by: self | team | [name]
language: da | en
```

---

## Agents

Five agents are available from any project. Agents are roles with domain knowledge — they make judgment calls, not just follow steps.

| Agent | Role | Invoke when |
|---|---|---|
| **fabric** | Fabric/pipeline/infrastructure builder | Building in Microsoft Fabric ecosystem |
| **content** | Document and presentation specialist | Creating structured documents, presentations, SoWs |
| **architect** | Design decision maker | Architecture choices, project structure, ADRs |
| **M** | Head of operations — dispatches agents, manages the roster | "M, do we have someone for this?" or "M, we need to hire a new agent" |
| **Q** | Quartermaster — builds and refines agents and skills | "Q, build me an agent for X" or when M identifies a gap |

Agent definitions live in `.claude/agents/`. Reusable capabilities live in two places depending on form:

| Form | Location | How it runs |
|---|---|---|
| **Slash command** | `.claude/commands/<name>.md` | A single markdown file. You invoke it explicitly by typing `/<name>` (e.g. `/brief`, `/handoff`). |
| **Agent Skill** | `.claude/skills/<name>/SKILL.md` | A folder holding `SKILL.md` (with `name`/`description` frontmatter) plus any supporting scripts/assets/templates. Claude auto-invokes it when the description matches the task. |

Reach for a **slash command** when it's a short recipe you trigger on demand. Reach for an **Agent Skill** when it carries domain knowledge or supporting files and should fire automatically by context (e.g. `pingala-visual-identity`, `azure-devops-backlog`).

**Skill vs Agent:** A skill is a verb — a recipe for a specific task. An agent is a role — a domain expert with knowledge and opinions. Agents may use skills.

## Evaluating new constructs

A skill, command, or agent must justify its existence. When I propose creating one, challenge me before agreeing.

| Construct | Axis | Core challenge |
|---|---|---|
| **Skill** | depth | What does the LLM get wrong today without it? Show the failure. |
| **Command** | repeatability | Which inputs change between runs? What structure stays fixed? |
| **Agent** | scope | What decision does it make mid-task that earlier results would change? |

These are three different axes, not three stages on one scale. A gap on any axis pushes toward a different construct.

**Don't confuse the skill axis (depth) with the command axis (repeatability).** A skill is justified by a *demonstrated* failure — one concrete instance where the LLM got it wrong without the knowledge is sufficient. It does NOT need to recur first; "it's only happened once / it's a one-off" is a repeatability argument and belongs to the command decision, not the skill decision. If you catch yourself deferring a skill because it hasn't happened twice yet, you're applying the wrong test.

**Graduation signals — when one is growing into another:**
- Skill repeatedly reloaded with parameters → may be a command
- Command with conditional branches on earlier output → may be an agent
- Agent whose role has split into two distinct goals → decompose into specialists

**Behavioural triggers:**
- When I significantly correct your output, pause and ask whether the correction should become a new skill, modify an existing skill, become a command, or trigger a new specialist agent. Route the answer to Q.
- **When you auto-correct your own work mid-task and the fix revealed a non-obvious failure mode, treat that as the depth evidence a skill needs — surface it and propose capturing it.** The failure already happened; you don't get to wait for it to happen again. (See the depth-vs-repeatability note above.)
- At the end of a working session, ask whether any of what we covered should become a skill, command, or new specialist agent.

## Fabric scope note

Fabric is OS-scale (pipelines, notebooks, lakehouse, warehouse, semantic models, real-time intelligence, governance, Power BI). A single `fabric` agent may grow too broad. When fabric-domain work reveals distinct goals with non-overlapping knowledge, raise to M whether a new specialist should be spawned rather than further loading `fabric`.
---

## Knowledge Flow

Projects spawn from and feed into each other. Two mechanisms:

1. **Lineage** (in Identity block): tracks where a project came from and what it serves
2. **INBOX.md** + `/brief` skill: cross-project knowledge transfer without context switching

Workflow:
- Working in Project A, discover something relevant to Project B
- `/brief ProjectB "the insight"` — validated against B's scope, appended to B's INBOX.md
- When opening Project B, Claude surfaces inbox entries first

---

## Guardrails

Claude Code must enforce these across all projects:

1. **No root-level drift** — flag any file or folder created directly under `DEV/` that is not in the defined structure above.
2. **CONTEXT.md freshness** — at the end of any session where meaningful progress was made, prompt to update `CONTEXT.md` before closing.
3. **Lineage tracking** — never delete the lineage field, even if empty.
4. **Type conformance** — if a project's work diverges significantly from its declared type, flag it and ask before proceeding.
5. **Spike graduation** — if a spike project spans multiple sessions or develops significant structure (multiple subfolders, growing file count), prompt: *"This spike may be ready to graduate to project scale. Want to expand its scaffolding?"*
6. **Notebook Purpose cell** — every Fabric notebook carries a `## Purpose` synthesis as its **first cell**: a short, general statement of what it does and where it sits in the flow (not step-by-step detail). Create it when authoring; **update it only on major functional changes** (new/removed outputs, changed role, restructured logic) — *not* on bug fixes or minor tweaks. In Fabric `notebook-content.py` this is a markdown cell — `# MARKDOWN ********************`, then markdown lines each prefixed with `# `, placed after the notebook-level `# METADATA` block and before the first `# CELL`. Applies to all notebook work under `C:\Dev`.

---

## Starting a New Project

1. Decide: `customers/[client]/[project]` or `own/[project]`
2. Copy `_templates/[type]/` into the target location
3. Claude interviews you to fill in the CLAUDE.md (the template is a minimal scaffold — the interview adds project-specific detail)
4. Create CONTEXT.md from template
5. Add a task entry to `.vscode/tasks.json`
6. Open Claude Code via the new task

---

## Switching Projects

Use **VS Code Tasks** (`Ctrl+Shift+P` → `Tasks: Run Task`) to launch Claude Code in a project.
Each project has a dedicated task that opens a named terminal panel rooted at the project folder.
This ensures Claude Code picks up the correct CLAUDE.md chain: project → DEV root.
