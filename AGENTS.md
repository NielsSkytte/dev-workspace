# AGENTS.md — Tool-Neutral Source of Truth

This workspace is **LLM-agnostic**. Any capable LLM, pointed at this folder, must be able to operate it. This file — not `CLAUDE.md` — is the canonical, complete description of how the workspace works. Tool-specific files (`CLAUDE.md`, `GEMINI.md`, …) are thin bootstraps that point here.

## Owner & audience

Solo workspace. All work is business-oriented — development, content, strategy, and customer delivery. Default deliverable audience is **Danish**, unless a project overrides it in its own identity.

## Governing principle: LLM-agnostic substrate; harness is a non-load-bearing accelerator

1. **Substrate is portable.** All durable content — knowledge, inbox, tasks, decisions (ADRs), conventions — is plain markdown in tool-neutral locations, readable and usable by any LLM with no special harness.

2. **Harness is an accelerator, never load-bearing.** Tool-specific features (Claude Code slash commands & skills, `CLAUDE.md`, MCP servers, scheduled agents) are permitted *only* to speed up operations that are also fully described in plain prose — here, or in the relevant README. Remove the harness and the operation must still be performable by hand.

   **Portability is about *capability and knowledge*, not *determinism and triggering*.** Auto-triggers — hooks, scheduled agents, anything that fires on its own — are permitted accelerators. They may add what prose cannot: a guarantee that a routine runs, and an automatic trigger to run it. But they must hold **no decision logic or knowledge** that isn't also written in this substrate; a hook is a dumb executor of a documented routine, never the source of one. Test: porting to another LLM may lose *automation* (the routine now runs only when the LLM acts on the instruction), never *capability* (the routine is still here, still doable by hand). If a hook script contains a rule you'd lose by deleting it, that rule was welded to the tool — move it here.

3. **Acid test.** Delete every tool-specific file (`.claude/`, `CLAUDE.md`, …) and point a bare LLM at this folder + `AGENTS.md`: everything must remain intact and operable. If deleting the harness loses knowledge or capability, that capability was wrongly welded to the tool — fix it.

4. **Permitted exception — bootstrap / initialization.** Tool-specific *initialization* is fine: a thin `CLAUDE.md` / `GEMINI.md` that tells the tool to read this file; MCP / credential setup; command definitions that merely wrap operations already documented in prose. **Bootstrap may be tool-specific; the system it boots may not.**

### Why this matters here

This is the **tool-portability** half of the AtomicCortex portability constraint, applied to the whole workspace (not just AtomicCortex): *structure is the asset, the LLM is a replaceable worker.* It is what makes a future Claude→Gemini switch — or offloading parts to a local LLM — nearly free.

## Folder structure

```
DEV/
├── AGENTS.md              ← tool-neutral source of truth (this file) — read first
├── CLAUDE.md              ← Claude Code bootstrap → points here
├── _templates/            ← project scaffolding (content/, function/)
├── ops/                   ← cross-project operating substrate (LLM-agnostic)
│   ├── TODO.md            ← workspace action capture (ICOR Input)
│   ├── tasks/             ← workspace task store (ICOR Output): open/ in-progress/ done/ cancelled/
│   ├── log/sessions.md    ← session log (ICOR Refine); continuity across sessions
│   └── memory/            ← memory substrate (Storage/Injection/Recall + skill-eval): store/ daily/ README.md
├── customers/
│   └── [client]/[project]/
├── own/
│   └── [project]/
├── .vscode/               ← tasks.json for project switching (Claude/VS Code accelerator)
└── .claude/              ← Claude harness (accelerators, not load-bearing): agents/, commands/, skills/
```

Everything under `ops/`, `customers/`, `own/`, `_templates/` is the portable substrate. `.claude/` and `.vscode/` are tool-specific accelerators — deletable without losing knowledge or capability (per the acid test).

## The two buckets

The only rule separating them is **delivery obligation**:

- `customers/` — someone external is waiting for output.
- `own/` — discretionary work, no external obligation.

## Projects

**Every project must have two files** — together they are the context-switching primitive:

| File | Purpose |
|---|---|
| `CLAUDE.md` | Project identity, type, rules, lineage |
| `CONTEXT.md` | Live state — current focus, open threads, next actions. **Keep it current.** |

Optional: `INBOX.md` — cross-project knowledge feed, written by the `/brief` routine from other sessions.

(The per-project `CLAUDE.md` filename is a convention inherited from the harness; its *content* — the identity block below — is portable knowledge any LLM can read.)

### Project types

Declared as `type:` in the project's identity block:

