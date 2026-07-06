---
id: agent-framework
ts: 2026-07-06T10:15:00Z
type: semantic
scope: workspace
source: session:24b948aa-4e8c-427d-9a54-bd2ffff040e6
tags: [project]
status: distilled
description: "Agent design — 7 agents (fabric-back/semantic/fabric-front + content, architect, M, Q); fabric split at the semantic model (the backend↔frontend contract); frontmatter required for invocation; skill=verb vs agent=role"
---

Seven agents defined in `.claude/agents/`, meta-pair named with a James Bond theme. The Fabric domain is split in three **at the semantic model** (2026-07-06) — the model is the contract between backend and frontend, and the collaboration surface with the frontend colleague:

- **fabric-back** — Fabric backend builder: sources → gold (pipelines, notebooks, lakehouses, warehouses, provisioning; Python over PySpark, medallion, Delta, abfss)
- **semantic** — semantic modelling specialist: relationships, DAX, Direct Lake/refresh, optimization, RLS, model docs, Prep for AI, Fabric data agents (owns the data-agent skill trio). Shared surface with the colleague who owns fabric-front — decisions go into model docs
- **fabric-front** — Power BI reports/visuals; **colleague-owned domain**, in Niels's sessions mostly review/routing/handover
- **content** — document/presentation specialist (format selection, audience, tone)
- **architect** — design decisions (separation of concerns, ADRs, project boundaries)
- **M** — head of operations, dispatches agents, manages roster, flags gaps (MI6 spymaster)
- **Q** — quartermaster, builds and refines agents and skills (MI6 weaponsmith)

**Why:** Same task patterns recur across projects. Agents carry domain knowledge so it doesn't need re-explaining each session. The fabric split happened when one agent covered non-overlapping goals (predicted by AGENTS.md > Fabric scope note).

**How to apply:** Skill = verb (recipe, stateless). Agent = role (domain expert with judgment); each agent definition lists its skill loadout. When a task fits an agent's domain, suggest invoking it. Fabric routing: data movement → fabric-back; model/measures/refresh/data agents → semantic; reports → fabric-front; cross-layer symptoms (wrong number, slow report) start at semantic, the contract owner.

**Harness lesson (2026-07-06):** agent `.md` files without YAML frontmatter (`name:` + `description:`) are just prose — the harness never registers them as invokable subagent types. Frontmatter + skill loadout + token-discipline paragraph (delegate exploration to subagents) are now mandatory in Q's format spec.

Related: [[workspace-design]], [[knowledge-flow]], [[skill-usage-evaluation]]
