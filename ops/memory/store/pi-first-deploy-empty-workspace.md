---
id: pi-first-deploy-empty-workspace
ts: 2026-11-25T23:59:00Z
type: semantic
scope: project:own/ProcessInsight
source: session 78a9d947 2026-11-25
tags: [process-insight, deploy, fabric, first-deploy]
status: distilled
description: "PI fresh deploy into an emptied Atomic-PI-Dev: 49:50 (deployment 21:50, pipelines 28:01) after five first-deploy fixes, Coverage before the first Main and run-once chain; to empty a git-connected workspace, disconnect git first"
---

2026-11-25. Five faults showed only on a first deploy (workspace id unknown before the first Update from git; redeploy loop after Fabric re-serialisation; the step's warehouse got no SQL connection; curated types read before the Curated warehouse existed; "deployed" reported with no workspace bound). Fixed in tools/deploy.py and tools/fabric_platform.py (AAI 0393238 and the two commits after). Emptying: deleting items while git stays connected, then committing the deletions, leaves Fabric refusing to recreate items whose logicalIds git tracked before (Update from git reports Succeeded, items stay "Deleted"); disconnect git, delete, empty the repo folder, reconnect (Automatic credential). The git connection is the one manual setup step. Replay page and timed transcript: own-wt-picli deployments/atomic-pi/demo/.
