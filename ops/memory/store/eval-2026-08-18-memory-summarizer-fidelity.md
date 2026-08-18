---
id: eval-2026-08-18-memory-summarizer-fidelity
ts: 2026-08-18T21:45:00Z
type: evaluative
scope: workspace
source: session:1515f867-fcac-47e5-97f0-1366fb517bfb
tags: [evaluation, memory, capture-hook, local-model, fidelity]
status: distilled
description: "The local summarizer inverted a 2-vs-27 count and turned a hedge into a prediction in the same session's records - both would have entered the store as fact"
---

Two fidelity defects in `daily/2026-08-18.md`, in records written for this session. Both were
caught by hand-reading before distillation; neither was flagged by anything automatic (sentinel not
dispatched - standing no-subagents-unless-asked instruction).

**Inverted counts.** Record `20260818T2113` reads: *"emptying 29 tables in Warehouse_Enriched_AX09
and 27 in Warehouse_Curated"*. The reply said 29 emptied in AX09 and **2** emptied in Curated with
**27 kept**. The summarizer took the larger adjacent number and attached it to the wrong verb - an
inversion that reads perfectly plausibly and would have entered the store as a data-loss figure
five times too large.

**Hedge promoted to prediction.** Record `20260818T2115` reads: *"will fail due to first-time
execution of Fail activities"* and *"A ping at 05:30 will detail the failure causes"*. The reply
said the run **may** stop early, and asked **Niels** to ping. A modal verb was dropped and an
instruction was reversed in direction.

**Pattern.** Both defects are of the same class: the summary is fluent, locally consistent, and
wrong in exactly the place where the number or the modality carries the meaning. Fluency is not a
fidelity signal, and the shorter the summary the more of the correction burden it silently takes on.

**Standing consequence.** Records touching counts, directions, or predictions get hand-checked
against the conversation before distilling - reading the daily stream is not optional even on a day
with no sentinel run. Related: `capture-turn-records-expanded-help` recurred again today; the
stream's one Markdown heading is an injected skill body (`## Core principle: a deployment copies
definitions, not environments`) stored as a User line.
