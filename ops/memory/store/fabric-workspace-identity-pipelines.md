---
id: fabric-workspace-identity-pipelines
ts: 2026-11-16T22:00:00Z
type: semantic
scope: workspace
source: session a2dfd1df (PDI proof in NielsWorkspace_Dev)
tags: [fabric, pipelines, workspace-identity, conditional-access, aeven]
status: distilled
description: "Fabric pipelines on a workspace identity: which activities work (proved 2026-11-16), Power BI REST 403 for a WI, Semantic model refresh activity works, LSROBOTokenFailure fixed by re-save"
---

- **LSROBOTokenFailure / AADSTS53000** (Aeven DEV, 2026-11-16): a pipeline runs on a refresh token
  stored when someone last saved it, bound to that device. A trivial edit (description) and save
  from a compliant device makes it run again (Microsoft pipeline troubleshooting guide).
- **Proved on the PDI, job `7d6a2eca`:** full `PL_MainExecution` Completed as the workspace
  identity. Notebook activity with a Notebook WI connection; InvokePipeline (InvokeFabricPipeline)
  on a FabricDataPipelines WI connection; warehouse Lookup/stored procedure through a SQL Server
  WI connection; lakehouse Files through ADLS Gen2 on OneLake; Semantic model refresh activity
  (`PBISemanticModelRefresh`) on a PowerBIDatasets WI connection. Tool: room `tools/run_identity.py`.
- **Power BI REST (`api.powerbi.com/v1.0/myorg/...`) answers 403 to a workspace identity token**,
  even `/groups`, with "Service principals can call Fabric public APIs" on in the Pingala tenant.
  The Fabric REST API (`api.fabric.microsoft.com/v1/workspaces/{ws}/semanticModels`) answers 200.
- **Tenant setting:** Microsoft docs: service principals and managed identities need "Service
  principals can call Fabric public APIs" for Fabric REST, and WI access to semantic models needs
  it. Not tested with the setting off (skipped 2026-11-16).
- `credentials.getToken('pbi')` in a notebook run on a WI connection returns the WI's app token.
