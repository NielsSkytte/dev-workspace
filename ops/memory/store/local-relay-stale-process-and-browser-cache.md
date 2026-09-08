---
id: local-relay-stale-process-and-browser-cache
ts: 2026-09-08T07:30:00Z
type: procedural
scope: workspace
source: /log
tags: [local-dev, fastapi, uvicorn, browser-cache, debugging, chrome, static-files]
status: distilled
description: "Two ways a local web prototype shows the old version after a fix: a stale server process still holding the port (kill listeners on the port before starting a new one, from PowerShell via Get-NetTCPConnection), and the browser caching styles.css / app.js (serve page files with Cache-Control: no-store during development). Both bit the Matas DataCompare app on 2026-09-07/08, three times"
---

**Symptom.** Owner: "the rewind did not work, it still shows the new layout"; "the values are
missing, we had them earlier". The served files were correct each time.

**Cause 1, stale server.** `python relay.py` started with `&` from a Claude shell survives the
shell and keeps port 8080; a later start fails to bind silently (or the old process answers). A
subagent stopped a stale relay twice and reported it; the third time the old one served pre-fix
CSS to the owner. Fix before every restart:
`Get-NetTCPConnection -LocalPort 8080 -State Listen | Select -Expand OwningProcess -Unique | % { Stop-Process -Id $_ -Force }`.
`curl` on the port proves something answers, not that it is the new code; check a marker string
in the served file when in doubt.

**Cause 2, browser cache.** Chrome kept `styles.css` across a plain reload; a hard reload
(Ctrl+Shift+R) or a query string fixed it once, but the owner's browser is not under our control.
Durable fix: a FastAPI middleware setting `Cache-Control: no-store` on every response while the
app is a moving target. Added to `relay.py` on 2026-09-08.

**Related trap from the same day.** A `table-layout: fixed` with per-column widths that summed to
the container width was fine at full width and hid two columns (zero pixels) when the card became
half-width. Fixed widths on tables that may be re-laid out are a smell; use auto layout with
`max-width` plus ellipsis on the long cells.
