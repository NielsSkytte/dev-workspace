---
id: harness-review-findings-2026-09-16
ts: 2026-09-16T14:45:00Z
type: evaluative
scope: workspace
source: /log
tags: [harness, review, hooks, skills, agents, parked]
description: Findings of the 2026-09-16 harness review, parked to be taken one by one: Tier A cleanups (vendor submodule and /update-skills, four over-limit skill descriptions, cleanupPeriodDays, MEMORY.md, CLAUDE.md size, snapshot selection) and Tier B decisions (sentinel and daily capture, unused agents, ADR-004).
status: distilled
---

Measured: hooks cost about 0.6 s per turn and 0.65 s at startup; first-turn latency median 5.3 s vs 9.6 s
for later turns, so startup slowness is the model reading (AGENTS.md about 14k tokens per read, CONTEXT.md
up to 140 KB in slices, task-selection round trips), not the hooks. The day brief and the card address the
reading; these remain:

Tier A (cleanups, low risk): remove `.claude/vendor/skills-for-fabric` submodule, `BUNDLES.md` and
`/update-skills`, repoint agents at the `powerbi-authoring@fabric-collection` plugin; trim the four skill
descriptions over the 1536-char limit; `cleanupPeriodDays` 365 (transcripts are the stall evidence and
vanish after 30 days); drop `store/MEMORY.md` and its /log step (the index duplicates frontmatter); shrink
`CLAUDE.md`; make `build_snapshot.py` select by recency and scope, not alphabet.
Tier B (decisions): whether sentinel and the per-turn daily capture earn their cost; delete the unused
agents m, content, fabric-front (no spawn on record) or keep as routing docs; ADR-004 value-model
re-evaluation is overdue; `/log` still mandates sentinel; three name-only skills are unexplained; the
project-root junctions may be redundant now that commands resolve, but customer folders are separate repos -
test before removing.
