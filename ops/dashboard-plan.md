# Dashboard - three pages

Decided 2026-09-21 with Niels. Supersedes the single `/overview` page. The findings this
builds on are in `dashboard-review.md`.

## The shape

| Page | Answers | Route |
|---|---|---|
| Today | what do I do now | `/` |
| Projects | where does everything stand | `/projects` |
| Time | what gets invoiced | `/time` |

### Today - the day's moves, grouped by project

Tiles (hours today, active sessions, unsent asks, triage count), then:

- **Needs triage** - the unchecked lines of `ops/TODO.md`, each with `Make it a task`,
  `Tick`, `Drop`, `Copy`
- **Due back today** - tasks whose `resume_on` is on or before today
- **Unsent asks** - `customer_ask: open`
- **In progress** - grouped by project, with the age of each `**Now (date):**`

Nothing else. A task with no move to make today does not appear here; it is on Projects.

### Projects - one ranked table, banded by activity

One row per project, worst attention first, in three bands: **Gone quiet** (status active,
idle > 14 d), **In flight** (worked < 14 d), **Dormant** (status not active).

Columns: project, status, last worked, standing date, tasks (in progress / open / parked),
blocked on, asks. Row click opens a drawer with goal, where we stand, open threads, next
actions, and a launch button. Customer rollup sits below the table.

This replaces the `Not working on - active projects gone quiet` panel, which stated the
problem without stating the position.

### Time - what gets invoiced

Hours chart, by-project chart, internal-hours triage, hygiene (UNSET project id, orphaned
folders, unfinalized days), and the week timesheet / month overview that are routes off the
current page.

## Why triage looked broken

It was not. `ops/TODO.md` holds 9 unchecked lines, the payload carries all 9 with correct
ages, and the panel renders them. `Make it a task` only launches a Claude session seeded with
`/task <item>` - nothing ever ticks the line, so the list can only shrink by hand. Oldest item
is 77 days.

`Tick` and `Drop` close it: both write `ops/TODO.md` directly, the way the task buttons already
write a task file.

    Tick   - [x] 2026-07-06 - ask Niels ...            (done 2026-09-21)
    Drop   - [x] ~~2026-07-06 - ask Niels ...~~        (dropped 2026-09-21)

## Rendering

Preact + htm, one pinned ~5 KB file vendored into the repo. No npm, no build step, no network
at runtime; htm uses tagged template literals, so there is no JSX and nothing to compile.

The reason is not taste. Every panel today rebuilds itself with `innerHTML` and re-attaches its
handlers - 38 `innerHTML` sites and 38 `onclick` assignments in `dashboard.html`. Auto-refresh
runs every 60 s and throws away an open drawer, an expanded triage row, the scroll position and
anything half-typed in the filter box. That is already true, and every interactive control
added from here makes it worse. A diffing renderer touches only what changed, so refresh stops
destroying interaction state, and each panel becomes a function instead of a string-building
block.

The Python side does not change: pure stdlib, no dependency, one server.

## Files

    ops/web/
      vendor/preact-htm.min.js   pinned, with its version recorded
      app.css                    tokens, layout, tables, drawer
      app.js                     fetch + cache, shared components (Tiles, FilterBar,
                                 Table, Drawer, Chart), launch, toast
      today.html
      projects.html
      time.html

`ops/dashboard.html` and `ops/today.html` are retired at the end, not at the start.

## Server work

1. **30 s TTL cache on `collect()`** - finding #4. Every `/api/data` request currently re-reads
   every task file, every CLAUDE.md and CONTEXT.md, every heartbeat, and re-parses the XLSX.
2. **POST routing table** - finding #3 in the original review. Three routes become four; the
   `startswith` chain stops paying its way.
3. **`POST /api/todo`** - `tick` and `drop`, writing `ops/TODO.md`.
4. **Static serving** for `ops/web/` - the handler serves two named pages today and nothing else.
5. **Project status on `projects`** - the table needs standing date, task counts and unsent asks
   per project. The resume-card fields already exist in the day-brief model; merge them in
   `collect()` rather than parsing the cards twice.

One `/api/data` payload stays, cached; each page reads its slice. No per-page endpoints.

## Sequencing

Each phase ends with the suite green, and the page it replaces still reachable until its
replacement is verified.

| Phase | Work | Visible change |
|---|---|---|
| 1 | TTL cache, POST routing table, `/api/todo`, project status fields, tests | none |
| 2 | `ops/web/` shell (vendor, app.css, app.js), Today ported, served at `/` | Today |
| 3 | Projects page at `/projects` | Projects |
| 4 | Time page at `/time`; retire `dashboard.html` and the old `today.html` | Time |

## What to watch

