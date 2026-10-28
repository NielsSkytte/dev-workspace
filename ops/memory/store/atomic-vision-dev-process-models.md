---
id: atomic-vision-dev-process-models
ts: 2026-10-28T19:30:00Z
type: semantic
scope: project:customers/Carl-Ras/process-insight
source: session:80a43015
tags: [process-insight, atomic-vision, fabric, git]
status: distilled
description: "Atomic Vision - Dev (4e7cb5f8, ADO pingalaglobal/data and ai/atomicvision, main, /) holds Inventory to deliver, Case to Resolution and Process Insight Coverage in 02 - Assets/Semantic Models; data stays in NielsWorkspace(_Dev) via Direct Lake on OneLake; changes only by branch + PR"
---

- Workspace `Atomic Vision - Dev` 4e7cb5f8-c8b9-4e2c-9602-46fed6dc8cad, Pingala tenant, git-connected to
  `pingalaglobal / data and ai / atomicvision`, branch `main`, directory `/`. Local clone `C:\Dev\pingala\atomicvision`.
- Repo rule (Mads's PLAN): every change on its own branch, merged after review, nothing committed
  directly to `main`. Merging a PR without review is blocked by the auto-mode classifier: ask Niels per PR.
- Layout: models in `02 - Assets/Semantic Models/`, reports in `02 - Assets/Reports/` (report
  `definition.pbir` byPath `../../Semantic Models/<name>.SemanticModel`).
- Data stays where it is (Niels, option B): the models are Direct Lake on OneLake and read
  Warehouse_Curated in NielsWorkspace / Warehouse_Curated_Dataverse in NielsWorkspace_Dev across
  workspaces (same region, West Europe). Verified: refresh Completed and queries return rows.
- After Update from git, Fabric may rewrite a report definition (import normalisation); commit it back
  from the workspace (Selective commitToGit), as Mads does.
- PRs 913-916 merged 2026-10-28. The coverage report uses Mads's Theme Test theme (AV-OJD) unchanged.
