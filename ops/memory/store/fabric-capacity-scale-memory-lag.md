---
id: fabric-capacity-scale-memory-lag
ts: 2026-08-27T10:05:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: session:50082637-f235-4ee7-be0d-fd881b292a68
tags: [fabric, capacity, semantic-model, refresh, scale]
status: distilled
description: "A Fabric capacity reports the new SKU as Active before the memory is allocated, so a refresh started right after a scale-up dies on Resource Governance - and the limit is only ever readable inside the failure message"
---

Hand-written from the session.

## Measured 2026-08-21, DEV model, same day, same SKU

| time | step | result |
|---|---|---|
| 16:17:24 | modelsize Before | `CapacitySku F32`, `CapacityState Active`, `ModelSizeMb 3246.9` |
| 16:18:42 | full refresh | **Failed** `0xC13E0003`, `DbSizeBeforeMb 2645`, `MemoryLimitMb 2474`, 77 s |
| 16:40:59 | full refresh | **Completed**, 501 s |

Nothing changed but the wait. The first attempt was handed a 2,474 MB ceiling for a 2,645 MB
model - over budget before it began - roughly 6 minutes after the scale. The success was roughly
21 minutes after it.

## The trap

`CapacitySku = F32` and `CapacityState = Active` are **not** the go signal. The capacity record
flips immediately; the memory arrives later.

## Why no pre-flight gate exists

`MemoryLimitMb` and `DbSizeBeforeMb` are parsed out of the **out-of-memory message text** by
`NB_Refresh_SemanticModel_Full`. They are populated on failed log rows and blank on successful
ones. There is no way to read the limit before a refresh, so the only available fix is to retry -
`PL_ScaleProcess_SP` retry 12 x 30 s (rungs pinned to 1, each failure ~77 s),
`PL_Update_SemanticModel` retry 2 (clearValues escalation allowed, each attempt can run hours).

## Related

The model is 3,246.9 MB of which **2,094.7 MB is dictionary** - 65%. Dictionary size, not row
count, is the lever: a 31% row cut across the three big facts did not stop the OOM.
