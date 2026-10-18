---
id: datacompare-swa-graphql-hosting
ts: 2026-10-18T15:00:00Z
type: semantic
scope: project:customers/Matas/DataCompare
source: /log
tags: [matas, datacompare, static-web-app, graphql, rls, hosting, decision]
status: distilled
description: "DataCompare hosting (2026-10-17/18): closed Azure SWA (Standard, custom Entra sign-in, MI as federated credential), no API server; page runs JS core over Fabric GraphQL as the user; schema v5 append-only + v6 RLS; Prod released by migrate scripts (pipeline SQLDB step fails); runbook in prototype/README"
---

- **Shape:** two SWAs (UAT, Prod) both reading the Prod DB; the page runs `app/dc-core.js` + `dc-rules.js`
  (ports of dc_api.py / rules.py, 38/38 golden cases identical) over GraphQL item `GQL_DataCompare` as the
  signed-in user (MSAL, scope `https://analysis.windows.net/powerbi/api/GraphQLApi.Execute.All`).
- **GraphQL facts:** a create mutation FAILS on a table with an enabled trigger; every NOT NULL column must be
  sent on create; no lt/gte/nin filters; 10,000-row pages; introspection off. Hence append-only rows
  (accept_rule, rule_event), actor/time CHECKs, status from `dc.v_rule`.
- **Access:** roles dc_prod/dc_uat, RLS by `compare_pair.environment`; grants are not serialized to git
  (`grant_access.py`).
- **Closed page:** Matas requires it (2026-10-17) -> Standard plan, one app registration + group per app,
  user-assigned managed identity trusted as federated credential (no client secret). The app registration
  needs ID token issuance or Entra refuses the SWA sign-in (AADSTS700054). Tested end to end on leita.dk
  2026-10-18. Scripts `setup_swa.ps1` / `deploy_swa.ps1` in GFOERPDataAnalysis `swa/`; Fabric git ignores it.
- **Prod release 2026-10-18:** pipeline deploy of SQLDB_DataCompare fails (CopyOverwriteResult.GenericError,
  nothing applied); migrate_v4/v5/v6.sql applied directly; GQL item + notebook via pipeline; Prod GQL reads
  Prod DB (`0d80e0f3` in workspace ac8e1c26).
- **PowerShell gotcha:** a helper `function Az { & az ... }` calls itself (case-insensitive) -> call depth
  overflow; use `az.cmd`.
