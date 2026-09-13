---
id: servicenow-zurich-basic-auth-role-and-api-facts
ts: 2026-09-13T21:00:00Z
type: semantic
scope: project:customers/Aeven/AtomicServiceNow
source: /log
tags: [servicenow, zurich, rest, basic-auth, sys_dictionary, sys_audit, aeven]
description: On ServiceNow Zurich a Basic-auth API user needs role snc_basic_auth_api_access (401 with a correct password otherwise); table columns come from sys_dictionary with inheritance via sys_db_object.super_class, and the dictionary lists columns the Table API never returns
status: distilled
---

Aeven ServiceNow POC, measured on the Zurich PDI (2026-09-12/13):

- Basic auth on the REST API is refused (401) unless the user holds `snc_basic_auth_api_access`
  (or OAuth2 client credentials are used). The user's time zone must be GMT for delta windows.
- Column catalogue: `sys_dictionary` rows for the table plus every ancestor along
  `sys_db_object.super_class`; ~3-5 dictionary columns per table (`rejection_goto`, `variables`,
  `cab_date`, ...) are never in the Table API response, so views may only reference what landed.
- `sysparm_display_value=false`, labels from `sys_choice` (concrete table, then `task`);
  transactional history from `sys_audit` / `sys_audit_delete` filtered by `tablenameIN...`;
  the Stats API gives counts; ACL-hidden rows make counts differ on `sys_dictionary`.
- Never the native Fabric ServiceNow connector (Niels).
