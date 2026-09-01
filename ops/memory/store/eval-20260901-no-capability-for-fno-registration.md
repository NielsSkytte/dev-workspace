---
id: eval-20260901-no-capability-for-fno-registration
ts: 2026-09-01T15:15:00Z
type: evaluative
scope: workspace
source: session:e15b57a5
tags: [workspace, skills, fno, time, browser, capability-gap]
status: distilled
description: "A full day of month-close ran with no skill covering it - the deferral below applied the repeatability test where the depth test belonged, was overruled, and the capability was built the same day as fno-time-registration + /fno"
---

> **SUPERSEDED 2026-09-01, same day.** The recommendation below - *"don't build one yet, revisit at
> the September close"* - **applied the wrong test and has been overruled by Niels.** It deferred on
> a *repeatability* argument ("revisit next month, if the Excel path works it needs no skill"), but
> the skill axis is **depth**: one demonstrated failure is enough, and this day produced eight, each
> in a production ERP, each corrected by Niels - `activity:` written on Carl Ras lines, `Bogfoer`
> instead of `Godkendelse`, Element Logic hunted in PING instead of PNO1, `Kategori` assumed
> mandatory, `Timer` assumed to recompute, an empty task lookup read as a resolved task, a `--topup`
> of +17,50 h nearly applied against its own evidence, and `0,75` typed into `Rolle-id`. AGENTS.md
> states this explicitly: *"If you defer a skill because it hasn't happened twice, you're applying
> the wrong test."*
>
> The transport observation below was **right and was kept** - it became the skill's doctrine rather
> than a reason not to build. **Built the same day:** the skill `fno-time-registration` (with
> `references/browser-fallback.md`) and the command `/fno`. The skill carries the eight failure modes
> and makes the Excel add-in paste the default with the browser grid as a guarded fallback; the
> command carries the fixed per-period sequence, including a pre-flight for time already registered
> in the period. **No agent was built** - every mid-task decision in this routine resolves to "put it
> back to Niels", which is a rule, not judgment.

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
