# ADR-001: Agent-Based Skill Routing Architecture

| Field       | Value                        |
|-------------|------------------------------|
| Status      | Draft                        |
| Date        | 2026-06-22                   |
| Author      | [Author]                     |
| Reviewers   | [Reviewers]                  |

---

## Context

Pingala is building an organisation-wide knowledge and automation layer on top of Claude Code. This layer consists of **skills** — structured markdown files (SKILL.md) encoding domain knowledge, patterns, and constraints — and **agents** — personas that apply those skills to specific task domains.

The skill library is expected to exceed 100 skills across domains including Fabric Infrastructure, Semantic Modelling, Delivery/Process, and Presales. Skills are developed centrally and shared across client engagements. Individual projects may require different subsets of skills, and the required subset may change as a project progresses through its lifecycle.

### Problem

Claude Code's native skill system loads all skills in `.claude/skills/` into context on every session. At scale this creates three problems:

1. **Context window pressure** — 100+ skills consume significant context budget, leaving less room for task content and conversation history.
2. **Triggering noise** — with all skills visible, Claude may activate the wrong skill or blend skills inappropriately.
3. **Coupling** — tying skills to project `.claude/` folders makes it hard to share and version them independently of projects.

A naive solution — duplicating skill files per project or per agent — creates maintenance debt and divergence across engagements.

---

## Decision

We adopt a **three-layer architecture** separating skill storage, agent definitions, and project configuration:

```
Shared Skill Library      →    Agent Definitions    →    Project CLAUDE.md
(vendor/skills-for-*/         (agents/*.md)              (lists relevant agents,
 SKILL.md files)               system prompts with        does not embed skills)
                               mandatory skill protocol)
```

### Layer 1: Shared Skill Library

Skills live in a centralised, versioned location outside any project — currently `C:\Dev\.claude\vendor\skills-for-fabric\` for Fabric skills. This path is referenced by agents, never copied into projects.

Skills are **not** installed into `.claude/skills/` on a per-project basis. The native `available_skills` auto-load mechanism is intentionally bypassed.

### Layer 2: Agent Definitions

Each agent is a self-contained markdown file (`agents/<domain>.md`) acting as a system prompt for a specific persona. Agent files contain:

- **Role and identity** — what the agent is and what it owns
- **Inline domain knowledge** — stable, high-confidence knowledge embedded directly (not loaded from files on every call)
- **Mandatory skill protocol** — explicit instruction to read relevant SKILL.md files before responding; phrased as a required pre-read step, not a suggestion
- **Skill library index** — list of available skill areas with paths, so the agent can self-direct to the right file
- **Invocation criteria** — when to activate this agent

Example mandatory skill protocol section:

```markdown
## Knowledge Base Protocol

Your skill library is at `C:\Dev\.claude\vendor\skills-for-fabric\`.

Before responding to any task, you MUST:
1. Identify which skill area(s) apply from the list below
2. Read `skills/<area>/SKILL.md` for each relevant area
3. Check `common/` for any referenced shared docs
4. Only then formulate your response

Do not rely on inline knowledge alone. Skill files contain authoritative,
up-to-date constraints and patterns. When in doubt, read the skill file.
```

This mandatory pre-read pattern is the critical enforcement mechanism. Soft suggestions ("when working on X, read Y") are insufficient — Claude will skip file reads when it feels confident from inline knowledge.

### Layer 3: Agent Index

A machine-readable registry (`agents/index.json`) enables orchestrator routing without loading all agent definitions into context simultaneously. The index is intentionally small — a few KB regardless of agent count.

```json
{
  "agents": [
    {
      "id": "fabric-infra",
      "name": "Fabric Infrastructure Agent",
      "description": "Workspace provisioning, pipelines, notebooks, lakehouse, Delta tables, REST API",
      "keywords": ["fabric", "pipeline", "notebook", "lakehouse", "delta", "deploy", "devops"],
      "definition": "agents/fabric-infra.md",
      "skills": ["sqldw-authoring-cli", "spark-authoring-cli", "e2e-medallion-architecture"],
      "model": "claude-sonnet-4-6",
      "local_eligible": false
    },
    {
      "id": "semantic-model",
      "name": "Semantic Modelling Agent",
      "description": "DAX, Power BI, TMDL, semantic layer design, measure authoring",
      "keywords": ["dax", "powerbi", "tmdl", "measure", "semantic", "report"],
      "definition": "agents/semantic-model.md",
      "skills": ["semantic-model-authoring", "powerbi-report-authoring"],
      "model": "claude-sonnet-4-6",
      "local_eligible": false
    },
    {
      "id": "delivery",
      "name": "Delivery Process Agent",
      "description": "Project delivery, documentation, templates, estimation, client communication",
      "keywords": ["delivery", "project", "estimate", "documentation", "template", "client"],
      "definition": "agents/delivery.md",
      "skills": ["delivery-templates", "estimation-patterns"],
      "model": "ollama/llama3",
      "local_eligible": true
    }
  ]
}
```

The `local_eligible` flag marks agents whose tasks are suitable for local model execution (see _Local Model Offload_ below).

### Layer 4: Project Configuration

Individual project CLAUDE.md files list which agents are relevant for that engagement. They do **not** embed skills or agent definitions inline — they reference agent files:

```markdown
## Agents

The following agents are available for this project:

- **Fabric Infrastructure**: `agents/fabric-infra.md`
- **Semantic Modelling**: `agents/semantic-model.md`

Invoke via `/fabric` or `/semantic`, or describe your task and the
orchestrator will route automatically.
```

When the required agent set changes mid-engagement (e.g. moving from build to reporting phase), only the project CLAUDE.md agent list is updated. Skill files and agent definitions remain unchanged.

