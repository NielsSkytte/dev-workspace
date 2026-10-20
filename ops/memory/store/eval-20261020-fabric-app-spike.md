---
id: eval-20261020-fabric-app-spike
ts: 2026-10-20T13:30:00Z
type: evaluative
scope: project:own/MetaAtomic
source: distilled
tags: [eval, skills, rayfin, browser-automation, own-repos]
status: distilled
description: "Fabric App spike: no skill covers Rayfin/Fabric Apps, `npx rayfin docs search` filled the gap (found externalEntraExchange); browser sign-in blocked so a headless token exchange was the way to verify"
---

- **Gap:** no workspace skill covers Fabric Apps / Rayfin. Every template defect (tsconfig, decorators, view keys) was
  found by trial. `npx rayfin docs search "<topic>"` reads the installed guide and answered the auth question in one call.
  Candidate for a `fabric-apps` skill once the Carl Ras build is done (Q to judge).
- **Should have fired earlier:** verification by browser was planned first and stalled on sign-in twice; looking for a
  headless path (the SDK's `signInWithEntraToken`) first would have saved a round trip with Niels.
- `own-repos` rules held: own commits without asking, customer Fabric-ETL push held for approval.
