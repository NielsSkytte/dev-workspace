---
id: fabric-notebook-token-identity
ts: 2026-08-11T18:30:00Z
type: semantic
scope: workspace
source: /log
tags: [fabric, spn, identity, notebook, api]
status: distilled
description: "A pipeline-triggered Fabric notebook's token comes from Fabric's internal token service — its appid is not the SPN's app registration; /v1.0/myorg refuses it, /v1/* accepts it, and testing with your own minted token gives a false pass"
---

Verified 2026-08-11 at Carl Ras, after a day spent on the wrong hypothesis.

A notebook run triggered by a pipeline (or the Job Scheduler API) does **not** get a token
for the service principal's app registration. It gets one from **Fabric's internal token
service**: the `appid` claim is a different application id entirely, and the token carries
`scp` with no `roles`.

Consequences:

- **`/v1.0/myorg/*` (Power BI compat) refuses that token — 403 with an empty body.**
  `/v1/*` (Fabric API) accepts the same token, one line apart in the same cell.
- **A 403 with an empty body from `/v1.0/myorg/*` is not a permissions problem.** The SPN
  was workspace Admin throughout, and `/v1/workspaces/{id}` succeeded concurrently.
- **Testing with your own minted token gives a false pass.** An externally minted
  client-credentials token for the *same* principal succeeds where the notebook's internal
  one fails. This is what makes the failure so persistently misdiagnosed as ownership or
  tenant settings.
- **semantic-link is only partly usable.** Microsoft supports a documented subset under the
  default token service; `refresh` is not on it, nor is anything reaching XMLA. Name
  resolution (`list_workspaces`, `resolve_workspace_name`) routes through the Power BI
  endpoint and 403s.

**The fix:** mint your own token from an SPN secret in Key Vault
(`notebookutils.credentials.getSecret` -> client credentials -> the endpoint), or use a
`/v1/*` equivalent and mint nothing. Reference implementation:
`Fabric-ETL/Util/Code/NB_Refresh_SemanticModel_Full.Notebook`.

The `fabric-deployment` skill previously recorded semantic-model ownership as the leading
hypothesis for this 403. That was wrong and is now corrected (`a297aa5`).
