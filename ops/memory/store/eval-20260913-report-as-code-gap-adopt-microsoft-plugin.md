---
id: eval-20260913-report-as-code-gap-adopt-microsoft-plugin
ts: 2026-09-13T21:00:00Z
type: evaluative
scope: project:customers/Aeven/AtomicServiceNow
source: /log
tags: [skills, fabric-front, pbir, skills-for-fabric, q, roster]
description: No house skill or agent could author a Power BI report as code; the fabric-front agent named the vendor skills but none was installed or readable, so Q adopted Microsoft's powerbi-authoring plugin instead of writing a skill
status: distilled
---

Trigger: Niels asked for a simple report on `Model_ServiceNow` built from code and to research
the tooling. What happened: the roster had nothing that fires on report authoring; a vendor
submodule pinned at an old version was never read by the harness and `/update-skills` assumed
copies into `.claude/skills` that were never made. Q's decision: adopt Microsoft's
`skills-for-fabric` > `powerbi-authoring` (installed at user scope by Niels the same session),
update `fabric-front` to point at it, no house PBIR skill. The report was then built following the
plugin's templates and validated with its CLI on the first pass. Follow-up: `/update-skills` is
redundant and should be retired or rewritten.
