---
id: carlras-prod-first-deploy-gaps-20261010
ts: 2026-10-10T18:30:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: /log
tags: [carl-ras, fabric, prod, deployment, variable-library, marketo, semantic-model, operation-hardening]
status: distilled
description: "Carl Ras PROD PL_MainExecution never ran green after the 09-25 TEST->PROD deploy; the causes were first-deploy gaps a deployment does not carry (Marketo column flags, two connections, VL_ModelId active value set, an older PROD model), not regressions"
---

- Every PROD `PL_MainExecution` run 09-25..10-02 failed; the schedule was then user-disabled.
- Marketo enriched: `Lakehouse_Util.marketo_columns` in PROD had 0 of 440 `include_in_enriched`
  (DEV/TEST 19). `NB_Metadata_Marketo` creates rows unflagged; the flags are hand-set data. With no
  views, `conn.query` returned None and the generator died on `len(None)`. Copied from TEST
  (`tools/marketo_seed_columns.py`); Raw/Enriched/Curated incl. Marketo green in PROD 10-10.
- Connections: `CON-WI-Notebook` empty in Prod value set; no Prod override for
  `CON-SQLFabric-ETL_Warehouse_Enriched_Marketo` (fell back to DEV's). Created via API by the SPN
  10-10: `CON_Notebook_WI_PROD` d732e390, `CON-WI-SQLFabric-ETL-Prod_Warehouse_Enriched_Marketo`
  0f03b197; roles mirrored from TEST. A connection must give a role to the principal the pipeline
  runs as, else `DMTS_EntityNotFoundOrUnauthorized`.
- PROD `VL_ModelId` active value set was "Default value set" (DEV model id) although its PROD set
  was right -> "model enumeration produced no tables". VL_Capacity/VL_PingalaUtils also on Default,
  harmless (Prod sets have no overrides).
- PROD model 09692cc9 is older than TEST's; 5 partitions read a missing `#"Source"` (patched
  10-11). TEST's model hardcodes the TEST server in 27 partitions with no parameter, so a model
  deploy without a data-source rule would point PROD at TEST data. Fix direction: Server parameter.
- `fabric_release.py` (`6171217`) now copies marketo flags and switches the active value set.
- Open 10-11: Scale Up/Down `Failed to create session`; PROD equals TEST on workspace identity,
  groups, notebook content and connection settings (allowUsageInUserControlledCode false on both).
