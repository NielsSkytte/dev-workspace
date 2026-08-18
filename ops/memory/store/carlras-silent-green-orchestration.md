---
id: carlras-silent-green-orchestration
ts: 2026-08-18T21:30:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: session:1515f867-fcac-47e5-97f0-1366fb517bfb
tags: [project, fabric, pipeline, orchestration, monitoring]
status: distilled
description: "Carl Ras: a Fabric activity whose failure is absorbed by a [Completed] successor makes its pipeline report Succeeded - CVR raw ingest was dead in TEST for 6 days behind a green nightly chain"
---

Hand-written from the session, not distilled from the raw stream (the local summarizer inverted
two of the counts - see `eval-2026-08-18-memory-summarizer-fidelity`).

## The mechanic

In a Fabric (ADF-lineage) pipeline, an activity that fails but whose failure is **handled** by a
successful downstream path does not fail the pipeline. `dependencyConditions: ["Completed"]` means
*succeeded-or-failed*, so wiring `B <= A[Completed]` makes A's failure "handled" the moment B
succeeds. The parent reports **Succeeded**.

Measured, not inferred: TEST run 2026-08-18 04:30, `PL_Execute_Raw` -> CVR **Failed**, `Raw`
activity in `PL_MainExecution` **Succeeded**, whole chain **Completed**.

## What it cost here

`PL_Ingest_Lakehouse_Raw_CVR` in TEST bound `CON-SQLLandingzone_Lakehouse_Landingzone_CVR`. That
variable had been renamed to `CON-WI-SQL-Landingzone-Lakehouse_Landingzone_CVR`; the **library**
reached TEST in the 2026-08-12 deployments and the **pipeline** did not. Selective deployments
split a rename across two items.

CVR last succeeded in TEST 2026-08-11. Failed on 08-12, 08-14, 08-17, 08-18 - and the parent
reported *Completed* on three of those four. Six days of enriched CVR and curated running green on
stale raw data, with no failed run anywhere to look at.

## The error message names the wrong variable

```
Failed to resolve variable library item '[VL_WorkspaceId|LandingZone_Workspace]
[VL_DatastoreId|Lakehouse_Landingzone_CVR] [VL_ConnectionId|CON-SQLLandingzone_...CVR]
[VL_ConnectionId|CON-SQLFabric-ETL_Lakehouse_Util] [VL_DatastoreId|Lakehouse_Util]'
ErrorCode: '10,10,10,401,10'. ErrorMessage: 'Ok,Ok,Ok,VariableNotFound,Ok'.
```

The `401 VariableNotFound` sits in slot 4 (`..._Lakehouse_Util`), which **is** present in TEST's
library. The absent one is slot 3. **Do not trust the positional mapping** - read the target
workspace's `variables.json` and diff it against the pipeline's `libraryVariables` block.

## Where the failures were being swallowed (whole project, 2026-08-18)

| Pipeline | Swallowed | Absorbed by |
|---|---|---|
| `PL_Execute_Raw` | CVR, Marketo | `Marketo <= CVR[Completed]`, `GTM <= Marketo[Completed]` |
| `PL_Execute_Enriched` | CVR | `Marketo <= CVR[Completed]` |
| `PL_Transform_Curated` | Dim, Bridge, Fact | the `[Completed]` chain to Outbound |
| `PL_Ingest_Raw_AX09/_CVR/_Marketo` | `ForEach - Ingest Tables` | `If tables updated <= ...[Completed]` |
| `PL_Ingest_Raw_Marketo` | `If tables updated` | `Raw_ExplodeActivityAttributes <= ...[Completed]` |
| `PL_ScaleProcess_SP` | `Refresh Semantic Model` | `Scale Down <= ...[Completed]` |

Propagating correctly: any activity that is a **leaf** with no `[Completed]` successor.

## The fix

Eleven `Fail` activities on `[Failed]`, one per swallowed activity (`b721df8`). Two notes that
generalise:

- A `Fail` after a `ForEach` still lets every iteration run first, so one bad table surfaces
  without cutting the run short.
- Where the `[Completed]` edge is **deliberate** (`Scale Down` must run whether or not the refresh
  worked), the `Fail` depends on **both** `X[Failed]` and the deliberate successor `[Completed]`,
  so the cleanup happens before the pipeline is allowed to fail.

## The rule

A green nightly chain is not evidence that the night was green. Before trusting a Fabric pipeline's
top-line status, walk `queryactivityruns` down through every child `pipelineRunId` - the child
runs do **not** appear as job instances of the child item, so `GET /jobs/instances` on the
sub-pipeline shows nothing and looks like it never ran.
