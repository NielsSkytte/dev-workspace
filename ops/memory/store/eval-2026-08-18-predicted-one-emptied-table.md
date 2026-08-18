---
id: eval-2026-08-18-predicted-one-emptied-table
ts: 2026-08-18T21:40:00Z
type: evaluative
scope: project:customers/Carl-Ras/datahub
source: session:1515f867-fcac-47e5-97f0-1366fb517bfb
tags: [evaluation, skills, fabric-deployment, fabric-warehouse-git, prediction]
status: distilled
description: "Told Niels one table would be emptied by the DEV->TEST hop; 31 were. The skill named ordinal changes as the rebuild trigger and I did not generalise it to column drops"
---

## The miss

Advising on whether to deploy everything DEV -> TEST, I flagged exactly one data casualty:
`enriched.SalesInvoiceTransactions`, "110 columns reordered -> DacFx rebuilds rather than alters".
Measured after the deploy: **31 tables emptied across three warehouses**, 29 of them because they
lost a single trailing column (`PIN_RowCheck`).

The evidence was in my own diff the whole time - I printed `-cols ['PIN_RowCheck']` for 29 tables
and read it as a harmless drop. The `fabric-warehouse-git` skill names ordinal changes and
`NOT NULL` drops as rebuild triggers; I treated that list as exhaustive instead of as examples of a
wider rule.

**Rule earned:** when a skill lists failure triggers, ask what the triggers have in common before
concluding a case is not covered. Here the common factor is "DacFx cannot express it as an in-place
ALTER", which covers every column-list difference.

## Cost

Low - TEST, and everything is CTAS-rebuildable from raw. But the advice Niels acted on understated
the recovery from "run the chain to refill one table" to "the enriched AX09 layer is empty until the
chain runs". Had this been PROD the difference is a maintenance window versus an outage.

## Skill firing

`fabric-deployment` **did not auto-trigger** - I invoked it explicitly with the Skill tool after
seeing `VariableNotFound`. That is the seventh consecutive session in which the Fabric skills did
not fire on their own, on a prompt containing the exact error string the skill lists as a trigger
(`VariableNotFound`, "a variable library / value set that differs between stages"). Once invoked it
was directly load-bearing: failure #3 named the cause, and its identity/ownership section produced
the `LastModifiedBy` and schedule-owner findings.

`fabric-warehouse-git` never fired and was never invoked - it is the skill that owns the rebuild
rule I got wrong.

## What went right, for contrast

The failure was found by **walking the run**, not by reading status: `GET /jobs/instances` showed
TEST green and showed the CVR sub-pipeline as never having run at all. Only recursing
`queryactivityruns` through each child `pipelineRunId` exposed CVR failing inside a Succeeded
parent. Same pattern as 2026-08-18's other session: the defects came from running the real thing
and reading the real output, not from reasoning about it.