| Type | Produces |
|---|---|
| `content` | Documents — wiki, slides, Word, markdown, presentations |
| `function` | Executable things — pipelines, notebooks, scripts, APIs, tools |

The `focus:` field sub-classifies (e.g. `sales`, `educational`, `architecture`, `notebook code`); the Purpose section elaborates.

### Scale

| Scale | Use |
|---|---|
| `spike` | Days. Quick experiment. Minimal docs. |
| `project` | Weeks+. Structured work. Full `CLAUDE.md` + `CONTEXT.md`. |

**Spike graduation:** if a spike spans multiple sessions or develops significant structure (multiple subfolders, growing file count), prompt to upgrade it to project scale.

### Identity block

Every project's `CLAUDE.md` starts with:

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

## Agents — the roster

Five agents (roles, not scripts) are available from any project. An agent is a **role with domain knowledge** that makes judgment calls — not just a checklist.

| Agent | Role | Invoke when |
|---|---|---|
| **fabric** | Fabric/pipeline/infrastructure builder | Building in the Microsoft Fabric ecosystem |
| **content** | Document and presentation specialist | Creating structured documents, presentations, SoWs |
| **architect** | Design decision maker | Architecture choices, project structure, ADRs |
| **M** | Head of operations — dispatches agents, manages the roster, runs the continuity loop | "M, do we have someone for this?" / "M, we need to hire an agent" |
| **Q** | Quartermaster — builds and refines agents and skills | "Q, build me an agent for X" / when M identifies a gap |

The Claude harness implements these as definitions in `.claude/agents/`; another LLM would express the same roles its own way. The roster and what each role decides is the portable part.

## Building new capabilities — skills, commands, agents

Reusable capability takes three forms. In the Claude harness these are concrete constructs; the **rubric for whether to create one** is portable thinking that applies under any LLM.

| Form | Is | Runs |
|---|---|---|
| **Skill** | a *verb* — a recipe carrying domain knowledge + supporting files | auto-invoked when its description matches the task |
| **Command** | a short recipe you trigger on demand | invoked explicitly (e.g. `/brief`, `/log`) |
| **Agent** | a *role* — a domain expert with knowledge and opinions; may use skills | dispatched for judgment-heavy work |

### Each construct must justify its existence — challenge before creating

| Construct | Axis | Core challenge |
|---|---|---|
| **Skill** | depth | What does the LLM get wrong today without it? Show the failure. |
| **Command** | repeatability | Which inputs change between runs? What structure stays fixed? |
| **Agent** | scope | What decision does it make mid-task that earlier results would change? |

These are three different axes, not three stages on one scale. A gap on any axis pushes toward a different construct.

**Don't confuse the skill axis (depth) with the command axis (repeatability).** A skill is justified by a *demonstrated* failure — one concrete instance where the LLM got it wrong without the knowledge is enough. It need NOT recur first; "it's only happened once" is a repeatability argument and belongs to the command decision. If you defer a skill because it hasn't happened twice, you're applying the wrong test.

**Graduation signals — one growing into another:**
- Skill repeatedly reloaded with parameters → may be a command.
- Command with conditional branches on earlier output → may be an agent.
- Agent whose role has split into two distinct goals → decompose into specialists.

**Behavioural triggers:**
- When the user significantly corrects output, pause and ask whether the correction should become a new skill, modify an existing one, become a command, or trigger a new specialist agent.
- When you auto-correct your own work mid-task and the fix revealed a non-obvious failure mode, treat that as the depth evidence a skill needs — surface it and propose capturing it. The failure already happened; don't wait for a repeat.
- At session end, ask whether anything covered should become a skill, command, or new specialist.
- **Skill evaluation feeds this.** When a skill should have fired and didn't, or fired unhelpfully, log it as an evaluative memory record (`type: evaluative`); periodically review accumulated observations (see *Memory* > Evaluation) and turn repeated signals into concrete skill edits.

### Fabric scope note

Fabric is OS-scale (pipelines, notebooks, lakehouse, warehouse, semantic models, real-time intelligence, governance, Power BI). A single `fabric` agent may grow too broad. When fabric work reveals distinct goals with non-overlapping knowledge, raise whether a new specialist should be spawned rather than further loading `fabric`.

## Knowledge flow

Projects spawn from and feed into each other. Two mechanisms:

1. **Lineage** (in the identity block): tracks where a project came from (`from:`) and what it serves (`to:`).
2. **`INBOX.md` + the `/brief` routine:** cross-project knowledge transfer without switching context.

