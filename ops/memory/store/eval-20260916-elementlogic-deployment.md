---
id: eval-20260916-elementlogic-deployment
ts: 2026-09-16T12:00:00Z
type: evaluative
scope: workspace
source: /log
tags: [evaluation, skills, email-outlook-ready, writing-voice, microsoft-docs, permissions]
description: email-outlook-ready + writing-voice fired on the handover email and held; microsoft-docs grounded the HTTP connector claim; the permission classifier blocked a read-only production query (Delta-log proof) until the owner allowed it - a day of three-hour engine work with correct skill routing
status: distilled
---

Fired and helped: `email-outlook-ready` + `writing-voice` on `email-lars-deployment.md` (one .md, subject
line, no em dashes; owner made no voice corrections, only content additions). `microsoft_docs_search`
grounded "HTTP connector supports Basic auth and Binary copy" before proposing the vault-free option.
Should have fired, did not: `fabric-pipeline-notebook` was not consulted for the parameter-cell vs
pipeline-parameter question; answered from the build.py record instead, correct but unskilled.
Correction the owner made that a check should have caught: the first handover checklist still carried
PAT-creation, Viewer and schedule steps Lars did not need ("he has the PAT, full access, no schedule
check") and asked for do-then-see steps - the deliverable was written from the runbook, not from Lars.
Harness: the auto-mode classifier denied a read-only production count with reason "Production Reads";
the owner allowed it explicitly and it ran with `dangerouslyDisableSandbox`. Bash heredocs with long
Python bodies failed to parse twice ("unexpected EOF"); writing the script to the scratchpad and running
it worked every time.
