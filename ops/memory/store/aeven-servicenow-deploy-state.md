---
id: aeven-servicenow-deploy-state
ts: 2026-10-04T12:00:00Z
type: semantic
scope: project:customers/Aeven/AtomicServiceNow
tags: [aeven, servicenow, deploy, git, workspace-repo, sync, variable-library]
status: distilled
description: "AtomicServiceNow ships by git: local repo is source, tools/sync_workspace_repo.py writes into the clones of dataaidemo (Pingala DEV) and MasterDataPlan (Aeven ITSM-ETL-Dev); ids per environment in config/environments.json"
---

- Pingala DEV: `NielsWorkspace_Dev` git-connected to DevOps `pingalaglobal/data and ai/dataaidemo`,
  folder `/ServiceNow`, main. Aeven DEV: `ITSM-ETL-Dev` (1fd1bd43) git-connected to
  `AutomationAIAndTools/MasterDataPlan`, folder `/`, main. Both reachable from the laptop (no VDI
  needed for git). Clones git-ignored at `AtomicServiceNow/workspace-repo/` (sparse, `ServiceNow/`
  minus Junk; a full clone fails on Windows path length) and `AtomicServiceNow/aeven-repo/`.
- Flow: generate (`build_notebooks.py`, `build_variables.py`, `build_model.py`) -> `python
  tools/sync_workspace_repo.py --repo aeven-repo [--add Item=Folder]` -> commit in the clone -> push
  (ask) -> Update from git. The sync matches items by folder name, swaps local logicalIds for the
  workspace ones, never writes .platform, definition.pbir, model `expressions.tmdl`, warehouses or
  lakehouses, and ignores designer normalisation (defaultValue "", empty parameters).
- Unpushed Aeven commits are kept in order by branching from origin/main and rebasing the waiting
  commits (Serving) on top.
- Variable libraries: default UNSET, value sets PingalaDev / AevenDev; activating one needs Save
  (a dot on the tab = unsaved; the asterisk only marks a required field).
- 2026-10-03 blocker: 8 tables return 0 rows to the Aeven integration user (counts exist) and
  sys_choice lacks name/element/value/language; access email drafted, not sent.
