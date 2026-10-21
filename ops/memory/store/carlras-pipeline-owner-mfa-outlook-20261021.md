---
id: carlras-pipeline-owner-mfa-outlook-20261021
ts: 2026-10-21T15:30:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: /log
tags: [carl-ras, fabric, pipeline, identity, mfa, outlook, metaatomic]
status: distilled
description: "Carl Ras 2026-10-21: PL_UpdateLineage runs as its LastModifiedBy (Niels); MFA (AADSTS50076) broke runs; re-stamp to the SPN is impossible while it uses an Outlook connection (not shareable)"
---

- A Fabric pipeline's notebooks run as the pipeline's LastModifiedBy, not as the caller: a run started by the
  `Fabric_Datahub` SPN failed with the owner's (Niels's) `AADSTS50076` MFA error on the user token.
- Re-stamping `PL_UpdateLineage` to the SPN (`tools/fabric_identity.py`) is refused while the pipeline uses a
  connection the SPN cannot use. Outlook connections cannot be shared at all ("Customers are not allowed to add
  or update principals for the connections of type: MicrosoftOutlook", 403).
- Copy Lineage (SharePoint) removed from the pipeline (DEV + Fabric-ETL `dbb40db`): Carl Ras has no SharePoint.
- Run `b2f898e6` (10-21 afternoon, started via API as Niels) ran both notebooks but "Send DQ mail" failed with
  `DMTS_EntityNotFoundOrUnauthorized` on connection 67345190. Niels parked the mail/owner question.
- `NB_DataQuality` takes the pyz from `Lakehouse_Util/Files/MetaAtomic/metaatomic.pyz` (abfss), `NB_MetaAtomic`
  from the Fabric-ETL clone: an engine release updates both.
- OneLake dfs upload: `PUT ?resource=file` with `Content-Length: 0` (the `overwrite=true` parameter gives 400).
