---
id: carlras-fno-sync-follows-parent-wp
ts: 2026-11-11T10:00:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: session 01c65527 2026-11-11 (F&O test observed in pingprod)
tags: [fno, carl-ras, devops, time]
status: distilled
description: "The DevOps -> Pingala F&O task sync follows the parent Work Package: moving a Task changes its F&O 'Formaal' and activity; booked hours stay on the Task"
---

Tested 2026-11-11: Task 524 moved from WP 518 to WP 554 in ADO. In F&O (project 230, Opgaver),
CarlRData-524 then showed Formaal "554 - Operational hardening", activity 112755 (same as 738 in
WP 554), hours N: 11.75 kept. So the F&O activity is per WP, and a Task's WP decides it.
Only Tasks tagged SyncToPingala reach F&O (the WP must carry the tag too). New Tasks require
Original Estimate in this ADO process (TF401320 when empty).
