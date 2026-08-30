---
id: eval-fabric-deployment-skill-missed-valueset-trigger
ts: 2026-08-30T00:00:00Z
type: evaluative
scope: workspace
source: /log
tags: [skill-evaluation, fabric-deployment, capture-turn, memory-hygiene]
status: distilled
description: The fabric-deployment skill should have fired on a value-set-differs-between-stages failure and did not; separately, capture_turn.py records slash-command help text as if it were a turn.
---

**`fabric-deployment` should have fired and didn't.** The session opened with a pipeline failing in
TEST at submit because a variable library value set differed between stages — a case the skill's
own description names explicitly ("a variable library / value set that differs between stages",
"a pipeline failing at submit with BadRequest and zero activity runs"). It never triggered; the
diagnosis was done by reading the repo directly. It landed correctly, but the skill exists so that
it lands fast. Likely cause is inference, not measured: the user's error string
(`InvalidExternalReferenceConnection` / `Invalid datasourceObjectId`) is not among the strings the
description lists, and it reads as a connection problem rather than a deployment problem. Worth
adding the connection-resolution error strings to the skill's trigger list.

**Capture-side gap in `capture_turn.py`.** Sentinel's review of 2026-08-24 → 08-30 found four of six
daily records had a slash-command **help text** as the User field — the hook captured the command
definition that the harness injects, and the local summarizer then dutifully summarized the
definition as if it were work, inventing completions ("selected a task to track", "committing five
curated memory records"). Those records were dropped rather than distilled. The fix belongs at
capture: filter turns whose User field is a command definition, rather than vetting them every day.

**Sentinel earned its place this round:** six records reviewed, zero safe as-is, three
re-summarized and three dropped. Every flag was a real overstatement — a hypothesis promoted to a
confirmation, a GUID asserted that the turn did not contain, a self-contradictory sentence.
