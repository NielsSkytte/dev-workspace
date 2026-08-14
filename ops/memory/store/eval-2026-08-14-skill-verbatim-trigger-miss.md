---
id: eval-2026-08-14-skill-verbatim-trigger-miss
ts: 2026-08-14T12:45:00Z
type: evaluative
scope: workspace
source: session:d96c18e1-0555-475f-a4be-0c76a71e9ca1
tags: [evaluative, skills, fabric-deployment, skills-fabric-deployment-late-trigger, memory-summarizer]
status: distilled
description: "evaluative: fabric-deployment lists DmsImportDatabaseException as a trigger, we hit that exact string, and it still did not fire - fifth consecutive session with Fabric skills silent, now against a verbatim match rather than a paraphrase"
---

Two days of work that was nothing but Fabric warehouse deployment. **No skill fired at any point.**

This is the sharpest instance yet, because it is no longer a paraphrase problem.
`fabric-deployment`'s own description lists as triggers:

> "Invalid object name" or "DmsImportDatabaseException" on a warehouse deploy

We hit, verbatim, in the Fabric portal:

```
Workload Error Code     DmsImportDatabaseException
Workload Error Message  ... File: viewfacttransform/Views/SalesTransactions.sql,
                        Error: Invalid column name 'ContactPersonId'.
```

and pasted it straight into the session. The skill stayed silent. `ObjectNotFoundInCollection`
appeared four separate times across two days; `pingala-fabric-platform`,
`medallion-migration-validation` and `fabric-rename-entity` were equally quiet.

**Why it matters more than the previous four instances.** `skills-fabric-deployment-late-trigger`
(2026-08-11) recorded the same skill failing to fire "across a full day of exactly the work it
describes", and `eval-2026-07-31-skills-available-not-firing` narrowed the cause to trigger-miss
rather than availability. Both involved *conceptual* matches. This one is a literal substring of
the description appearing in the user's message. That rules out description quality as the
remaining explanation and points at the trigger mechanism itself.

**Cost.** `fabric-rename-entity` advertised "removing an import-artifact suffix (e.g. a trailing
`(1)`)". We spent two failed Update-from-git attempts on the theory that `AlternativeChart
OfAccount(1)` was a DacFx shadow table. The actual cause was an `xmla.json` semantic-model
namespace collision. Had that skill fired it would have made things *worse* — following it would
have renamed a legitimate model entry and broken the warehouse. Q has since narrowed its
description to exclude table-name `(1)` and redirect to `fabric-warehouse-git`.

So the fifth silent session also produced the first evidence that a *mis-scoped* skill firing is a
worse outcome than none firing. Trigger precision matters in both directions.

## Second observation: the daily summariser has degraded, badly

Sentinel returned **39 fidelity flags** across `daily/2026-08-13.md` and `daily/2026-08-14.md` —
8 drop, 29 re-summarize — and the verdict *"no record here is safe to distill as-is on the
PIN_RowCheck / Update-from-git thread."*

The 2026-08-11 session flagged **one** such record. This is 39.

Failure modes, in order of frequency:
- **Proposal recorded as completed action** — the exact mode flagged last session. Four instances,
  including "triggered the execution of `PL_MainExecution`" when the user's very next message was
  "cant we fix this without running the entire pipeline?"
- **Superseded diagnoses asserted as fact** — three of my in-session diagnoses were overturned by
  evidence within minutes; the summariser recorded the wrong versions flat, without the correction
  that followed in the next record.
- **Actor inversion** — "The assistant blocked the classifier" (it was the reverse); portal grants
  Niels performed credited to the assistant.
- **Record shape** — three records captured injected skill-file bodies or expanded slash-command
  help as the User line. That is `capture-turn-records-expanded-help` recurring.

**And the coverage gap is the real finding.** Sentinel confirmed that *no assistant body on either
day* contains the 2.57x measurement, the 1,851,644-row permanent loss, the six-failure count, the
two classifier-blocked attempts, or the "8th attempt" milestone. The summariser did not merely
distort the session — it missed everything that mattered about it. Both curated records from this
session were hand-written.

**Rule earned:** when sentinel's flag count jumps an order of magnitude, do not treat it as records
needing repair. Treat the day's raw stream as unusable and hand-write from the conversation.

Related: [[skills-fabric-deployment-late-trigger]], [[eval-2026-07-31-skills-available-not-firing]],
[[capture-turn-records-expanded-help]]
