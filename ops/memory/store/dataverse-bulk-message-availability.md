---
id: dataverse-bulk-message-availability
ts: 2026-09-02T16:30:00Z
type: semantic
scope: workspace
source: session:09fdd4d6
tags: [dataverse, documentation-drift, verification]
status: distilled
description: "Microsoft documents Account and Contact as NOT supporting CreateMultiple/UpdateMultiple; a live environment registered both - bulk-message availability is per-environment and must be queried, never read off the page"
---

Microsoft's *Optimize performance for bulk operations* page names Account and Contact as core tables
that **do not** support the bulk operation messages. Measured in the Carl Ras DEV environment on
2026-09-02, `sdkmessagefilters` returns registrations of **both** `CreateMultiple` and
`UpdateMultiple` for `account` **and** `contact` — and a table supporting both supports
`UpsertMultiple`.

```
GET /api/data/v9.2/sdkmessagefilters?$select=sdkmessagefilterid
    &$filter=sdkmessageid/name eq 'CreateMultiple' and primaryobjecttypecode eq 'account'
```

**Availability is a property of the environment, not of the documentation** — and the drift runs in
both directions, so query it before designing around either answer.

It did not change the design: `$batch` was chosen anyway, because `UpsertMultiple` returns `204`
with no per-record result and rolls the whole request back on a single bad row, while `$batch`
reports per operation and isolates the failure. **When an integration needs an audit trail, the
per-record result matters more than the throughput.**

Related: duplicate-detection rules are irrelevant to an API push — detection is **suppressed by
default** on Web API create/update and only runs with `MSCRM.SuppressDuplicateDetection: false`.
Seven rules were Active and Published here and are correctly ignored.
