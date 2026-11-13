---
id: aeven-repo-access-only
ts: 2026-11-12T10:00:00Z
type: feedback
scope: project:customers/Aeven/AtomicServiceNow
tags: [aeven, access, fabric, guardrail]
status: distilled
description: "No access to Aeven from here, only their MasterDataPlan repo: never call Aeven's Fabric (az/fab/REST) to verify ids, names or runs; ask Niels"
---

- Fact (Niels, 2026-11-12): from this machine there is no access to Aeven at all, only to the
  MasterDataPlan repo. Aeven's Fabric is reached only by Niels in his Aeven session.
- Why recorded: on 2026-11-12 the session called the Fabric REST API for Aeven's connections
  instead of using the id Niels gave. Niels: "you should know this by now".
- How to apply: take ids, names and run results at Aeven from Niels; never try to verify them.
  Rule is in the project room `AGENTS.md` > Rules of engagement.
