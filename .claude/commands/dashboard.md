Open the visual workspace dashboard — one page showing what is in flight, what has gone quiet, hours per project/customer, open tasks, and data hygiene. Derived live from `ops/tasks/`, `ops/time/`, every project's `CLAUDE.md` + `CONTEXT.md`, and `ops/TODO.md`. It writes nothing. The full description lives in `AGENTS.md` > *Dashboard*.

Usage:
  /dashboard           <- start the local server and open it in the browser
  /dashboard json      <- print the collected payload instead (no browser, no server)

## Instructions

### `/dashboard` — serve it

Run in the **background** (it is a long-running server):

```
python C:\Dev\ops\dashboard.py
```

It binds `127.0.0.1:8787`, opens the default browser, and serves until stopped. If the port is
already in use a dashboard is already running — just tell the user to open
<http://127.0.0.1:8787/> rather than starting a second one.

Report the URL and stop there. Do **not** narrate the page contents — the point of the dashboard
is that the user reads it themselves. If the user asks a question about something on it, answer
from the underlying files.

### `/dashboard json` — the payload

Run `python C:\Dev\ops\dashboard.py --json`. Use this when the user wants the numbers in chat
rather than in a browser, or when debugging the collector.

### Notes

- **Registration is dual, like the hooks.** This file covers workspace-root sessions; a thin pointer at
  `~/.claude/commands/dashboard.md` covers every other session, because commands do not cascade into
  project-rooted sessions. Keep both pointing at the same script.
- The page re-fetches `/api/data` **every 30 s** (toggle with the *Auto* button) and on **Refresh**, so
  it is never stale — no regeneration step, no generated file to commit. Auto-refresh pauses while the
  browser tab is hidden, while a drill-down drawer is open, and while the filter box has focus; scroll
  position in both panes survives a refresh.
- **Layout:** a fixed top band (header, alerts, stat tiles) over two independently scrolling panes —
  left third = what needs you (*Needs triage*, *Open tasks*, *Needs attention*), right two-thirds =
  the overview (charts, in flight, gone quiet, customers). Below 1000 px wide it collapses to one column
  and the page scrolls normally.
- **Hours chart period** — defaults to the **current calendar month**, with a *Last month* toggle
  (remembered between visits). It plots **every date in the month**, so an untracked day is drawn as an
  explicit zero (a baseline stub) rather than disappearing — the gaps are the point. **Weekends carry a
  shaded band** behind the column, a bold day number, and `Sat/Sun · weekend` in the tooltip, so an empty
  stretch can be read as "weekend" rather than "lost time" at a glance. Weekend days are never dropped:
  work does land on them, and when it does the bars draw over the band exactly as on a weekday. The
  *By project* chart beside it follows the same month, so the pair never shows two different periods.
- **Filters** — a chip bar at the top of each pane, sticky while that pane scrolls, remembered in
  `localStorage` between visits. Left: which sections to show, plus task state (in progress / open).
  Right: **project scope — Customers / Own / Dev** — which drives the whole right pane including the
  hours chart (billable = customer work, internal = own + Dev), plus which sections to show. A group can
  never be emptied — turning the last chip off turns them all back on. The **stat tiles stay global on
  purpose**: they are the unfiltered glance, so a filter can never hide a total from you.
- `/api/launch` takes three modes, all confined to `C:\Dev`: `claude` (new Windows Terminal running
  `claude` rooted at a project — which is what makes that session's time attribute to it, and which
  can carry an initial prompt), `code` (open the folder), `file` (open one file). Anything else is
  rejected.
- **Needs triage** sits directly under the tiles: every unchecked `ops/TODO.md` item with its age and a
  *Make it a task* button that starts a session seeded with `/task <item>`. It is the ICOR Input→Control
  step made visible. The page cannot tick the item off — do that in `ops/TODO.md` when the task exists.
- **Open tasks** rows open the task itself (What / Why / Context / full Log / activity + ADO id), with
  *Open task file* and a link across to its project.
- A project drawer's **Status check-in** button launches a session at that project seeded with
  `/checkin` — the one-category-at-a-time interview that updates its `CONTEXT.md` (see `AGENTS.md` >
  *Dashboard* > *Check-in*). Use it when arriving cold; use `/handoff` when a real session just happened.
- Everything on the page is derived. To change what it says, change the source: the project's
  `CONTEXT.md` (status, last worked, next actions, blocked on), its `CLAUDE.md` `## Identity`
  (`fno_code`), the task files, or the timesheets.
