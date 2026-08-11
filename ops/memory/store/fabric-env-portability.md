---
id: fabric-env-portability
ts: 2026-08-11T09:15:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: session:7500d6dd
tags: [fabric, deployment-pipeline, notebook, pipeline, variable-library, carl-ras, datahub, portability]
status: distilled
description: "Fabric items must carry no per-environment literals; variable libraries are the environment contract and an unresolved alias kills a pipeline at submit"
---

Two failure modes found deploying `Warehouse_Enriched_GTM` + `Warehouse_Enriched_Marketo`
DEV -> TEST (Fabric-ETL Deployment pipeline, 2026-08-11). Both are general to any Fabric
estate with a multi-stage deployment pipeline, not GTM-specific.

## 1. Per-environment literals in notebook/pipeline code

`NB_Raw_GTM` resolved its **destination** with
`lakehouse.get(name="Lakehouse_Raw_GTM", workspaceId="fe4c7544…")` — the DEV workspace id.
Deployed to TEST it would have written into DEV's Raw lakehouse **and reported success**.
Silent cross-environment write, the worst class of this bug. Fixed `f3be10b` with
`runtime.context["currentWorkspaceId"]`.

- Destination (anything per-environment) -> resolve at runtime, or read from a variable library.
- Source -> pin only when the resource really is shared across environments. Carl Ras has exactly
  one: the `Landingzone` data workspace `5ec283c4-9f90-4ea9-a056-9faceb84ce25`.
- **The notebook's `default_lakehouse` META is not evidence.** The deployment pipeline *does*
  remap it (verified: TEST's copy pointed at TEST's lakehouse). Code calling `lakehouse.get()`
  with a literal never reads it. I checked the binding, called the notebook safe to run, and was
  wrong — read the code. See [[eval-2026-08-11-binding-is-not-code]].
- Portability review = grep the item for GUIDs, account for every one.

## 2. Variable libraries are the environment contract

`VL_DatastoreId`, `VL_ConnectionId`, `VL_WorkspaceId`, `VL_ModelId`, `VL_PingalaUtils`. A pipeline
binds them under aliases in its `libraryVariables` block:
`SourceLakehouseId -> VL_DatastoreId.Lakehouse_Landingzone_Marketo`.

- **An alias that cannot resolve fails the pipeline at submit**: `RequestExecutionFailed` /
  `BadRequest`, ~8 s, zero activity runs, no naming of the offending variable. Nothing in the
  message points at variable libraries.
- Cause at Carl Ras: the Marketo variables were added to DEV's libraries (commit `72a8a71`) but
  the libraries were never deployed to TEST. TEST's `VL_ConnectionId` still carried the older CVR
  name `CON-SQLLandingzone_Lakehouse_Landingzone_CVR` vs DEV's `CON-WI-SQL-…`, which dates them.
- Adding a stream = add the variables **+** deploy the libraries to every stage **+** fill that
  stage's value-set override. No override -> the default value is used; correct for a shared
  resource, wrong for anything per-environment.
- Diagnostic: when a deployed pipeline fails fast with no stated reason, diff the variable
  libraries between stages before anything else. `getDefinition` on a VariableLibrary is a 202
  LRO — poll `Location`, then `Location/result`; `fab api` does not follow it.

## Related, same session

- A Fabric **warehouse import binds cross-database three-part names at `CREATE VIEW` time**, so an
  Enriched warehouse cannot deploy into a stage where the Raw lakehouse has no tables
  (`Invalid object name 'Lakehouse_Raw_GTM.dbo.events'`). Deployment pipelines copy the lakehouse
  item, never its data.
- A **failed warehouse import leaves the item behind unpaired** (`targetItemId: null`), so the
  retry collides on display name. Delete the orphan in the target stage before redeploying.
