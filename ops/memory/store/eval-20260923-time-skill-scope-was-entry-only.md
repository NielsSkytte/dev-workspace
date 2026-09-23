---
id: eval-20260923-time-skill-scope-was-entry-only
ts: 2026-09-23T12:00:00Z
type: evaluative
scope: workspace
source: /log
tags: [evaluation, skills, time-tracking, fno, knowledge-substrate]
status: distilled
description: "Asked for the skill covering how time is tracked, the workspace had none - fno-time-registration stops at entry and the chain from keystroke to entry figure lived only in ops/time/README.md; a new end-to-end skill time-tracking-to-fno was written and now overlaps the old one"
---

What happened: the owner asked for "the skill we use to keep track of how we use time ...
including how we go from keyboard time to F&O entry", to hand to a colleague. No skill fired,
and none existed for the question. `fno-time-registration` covers only the last link - the
journal - and its description is written entirely in entry vocabulary (register, journal,
Godkendelse, Bogfoer), so a question about capture, attribution or the rollup does not reach it.
Everything before entry was substrate-only: `ops/time/README.md` (736 lines), five ADRs and a
dozen memory records.

Skill observation: the gap was in **scope**, not depth. The knowledge was written down and
correct; no construct carried the chain end to end, so it could not fire and could not be
handed to anybody.

Written: `.claude/skills/time-tracking-to-fno/` - SKILL.md plus `value-and-entry-figure.md`,
`fno-entry.md`, `browser-fallback.md`, `setup-and-by-hand.md`. Self-contained and ASCII-only so
it can be shared outside this machine.

Consequence, open: it now duplicates `fno-time-registration` on the entry link, and `/fno`
still points at the old one. Two copies of a production-ERP runbook will drift. The
recommendation on the table is to delete `fno-time-registration` and repoint `/fno`; the
owner has not answered. See `ops/TODO.md`.

Rule for next time: when a substrate file is the only home for a routine that spans several
stages, a question about the middle of the chain has nothing to fire on. Judge a skill's scope
against the whole chain, not against the stage where the errors happened.
