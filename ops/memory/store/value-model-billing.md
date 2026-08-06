---
id: value-model-billing
ts: 2026-08-06T07:30:00Z
type: semantic
scope: workspace
source: session:cc6dd81c
tags: [workspace, time, billing, adr-004, provisional]
status: distilled
description: "Value model (ADR-004): keyboard hours measured + weighted hours derived from tool evidence; five tiers, deliverable classes weighting lines not hours, caps per customer not per day; the multipliers are judgement and T5 is fitted to one point"
---

Second number alongside the timesheet, derived from what a session produced rather than how long
it lasted. Spec in `ops/time/README.md` section 7, reasoning in
`ops/decisions/ADR-004-value-based-billing.md`, implemented by `ops/time/value.py` (derive-only;
`rollup.py` still owns the timesheet and F&O entry). **Status: PROVISIONAL, re-evaluate end of
2026-08.**

**The finding that motivated it.** Over 2026-07-07 to 2026-08-04, 23 working days, 579 turns
(98% matched to transcripts): **13.82 h of billable keyboard time produced 58.00 h on the
timesheet**. The current model therefore already bills at **4.2x** measured production, via idle
gaps, the 5-minute tail and the 0.5 h floor - blindly, with no evidence and no way to explain any
individual number. The value model bills ~8x *with* a file list and a line count behind every hour.

**Keyboard time is measured, not inferred.** A turn runs from the user prompt to its last
production event, **bounded by both the transcript and the heartbeat**: the transcript ends a turn
whose `Stop` never fired, the heartbeat bounds a turn whose segmentation broke on a resumed
session. Intra-turn gaps are capped at 5 minutes - the same rule already used between turns,
applied one level down. 3,052 raw heartbeat minutes become **1,245 active minutes**.

**Five tiers from tool evidence**, multipliers T1 2.0x / T2 3.0x / T3 3.0x / T4 6.0x / T5 25.0x.
T5 is assigned per *stretch* (a subsystem does not fit in one turn): >=600 weighted lines, or one
new file >=300. **The `files >= 8` gate was dropped** - it fired twice in the measured month and
was wrong both times, catching many small config edits rather than a subsystem.

**Deliverable classes weight the changed-line count, never the hours** - the count feeds the tier
gates and the new/rebuild/revision/adjustment call. Knowledge (`CONTEXT.md`, `README.md`, `docs/`,
`wiki/`) at **2.0x** on Niels's call that information is denser per line than code; other `.md`
1.5x; code 1.0x; `ops/memory/` 0.5x; other `ops/` 0.25x; `ops/tasks/`, `ops/time/` and
`ops/memory/daily/` at **0**. The last is zero on fact, not judgement: those records are written
by the local Ollama summarizer in `capture_turn.py`, not produced by the engagement. Before this
rule five of six "deliverables" on a Carl-Ras row were the workspace's own memory records.

**Caps are per customer, not per day** (Niels, 2026-08-06): 9 h per customer per day is the only
hard cap, because the only view a customer has is their own line and customers cannot see each
other. 15 h across all customers is a **soft review flag counting weighted hours, not clock hours**
- it means "check the classifier", never "you worked 15 hours". 24 h is an assertion. Scoping the
cap per customer rather than per day **halved the date-shifting**: 14.50 h moved to 7.75 h. Spill
is `consolidate_week` (`rollup.py:270`) run backwards with two guardrails it does not need - never
cross a month boundary (may already be invoiced), and distance beats the worked-day preference
(without it, hours moved 13 days backwards).

**T5 stays T&M.** Fixed price, deliverable bands and a per-deliverable scope floor were each
proposed and rejected. The reason bands and per-event pricing fail: **a T5 event is evidence that
a subsystem was built, not a deliverable**. 8 genuine events in the month mapped to **6
deliverables**, and the ElementLogic lineage engine alone accounted for three of them - pricing per
event would bill one deliverable three times.

**What is derived and what is judgement** - the distinction is why the ADR is provisional. Derived
and reproducible: keyboard time, turn/stretch boundaries, tier assignment, line counts, classes,
repeat-work calls, T5 detection, caps, spill, the audit record. **Judgement:** the T1-T4
multipliers (Niels's estimate of the acceleration, never tested) and T5 x25 (fitted to one
completed deliverable - see `eval-2026-08-06-fitted-is-not-validated`).

**Known gaps.** High-value/low-line work reads too cheap - a 40-line DAX fix that unblocks a
go-live scores T4, not T5, and nothing in the evidence model can see this. **14% of billable
weighted hours sit in stretches that wrote no file at all** (advisory and analysis), carrying no
deliverable evidence, so no part of the tier model can validate them either.

**Guardrail 7 tension, accepted.** The model reads Claude Code transcripts from
`~/.claude/projects/` - tool-specific, outside `C:\Dev`, not in the OneDrive mirror. Mitigation:
`ops/time/value/` is the durable record and is now backed up; section 7 states the model
tool-neutrally so it can be re-implemented; `rollup.py`, the timesheet and F&O entry stay
independent of it. Transcript retention is a live dependency - days not yet derived are lost if
Claude Code prunes.
