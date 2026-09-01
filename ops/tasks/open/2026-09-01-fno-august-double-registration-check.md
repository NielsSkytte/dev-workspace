---
title: Resolve whether August 2026 is double-registered in F&O — 33,00 h posted outside our six journals
status: open
created: 2026-09-01
project:              # workspace-level (time / finance)
owner: self           # needs F&O access and Niels's judgment on what the pre-existing lines are
priority: high
blocked_by: Browser bridge was down at the end of 2026-09-01; needs a look at F&O directly
activity:
fno_task:
source: session
---

## What
Determine whether August 2026 is registered twice in F&O, and by how much.

## Why
The utilisation page read **33,00 h for August** at a point when all six of our PING journals were
still **unposted** and totalled ~137 h. That 33,00 h therefore came from lines posted **outside**
our journals. Our six journals have since been approved and posted, adding **138,75 h** (PING) on
top. If the pre-existing lines cover the same August days, the month is over-registered by up to
33,00 h — on customer-billable time.

Not yet established as a defect: the 33,00 h may belong to other days, another resource, or a
different measure on that page. It has not been looked at.

## Confounder to keep in mind
`PING-021926` (W32) also totals **33,00 h**. That is a numeric coincidence, not the same figure —
when the utilisation page showed 33,00 h, W32 stood at 24,75 h. Don't let the collision short-circuit
the check.

## How to check
1. Timekladde → set `Vis` to **Bogført**. List every August 2026 journal beyond our six
   (`021924` `021926` `021928` `021953` `021954` `021975`) and PNO1 `004431`.
2. For each, open `Linjer` and note the dates, project ids and hours.
3. Compare against `ops/time/timesheet/2026-08/` and the dashboard's August F&O-entry figures.
4. If days overlap → decide what to reverse (`Tilbagefør`), and re-check the month total.
5. If they don't overlap → nothing to fix; the utilisation figure was simply lagging, and the
   August total is 145,00 h + whatever the pre-existing lines legitimately add.

## Context
- August closed at **145,00 h** — PING 138,75 (six journals, approved then posted by Niels) + PNO1
  `004431` 6,25 (already posted).
- Timesheet measures **125,00 h of 120,00 h** (104%) after the vacation week — see
  `ops/memory/store/time-shortfall-can-be-in-the-target`.
- Approve-vs-post and why utilisation lags: `ops/memory/store/fno-month-close-approve-not-post`.
- Session narrative: `ops/log/sessions.md` > `## 2026-09-01`.

## Log
- 2026-09-01 — raised at wrap-up when Niels asked when we closed the 33-hour week. The question
  surfaced that the utilisation figure predates our journals. Deferred to 2026-09-02 by Niels
  (*"vi kigger på det i morgen"*); the browser bridge was down and nothing was verified.
