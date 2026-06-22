---
id: knowledge-flow
ts: 2026-05-26T15:41:39Z
type: semantic
scope: workspace
source: session:d4312c2c-133a-40da-9be4-adf97e82ea38
tags: [project]
status: distilled
description: "Cross-project knowledge transfer via /note command and INBOX.md — solves context blending problem"
---

User context-switches frequently and projects spawn from each other mid-work. Key problem: learning something generic while doing customer-specific work, needing to feed it to another project without switching context.

Solution: `/brief ProjectPath "insight"` skill + `INBOX.md` per project.
- /brief validates scope against target project's CLAUDE.md before appending
- INBOX.md is surfaced at session start
- Entries are processed and cleared by the user

**Why:** User previously blended projects in one context, which was suboptimal. This preserves context isolation while enabling knowledge transfer.

**How to apply:** When working in a project and discovering something relevant elsewhere, suggest /note rather than switching context or noting it in the current project's files.

Related: [[workspace-design]], [[agent-framework]]
