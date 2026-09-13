---
id: fabric-tsql-empty-string-try-cast-and-datediff-big
ts: 2026-09-13T21:00:00Z
type: semantic
scope: project:customers/Aeven/AtomicServiceNow
source: /log
tags: [fabric, warehouse, t-sql, try_cast, nullif, datediff_big, enriched]
description: In a Fabric warehouse TRY_CAST('' AS DATETIME2) is 1900-01-01 and TRY_CAST('' AS BIGINT) is 0, so every cast of an API string column goes through NULLIF(col,''); DATEDIFF in seconds from 1970 overflows INT, use DATEDIFF_BIG
status: distilled
---

Measured on Aeven 2026-09-13: ServiceNow sends `''` for an unset field. The generated Enriched
views cast with `TRY_CAST([col] AS type)` and resolve hours came out as -60 years because `''`
became 1900-01-01 and 0. Fix in `src/snow_enriched.py`: `TRY_CAST(NULLIF([col], '') AS type)` for
every non-text type; BIT via CASE on 'true'/'false'. Glide durations (datetime offset from
1970-01-01) become seconds with `DATEDIFF_BIG(SECOND, '1970-01-01', col)`; plain `DATEDIFF`
overflows. `EXEC [schema].[proc]`, never `EXEC [schema.proc]`.
