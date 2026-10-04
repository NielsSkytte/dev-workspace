---
id: servicenow-acl-zero-rows-vs-stats-count
ts: 2026-10-04T12:00:00Z
type: semantic
scope: global
tags: [servicenow, acl, table-api, stats-api, ingest, sys_dictionary]
status: distilled
description: "ServiceNow: the stats API counts rows the Table API will not return; 0 rows landed with source_count > 0 means row-level read ACLs, missing columns mean field-level ACLs"
---

- Measured at Aeven (test instance, 2026-10-03): sys_dictionary count 230,517 / returned 0;
  core_company 505/0, change_request 3,610/0, problem 796/0, sc_req_item 5,794/0, sc_request 5,632/0,
  sc_task 779/0, sys_db_object 7,492/7,400. sys_choice returned only label, sys_id, sys_domain,
  sys_domain_path. The copy succeeds (HTTP 200, `{"result":[]}`), so nothing fails by itself.
- Inference: `stats/<table>` aggregates ignore record ACLs; the Table API applies row and field ACLs.
  The fix is on the customer side (read ACLs, or a role such as personalize_dictionary for
  sys_dictionary).
- AtomicServiceNow logs such a load as `status = Empty` in ingest_log (rows_landed 0, no mirror), and
  NB_Metadata falls back to a mirror-based catalogue when sys_dictionary is empty.
- Separate symptom: a page whose `result` is a string ("Transaction cancelled: maximum execution time
  exceeded") is the REST transaction quota; a smaller page_size (incident 2000) avoids it.
