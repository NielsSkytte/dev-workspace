---
title: Carl Ras — decide the "connector" abstraction for API sources (CVR / GTM / Marketo) vs Atomic
status: open
created: 2026-08-07
project: customers/Carl-Ras/datahub
owner: architect
priority: normal
blocked_by:
activity: MarketoImport
fno_task:
source: handoff
---

## What
Decide whether API-based sources get a shared **connector** abstraction that plugs into Atomic,
or stay hand-shaped per source.

## Why
Niels, 2026-08-07: "the ideal setup will be one where we create a 'connector' for things like
cvr, gtm, marketo and that they then plug into atomics structure, but we should not do this
blindly (remember atomic was built for FnO)."

Three API sources now exist and no two land the same way:

| Source | Landing mechanism | Watermark | Run by |
|---|---|---|---|
| CVR | ES scroll paging, full overwrite every run | none | hand |
| GTM | Event Hub Capture blobs via a OneLake shortcut | file log + date lookback | hourly pipeline |
| MARKETO | Bulk Extract job cycle (create/enqueue/poll/fetch) | job log keyed on exportId | daily pipeline (disabled) |

The Raw layer downstream of them is uniform (AutoLoader + SCDMerger) — for AX09, CVR and now
Marketo. GTM is the exception and is handed off separately.

## Context
The constraint that makes this a real decision rather than a refactor: **Atomic was designed for
F&O**, where the source is a Delta table with Change Data Feed and the shape is uniform. An API
source has none of that — it has auth, paging, rate/volume ceilings, job lifecycles, and a
different incremental key per entity. What generalises is probably the *landing contract*
(one Delta table per entity, all columns as text, an idempotent job log, audit columns), not the
extraction.

Related and unsettled: `design/MARKETO_INGEST_DESIGN.md` §3.3 put the Marketo metadata tables in
`Lakehouse_Util` deliberately separate from the existing AX09/CVR tables, because AX09 and CVR
are close to production. Where metadata-driven configuration should actually live is part of the
same larger decision.

Do not start until the Marketo chain has run end to end — the whole point is to generalise from
something proven, not from a design.

## Log
- 2026-08-07 — created (handoff from the Marketo ingest build)
