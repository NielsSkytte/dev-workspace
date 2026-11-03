---
id: project-room-sync-collision
ts: 2026-11-03T22:00:00Z
type: evaluative
scope: project:customers/Aeven/AtomicServiceNow
tags: [project-room, collaboration, kresten, sync, customer-repo]
status: distilled
description: "First joint-work test of the Aeven project room: both people synced the same change to Aeven within an hour; room rule added"
---

- 2026-11-03: Kresten synced his SQL_Util config-schema change to MasterDataPlan himself; Niels's session
  prepared the same sync an hour later. `now/kresten.md` said backend changes are done with Niels and did not
  mention the sync, so the room did not show it. Git prevented damage (the duplicate was uncommitted).
- Rule added to project-room AGENTS.md (`499c458`): before a sync to Aeven pull the room and the clone and read
  the other's `now/`; after the push note "synced to Aeven <commit>" in your own `now/`.