- `ops/TODO.md` is hand-maintained, so tick and drop must leave every other byte alone. Same
  test discipline as `_apply_fm`, which caught two real defects.
- Merging the day-brief model into `collect()` adds a pass per cache miss.
- The vendored file gets its version and origin recorded next to it, and is never fetched at
  runtime.

---

# Built 2026-09-21

| Phase | State |
|---|---|
| 1 - cache, POST routing table, `/api/todo`, project fields, tests | done |
| 2 - `ops/web/` shell and Today at `/` | done |
| 3 - Projects at `/projects` | done |
| 4 - Time at `/time`, and the two old pages retired | done |

`ops/web/`: `app.css` (368 lines, the tokens and component rules lifted verbatim from
`dashboard.html` so the validated palette is unchanged), `app.js` (the shared shell, data
hook, drawer, toast and launch), `vendor/` (preact 10.29.8 + htm 3.1.1, ~16 KB, see its
README), and three pages, each a 13-line document plus its own module.

## Phase 4, and what changed about it

The brief for the Time page changed when it was built: not "port the timesheet" but **be able
to enter the month in F&O, always**. The required data has to be present, and where it is not,
fixable from the page. Showing what to type is the start of that, not the end of it.

So the page is the entry surface, and it knows the rule it is registering against.

**`Enter`** - Month, Week, Companies, Customers, Consolidated in one sticky bar, then:

- **Ready to enter**, the gate. Every line is held against the customer's own registration
  rule, and what is short is named with the hours riding on it.
- **Totals per company**, the reconciliation figure - one F&O timesheet per company.
- **One block per company**, with *Copy rows* (TSV) and *Excel* (a real .xlsx, built with
  zipfile; there is no dependency to add). Both carry exactly the visible rows.
- **The week behind the numbers** - the five evidence sections, unchanged in substance.

**`Review`** keeps the month's shape: hours, by project, internal position, hygiene.

Clicking a line opens the editor, which offers **two grains** on purpose:

| | Writes | Fixes |
|---|---|---|
| Correct this day | `ops/time/timesheet/<YYYY-MM>/<date>.md` | the hours being entered now |
| Set `fno_code` | the project's `## Identity` | every line from here on |

A day still accruing has no finalized file, so the editor says so instead of failing. A
consolidated line has no single row behind it, so the editor says that too.

`ops/dashboard.html` and `ops/today.html` are gone. Their last state is commit `09b0a41`,
committed before the delete so the uncommitted work in them survives in history.

## Where the rule lives now

`ops/time/README.md` 4.1 recorded what each customer registers on, in prose - readable, and
unusable by anything. The machine-readable copy is now in the `## Customer` block of
`customers/<client>/CLAUDE.md`, beside `name` and `status`, read by `ops/lib/fno.py`:

    fno_requires: task            what a line must carry: task, activity, description
    fno_billable: no              the line goes in as `Linjeegenskab: No charge`
    fno_description: ...          the required Beskrivelse (on the project - it is the engagement)
    fno_firma/fno_code/fno_activity   override the sheet for a customer it does not list

Absent means nothing extra is required. Five nodes carry a rule: Carl Ras and Matas (task),
Tystofte and Vestforbraending (activity, and Vestforbraending `No charge`), Element Logic
(activity + description). The README table stays as the record of what was confirmed and when.

## How it was verified

No browser extension was reachable, so each page was rendered under jsdom against the
running server and checked for script errors, headings, tiles and row counts. All three
render clean. The write path was exercised end to end - tick and drop - against a copy of
the workspace in a temp directory, never against `ops/TODO.md`.

160 unit tests pass, 29 of them new: the `TODO.md` write path (indentation, CRLF, a
missing trailing newline, a stale line, an out-of-range line, a line that is not an open
item), the band rule, the two memos, and the POST routing table.

## What phase 4 turned up in the live data

- **A `?` in the sheet was being read as a Proj ID.** `TidsregInfo.xlsx` writes `?` and `6013-?`
  for "not assigned yet". Six Aeven lines were flagged `conflict` against a value that was a
  placeholder on one side, and a `?` was reaching the entry rows as though it were a code. A
  placeholder is now the absence of a value: it neither fills a gap nor conflicts with anything.
- **16 September lines, 12.5 h, cannot be entered as they stand** - 15 Carl Ras lines with no
  ADO task (the customer registers on task, always) and one line on the `customers/Aeven`
  customer node, which has no `fno_code`. August is clean.

## Two defects found on the way

- `_apply_fm` (fixed earlier the same day): a task-file value carrying a backslash raised,
  and one carrying a group reference silently rewrote itself.
- `launch("")`: an empty path resolved to the server's own working directory, which is
  inside the workspace and exists, so it passed the guard and started a session there.
  Found by a test that started a real one. Now refused.
