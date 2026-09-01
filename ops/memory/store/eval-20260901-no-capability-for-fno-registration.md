---
id: eval-20260901-no-capability-for-fno-registration
ts: 2026-09-01T15:15:00Z
type: evaluative
scope: workspace
source: session:e15b57a5
tags: [workspace, skills, fno, time, browser, capability-gap]
status: distilled
description: "A full day of month-close ran with no skill covering it - the routine is now written down in README 4.1 and the F&O entry column, and the real bottleneck was the browser bridge, not the knowledge"
---

**Skill-evaluation checkpoint for 2026-09-01.** Skills that fired: `/log` only. Skills that should
have fired: none exist. A seven-hour month-close — the single most repeated financial routine in the
workspace, run twelve times a year — has no command, skill or agent behind it.

**Don't build one yet, and here is the reason.** The knowledge half of the gap closed itself today:
`ops/time/README.md` §4.1 now holds the per-customer registration protocol, and the dashboard's
week/audit page produces the exact lines to enter, grouped by customer and date, at the F&O entry
figure. That is the part a skill would have carried. What remains is not knowledge but **transport**,
and transport is where the day was actually lost.

**The bottleneck was the browser bridge.** Across the session: the extension dropped twice, the tab
group was rebuilt three times, screenshots timed out on CDP repeatedly, a *"Permission denied for
this action on this domain"* blocked `pingprod.operations.dynamics.com` until the site was granted,
and the page **rescaled between screenshots** so coordinates went stale mid-sequence. That last one
put `0,75` into `Rolle-id` in a **production** journal (*"Der kunne ikke findes en entydig Resource
category view-post"*); the line was deleted and re-entered. Twice `Kopier` opened where `Linjer` was
aimed, because the toolbar shifts at narrow widths. A failed `Ny` appended to an existing row and
produced `600003600003`.

**So the next capability is a transport, not a recipe.** The dashboard already has *Copy rows*;
F&O's Excel add-in takes a paste. Driving a production ERP grid one coordinate at a time is the
thing to stop doing, and a skill that encoded *that* workflow would encode the wrong one. Revisit at
the September close — if the Excel path works, the routine is two steps and needs no skill at all.

**One method note that did hold.** Every contradictory task id was put back to Niels rather than
guessed: 490→496→490, 493→553, and both `555` and `524` reading as empty lookups. Three of those
were real ambiguities and one was a task that did not yet exist. Guessing any of them would have
mis-billed a customer.
