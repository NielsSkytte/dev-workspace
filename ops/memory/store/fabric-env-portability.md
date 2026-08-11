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

**Estate sweep done 2026-08-11.** Four code-level hits, all Marketo, three notebooks — fixed in
`147b13e`: `NB_Raw_ExplodeActivityAttributes_Marketo` (`raw_workspace_id`),
`NB_Metadata_Marketo` (`util_workspace_id`), `NB_Generate_ViewTransform_Marketo`
(`warehouse_workspace_id`, `util_workspace_id`). The explode notebook is an *activity inside*
`PL_Ingest_Lakehouse_Raw_Marketo`, so every TEST run of that pipeline was writing
`activity_attributes` into DEV. AX09, CVR and the `Util/Code` notebooks are clean — their only
matches are the META binding line the deployment pipeline rewrites. No item-level GUIDs are
hardcoded anywhere in code, only workspace ids.

**Fix pattern** where the id sits in a PARAMETERS CELL: keep the parameter, default it to `""`,
and resolve after the imports —
`util_workspace_id = util_workspace_id or runtime.context["currentWorkspaceId"]`. Deliberate
cross-workspace targeting stays possible; the wrong default goes away. (`notebookutils` is not
imported yet inside a parameters cell, so the resolution cannot live there.)

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
- **`Lakehouse_Util` is a data-carrying dependency, not just an item.** The house ingest reads
  `Lakehouse_Util.rawtablekeymap_<source>` on every run, and the deployment pipeline copies the
  lakehouse item without it. `PL_Ingest_Lakehouse_Raw_Marketo` failed in TEST with
  `[TABLE_OR_VIEW_NOT_FOUND] Lakehouse_Util.rawtablekeymap_marketo`. Cure: run
  `NB_Table_PrimaryKeyMap_<source>` once per environment before the first ingest — its own header
  says so. Standing up a source in a new stage therefore means seeding `Lakehouse_Util`
  (`rawtablekeymap_*`, and for Marketo also `marketo_entities` / `marketo_columns` from
  `NB_Metadata_Marketo`) as well as the Raw lakehouse.
