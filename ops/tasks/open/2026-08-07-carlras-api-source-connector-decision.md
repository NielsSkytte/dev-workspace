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
- 2026-08-31 — **VERIFIED: the gate is met.** The Marketo chain ran end to end —
  `PL_Ingest_Marketo` (LZ) Completed 2026-08-20 12:46-12:51, `PL_Ingest_Lakehouse_Raw_Marketo`
  Completed 2026-08-21 08:23-08:32, `PL_Transform_Enriched_Marketo` Completed 08:41-08:43, each
  starting after the previous stage succeeded. Nothing in the chain has run since 08-21, and the
  Marketo daily schedule is still disabled — so it is **proven once by hand, not proven as a
  repeatable schedule.**
  - **The three-source table is still accurate.** CVR: ES scroll paging, full overwrite, no
    watermark, and **still has no pipeline at all** — only bare notebooks, zero job history. GTM:
    hourly, enabled, still on its bespoke polars notebook and its own `sequence_number` watermark,
    **not** moved to the AutoLoader shell. Marketo: daily, still disabled.
  - **No fourth API source exists.** Enumerated both DEV workspaces — only AX09, CVR, GTM, Marketo.
  - **Correction to the §3.3 framing:** the *landing contract* has already generalised on its own.
    `Lakehouse_Util` carries `rawtablekeymap_{ax09,cvr,marketo}` and `AutoLoader_{AX09,CVR,Marketo}`
    on one uniform naming pattern. What is genuinely Marketo-only is *catalogue* metadata —
    `marketo_entities`, `marketo_columns`, `marketo_fieldpush_reference` — needed because Marketo's
    API surface is dynamic where AX09 and CVR have fixed shapes. That is evidence **for** the task's
    own hypothesis: the landing contract generalises, the extraction does not.
  - **Assessment, not measurement:** the decision is ripe for the landing-contract half only. Full
    connector scope still waits on GTM converging onto the shared Raw shell and on Marketo running
    unattended at least once. Niels decides.
  - **Unresolved:** no evidence found in these two repos of the separate metadata-driven Atomic
    ingest effort said to be underway elsewhere. That is a search-scope gap, not proof of absence —
    and if it lands it could make this decision moot. Worth a direct ask before committing.
- 2026-08-07 — created (handoff from the Marketo ingest build)