Workflow: working in Project A, you discover something relevant to Project B → brief it to B (validated against B's scope, appended to B's `INBOX.md`) → when you next open B, its inbox entries surface first.

`ops/TODO.md` (workspace action capture) is distinct from a project's `INBOX.md` (its curated incoming-knowledge feed).

## Continuity loop

The workspace remembers across sessions through three plain-markdown artifacts in `ops/`, plus a routine M follows:

- `ops/TODO.md` — raw action capture (ICOR **Input**). Anything to act on later. (`/todo`)
- `ops/tasks/` — tracked work, state-by-folder: `open/ → in-progress/ → done/ | cancelled/` (ICOR **Output**). (`/task`)
- `ops/log/sessions.md` — chronological record of what happened/decided each session (ICOR **Refine**). (`/log`)

**Session start is context-scoped — read where you are, then surface what's open there:**

- **Workspace root (`C:\Dev`)** → the *workspace walk*: read `ops/tasks/in-progress` and `ops/tasks/open`, the unchecked items in `ops/TODO.md`, and the latest `ops/log/sessions.md` entry; surface open work and suggest a focus.
- **Inside a project (`customers/…` or `own/…`)** → the *project walk*: read that project's `CONTEXT.md` (plus any "Related contexts" it names) and surface unread `INBOX.md` entries before the first request. The workspace store is not re-walked here — the project is the frame.

**Session end — the log:** append a dated entry to `ops/log/sessions.md` — what was done, decided (link ADRs), tasks created/moved, and next focus — and distill the day's raw memory stream (`ops/memory/daily/`) into curated records (`ops/memory/store/`). See *Memory*.

This routine is tool-neutral: any LLM pointed at this folder can run it by reading the files — the scope is just "which folder did the session start in." The Claude harness only *accelerates* it: a `SessionStart` hook in `C:\Dev\.claude` fires the workspace walk automatically at root and emits the memory snapshot (it does not cascade, so it is naturally root-only), the cascading `CLAUDE.md` carries the project-walk rule into every project session, and `/todo` / `/task` / `/log` wrap the file edits. Remove the harness and the walk is still fully described here for any LLM to do by hand. Owned by M.

## Memory

A dedicated **memory substrate** lives at `ops/memory/` — distinct from the continuity loop's action/work/narrative artifacts. It does four jobs (the Storage/Injection/Recall framing plus an evaluative layer):

- **Storage** — every turn is captured as a raw record in `ops/memory/daily/YYYY-MM-DD.md`; durable keepers are distilled into `ops/memory/store/*.md` (raw->distilled mirrors TODO->tasks).
- **Injection** — at session start a capped (~1.3k token) snapshot of identity + behavioral preferences + key knowledge is surfaced.
- **Recall** — search `store/` then `daily/` by keyword; cite the source file, and say so plainly when nothing matches.
- **Evaluation** — skill observations (`type: evaluative`) accumulate and distill into skill edits: the workspace judging its own tools.

Every record carries one shape (`id, ts, type, scope, source, tags, status`) — markdown now, a database row when scale demands it (any index is rebuildable from the markdown, which stays the source of truth; `scope` is present from day one so a future team "company brain" is a tag-and-filter, not a re-architecture). The full spec and the **by-hand recipe for each job** live in **`ops/memory/README.md`** — that file plus the markdown records are the entire system, runnable by any LLM with no harness.

The Claude harness accelerates it: a `Stop` hook (`capture_turn.py`) writes the per-turn record; the `SessionStart` hook (`build_snapshot.py`) emits the snapshot; `/log` distills the day. Native Claude auto-memory is **disabled** (`autoMemoryEnabled: false` in `.claude/settings.json`) so `ops/memory/` is the single home. Owned by M.

## Conventions

- **A referenced customer always has a project.** The moment work references a customer with no folder under `customers/<Customer>/`, scaffold at least a **placeholder** project (`CLAUDE.md` + `CONTEXT.md` from the templates, fields inferred from context and marked `PLACEHOLDER`, plus a VS Code task entry) before proceeding — don't leave the work orphaned at workspace level or block on a full interview. The placeholder is a stub to be fleshed out later via the `/new-project` interview, not a finished project. This keeps every customer obligation anchored to a real project home. (Decided 2026-06-15 during a `/task` triage that named "Melbye" with no project.)

