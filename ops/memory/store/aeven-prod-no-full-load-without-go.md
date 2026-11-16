---
id: aeven-prod-no-full-load-without-go
ts: 2026-11-13T11:26:00Z
type: semantic
scope: project:customers/Aeven/AtomicServiceNow
source: session 9b6af283
tags: [aeven, production, rule, full-load]
status: distilled
description: "Niels promised Aeven no full load against their production ServiceNow without their go; before any PROD run, tell Niels what it will load (full vs delta, per table)"
---

Rule from Niels 2026-11-13: Aeven's production ServiceNow must not get a full load without Aeven's
go. Before Niels starts a run at Aeven PROD, state what it will request per table (full or delta).
Consequences 2026-11-14: Saturday full reload removed from the config; `sys_dictionary` disabled at
Aeven; `sys_choice` is the only table always loaded full (small).
