---
id: customer-repos-github-backup
ts: 2026-11-18T18:00:00Z
type: semantic
scope: workspace
source: session:1a6805df
tags: [git, backup, decision]
status: distilled
description: "Customer unit repos back up to PRIVATE NielsSkytte/customers (one folder per customer, history kept, .secrets included by Niels's choice); /log runs sync-customers.ps1 -All"
---

Decided by Niels 2026-11-18: the local unit repos `C:\Dev\customers\<Customer>` stay one repo each, with no
remote, and are pushed with their history into `github.com/NielsSkytte/customers` (private, Niels's
personal account, never atompower4us) by `ops/bin/sync-customers.ps1 <Customer>|-All` (wraps
`sync-aai.ps1 -Remote/-Root/-Work`; long paths enabled). Credentials in `.secrets/` travel with it on
purpose. `/log` step 8 runs `-All`; `/new-project` syncs a new customer. DevOps code repos nested in a
unit repo are not backed up there (their own remotes). AGENTS.md secrets rule updated.
