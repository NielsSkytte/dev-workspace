---
id: eval-20260831-warehouse-git-skill-miss
ts: 2026-08-31T10:35:00Z
type: evaluative
scope: workspace
source: session:f17772e8-6514-4c38-b590-03daab4595e6
tags: [evaluation, skills, fabric-warehouse-git, sentinel]
status: distilled
description: "Skill evaluation 2026-08-31: fabric-warehouse-git should have fired on the curated drift finding and did not; sentinel fired as mandated and caught two records that would have planted false facts"
---

## `fabric-warehouse-git` — should have fired, did not

**Trigger context:** the session found that DEV's `Warehouse_Curated` diverges from git on three
view bodies while Fabric's `git/status` reports the warehouse clean, and that the affected view had
lost its `-- Auto Generated (Do not modify)` header.

The skill's own description names this territory explicitly — *"drift between a workspace and its
branch"*, *"the 'Auto Generated (Do not modify)' header and its hash"*, *"validating .sql files
before committing them"*, *"why is source control showing the whole warehouse as one item"*. It did
not fire, and I did not invoke it.

**Consequence:** none in output — the finding was measured directly with `OBJECT_DEFINITION` and is
correct. But the skill holds the failure modes for what happens *next* (committing the hand-patch,
DacFx rebuilding a table and emptying it), and that is precisely the decision now sitting open. The
skill would have been most valuable at the point the finding landed, not afterwards.

**Suspected cause (inference):** the session framing was "verify task status", not "get a schema
change through git". The trigger vocabulary in the skill is oriented to *doing* a sync, not to
*discovering* drift during an audit. Worth considering whether its description should also catch
read-only drift discovery.

## `sentinel` — fired as mandated, and earned it

Dispatched on `daily/2026-08-31.md` before distillation per the standing `/log` rule. Checked 17
records, returned **8 flags, 2 must-fix**:

- One record claimed the session had *"corrected several issues in the Fabric and customer repos"*.
  The session was read-only against both, and another record in the same file said so. Distilled
  as-is, that would have planted a false "we write to customer repos" fact in the snapshot.
- One asserted a task was *"complete with no further actions needed"* when PROD promotion and the
  TEST Direct Lake model remain open — a closure claim that would have suppressed live work.

Both were corrected in place with a `[sentinel-corrected]` marker rather than distilled. Two further
flags were the known rule-4 violation (a slash-command's expanded help text captured as the User
body, carrying model-directed instructions and non-ASCII arrows) — recurring, and the same class as
`capture-turn-records-expanded-help`.

**One flag was a false positive:** sentinel questioned "F64" as invented SKU vocabulary. F64 is real
— it appears in the measured job-run error text. The cause is mine: the fidelity context I handed it
listed the session's key figures but omitted F64, so it correctly flagged a specific it had no way to
corroborate. When briefing sentinel, give it the full measured set or tell it which claims are
uncorroborated.

## Observation for the capture hook

Nine task-notification records exist for twelve dispatched agents. Most likely several notifications
landed in one turn, but a silently dropped turn is a memory gap — worth confirming against
`capture_turn.py` if the count mismatches again.
