---
id: eval-2026-08-27-authoring-defects-uncovered
ts: 2026-08-27T10:20:00Z
type: evaluative
scope: global
source: session:50082637-f235-4ee7-be0d-fd881b292a68
tags: [evaluation, skills, fabric-warehouse-git, fabric-deployment]
status: distilled
description: "fabric-warehouse-git and fabric-deployment both fired and both helped this session - but two self-inflicted authoring defects fell in the gap between them, and a tool's own error handling caused a misdiagnosis"
---

Hand-written from the session.

## What worked

`fabric-warehouse-git` fired on the cross-warehouse import failure and its **failure 4** named the
cause and the cure exactly. `fabric-deployment` fired on the DEV->TEST promotion question and its
**failure 1** gave the ordering rule. Both earned their place - a change from the run of sessions
where they stayed silent (`eval-2026-08-21-fabric-skills-silent`).

## What no skill covered

Two defects I introduced, each costing a failed operation:

1. **Hand-wrote the `-- Auto Generated` header** on new serialised `.sql`. Fabric prepends its own
   and eats the leading `-` of the existing one. Failed the TEST deployment.
2. **Put em dashes in SQL comments.** They do not survive the round trip; inside a `--` line
   comment the parser meets a stray `-`. Failed the DEV sync.

Neither is in any skill. Both are now rules in `datahub/CLAUDE.md`, which per
`eval-2026-08-21-fabric-skills-silent` is exactly the place that stops a skill being reached for -
so this is a candidate for `fabric-warehouse-git` rather than a project file.

## A tool that lied

`tools/wh_query.py` reported error 15816 "not supported in distributed processing mode" from its
`cur.nextset()` probe **after** a DDL statement had already applied. I read that as a broken
`dim.Date` rebuild and reported a defect that did not exist. Fixed the tool to break on that code.
**Method note:** when a statement reports failure, check whether its effect landed before
diagnosing the cause.

## A gate that cannot exist

I proposed polling `MemoryLimitMb` before a refresh. It is only ever reported inside the
out-of-memory message, so there is nothing to poll. Retry was the achievable answer.
