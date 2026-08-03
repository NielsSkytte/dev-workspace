---
id: fno-time-entry
ts: 2026-08-03T09:00:00Z
type: semantic
scope: workspace
source: session:972e353e
tags: [project, reference, time-tracking, dashboard]
status: distilled
description: "Entering tracked time in F&O: three internal companies (PING/PNO01/Power) from ops/TidsregInfo.xlsx, one timesheet per company, the 5 h entry-consolidation rule, and internal time tracked but never entered"
---

The last mile of time tracking: turning `ops/time/timesheet/` into F&O entry lines. Built as a
separate **timesheet page** on the dashboard (`#timesheet/month|week1|week2`), not a dashboard
section -- it is a working document you open, not a thing to watch.

**Internal companies are the outermost grouping.** F&O takes **one timesheet per internal
company**, so the page groups by company before anything else. The mapping lives in the owner's own
`ops/TidsregInfo.xlsx` (columns `Firma | Kunde | Projektnr | Aktivitet | Task`), read live from the
workbook with stdlib `zipfile` + `ElementTree` -- no exported copy, so editing the sheet moves the
dashboard. Three companies as of 2026-08:

- **PING** -- Carl-Ras (230-02), JTJ (239-01), Matas (212-01), Vestforbraending (222, activity 111749)
- **PNO01** -- Element Logic (6001-01, activity 600003), Melbye (6013-?)
- **Power** -- Aeven (?), Finansforbundet (4053-01, activity Moeder), Tystofte (4048-1, activity datakilder)

Customer names are matched by normalising case, spaces, hyphens and Danish letters. Two need an
alias: `JTJ` -> JoeAndTheJuice, and `Vestforbraeding` -- a **typo in the sheet**, missing the n
(correct is Vestforbraending). Fix the xlsx and that alias goes dead.

**Proj ID precedence:** the timesheet's own `fno_code` wins; the sheet fills a gap and the cell is
marked `(sheet)`; a disagreement is flagged `conflict` and never silently resolved. The sheet
currently supplies four IDs the workspace has as `UNSET`.

**Internal time is tracked but NOT entered** (owner, 2026-08-01). `Dev` and `own/` get their own
block headed "not entered in F&O", excluded from the "To enter in F&O" total but included in the
period total, so the month still reconciles. They have no company and are not in the sheet.

**Consolidation is more aggressive here than in /time.** The entry page passes
`ENTRY_MERGE_THRESHOLD = 5.0` to `rollup.consolidate_week` (which gained an optional `threshold`
arg); `/time` keeps `MERGE_THRESHOLD = 2.0`. July: 73 raw rows -> 48 at 2 h -> **40-42 at 5 h**,
totals identical to the cent and no project's hours shifted. The point is fewest lines to type.

**Raising the threshold broke the day cap, and that had to be fixed.** Bigger entries get swept in,
so a group can exceed `DAY_CAP` (9 h) -- Matas/DataCompare summed to 10.50 h in one ISO week and the
old code, finding no day with room, dumped the whole group on `own_days[0]`, producing a **15 h
day**. `consolidate_week` now fills the *fewest days that can hold the group*, each up to the cap,
preferring days actually worked. Rare at 2 h, immediate at 5 h.

**Consolidation moves hours to a different date within the same ISO week** -- the date you enter is
not always the date worked. Inherent to the feature; it just matters more at 5 h.

Open at time of writing: Aeven's `Projektnr` is literally `?` in the sheet (4.25 h in July) and
Melbye's is `6013-?`; neither can be entered as-is.
