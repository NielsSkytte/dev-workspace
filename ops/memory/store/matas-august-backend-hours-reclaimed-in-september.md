---
id: matas-august-backend-hours-reclaimed-in-september
ts: 2026-09-07T13:30:00Z
type: semantic
scope: project:customers/Matas/DataCompare
source: /log
tags: [matas, time-tracking, billing, decision, adr-004, reclaim]
status: distilled
description: "Owner decision 2026-09-07: the DataCompare backend build (config store, canonical layer, match engine, July 16 - Aug 3) was billed at measured keyboard hours, 13.50 h against 28.00 h weighted; August stays as entered and the 14.50 h gap is reclaimed on September DataCompare days as part of building the front end, on Task-65905 / activity 111953, tracked in ops/time/reclaim.md"
---

The August F&O month is closed and is not modified. The under-billing comes from agent-built days
where a few owner turns produced whole subsystems (08-03 match engine: 0.44 h keyboard, 7.50 h
weighted). The owner's rule: recover the gap in the month the front end is built, on the same
project and task, and say so to Matas if asked; the work is one deliverable across the months.

Mechanism: `ops/time/reclaim.md` holds the open amount (14.50 h) and a consumption log; at each
September /log the Matas days being finalized carry extra hours until the ledger reads zero. The
days in early July with no value record (5.25 h billed) are not part of the claim, because there is
no evidence to size them. This is also ADR-004 evidence: on agent-built days the measured number
is not the deliverable.
