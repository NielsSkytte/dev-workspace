---
id: eval-20260909-warehouse-git-skill-header-gap
ts: 2026-09-09T09:40:00Z
type: evaluative
scope: workspace
source: session:013vShXhG3vYkCCgx6L6cwY5
tags: [evaluation, skills, fabric-warehouse-git, fabric-deployment]
status: distilled
description: "Skill evaluation 2026-09-09: fabric-warehouse-git lists the Auto Generated header as a trigger but did not fire on a repeated DmsImportDatabaseException, and it lacks the two facts that settled the case - the header is Fabric's, and an LF-terminated header is the trigger for the mangling"
---

## `fabric-warehouse-git` - did not fire, and has a gap

Trigger context: the user pasted a `DmsImportDatabaseException ... Incorrect syntax near '-'` from
Update from git for the fourth time and asked what the `Auto Generated (Do not modify)` string is.
Both strings are in the skill's own trigger list. The skill was read manually, not auto-invoked.

What it had: failure 6 (hash derives from Fabric's parsed model, cannot be recomputed) - correct
and useful. What it lacked: that the header is Fabric's serialiser output (provable from any
commit-from-workspace diff), that Fabric writes it CRLF-terminated on an otherwise-LF file, and
that an LF-terminated header is what makes the next workspace commit produce the `- Auto Generated`
line. The session derived all three from repo history and negative tests with a local DacFx build.

Action: fold the three facts and the local-build gate into the skill (Next in the session log).
`fabric-deployment` also names `DmsImportDatabaseException` as a trigger and did not fire; the
case was a git sync, so its silence was correct by its own boundary.
