---
id: carlras-marketo-bulk-allocation-shared
ts: 2026-09-09T15:00:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: session:session_01VVkv3Dm4Aerpg1xZFDu2cU
tags: [project, marketo, ingest, bulk-extract, quota, impact]
status: distilled
description: "The Marketo 500 MB/day bulk-extract allocation is shared with Impact's Fivetran; our NB_Ingest_Marketo budgets 450 of it as if we owned it, and our export_log shows two days that could have starved Impact (08-09 1,735 MB, 08-20 500 MB) and nothing since - so a limit hit on 09-07 was not ours"
---

Benno (Impact), 2026-09-09 via Niels: "the limit of 500 has been reached a few times recently". Inference (his words were only "the limit of 500"): the 500 MB/day bulk-extract allocation.

- Our spend (`Lakehouse_Landingzone_Marketo.dbo.export_log`, SQL endpoint host `...ysb4exuqt6uu5icwt6woxbgoeu`): 08-07 10 MB, 08-09 1,735 MB, 08-10 42 MB, 08-11 7 MB, 08-20 500 MB, nothing after. No local extract after 08-20 either (`out/marketo_calls/` newest 08-20).
- 09-06/07 ruled out: every Marketo-named pipeline/notebook run across all 15 Fabric workspaces since 09-04 was checked; only `NB_Generate_ViewTransform_Marketo` in TEST at 05:30 UTC, which makes no Marketo call.
- `daily_budget_mb = 450` in `NB_Ingest_Marketo` must drop to a share before the inbound schedule is re-enabled; the activities guard (`activity_type_ids`) is still not implemented.
- The screenshot Niels showed for 09-07 is an Azure Logic Apps run history (identifier `08584...CU99`), daily 02:36 local = 00:36 UTC, failed in 1.19 s on 9/7; gap in runs 08-20 to 09-01, re-created 09-02. Not visible in the Carl Ras subscription we can see. Owner and error text to ask Benno.
- Detail: `datahub/design/MARKETO_INGEST_DESIGN.md` section 10.
