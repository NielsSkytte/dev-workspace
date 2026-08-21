---
id: fabric-refresh-telemetry-is-empty
ts: 2026-08-20T16:00:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: session:8374f87e-2a3d-4166-8017-4515139d44c8
tags: [fabric, semantic-model, refresh, telemetry, rest-api, dax]
status: distilled
description: "A Fabric semantic-model refresh reports nothing about what it cost - executionMetrics comes back as an empty array from every endpoint - so measure the model with the storage DMVs instead, and those run only over executeDaxQueries"
---

Hand-written from the session.

## The enhanced-refresh API returns no metrics

`GET /v1.0/myorg/groups/{g}/datasets/{d}/refreshes/{id}` documents
`refreshAttempts[].executionMetrics` with `durationMs`, `totalCpuTimeMs`, `vertipaqTotalRows` and
`approximatePeakMemConsumptionKB`. Measured against Carl Ras DEV on 2026-08-19/20, on the last four
refreshes, successful and failed alike, it comes back as:

```json
"refreshAttempts": [{"attemptId": 1, "startTime": "...", "endTime": "...", "executionMetrics": []}]
```

**An empty array.** The same on `GET .../refreshes` (the history list), which carries the identical
`RefreshAttempt` schema. Microsoft documents the field and states **no condition** under which it
populates; an empty array is not documented anywhere.

No other REST route carries it either, all checked on Learn:

- Fabric Job Scheduler `ItemJobInstance` - only `status`, `startTimeUtc`, `endTimeUtc`,
  `failureReason`. No CPU, memory or rows.
- Fabric SemanticModel Items API - has **no refresh operation at all**; `sempy` and the Data Factory
  *Semantic model refresh* activity both wrap the same Power BI API.
- `/myorg/admin/capacities/{id}/refreshables` - `averageDuration` and `medianDuration` in seconds,
  aggregated over a window. No memory, no size, no rows.

The portal's refresh-detail page (`app.powerbi.com/groups/{ws}/datasets/{ds}/refreshdetails/{id}`)
now shows the execution metrics **without Log Analytics**, so the server holds them. Nothing
documented returns them.

## What the same payload does give you

- `startTime` / `endTime` - a real server-side duration, no zone suffix at the top level but both
  from the same clock.
- `objects[]` with per-table status, **published while the refresh is still running** (41 objects,
  statuses moving). The `asynchronous-refresh` page shows this; the REST reference's in-progress
  sample does not. The reference sample is at `NotStarted`, which is why it has no array.
- `numberOfAttempts`, `messages[]` (warnings included).

## Measure the model instead - and only over executeDaxQueries

Rows and VertiPaq footprint are reachable post-refresh from the storage DMVs:

| Function | Gives |
|---|---|
| `INFO.STORAGETABLES()` | `ROWS_COUNT` per table |
| `INFO.STORAGETABLECOLUMNSEGMENTS()` | `USED_SIZE`, `ALLOCATED_SIZE` |
| `INFO.STORAGETABLECOLUMNS()` | `DICTIONARY_SIZE` |

`USED_SIZE + DICTIONARY_SIZE` is Microsoft's own definition of semantic model size. Filter
`TABLE_ID` starting `H$` or `R$` - those are the engine's hierarchy and relationship structures, not
model tables. Carl Ras DEV, 2026-08-20: 3,212 MB (used 1,174 + dictionary 2,039), 27,722,911 rows
across 41 tables, collected in under 3 seconds.

**Two traps, both measured:**

1. `executeQueries` answers **HTTP 400 "Failed to execute the DAX query"** for every `INFO.STORAGE*`
   function - as a service principal and as a user. Its reference page still says *"MDX, INFO
   functions and DMV queries are not supported"*. Note `INFO.VIEW.COLUMNS()` **does** work there
   (841 rows) - `INFO.VIEW.*` is a normal DAX expression usable in calculations, the storage ones
   are DAX-query-only and need **write permission** on the model.
2. `executeDaxQueries` takes a single `query` **string** where `executeQueries` takes a `queries`
   **array**. Post the array shape and it returns an **empty Arrow stream with HTTP 200** - not an
   error. It is Premium/Fabric only and needs the XMLA tenant setting; the response is Arrow IPC,
   so `pyarrow.ipc.open_stream` it.

This is the model's resident footprint, not the refresh's peak memory. Peak memory has no
non-trace, non-Log-Analytics, non-workspace-monitoring source.

## The one number that only a failure gives you

The effective **per-model memory ceiling** appears nowhere in any API - only inside the
out-of-memory message, as `memory limit N MB` next to `database size before command execution M MB`,
where `N + M` is the SKU ceiling. So log the capacity SKU separately (ARM) if you want to know what
a run actually got.
