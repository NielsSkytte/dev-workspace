---
title: Carl Ras — move GTM's Enriched views to the generated (metadata-driven) pattern
status: cancelled
created: 2026-08-07
project: customers/Carl-Ras/datahub
owner: self
priority: normal
blocked_by:
activity: MarketoImport
fno_task:
source: handoff
---

## What
Apply the generated-`viewtransform` mechanism built for Marketo to GTM as well.

## Why
Niels, 2026-08-07, on the hand-written views: "the handwritten views are another thing we are
looking into, again lets built it separate for marketo (and gtm, again do handoff, but dont work
on it), but in the way you say generated."

## Context
Marketo now has `NB_Generate_ViewTransform_MARKETO` (`02 - Enriched/MARKETO/`), which reads
`Lakehouse_Util.marketo_columns` and issues `CREATE OR ALTER VIEW` into
`Warehouse_Enriched_MARKETO.viewtransform`, then drops any view the metadata no longer asks for.
Everything downstream is unchanged — `PL_Transform_Enriched_*` still discovers views with
`SELECT TABLE_NAME FROM INFORMATION_SCHEMA.VIEWS` and `sp_CreateTableAsSelect` still CTASes them.

To do the same for GTM: a `gtm_columns` equivalent (GTM's Raw `events` table has 21 flattened
columns, currently fixed in a `BODY_FIELDS` literal inside `NB_Raw_GTM`), and a generator
notebook. Note GTM's `Warehouse_Enriched_GTM` already carries a hand-written
`viewtransform/Views/Events.sql`, which the generator would replace.

Do not start this before the Marketo generator has run for real — the DDL path through
`notebookutils.data.connect_to_artifact` is undocumented and unproven (see
`design/MARKETO_INGEST_DESIGN.md` §5, open item 2).

## Log
- 2026-08-07 — created (handoff from the Marketo ingest build)

- 2026-08-17 — MERGED into `2026-07-16-carlras-gtm-inbound-ingest` and closed as a separate task. Its content was folded into that task verbatim; nothing dropped.
