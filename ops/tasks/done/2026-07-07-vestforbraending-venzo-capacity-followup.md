---
title: Vestforbrænding — follow up with Venzo on Fabric capacity creation
status: done
created: 2026-07-07
project: customers/Vestforbraending/fabric-capacity
owner: self
priority: normal
blocked_by:
activity:
fno_task:
source: todo
---

## What
Follow up with Venzo about creating the Fabric capacity for Vestforbrænding.

## Why
Only open motion for this prospect; without the follow-up the thread dies.

## Context
- Project: `customers/Vestforbraending/fabric-capacity` (PLACEHOLDER, scaffolded 2026-07-07 —
  the prior thread with Venzo is not on file, reconstruct from mail when picking this up).
- No fno_code (no signed engagement) — time bills as project-level only.

## Log
- 2026-07-07 — created (promoted from TODO 2026-07-06 at the day-start routing pass; customer
  node + placeholder project scaffolded the same day per the referenced-customer convention)
- 2026-07-20 — DONE. Capacity exists; the real blocker was Dataverse "Link to Microsoft Fabric"
  not showing existing workspaces. Root cause: svc_CRMSandbox lacked capacity Contributor in the
  Fabric Admin Portal (Azure-RBAC Contributor on the capacity resource did not substitute).
  Fixed by granting admin-portal capacity Contributor (reached via Fabric admin PIM). Gotcha
  documented in the `fabric-project-access` skill §8.5; resolution in the customer CONTEXT.md.
