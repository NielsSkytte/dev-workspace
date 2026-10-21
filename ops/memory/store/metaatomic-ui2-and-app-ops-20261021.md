---
id: metaatomic-ui2-and-app-ops-20261021
ts: 2026-10-21T15:30:00Z
type: semantic
scope: project:own/MetaAtomic
source: /log
tags: [metaatomic, fabric-app, rayfin, ui, data-quality, carl-ras]
status: distilled
description: "MetaAtomic 2026-10-21: UI v2 chosen and rendered by the engine (one template per page); simpler DQ page; Rayfin deploy/sign-in failure modes found at Carl Ras"
---

- Niels chose UI v2 (10-21). The engine now writes v2 pages itself (own `76ffa01`): DQ template in
  `dq_profile/app/`, lineage `lineage_engine/viewer.html`, streams `stream_matrix/template.html`, tokens
  `portal/tokens.css`. Each page carries `<meta name="ma-ui" content="2">`; `ui2/retemplate.js` passes those
  through and still converts v1 pages from older runs. The app builds v2 unless `VITE_UI=1`.
- DQ page simplified after customer feedback (own `3c6bff7`): 5 views (Overview, Report impact, Tables, Issues,
  Manage checks), overview > table > issue drill-down. Cause of the BudgetLedger/Timeliness mismatch: the
  post-load row check judges a whole table but was recorded on its first column under Consistency, and the
  Summary counted only where an issue starts while Report impact counted inheritance. The page now counts a
  stale row check as Timeliness and shows whole-table checks once; the engine and run mail still say
  Consistency (open).
- Rayfin (CLI 1.36.2) at Carl Ras: `rayfin up` printed success while the store connector apply had failed
  (only a warning in `~/.rayfin/logs`); a failed static deploy leaves the item with `NO_DEPLOYMENT_FOUND` until
  the next good `up`; a browser's saved sign-in was refused after a redeploy (401 / "Could not acquire the app
  owner's credentials for this connector") until a fresh browser profile. `rayfin login` needs
  `STORE_WORKSPACE_ID`/`STORE_ITEM_ID` set because it parses rayfin.yml first. The Fabric REST items API
  answers `RequestFailed` for app items (no delete by API).
- Always grep the deploy log for `up.warning Connector` after `rayfin up`.
