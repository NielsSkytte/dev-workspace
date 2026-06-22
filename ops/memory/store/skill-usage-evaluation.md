---
id: skill-usage-evaluation
ts: 2026-06-19T14:04:02Z
type: semantic
scope: workspace
source: session:e642cd4e-5e1c-4a28-a96c-9d9f9a890aa7
tags: [project]
status: distilled
description: "Core goal — evaluate which skills fire/don't-fire/help during real work and feed it back into skill revision; the missing evaluative-memory layer"
---

Skill-usage evaluation is a **core wanted capability** for this workspace: treat *which skills fired, which should have fired and didn't (under-trigger), which fired uselessly (over-trigger / low quality), and which fired and genuinely helped* as first-class captured knowledge — observed during real sessions and accumulated into skill description/body revisions over time.

This is the missing **evaluative / reflective** memory layer, on top of the three the workspace already runs: episodic ([[knowledge-flow]] / `sessions.md` — what happened), semantic (`AGENTS.md` + memory files — facts/conventions), and procedural (the skills — how to do things). The evaluative layer is the system judging its *own tools* and feeding that back into the procedural layer.

It mirrors the workspace's existing **raw→distilled** pattern: per-session skill observations (raw) → periodic skill revisions (distilled), exactly like TODO→tasks and `sessions.md`→conventions. It is substrate work (any LLM should run it), AtomicCortex-aligned — see [[atomiccortex-vision]] — not a Claude-harness feature.

Context: Pingala is independently working on memory / knowledge-capture approaches; the user is aware of several specific approaches and wants to explore them. The fact that the company is working on this is itself flagged as capture-worthy knowledge.

**Why:** under/over-triggering and skill quality are invisible unless deliberately observed; without capture, skills never improve from real use.
**How to apply:** when a skill should have fired and didn't, or fired and didn't help, log it as a session learning; periodically distill the accumulated observations into concrete skill edits.

**Foundation (2026-06-19):** this rides on the memory mechanics from [[memory-arch-three-jobs]] — skill observations are just memory records with `type: evaluative` in the same store (raw daily stream -> distilled skill edits). Not a separate system; a record type. Build the mechanics first, layer skill-eval on top.
