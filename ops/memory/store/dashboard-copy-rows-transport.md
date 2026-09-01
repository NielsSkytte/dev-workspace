---
id: dashboard-copy-rows-transport
ts: 2026-09-01T18:00:00Z
type: semantic
scope: workspace
source: session:e15b57a5
tags: [dashboard, time, fno, registration, transport, defect]
status: distilled
description: "Copy rows is the intended transport into F&O, and it carries three traps - the same button means F&O entry on the week page and work time on the Month page, it ignores the customer chip filter so it can copy more rows than are shown, and its hours use a dot decimal against F&O's comma"
---

The 2026-09-01 August close was lost to **transport**, not knowledge: the browser extension dropped
twice, the tab group was rebuilt three times, screenshots timed out, and the page **rescaled between
screenshots**, which put `0,75` into `Rolle-id` in a production journal. The intended replacement is
the dashboard's **Copy rows** into F&O's Excel add-in. Verified against `ops/dashboard.html` the same
day, that button has three traps.

**1. One button, two meanings.** `entryView()` renders the F&O entry blocks on both the week/audit
page and the Month page. The week page passes a `scale`, so its hours are the **F&O entry** figure
distributed per dimension in 0,25 h steps; the Month page passes nothing, so its hours are plain
**work time**. Registration uses F&O entry. **Copy from the week/audit page.**

**2. Copy rows ignores the customer chip filter.** The visible table filters on
`r.firma === f && !TSCUST.has(custOf(r))`; the copy handler filters on `r.firma` alone. Copying with
a customer deselected puts **more rows on the clipboard than are on screen** — a silent
over-registration. Clear the chips before copying, and reconcile the copied row count against the
block.

**3. Dot decimals.** `h()` emits `7.5` / `1.25` / `8` (two decimals, trailing `.00` stripped, dot
separator). F&O expects the Danish comma. Convert, and check the first pasted line.

**The payload** is TSV with a header row: `Date, Customer, Project, Proj ID, Activity, Task, Hours`,
dates ISO. There is **no company column** — the company is the block you copied from, and one block
exists per Firma, so PING and PNO1 are separate copies and separate journals. That grain matches the
journal grain exactly (one per ISO week per company).

**Nothing outside the browser reproduces the entry hours.** The scaling (`entryOf`, `TURNS_PER_H=10`,
`FILES_PER_H=8`) lives only in the dashboard's JavaScript. `dashboard.py --json` and
`rollup.py --week/--month` both give **work time**, not entry hours. So the dashboard is a hard
dependency of a close until that scaling moves into Python.

Encoded in the skill `fno-time-registration` and the command `/fno`.
