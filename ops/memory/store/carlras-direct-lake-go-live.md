---
id: carlras-direct-lake-go-live
ts: 2026-11-18T19:45:00Z
type: semantic
scope: customers/Carl-Ras/datahub
source: session:1a6805df
tags: [fabric, direct-lake, power-bi, production]
status: distilled
description: "Carl Ras PROD on Direct Lake (11-18): Model_OneLake had read TEST data; viewers saw empty visuals (SSO); fixed with workspace-identity connection, auto-update off, pipeline frames the model"
---

State 2026-11-18 (Carl Ras, Semantic-Model PROD ws c0053725):
- PROD `Model_OneLake` (0abb3f3f) read Fabric-ETL-TEST (OneLakeSourceUrl) for a week; repointed via
  Default.UpdateParameters, Niels then set the PROD parameter rule. Counts matched the Import model.
- First business users saw empty visuals: Direct Lake on OneLake without a bound connection reads as the
  viewer, who needs Read + ReadAll on the source item. Fix: share PROD Warehouse_Curated (Read + ReadAll)
  with the Semantic-Model PROD workspace identity, connection
  `CON-WI-OneLake-Warehouse_Curated_PROD-SemanticModel` (8756645d, SSO off), bindConnection on both PROD
  models. TEST uses `CON-WI-ADLS-OneLake-Warehouse_Curated_TEST` (a556a678). Not yet confirmed by a non-admin user.
- "Keep Direct Lake data up to date" OFF on both models in TEST and PROD; `PL_Update_SemanticModel` ->
  `NB_Frame_SemanticModel` (Fabric-ETL 87190db) frames Model_OneLake after Curated; Import `Model` no
  longer refreshed from 11-19.
- Generic lesson lives in the fabric-deployment skill, references/powerbi-report-model.md section 4b.
