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
| 4 - Time at `/time` | partial, see below |

`ops/web/`: `app.css` (368 lines, the tokens and component rules lifted verbatim from
`dashboard.html` so the validated palette is unchanged), `app.js` (the shared shell, data
hook, drawer, toast and launch), `vendor/` (preact 10.29.8 + htm 3.1.1, ~16 KB, see its
README), and three pages, each a 13-line document plus its own module.

## Phase 4 is not finished, on purpose

The Time page carries the hours chart, the by-project chart, the internal-hours position
and hygiene. It does NOT carry the F&O entry blocks, the week audit or the reassignment
write path. Those are about 600 lines of dense UI that put numbers in front of an invoice,
and there was no browser available this session to exercise them in. They stay where they
are, on `/overview#timesheet/...`, linked from the Time page.

So `ops/dashboard.html` is still live and still needed. It is out of the main nav; the
only way in is the two timesheet links.

Remaining, in order:

1. Port `entryView`, `renderAudit` and `bindReassign` to the Time page, with the reassign
   path exercised against a throwaway workspace the way `/api/todo` was.
2. Retire `ops/dashboard.html` and the superseded `ops/today.html`.

## How it was verified

No browser extension was reachable, so each page was rendered under jsdom against the
running server and checked for script errors, headings, tiles and row counts. All three
render clean. The write path was exercised end to end - tick and drop - against a copy of
the workspace in a temp directory, never against `ops/TODO.md`.

160 unit tests pass, 29 of them new: the `TODO.md` write path (indentation, CRLF, a
missing trailing newline, a stale line, an out-of-range line, a line that is not an open
item), the band rule, the two memos, and the POST routing table.

## Two defects found on the way

- `_apply_fm` (fixed earlier the same day): a task-file value carrying a backslash raised,
  and one carrying a group reference silently rewrote itself.
- `launch("")`: an empty path resolved to the server's own working directory, which is
  inside the workspace and exists, so it passed the guard and started a session there.
  Found by a test that started a real one. Now refused.
