---
id: carlras-ado-wp-sync-before-task
ts: 2026-11-25T20:40:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: session b05a9093 2026-11-25
tags: [fno, carl-ras, devops, time]
status: distilled
description: "Carl Ras ADO: create the Work Package with SyncToPingala, wait until the sync stamps its D365Activity, then create the booking Task; a Task created seconds after the WP gets no D365Task until SyncToPingala is removed and re-added"
---

Seen 2026-11-25: WP 884 + Task 885 created two seconds apart; sync stamped 884 (activity 113076) a minute later, 885 had no D365Task. Removing and re-adding the SyncToPingala tag on 885 got CarlRData-885 within minutes. Niels: Task before WP sync normally fails.
