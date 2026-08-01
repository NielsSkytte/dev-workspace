---
id: dashboard-internal-hours-triage
ts: 2026-08-01T12:35:00Z
type: semantic
scope: workspace
source: session:972e353e
tags: [project, reference, dashboard, time-tracking]
status: distilled
description: "Dashboard internal-hours triage: joins each Dev/own stretch to its session, co-worked projects and turn text so internal time can be traced and redistributed; derive-only, choices in localStorage"
---

Built 2026-08-01 to answer "where did the internal hours actually go, and does any of it belong to a
customer?" -- a question the dashboard could not answer at all (it showed `Dev 24.25 h` and stopped).

**The join that makes it work.** The turn-hook writes `id: <utc-ts>Z-<session8>` above every record
in `ops/memory/daily/`, and the heartbeat carries the same `session`. That is the only link between
"time was spent" and "this is what was being said". `rollup.load_heartbeats` dropped `session`;
it now passes it through -- **passthrough only, the rollup must never group by it** (that fragments
stretches; see [[time-reassignment-method]]).

**Co-occurrence filters, turn text decides.** A stretch worked in a session that also touched a
customer project is a *candidate*, not a verdict. Session `8b788acf` co-occurred with Melbye and
Tystofte but was genuinely workspace work (design-lead pass on the `dev-workspace` repo) -- a pure
co-occurrence rule would have moved it wrongly. The panel therefore shows up to 3 deduped user
prompts per stretch and never auto-selects. ~10% of turns are harness noise (skill preambles,
task-notifications, echoed tool output) and are filtered out of the evidence.

**Derive-only holds.** The dashboard still writes nothing to the substrate (Guardrail 7). Choices
persist in `localStorage`, and the left-pane section states plainly "N reassignment(s) saved in this
browser -- not yet applied to any timesheet", so *decided* is never confused with *done*. Two exits:
`Copy plan` (a Project -> Activity -> Task table mirroring F&O) and `Apply in a session ->`, which
launches a session at `C:\Dev` carrying the plan as its opening prompt -- collapsed to one line,
because a newline survives Python's argv quoting but not reliably through `wt`.

**Discoverability was the first thing to get wrong.** It shipped as a text link in a tile footer,
where `.pill-link:hover` painted a light background under light text and rendered it invisible. The
owner could not find it. It is now a named left-pane **section** with its own filter chip. Lesson:
a review surface the user is meant to notice cannot live behind a hover state inside a tile.

**Related liveness fix.** `active_sessions()` reported every entry in `ops/time/active-task` as
active; that file records which tag a *session id* holds and keeps entries 7 days, and knows nothing
about whether the session still exists. Four of six tags were from closed windows -- one had never
emitted a heartbeat at all -- while the alert claimed "time is billing to that task". Liveness now
comes from the last heartbeat, in three states: `live` (within `IDLE_TIMEOUT`, reusing the rollup's
own constant), `idle` (<=12 h, window may be open), `stale`. Last-heartbeat cannot prove a window is
open, so two states would have been a lie in one direction or the other.
