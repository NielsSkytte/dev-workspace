---
id: eval-2026-11-25-processinsight-skills
ts: 2026-11-25T23:59:00Z
type: evaluative
scope: project:own/ProcessInsight
source: session 78a9d947 2026-11-25
tags: [skills, fabric-warehouse-git, fabric-deployment, semantic-model]
status: distilled
description: "ProcessInsight 2026-11-25: no Fabric skill was read; Fabric first-deploy behaviour (logicalId reuse after delete, new-warehouse connection timing) was learned live and belongs in fabric-deployment"
---

Skills in play: none auto-fired; the fabric index was loaded earlier in the session but no SKILL.md was read for the fresh deploy. Two findings belong in fabric-deployment: (1) after deleting items in a git-connected workspace and committing the deletions, Update from git silently skips recreating items with the same logicalIds; (2) a warehouse created by Update from git needs its SQL connection created before its pipelines run. Microsoft skills-for-fabric semantic-model-authoring and data-goblin power-bi-agentic-development were reviewed into docs/research (GPL repo: ideas only).
