---
id: pi-one-date-dimension
ts: 2026-11-25T23:59:00Z
type: semantic
scope: project:own/ProcessInsight
source: session 78a9d947 2026-11-25
tags: [process-insight, semantic-model, dates, modelling-rule]
status: distilled
description: "PI model generator: one DimDates only; active relationship on the obvious date (created/ordered, marked primary_date, onboarding asks), other dates inactive and used via USERELATIONSHIP; no per-role date tables without a stated requirement"
---

Niels, 2026-11-25: "one dimdates only, never more unless its a very specific requirement". A per-role date table pattern (R3a, date_roles in measures.yaml) was built and dropped the same day; Niels had not seen it in best practice. CROSSFILTER ( primary date, DimDates, NONE ) stays only for state-at-a-point measures (13 of 241 in Inventory to deliver). Facts with several dates also get one base count per date (R1a, `<Table> Rows by <Date>`), Niels's idea, so a date context shows each date's count. Lesson: state the source of a modelling pattern before building it (Niels asked "where did you come up with that pattern").
