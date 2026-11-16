---
id: aeven-system-tables-lakehouse-util
ts: 2026-11-16T13:16:00Z
type: semantic
scope: project:customers/Aeven/AtomicServiceNow
source: session 37ad8ee1
tags: [aeven, servicenow, design, decision]
status: distilled
description: "Decision 2026-11-16 (room 5041596): system tables out of config, in Lakehouse_Util, loaded first; sys_dictionary delta or full via system_full; landed mode, fields/exclude_fields, weekly full reload removed"
---

Niels's aim: Aeven's operations staff extend ingestion themselves (add a table from a
sys_dictionary-validated list, include/exclude columns, default all) without being able to break the
system tables. Built 2026-11-16 (room `5035d4a`..`60ce613`, dataaidemo `7b8281c`):
`sys_db_object`, `sys_choice` (full) and `sys_dictionary` (delta; full when named in the
`system_full` parameter or absent) are fixed in code and load first into Lakehouse_Util;
`PL_Ingest` order is system tables, `NB_Metadata`, other tables. Column choice lives only in
`servicenow_columns`, from `sys_dictionary`. Removed: `catalogue_source`/`landed` mode,
`KNOWN_COLUMNS`, `fields`, `exclude_fields`, `full_reload_weekday`. About 2,400 lines out, 1,050 in.
