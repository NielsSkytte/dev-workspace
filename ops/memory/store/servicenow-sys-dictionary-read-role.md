---
id: servicenow-sys-dictionary-read-role
ts: 2026-11-16T16:30:00Z
type: semantic
scope: project:customers/Aeven/AtomicServiceNow
source: session a5817e48
tags: [servicenow, acl, sys_dictionary, delta]
status: distilled
description: "PDI dev443926: svc_fabric_oauth (itil, snc_read_only, personalize_choices) counts 154,011 sys_dictionary rows but reads ~51 and gets 403 on a sys_updated_on filter; personalize_dictionary fixes both"
---

Found 2026-11-16 on the PDI. With `itil`, `snc_read_only`, `personalize_choices`, the stats API
returns 154,011 for `sys_dictionary`, the Table API returns almost no rows (full load landed 51),
and `sysparm_query=sys_updated_on>=...` returns 403 "Field(s) present in the query do not have
permission to be read" (so the delta fails; the pipeline logs Skipped and keeps the old copy).
Read ACLs on `sys_dictionary` / `sys_dictionary.*` accept `personalize_dictionary`, `admin`,
`analytics_viewer` and others. Granting `personalize_dictionary` (also grants write) to
`svc_fabric_oauth` made rows and the `sys_updated_on` filter readable. Aeven's integration user
needs an equivalent role, or the column catalogue is partial and the delta fails.
