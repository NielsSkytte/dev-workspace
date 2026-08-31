# Absence register

Why a workday had no keyboard time. Hand-maintained; `rollup.py --check` reads it and stops asking
about a date once it appears here. See `ops/time/README.md` section 8.

**Kinds**

| Kind | Meaning | Effect on the timesheet |
|---|---|---|
| `vacation` | Ferie | No timesheet. The day is removed from the week/month target. |
| `holiday` | Public holiday / closure | No timesheet. Removed from the target. |
| `sick` | Sygdom | No timesheet. Removed from the target. |
| `offline` | Worked, but not at this keyboard (customer meeting, workshop, travel) | Full day (7.5 h) claimed on the named project at the next rollup. Stays in the target. |

`Project` is required for `offline` (a workspace project path, e.g. `customers/Carl-Ras/datahub`)
and ignored for the others. Keep the table sorted by date.

| Date | Kind | Project | Note |
|---|---|---|---|
| 2026-08-26 | vacation | | |
| 2026-08-28 | vacation | | |