- **Scripts are ASCII-only.** Anything this workspace executes under Windows PowerShell 5.1 — `SessionStart` hooks, `.ps1` files, any script PS parses — must use ASCII punctuation: plain `-` (not `—`), straight quotes (not `“ ” ‘ ’`), `...` (not `…`). PS 5.1 reads BOM-less UTF-8 as Windows-1252, where an em-dash's bytes decode to a smart quote `”` that the tokenizer treats as a string delimiter, silently corrupting the parse. (Found 2026-06-15: the session-start hook had this latent bug and never ran.) Encoding-proof alternative if non-ASCII is unavoidable: save as UTF-8 *with* BOM. ASCII-only is simpler — prefer it.

- **Offer the commit-to-test at the moment it unblocks the next step.** When local changes have reached the point where committing + pushing is the *prerequisite for the next action* — running or testing them where pushed code is consumed (a Git-synced Fabric workspace via *Source control -> Update*, a CI run, a deploy, a cross-repo handoff) — proactively offer to commit and push *then*, phrased as a prompt the user approves. Don't push silently, and don't sit on a finished change waiting to be told. **The user's explicit OK is always required before any commit/push.** This is not a "checkpoint every change" rule — ordinary in-progress saves are not auto-offered; the trigger is specifically "a push is what unblocks testing / deploy / handoff." Generic across all projects and agents; owned by M. (Decided 2026-06-15: a Fabric notebook edit sat uncommitted, so Fabric had no update to test.)

## Guardrails

The operating LLM must enforce these across all projects:

1. **No root-level drift** — flag any file or folder created directly under `DEV/` that is not in the folder structure above.
2. **CONTEXT.md freshness** — at the end of any session with meaningful progress, prompt to update the project's `CONTEXT.md` before closing.
3. **Lineage tracking** — never delete the lineage field, even if empty.
4. **Type conformance** — if a project's work diverges significantly from its declared `type:`, flag it and ask before proceeding.
5. **Spike graduation** — if a spike spans multiple sessions or grows significant structure, prompt to graduate it to project scale.
6. **Notebook Purpose cell** — every Fabric notebook carries a `## Purpose` synthesis as its **first cell**: a short, general statement of what it does and where it sits in the flow (not step-by-step detail). Create it when authoring; **update it only on major functional changes** (new/removed outputs, changed role, restructured logic) — *not* on bug fixes or minor tweaks. In Fabric `notebook-content.py` this is a markdown cell (`# MARKDOWN ********************`, then markdown lines each prefixed with `# `), placed after the notebook-level `# METADATA` block and before the first `# CELL`. Applies to all notebook work under `C:\Dev`.
7. **LLM-agnostic substrate** — durable content (knowledge, inbox, tasks, ADRs, conventions, **memory**) stays as plain markdown in tool-neutral locations; tool-specific harness (slash commands, skills, `CLAUDE.md`, hooks) is a non-load-bearing accelerator only. Tool-specific bootstrap/initialization is permitted. Auto-triggers (hooks, scheduled agents) are permitted accelerators — they may add automation and determinism, but no decision logic or knowledge that isn't also in the substrate. Acid test: deleting `.claude/` + `CLAUDE.md` must lose no knowledge or capability. (Full statement: Governing principle, above.)
8. **Continuity loop** — session start is context-scoped (workspace walk at root, project walk inside a project); session end offers a session-log entry. The Claude harness accelerates this via the `SessionStart` hook (root) and the cascading `CLAUDE.md` (project walk); the routine itself is in *Continuity loop*, above. Owned by M. The **memory substrate** (Storage/Injection/Recall + skill-eval) is a peer system at `ops/memory/` — see *Memory*.
9. **Scripts are ASCII-only** — any script run under Windows PowerShell 5.1 must use ASCII punctuation (see *Conventions*, above).

## Working with projects

**Starting a new project:**
1. Decide the home: `customers/[client]/[project]` or `own/[project]`.
2. Copy `_templates/[type]/` into the target location.
3. Interview the owner to fill in `CLAUDE.md` (the template is a minimal scaffold; the interview adds project-specific detail).
4. Create `CONTEXT.md` from the template.
5. Register a project entry (in the Claude harness: a `.vscode/tasks.json` task that launches rooted at the project folder).

**Switching projects:** open the session rooted at the project folder so the context chain resolves project → workspace root. In the Claude harness this is a VS Code Task per project; under another tool, simply start the session in that folder.

## Status

Founding principle recorded 2026-06-11. Substrate relocated out of the harness folder to `ops/` (TODO capture + task store + session log) the same day. **2026-06-15: Part 2 complete — all workspace conventions migrated from `CLAUDE.md` into this file; `AGENTS.md` is now the full operational doc a bare LLM can run from, and root `CLAUDE.md` is a thin Claude bootstrap pointer.**
