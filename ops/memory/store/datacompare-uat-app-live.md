---
id: datacompare-uat-app-live
ts: 2026-11-11T12:00:00Z
type: semantic
scope: project:customers/Matas/DataCompare
source: /log
tags: [matas, datacompare, static-web-app, msal, graphql, uat]
status: distilled
description: "DataCompare UAT app live 2026-11-10 on Prod data; MSAL needs an anonymous redirect.html behind a closed SWA; GraphQL limits; SWA CLI deploy-folder quirks; Free licence enough for non-Power BI items"
---

- **UAT app (2026-11-10):** swa-datacompare-uat in rg-datacompare-weu-uat (subscription MatasGroup D365FO Dev), https://zealous-rock-09f016303.6.azurestaticapps.net, app reg "DataCompare UAT" bce553fe, group "DataCompare UAT users". The host name stays unless the SWA resource is recreated.
- **Interim (owner):** deployed `deploy_swa.ps1 -Environment prod -AppEnvironment uat`; the UAT group is in dc_uat and dc_prod. The header badge shows "UAT app" + "Data: PROD". Reverse: redeploy `-Environment uat`, `ALTER ROLE dc_prod DROP MEMBER [DataCompare UAT users]`.
- **Closed SWA + MSAL redirect flow:** Entra's return to `/#code` arrives without the SWA session cookie, so a closed root re-authenticates and loses the hash (endless sign-in). Fix: MSAL `redirectUri` = anonymous `/redirect.html` (route before `/*`), which does `location.replace('/' + location.hash)`; the SPA redirect URI on the app registration must match.
- **Fabric GraphQL limits:** 64 MB per response, 100,000 rows per paginated query, 100 s per request. dc-core.js pages at 10,000 rows, splits findings by field (parts of 3,000) and by company, and caches fixed reads; load ~6 s -> ~3 s.
- **SWA CLI:** picks up any staticwebapp.config.json below the cwd and refuses to run inside the deploy folder; build to `out/swa/<env>` (cleared each build) and deploy from `out/swa`.
- **Licensing:** a Free Fabric licence can use shared non-Power BI items (GraphQL, SQL DB) on any F SKU; Pro below F64 applies to Power BI content only (Microsoft Learn, checked 2026-11-10). An earlier claim that Sara needed Pro was wrong.
- **Custom name:** a CNAME (e.g. `datacompare-uat.matasgroup.com` -> the azurestaticapps host) from Matas IT, then add the custom domain on the SWA and its redirect URIs on the app registration.
