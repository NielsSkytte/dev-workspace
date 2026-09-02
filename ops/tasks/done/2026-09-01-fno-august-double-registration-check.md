---
title: Resolve whether August 2026 is double-registered in F&O — 33,00 h posted outside our six journals
status: done
created: 2026-09-01
project:              # workspace-level (time / finance)
owner: self           # needs F&O access and Niels's judgment on what the pre-existing lines are
priority: high
closed: 2026-09-02
resolution: not-a-defect
blocked_by:
activity:
fno_task:
source: session
---

## Resolved 2026-09-02 — no double registration
Utilisation now shows **145,00 h** for August: exactly what was entered (138,75 PING + 6,25 PNO1),
not 145 + 33. The 33,00 h read on 01-09 was **our own time, partially aggregated** while the page
lagged behind the posting — not lines from another source. Nothing to reverse.

**The reasoning error worth keeping.** A figure on a lagging report was treated as evidence of a
*separate source* ("that 33,00 h therefore came from lines posted outside our journals"). The
premise it rested on — that the page was current — was never established, and the arithmetic that
seemed to confirm it (W32 at 24,75 h when the page showed 33,00) only proved the page disagreed with
the journals, which is exactly what a lag looks like. **A stale number is not a second number.**
Before inferring a source from a total, establish that the report is current.

## What (original)
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
- 2026-09-02 — closed. Niels: *"nu er alle 145 timer registeret under utilization"*. The figure
  matches the entered total exactly, so the 33,00 h was never a separate posting. No action taken.
