---
id: feedback-pingala-tenant-is-dev
ts: 2026-10-16T15:00:00Z
type: semantic
scope: workspace
source: session:78a2d310-6388-447e-b137-3d87b961156c
tags: [feedback]
status: distilled
description: "Pingala's own Fabric tenant is development only: runs, deploys and item changes in Pingala workspaces (e.g. NielsWorkspace_Dev, any *_Dev) are done without asking"
---

Owner, 2026-10-16: "on _dev run anything you want, also at pingala here we are never in actual
production, all is development."

**How to apply:** in Pingala's tenant (nchristensen@pingala.eu, e.g. `NielsWorkspace_Dev`), create,
update, deploy and run items (notebooks, pipelines, lakehouses, warehouses, SQL) without asking,
then report. Long Spark runs included. This does not change the customer rule in `C:\Dev\CLAUDE.md`
("If you can do it, do it"): a customer-tenant mutation or a customer-facing push is still asked
first.

**Why:** a notebook run in NielsWorkspace_Dev was blocked as a "production deploy" and he had to
unblock it by hand.
