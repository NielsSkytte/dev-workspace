---
id: fabric-deployment-copies-enabled-schedules-and-prod-lakehouse-endpoints-mwc
ts: 2026-09-09T21:00:00Z
type: semantic
scope: workspace
source: /log
tags: [fabric, deployment-pipeline, schedule, prod, lakehouse, sql-endpoint, mwc-token, carl-ras, operation-hardening]
status: distilled
description: "Two PROD facts measured at Carl Ras 2026-09-09: a TEST->PROD deployment brought an ENABLED weekly schedule for PL_MainExecution into PROD in TEST's own 06:30 slot, which would have fired the first PROD chain run ever alongside TEST's; and every PROD lakehouse SQL analytics endpoint refuses every query with 'Retrieval of MWC token used for accessing storage failed' while the PROD warehouses answer, which blocks counting raw and any cross-database read of raw from the enriched warehouses"
---

**Schedules travel with a deployment, enabled.** After the 10:37 TEST->PROD deployment the PROD
`PL_MainExecution` had schedule `c55ea6b0`, weekly Mon-Fri 06:30 Romance Standard Time, enabled, the
same as TEST's `16fb5ff0`. Disabled through the Job Scheduler API (PATCH the schedule with
`enabled: false` and the same configuration). Check schedules after every deployment to PROD. TEST's
"04:30 UTC" runs are this 06:30 Copenhagen slot.

**PROD lakehouse endpoints.** `Lakehouse_Raw_AX09`, `Raw_CVR`, `Raw_Marketo` and `Util` in the PROD
workspace `cf1a5ca2` answer every SQL query with `42000 ... Retrieval of MWC token used for accessing
storage failed with error 0xa`, from a laptop with Niels's token and from a Fabric notebook alike,
before and after data was loaded. The PROD warehouses count fine. Inference: the endpoints cannot
obtain a OneLake token. Consequence: no row count for raw in PROD, and the enriched warehouses'
cross-database reads of raw will fail the same way. Carl Ras platform ticket; nothing in the repo
fixes it.

**Also learned tonight.** `PL_Ingest_Lakehouse_Raw_Marketo` reads `Lakehouse_Util.rawtablekeymap_marketo`,
which only `NB_Table_PrimaryKeyMap_Marketo` writes, by hand, once per environment; PROD had never had
it. A pipeline whose last modifier is a person runs on that person's refresh token, and Conditional
Access can kill it (`AADSTS530036`); `tools/fabric_identity.py --only pipelines --apply` re-stamps it
to the SPN in one call, and the TEST Marketo ingest ran clean three minutes later.
