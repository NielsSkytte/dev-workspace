---
id: fabric-app-function-30mb-limit
ts: 2026-10-26T13:40:00Z
type: semantic
scope: workspace
source: session:38b6cca4
tags: [fabric, fabric-app, metaatomic, limits]
status: distilled
description: "A Fabric App (Rayfin) function response is capped at 30 MB (ResponseTooLarge); MetaAtomic pages are now compact and split into files of <= 8 M characters, loaded by both v1 and v2 shells"
---

Seen 2026-10-26 on Pingala base (fit-fawn): `ResponseTooLarge: Function's response size is larger than the
30 megabyte limit` on the lineage (115 MB) and data-quality (38 MB) pages. Carl Ras DEV lineage was at
28.2 MB (94 % of the limit), so size grows with the F&O estate. Fix in own `8c302b6` + `08d81d1`: compact
page data, split into parts of <= 8 M characters, reassembled by the app shell. The default shell is v2,
which has its own loader; a change to the v1 loader alone leaves pages empty. Related: [[metaatomic-dq-run-time-20261029]].
