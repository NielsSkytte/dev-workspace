---
id: fabric-updatedefinition-skips-id-translation
ts: 2026-08-21T11:05:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
tags: [fabric, git-integration, api, deployment, pitfall]
status: distilled
description: "The git import rewrites logicalIds to object ids and a zeroed workspaceId to the real one; updateDefinition does not, so pushing a repo copy straight into a live item breaks every reference - and it returns 400 while applying the write anyway"
---

Fabric's serialised pipeline JSON is **not** what the live item holds. The repo stores
`notebookId` and ExecutePipeline `referenceName` as **logicalIds**, and `workspaceId` as
`00000000-0000-0000-0000-000000000000`. Update-from-git translates both on import. The
`items/{id}/updateDefinition` REST API does **not**.

A logicalId is the same GUID bytes in a different grouping order, so the two forms look unrelated
but are mechanically convertible: workspace `8e8d5c15-ac30-4a4a-b43a-ec2b296728d3` is git
`296728d3-ec2b-b43a-4a4a-ac308e8d5c15`.

Symptoms of pushing a repo copy directly, in the order they appear as each layer is patched:
- `Failed to get workspace details ... BadRequest` - the zeroed `workspaceId` reached the service
- `PowerBIEntityNotFound` at job start - `notebookId` is still a logicalId

**Also: `updateDefinition` returns HTTP 400 `UnknownError` for pipelines while still applying the
write.** Verified by reading the definition back after the error. Do not retry on it, and do not
assume the item is unchanged.

Reconstructing the translation by hand is the wrong instinct even when it is mechanically possible.
The route back is a normal Update from git, which repairs the item and applies the intended change
in one pass.

**Boundary that came out of this (Niels, 2026-08-21):** Claude does not run Update from git — it is
all-or-nothing across the branch and he routinely has other work in flight. The reserved thing is
the sync itself, not DEV: fixing DEV directly is fine when it is what lets a commit land, and DEV
data may be deleted where our own code regenerates it. The test for deletable is regeneration, not
importance.