---

## Invocation Model

Two invocation paths are supported:

**Explicit** — user invokes an agent directly via slash command (e.g. `/fabric`) or by stating intent. Suitable for focused sessions where the domain is known upfront.

**Orchestrated** — an orchestrator agent reads the index, scores the user's request against agent keywords and descriptions, and either auto-routes (high confidence) or presents options to the user (ambiguous). The orchestrator carries zero domain knowledge — only the index and routing logic.

The orchestrator pattern is preferred for general sessions and multi-domain tasks. It is defined in the root CLAUDE.md.

---

## Local Model Offload

Agents marked `local_eligible: true` in the index may be routed to a local LLM (e.g. Ollama) rather than the cloud API. Primary drivers are:

1. **Cost** — repetitive or low-complexity tasks (documentation generation, template filling, estimation)
2. **Privacy** — tasks involving client-sensitive data that should not leave the local network

The routing architecture is model-agnostic: the orchestrator passes task + skill paths to whichever runtime handles the target agent. The skill files themselves are identical regardless of which model consumes them.

Local model capability is a future state. Agent definitions should be written to be model-agnostic from day one (no Claude-specific syntax in skill files, no reliance on extended context beyond what a capable local model supports).

---

## Skill File Format

Skills follow the standard SKILL.md format with YAML frontmatter:

```yaml
---
name: skill-name              # kebab-case, max 64 chars
description: "..."            # triggering signal, max 1024 chars
compatibility: "..."          # optional — surfaces or tools required
license: "..."                # optional
metadata:                     # optional — free-form nested dict
  version: "1.0"
  domain: fabric
  author: [Author]
---
```

The `metadata` block is the appropriate place for versioning, authorship, and domain tagging. It is not parsed by the native skill system but is available for custom tooling.

Skills do **not** live in `.claude/skills/`. They live in the shared library and are referenced by path from agent definitions.

---

## Directory Structure

```
C:\Dev\
  .claude\
    vendor\
      skills-for-fabric\       ← Microsoft Fabric skill library (external/vendored)
        skills\
          sqldw-authoring-cli\SKILL.md
          spark-authoring-cli\SKILL.md
          semantic-model-authoring\SKILL.md
          ...
        common\                ← shared reference docs
  
  AtomicCortex\                ← or equivalent org workspace root
    CLAUDE.md                  ← root: orchestrator definition + agent index reference
    agents\
      index.json               ← machine-readable agent registry
      fabric-infra.md          ← Fabric Infrastructure Agent definition
      semantic-model.md        ← Semantic Modelling Agent definition
      delivery.md              ← Delivery Process Agent definition
      presales.md              ← Presales Agent definition
    skills\                    ← org-owned skills (non-vendored)
      delivery-templates\SKILL.md
      estimation-patterns\SKILL.md

  projects\
    <client-engagement>\
      CLAUDE.md                ← lists relevant agents only; no skills embedded
      CONTEXT.md               ← project-specific context
```

---

## Consequences

### Positive

- Skills are versioned and maintained independently of projects
- Changing the skill set for a project mid-engagement requires only updating the project CLAUDE.md agent list
- Agent definitions are portable — the same agent can be used across any number of projects
- The index enables orchestrator routing without loading all agents into context
- Architecture is LLM-agnostic; local model offload is a configuration change, not a redesign
- Context window is used efficiently — only skills relevant to the active agent and task are loaded

### Negative / Risks

- **Mandatory skill reads add latency** — each task may trigger one or more file reads before a response. Acceptable for quality, but noticeable in fast-paced sessions.
- **No native enforcement** — the mandatory pre-read protocol relies on Claude following CLAUDE.md instructions. There is no hard technical gate preventing Claude from skipping file reads in long sessions. Mitigation: keep inline domain knowledge current enough to be useful as fallback, and periodically review agent behaviour.
- **Path coupling** — agent definitions reference absolute or relative paths to skill files. If the skill library moves, agent definitions must be updated. Mitigation: use a consistent, stable root path; consider an environment variable or config entry as the library root.
- **Local model fidelity** — local models may not follow the mandatory skill protocol as reliably as Claude. Skill files and agent prompts should be tested against target local models before enabling `local_eligible`.

---

## Alternatives Considered

### A: Native `.claude/skills/` per project
All skills installed into each project's `.claude/skills/` folder. Rejected — creates duplication, maintenance debt, and coupling between skill versions and project lifecycle.

### B: Dynamic CLAUDE.md injection
Orchestrator writes a temporary CLAUDE.md at session start listing only active skills. Rejected as primary pattern — fragile, hard to debug, not portable to non-Claude runtimes.

### C: MCP server as skill router
A lightweight MCP server exposes a `list_skills(domain)` tool; agents call it to retrieve relevant skill content. Not rejected — this is the preferred long-term target architecture, particularly for local model offload. Deferred until the agent layer is stable and the value of MCP-based routing is validated.

---

## Open Questions

- [ ] Should the agent index live at the workspace root or be embedded in root CLAUDE.md?
- [ ] How do we handle skills that span multiple agent domains (e.g. a shared authentication pattern used by both Fabric and Semantic agents)?
- [ ] What is the review/approval process for adding or modifying skills in the shared library?
- [ ] At what point does the mandatory skill pre-read become a performance problem, and what is the mitigation (caching, summarisation)?
- [ ] Define the threshold criteria for `local_eligible` — complexity, data sensitivity classification, or both?

---

## Related

- CLAUDE.md hierarchy design (root → workspace → project)
- AtomicCortex agent roster (M dispatcher, Q quartermaster, domain agents)
- Skill authoring guidelines
- ADR-002: MCP Skill Router (future)
