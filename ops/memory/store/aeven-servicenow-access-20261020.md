---
id: aeven-servicenow-access-20261020
ts: 2026-10-23T12:00:00Z
type: semantic
scope: project:customers/Aeven/AtomicServiceNow
tags: [aeven, servicenow, acl, access, paging, conditional-access, fabric-api]
status: distilled
description: "Aeven access state after run 20261020T080536Z; Fabric API blocked from the laptop by Aeven CA (compliant device), checks run in-workspace; full loads page to the stats count"
---

- Aeven tenant `eae82d0e-...`: az token request fails AADSTS53000 (Conditional Access requires a
  compliant Intune device); sign-in frequency 8 h (AADSTS70043). Fabric API at Aeven is not reachable
  from the laptop. Workaround: a read-only Python notebook cell in `ITSM-ETL-Dev` reading
  `Lakehouse_Landingzone_ServiceNow` `ingest_log` + mirrors (failed/empty tables, landed < count,
  columns empty in every row); Niels runs it and pastes the output.
- Run `20261020T080536Z` (full, no errors): sys_choice all fields (17,979 rows). Still blocked:
  `sys_dictionary.internal_type` empty in all rows (filled on the PDI, so access, not data),
  `alm_asset` stats count 0, empty fields on 13 tables. sys_audit / sys_audit_delete not called
  (`enabled: false`); their access error is from the 10-03 test. 13 tables land fewer rows than counted.
- Aeven's first reply (by 10-23): many empty fields may be unused in test. Does not explain
  internal_type or the audit tables; could explain alm_asset (count 0).
- Paging (decision 2026-10-20, `e499775` / MasterDataPlan `c783d94`): full loads page with
  `RANGE:0:<count+page_size>:<page_size>` from the stats count, no end condition; delta keeps
  `EndCondition:$.result Empty`. Inference, not proven: an ACL-filtered page can be empty with
  readable rows after it, so the Empty stop may cause part of the row gaps. Not run yet at Aeven.
- Gotcha: re-rendering with `tools/build_notebooks.py` overwrites `PL_MainExecution` `.schedules`
  with `MAIN_SCHEDULE` (Cron 60, disabled); the committed daily 06:00 (`2311b39`) must be restored
  or the generator fixed.
