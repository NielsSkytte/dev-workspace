---
id: eval-20260908-fabric-platform-skill-did-not-fire
ts: 2026-09-09T06:15:00Z
type: evaluative
scope: workspace
source: /log
tags: [evaluation, skill, pingala-fabric-platform, fabric, git-integration, fab-cli]
status: distilled
description: "The pingala-fabric-platform skill carries the git-not-fab-import authoring rule, and it did not fire during a session that created a notebook, a schedule and lakehouse files in a git-connected Fabric workspace with fab import. The rule was rediscovered the expensive way: the workspace read permanently Modified against the branch, an attempt to clean it deleted the item, and a portal Commit made the deletion permanent"
---

**What happened.** The session ported the DataCompare daily run into Fabric: a probe notebook, a
production notebook, a schedule and four code files uploaded to a lakehouse - all through `fab import`
and the REST API, in a workspace connected to the Matas Azure DevOps repo. The
`pingala-fabric-platform` skill owns exactly this ground and states the authoring rule (git, not
`fab import`). It never fired, and nothing in the session prompted a read of it.

**What it cost.** The imported item never matched the branch, so the workspace git panel stayed
Modified even after a portal commit. Clearing it by deleting the item and calling `updateFromGit` did
not restore the item - the API is a no-op when the workspace head already equals the remote commit -
and the owner's next portal action committed the deletion, removing the notebook and its schedule from
the branch. Recovery was a re-import from the local clone, and the item still needs a portal commit.

**Why it did not fire.** The skill's description is oriented to architecture and platform questions
("our Fabric setup", workspace structure, medallion, CI/CD). Nothing in it points at the act of
*writing an item into a workspace*, which is the moment the rule matters. A trigger phrase set around
`fab import`, "create a notebook in the workspace", "deploy to the workspace" and "git-connected
workspace" would have caught this session on its first import.

**Worth noting for the loop.** The rule was not unknown to the workspace - it is written down. The
failure was retrieval at the moment of action, which is what a skill trigger is for. This is the
second Fabric-adjacent rule this month whose cost was paid before the note was read.
