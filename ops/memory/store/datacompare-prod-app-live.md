---
id: datacompare-prod-app-live
ts: 2026-11-12T16:00:00Z
type: semantic
scope: project:customers/Matas/DataCompare
source: /log
tags: [matas, datacompare, static-web-app, prod, entra]
status: distilled
description: "DataCompare Prod app live 2026-11-12: swa-datacompare-prod (salmon-grass host), MI c8573a9b, app reg 820c064e applied by Syed, Prod group in dc_prod"
---

- **Prod app (2026-11-12):** swa-datacompare-prod (Standard) in rg-datacompare-weu-prod, subscription MatasGroup D365FO Prod 9d2e9d4c-4a2b-43fc-802f-c2dd74de6f2d, https://salmon-grass-03a388b03.3.azurestaticapps.net. Managed identity id-swa-datacompare-prod: principal c8573a9b-67f5-4620-b743-6273fbcd2ad0, client 2858e609-a613-43a0-bb0b-962a2601267a. App reg "DataCompare Prod" 820c064e-f317-4a0b-ac45-90ff0ac62898.
- **Route without Owner on the app registration:** run only the Azure half of setup_swa.ps1 (SWA, identity, identity assign, app settings), then send Syed the federated credential (issuer tenant v2.0, subject = MI principalId, audience api://AzureADTokenExchange), Web callback + SPA redirect.html URIs and ID token issuance. Done this way 2026-11-12.
- **Access:** "DataCompare Prod users" (2 members 2026-11-12: Sara Jeftic, Niels) in dc_prod by grant_access.py, items shared by the owner. Workspace admins see data without any group (db_owner), so an admin's "data loads" proves nothing about group access.
- **Git Bash + az:** a resource id argument is rewritten to `C:/Program Files/Git/subscriptions/...` unless `MSYS_NO_PATHCONV=1`; values read from `az ... -o tsv` or Python on Windows can carry `\r` into later az arguments (an app setting got a trailing CR). Check values after setting them.
- **Open:** two CNAMEs ordered from Matas IT (UAT, Prod); outsider-refused check not done.
