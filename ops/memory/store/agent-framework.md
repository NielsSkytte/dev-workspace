---
id: agent-framework
ts: 2026-05-26T15:41:37Z
type: semantic
scope: workspace
source: session:d4312c2c-133a-40da-9be4-adf97e82ea38
tags: [project]
status: distilled
description: "Agent design — 4 agents (fabric, content, architect, hr), skill=verb vs agent=role, agents carry domain knowledge across projects"
---

Five agents defined in `.claude/agents/`, named with a James Bond theme:
- **fabric** — Fabric/pipeline builder (Python over PySpark, medallion, Delta, abfss)
- **content** — document/presentation specialist (format selection, audience, tone)
- **architect** — design decisions (separation of concerns, ADRs, project boundaries)
- **M** — head of operations, dispatches agents, manages roster, flags gaps (named after MI6 spymaster)
- **Q** — quartermaster, builds and refines agents and skills (named after MI6 weaponsmith)

**Why:** Same task patterns recur across projects. Agents carry domain knowledge so it doesn't need re-explaining each session.

**How to apply:** Skill = verb (recipe, stateless, e.g. /fill-sow). Agent = role (domain expert with judgment). Agents may use skills. When a task fits an agent's domain, suggest invoking it rather than doing the work without the agent's knowledge base.

Related: [[workspace-design]], [[knowledge-flow]]
