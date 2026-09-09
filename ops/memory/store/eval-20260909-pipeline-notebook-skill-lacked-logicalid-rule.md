---
id: eval-20260909-pipeline-notebook-skill-lacked-logicalid-rule
ts: 2026-09-09T12:30:00Z
type: evaluative
scope: workspace
source: /log
tags: [evaluation, skill, fabric-pipeline-notebook, fabric-rename-entity, git-integration, pipeline, logicalId]
status: distilled
description: "A pipeline hand-written in a git-serialized Fabric repo referenced its notebook by the workspace item id; Update from git failed with a missing SynapseNotebook dependency. The skill that fires on the task (fabric-pipeline-notebook) had no git-serialization content, and the skill that held the rule (fabric-rename-entity) only triggers on renaming. Q extended the first skill with the rule and a mandatory grep of a sibling item"
---

**What happened.** The main session filled `PL_UpdateLineage` in the Carl Ras `Fabric-ETL` repo with
one `TridentNotebook` activity and set `notebookId` to the id the Fabric REST items API returned.
Fabric's update from git failed: `Missing Dependencies ... ArtifactType: 'SynapseNotebook'`. The
right value is the logicalId in the notebook's `.platform` file, which every other pipeline in the
same repo already used. Fixed in one commit, `cc78d52`.

**Why nothing caught it.** `fabric-pipeline-notebook` matched the task phrasing almost word for
word but had nothing on `.platform`, `logicalId` or `pipeline-content.json`. `fabric-rename-entity`
states the rule, but all its triggers are about renaming. No skill said "never the workspace item
id". The junctions were checked and were not the cause.

**Fix.** Q extended `fabric-pipeline-notebook`: triggers on hand-editing pipeline definitions and
on the failure text, the rule with the all-zero same-workspace `workspaceId`, and a required check
whose second step is to grep a sibling pipeline in the repo and match its pattern. `fabric-back`'s
skill table names the rule; M's Performance Log has the row. Committed `b7d215c`.

**Also a verification miss.** Both facts were on screen, the sibling's `notebookId` and the
notebook's `.platform`, and were not cross-checked. The skill now makes that check a step, which
is the general lesson: when writing a reference by hand into a serialized repo, copy a sibling's
pattern before trusting an id from an API.
