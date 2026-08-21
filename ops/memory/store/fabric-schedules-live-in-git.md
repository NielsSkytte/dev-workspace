---
id: fabric-schedules-live-in-git
ts: 2026-08-20T16:20:00Z
type: semantic
scope: global
tags: [fabric, git-integration, deployment, schedules, service-principal]
source: session:8374f87e-2a3d-4166-8017-4515139d44c8
status: distilled
description: "Fabric item schedules are part of the item definition - a .schedules file in the repo - so deleting one in the portal does not stick, and every sync stamps whoever ran it as the schedule owner"
---

Hand-written from the session, measured on Carl Ras Fabric-ETL.

## Schedules are in the definition

A git-connected pipeline serialises as `<Name>.DataPipeline/.schedules` alongside
`pipeline-content.json`, and the `getDefinition` API returns it as a part. Consequences:

- **Deleting a schedule in the portal does not stick.** It is recreated by the next Update from
  git. Remove it from `.schedules` in the repo instead.
- **The deployment pipeline compares them**, so any schedule that exists in one stage and not the
  other is flagged as *different* forever, with no way to clear it from the source side. Deployment
  rules cover data sources and parameters only.

Timestamps proving the round trip: DEV's two schedules were both recreated at 12:01:17 by an Update
from git, TEST's at 12:05:13 by a deployment, on 2026-08-20.

## The pattern that costs least

**One schedule object per pipeline, defined in git and disabled there, enabled in the stage that
actually runs it.** The comparison then differs by a single `enabled` flag, which is readable, and
the schedule stays in source control where it can be reviewed and restored. The alternative - no
schedule in DEV, one created by hand in TEST - puts the whole object outside git and flags the
entire part.

## Ownership follows whoever synced

The schedule's `owner` is set to the principal that performed the git update or the deployment, not
to the item's author. Four schedules across two workspaces all came out owned by the named user who
ran the sync. A user-owned schedule stops running when that account is disabled - which has already
happened on this project.

So SPN ownership is not something you set once: it holds only if **the release itself runs as the
SPN**. Setting it by hand through
`POST /v1/workspaces/{ws}/items/{id}/jobs/{jobType}/schedules` works (the creating principal becomes
the owner) but is reverted by the next person-run deployment.

Create before delete when replacing a live schedule, so the stage is never left unscheduled.
