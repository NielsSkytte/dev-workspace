---
id: dataverse-writeback-from-fabric
ts: 2026-09-02T16:30:00Z
type: semantic
scope: customers/Carl-Ras/datahub
source: session:09fdd4d6
tags: [dataverse, fabric, outbound, atomic, reverse-etl]
status: distilled
description: "Writing Fabric curated data into Dataverse: alternate-key addressing is the whole mechanism, Web API $batch beats UpsertMultiple on failure isolation, and the Atomic outbound layer needed no new plumbing"
---

Second reverse-ETL stream on the Carl Ras platform, after Marketo. Target is the **standard
Dataverse `account` and `contact` tables** in `carl-ras-dev.crm17.dynamics.com`, feeding a D365
Sales/Service app that Pingala is building (unmanaged solutions `CarlRasSales`, `CarlRasService`).

**The mechanism is ordinary HTTP.** No connector, no sync engine. One `PATCH` per row, addressed by
business key rather than GUID:

```
PATCH /api/data/v9.2/accounts(accountnumber='00418')
```

**The alternate key is the entire trick and the entire dependency.** Without one, that URL does not
exist and every row returns 404. A Dataverse alternate key **cannot be altered — only dropped and
recreated** — so the key and the view's company/scope filter are one decision, not two. A key whose
index is still `Pending` fails exactly like a missing key.

**`$batch`, not `UpsertMultiple`.** Up to 1,000 operations per request; each record is a
**top-level part, never a changeset**, because a changeset is atomic and one bad row would roll back
the rest. `Prefer: odata.continue-on-error` is required or the batch stops at the first failure.
Responses come back in **request order**, which is the only key from a response back to its input.
Line endings must be **CRLF** throughout — bare LF gives `System.ArgumentException: Stream was not
readable`.

**Parent links bind on the alternate key too**
(`"parentcustomerid_account@odata.bind": "/accounts(accountnumber='20022900')"`), so accounts must be
written before contacts.

**The Atomic outbound layer absorbed this with no new plumbing.** A new view in
`viewoutboundtransform` is discovered and materialised by `PL_Transform_Curated_Outbound` on its
own; adding an outbound table is one view and nothing else. The layer built for Marketo generalised
on first reuse.

**Not a full-row overwrite.** The app writes these rows too (`cr_overridecontactinterval` is a user
toggle), so the push owns only the columns it stamps and an unknown is **omitted**, never sent as
null. `notebookutils.credentials.getToken` has **no Dataverse audience** — only `storage`, `pbi`,
`keyvault`, `kusto` — so a secret or a Fabric Connection is unavoidable from a notebook.
