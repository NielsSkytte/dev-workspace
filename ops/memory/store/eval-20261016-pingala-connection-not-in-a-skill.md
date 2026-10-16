---
id: eval-20261016-pingala-connection-not-in-a-skill
ts: 2026-10-16T12:00:00Z
type: evaluative
scope: workspace
source: /log session a007db1c
tags: [skill-eval, fabric-project-access, auth, memory, pingala]
status: distilled
description: "Asked to use 'my Pingala Fabric connection', the session guessed the wrong tenant (fb4a802d) and asked Niels to log in; Niels had to say 'check if you missed a skill'. fabric-project-access was invoked and did not help; the answer was memory tenant-scoped-cli-auth"
---

- **Trigger:** 2026-10-16, process-insight, copying the test source into a Pingala workspace.
  The session read `az account list`, took the tenant listed next to nchristensen@pingala.eu
  (`fb4a802d`) as Pingala's, and asked Niels for an interactive login.
- **Correction from Niels:** "you should have a connection to fabric in pingala with my account,
  we have discussed this, check if you missed a skill". `fabric-project-access` was then invoked:
  it covers customer access requests, not Pingala's own connection, so it did not help. The fact
  was in memory record `tenant-scoped-cli-auth` (default `fab` profile = Niels's Pingala user,
  tenant `5e8d3c87`).
- **Outcome:** both the fab and the az refresh token had expired (90 days), so a login was needed
  anyway; it took three exchanges where one would have done.
- **Gap:** no skill or AGENTS.md line says where Pingala's own tenant id and Fabric workspace live.
  New record `az-cli-account-by-subscription-pingala-tenant` now holds them. Candidate: add a
  "Pingala's own tenant" line to `fabric-project-access` or `pingala-fabric-platform`.
