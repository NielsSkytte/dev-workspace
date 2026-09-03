---
id: eval-20260902-no-dataverse-writeback-skill
ts: 2026-09-02T16:35:00Z
type: evaluative
scope: workspace
source: session:09fdd4d6
tags: [skills, evaluation, fabric, dataverse]
status: distilled
description: "A full day building a Fabric->Dataverse write-back fired zero skills; fabric-warehouse-git had a live trigger (new .sql into a git-connected warehouse) and did not fire, and its 'Auto Generated header' rule was followed only because it is duplicated in the project CLAUDE.md"
---

**No skill fired in this session.** The work was a Fabric-to-Dataverse reverse-ETL build: two new
warehouse views committed through git, two new Fabric items authored, a dry run in DEV.

**`fabric-warehouse-git` had a real trigger and did not fire.** Its description names "adding a
column or view to a Fabric Warehouse travelling through git", "the Auto Generated (Do not modify)
header", and "validating .sql files before committing them" — all three happened. The rules were
followed anyway (no header on a new file, pure ASCII, body starting at `/*`), but **only because
they are duplicated in `customers/Carl-Ras/datahub/CLAUDE.md`**. A customer without that
duplication would have got the failure the skill exists to prevent. Same pattern as
`eval-20260901-no-capability-for-fno-registration`: the guardrail held by luck of context, not by
the mechanism meant to carry it.

**No skill covers Dataverse as a write target.** `fabric-project-access` mentions Dataverse only
for *Link to Fabric* access problems, and `pingala-fabric-platform` covers Dataverse integration
inbound. The genuinely reusable findings from this session — alternate-key addressing, `$batch`
over `UpsertMultiple`, CRLF, the doc/environment drift on bulk messages, `getToken` having no
Dataverse audience — currently live only in a customer design doc and in memory.

**Not yet evidence to build one.** Per the freeze rule this is one occurrence at one customer.
Recorded so a second Dataverse write-back at another customer is recognised as the repeat, rather
than researched again from zero.
