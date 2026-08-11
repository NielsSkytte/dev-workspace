---
id: eval-2026-08-11-stale-context-restart
ts: 2026-08-11T00:00:00Z
type: evaluative
scope: workspace
source: session:5bbffdc6-903f-456e-9d01-a37807792a96
tags: [evaluation, skills, continuity, session-hygiene]
status: distilled
description: "A session resumed after eight days of other sessions: the in-flight analysis was superseded and nearly re-delivered as new; skills stayed silent again"
---

**The near-miss.** This session began 2026-08-03 mid-analysis (the Marketo→AX09 match) and resumed
2026-08-11 after eight days in which other sessions built the entire Marketo ingest. On resuming I
offered to write up the 08-03 result — a 995-row research-cohort number — as if it were current.
Niels asked for a state check first. It was warranted: Raw already held 31,217 leads, and re-running
the same query on the real population gave **87.0%** instead of 54.8%. The offer would have written
a wrong number into two design documents.

**Rule earned: a long-paused session's in-flight result is a hypothesis, not a finding.** Before
delivering anything computed before the pause, re-check the inputs it was computed from. Elapsed
time is the trigger, not whether the work "feels" finished. The continuity walk covers session
*start*; it does not cover *resumption mid-task*, which is where this fell through.

**Skills: silent again, fourth consecutive occurrence.** The session ran Fabric lakehouse reads,
Delta/OneLake access, medallion Raw-layer questions and an identity/bridge modelling decision, in a
project-rooted session with the roster loaded. `pingala-fabric-platform`,
`medallion-migration-validation` and `semantic` (bridge/many-to-many modelling is squarely its
brief) all stayed silent. Consistent with [[skills-fabric-deployment-late-trigger]] — this is a
trigger-matching problem, now observed across five distinct skills, not an availability problem.

**What did work.** Guardrail 11 fired correctly and stopped real damage: `fab` was authenticated to
the Matas tenant while the session sat in Carl Ras, and the pre-flight check caught it before any
listing was read. That incident produced the tenant shim ([[tenant-scoped-cli-auth]]), so the
guardrail paid for itself twice — once by catching the error, once by motivating the fix.

**Local summarizer fidelity flag.** The `daily/2026-08-11.md` record for the turn "so what to do?"
states *"The assistant committed uncommitted internal repos and prepared the TEST release."* Nothing
had been committed at that point — the reply was a recommendation to commit. The summarizer
converted a proposal into a completed action. Not distilled; recorded here because it is the same
failure class as the 07-31 batch (a summary that inverts or over-claims what the turn contained).
