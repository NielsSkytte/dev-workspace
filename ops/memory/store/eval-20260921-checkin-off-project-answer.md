---
id: eval-20260921-checkin-off-project-answer
ts: 2026-09-21T10:40:00Z
type: evaluative
scope: workspace
source: /log
tags: [skill-evaluation, checkin, capture-turn, memory-hygiene]
status: distilled
description: "/checkin on Matas took an answer meant for Carl Ras (Marketo delta write-back) into a Matas thread; it was caught by the names in it, not by the routine. Separately, capture_turn.py again stored skill bodies (/checkin, /log, /switch-task) as the User field"
---

**`/checkin` has no project-fit check on a typed answer.** At the Matas check-in, the owner's
answer to the regression-detection thread was about Marketo, Fivetran/Census, Benno and 130,000
records - Carl Ras datahub material. The assistant caught it because none of those names occurs in
the Matas record, asked where it belonged, and sent it to the Carl Ras INBOX with `/brief`. The
routine itself only says "if an answer is ambiguous, ask one more card"; it does not name the case
of an answer that belongs to another project. Inference: the owner had several sessions open.

**Capture gap recurs.** Sentinel flagged the `/checkin`, `/log` and `/switch-task` skill bodies
captured into the User field (09-18 and 09-21), the same pattern as
`eval-fabric-deployment-skill-missed-valueset-trigger` (2026-08-30) and the 09-17 flags. Five empty
Carl Ras turns on 09-21 ("no text extracted"). The fix belongs in `capture_turn.py`'s User
extraction, not in single records.
