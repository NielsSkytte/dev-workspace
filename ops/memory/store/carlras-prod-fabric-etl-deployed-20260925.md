---
id: carlras-prod-fabric-etl-deployed-20260925
ts: 2026-09-25T18:20:00Z
type: episodic
scope: project:customers/Carl-Ras/datahub
source: /log
tags: [carl-ras, fabric, prod, deployment-pipeline, schedule, connections, operation-hardening]
status: distilled
description: "Carl Ras Fabric-ETL went TEST->PROD in full on 2026-09-25 (5 warehouses; the empty GTM/Marketo shells were deleted by the owner after TargetArtifactNameConflict); PROD seed ran and identities are on the SPN, the PROD PL_MainExecution schedule came over enabled (first run Mon 2026-09-28 06:30), and two PROD connections were still missing"
---

- TEST->PROD 2026-09-25 (portal, Niels): all Fabric-ETL items incl. five warehouses. The first
  attempt returned `400 TargetArtifactNameConflict` - PROD items with TEST's names but not linked
  to them. Re-linking without deleting was offered; the owner deleted the two empty shells
  (`Warehouse_Enriched_GTM`, `_Marketo`, leftovers of the failed 09-09 deploy).
- After the deploy: PROD seed ran (`GetEnums` fails - it reads Pingala's own Key Vault and D365;
  no stage has an enums table), `NB_Metadata_Marketo` ran, identities re-stamped to the SPN.
- TEST run `9b63f26c` green 15:34-17:08 UTC: `outbound.Dataverse_Contact` 5,000 -> 46,945 (the old
  `TOP` gone); TEST within 3 % of DEV except `fact.GeneralLedgerTransactions` (+12 %).
- Open at 2026-09-25 18:20 UTC: `CON_Notebook_WI_PROD` and a WI SQL connection to PROD
  `Warehouse_Enriched_Marketo` (Niels creates them), then `VL_ConnectionId` Prod.json;
  `VL_DatastoreId` Prod.json fixed locally, not committed. The PROD `PL_MainExecution`
  schedule is ON, so the first PROD run is Monday 2026-09-28 06:30.
