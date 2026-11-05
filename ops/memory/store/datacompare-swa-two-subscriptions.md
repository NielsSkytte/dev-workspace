---
id: datacompare-swa-two-subscriptions
ts: 2026-11-05T18:30:00Z
type: semantic
scope: project:customers/Matas/DataCompare
source: /log
tags: [matas, datacompare, static-web-app, azure, rbac, go-live]
status: distilled
description: "Matas SWA plan (2026-11-05): UAT first, two resource groups in D365FO Dev and Prod subscriptions; Contributor is enough for the scripts; gaps: Assignment required, provider registration, names; runbook assumes one rg"
---

- **Matas's plan (reply received 2026-11-05):** UAT first, then Prod. Matas creates two resource groups in West Europe (subscriptions MatasGroup D365FO Dev and MatasGroup D365FO Prod), Contributor for Niels on both, UAT and Prod groups with Niels as first member, two app registrations with admin consent, Niels as owner.
- **"Team" in that reply (owner):** Niels plus someone with F&O access. Niels creates the apps and identities and grants Fabric access; the F&O person sets up Link to Fabric for UAT.
- **Contributor on the resource group** covers the Azure steps of `setup_swa.ps1` and `deploy_swa.ps1`. App registration ownership covers the federated credential and redirect URIs. Not yet proven under that limited role: leita.dk was Niels's own tenant.
- **Not in Matas's list:** "Assignment required = Yes" and the group assignment on the enterprise applications (email 07 item 2). Registration of `Microsoft.Web` and `Microsoft.ManagedIdentity` is a subscription-level action. Niels wrote to Matas himself on 2026-11-05; the content of that message is not in this record.
- **Runbook gap:** `prototype/README.md` assumes one `rg-datacompare`; the scripts have no subscription setting. Update when the names arrive.
