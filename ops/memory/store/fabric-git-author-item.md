---
id: fabric-git-author-item
ts: 2026-08-01T12:40:00Z
type: procedural
scope: workspace
source: session:11777a94
tags: [fabric, git, cicd, notebook, devops, platform, serialization, matas]
description: "Create a Fabric workspace item from git instead of the UI: the .platform v2 folder shape, logicalId, and why a plain .py in the repo is invisible to Fabric"
status: distilled
---

When a workspace is git-connected, you can author an item **in the repo** and have Fabric
create it on **Update from Git** - no clicking in the UI, no paste. Useful whenever the repo
is the declared home for solution code.

## The trap

A plain `.py` (or `.sql`, `.json`) committed to the repo is **invisible to Fabric**. It is
just a file. Fabric only recognises an item as a directory:

```
<DisplayName>.Notebook/
  .platform            <- required
  notebook-content.py  <- the item definition
```

## .platform (version 2)

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
  "metadata": { "type": "Notebook", "displayName": "NB_Name", "description": "..." },
  "config":   { "version": "2.0", "logicalId": "<guid>" }
}
```

- `type` is **case-sensitive**; do not improvise it.
- A v2 directory has `.platform` and must NOT also contain the v1 pair
  (`item.metadata.json` + `item.config.json`).
- `logicalId` is the cross-workspace identity key. MS Learn: it is generated "when the
  workspace is connected to a Git branch **or a new item is synced**", so omitting it works -
  but authoring a fresh GUID is deterministic and matches what Fabric itself writes.
  **Never copy an item directory without changing it** - duplicate logicalIds block commits
  and updates (this is the single most common git-integration error in the troubleshooting doc).

## What Update from Git actually does

Fabric matches an incoming definition to a workspace item by **displayName + item type**.
No match -> it **creates** the item. This is why a branch holding item definitions can
deploy a whole solution into an empty workspace.

## Practical notes

- Get the format from a **working repo**, not from docs - `Carl-Ras/datahub` has real
  serialised notebooks (`Landingzone-ETL/CVR/NB_Ingest_CVR_polars.Notebook/`).
- Python (not PySpark) notebook: `kernel_info.jupyter_kernel_name: python3.12`, cells tagged
  `language_group: jupyter_python`.
- Cell separators in `notebook-content.py` are literal: `# CELL ********************`,
  `# MARKDOWN ********************`, each followed by a `# METADATA` / `# META {...}` block.
- Guardrail 6 still applies: first cell is a `## Purpose` markdown cell.
- Check the connection before assuming: `fab api "workspaces/<id>/git/connection"` returns
  branch, directoryName, `gitConnectionState` and the synced `head`. Cheaper than asking.
- Git folder placement decides the workspace folder. `fab mkdir` puts data items at the
  workspace ROOT and `fab ls` hides folders entirely - move via `fab api` before committing.

See [[fabric-warehouse-ddl-pyodbc]] for the other "drive Fabric from outside the UI" route.
