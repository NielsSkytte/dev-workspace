---
id: az-cli-account-by-subscription-pingala-tenant
ts: 2026-10-16T12:00:00Z
type: procedural
scope: workspace
source: /log session a007db1c
tags: [az-cli, auth, pingala, fabric, tenant]
status: distilled
description: "Pingala's Entra tenant is 5e8d3c87-f9c4-4575-a670-d76860aa43e2 (nchristensen@pingala.eu), not fb4a802d; `az account get-access-token --tenant X` uses the CURRENT account, so pick the account with --subscription; refresh tokens die after 90 days unused"
---

- **Pingala tenant:** `5e8d3c87-f9c4-4575-a670-d76860aa43e2`, account nchristensen@pingala.eu,
  subscription `cbe55770-cf9e-46ae-acd8-88d306852aea`. The default `fab` profile
  (`~/.config/fab/auth.json`) names the same tenant. `fb4a802d-9e80-46cd-be96-51bd1ac0e576` is a
  different tenant the pingala.eu account also appears in; on 2026-10-16 it was wrongly named as
  Pingala's in chat.
- **`--tenant` does not select the account.** With several accounts cached, `az account
  get-access-token --tenant <t>` asks with the default account and fails (AADSTS50020) when that
  account is not in `<t>`. Use `--subscription <id>` (a tenant-level account's id is the tenant id
  only when it has no subscriptions). Scripts that read two tenants pass one subscription id each
  (leita.dk `acc765f5-...`, Pingala `cbe55770-...`), so the default account does not matter.
- **90-day inactivity** kills both the az and the fab refresh token (AADSTS700082). Fix: one
  interactive `az login --tenant <t> --allow-no-subscriptions`; when the WAM account picker is
  cancelled or hidden, add `--use-device-code`. A fresh `az login` becomes the default account.
- Pingala Fabric for product tests: workspace `NielsWorkspace_Dev`
  `027b8a56-3500-4600-a9be-6876bc8a4540`, capacity F8 `msfabricpingala`, West Europe.

Related: [[tenant-scoped-cli-auth]], [[fab-console-login-and-silent-sql-onelake-tokens]]
