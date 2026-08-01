---
id: carlras-marketo-source-findings
ts: 2026-08-01T00:00:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: session:9ac996f0-d2cc-4caa-a6c8-e7f774f19536
tags: [project, marketo, extraction]
status: distilled
description: "Carl Ras Marketo as an inbound source: mechanics all proven, but the account bridge is empty and no ERP key exists on the person"
---

First real Bulk Extract run against Carl Ras Marketo `569-TGK-793` (2026-07-31, 13 jobs, ~2.5 MB
of the shared 500 MB/day). Full detail in `design/MARKETO_EXTRACTION.md` v0.2; the durable
conclusions:

**The mechanics are settled and are not the problem.** Read-Only Lead / Activity / Custom Object
all proven by completed jobs. The **`updatedAt` filter IS available** on this subscription —
proven by custom-object extracts, which is the strictest test since custom objects offer no
`createdAt` at all. The v0.1 fallbacks (Change Data Value replay, periodic full re-extract,
static-list scoping) are therefore unnecessary. Activities are ~5 MB/day, ~170 MB per 31-day job:
**not** the constraint the 500 MB ceiling implied; a backfill to 2021 is weeks, not months.

**Churn is a batch job, not users.** ~12% of the base moves per day (a floor — an extract holds
only each person's *latest* update), ~68% within a week. Updates cluster into 07:08-07:13 daily
plus small 11:00/14:00 runs, and hit year-old records with the same signature as fresh ones. So
**daily incremental is worth it, weekly degenerates to a near-full extract.**

**What blocks it is the data, not the API.** `account_c` and `accountLink_c` — the two objects
v0.1 called the materialised account identity model — are **empty** (0 rows across three windows
including their 2021 creation month, while controls returned rows). Only `orderLine_c` and
`purchase_c` of the eight custom objects hold data. And **no ERP key is populated on the person**:
`messageAccountNo`, `debitorGroup`, `aXUpdatePermission*` all empty across 995 rows. Account data
exists only denormalised onto each person (`accountName`, `accountSegment1`, `totalSalesAccount*`).
Email is the only field on 100% of rows.

**Why:** v0.1 asserted the account model was materialised on the strength of `describe` calls.
Describe proves a schema exists, never that it holds rows — the §4 caveat said so and the §5.1
claim contradicted it anyway. Generalises: **schema is not data; verify populated-ness separately.**

**How to apply:** the open question is no longer "can we extract" but "is it worth extracting".
Two checks, both doable from our side with no Impact input and no further extraction: match the
995 extracted emails against AX09 contact/debitor emails for a bridge match rate, and compare the
account/order fields against AX09 to find what Marketo merely re-exports (0 of 227 person fields
are `crmManaged`, so none of it arrived by native sync — AX09 is the likely origin). Marketo's
genuinely unique contribution looks like the engagement stream plus its own scoring/segmentation;
`1 Visit Webpage` + `3 Click Link` are 47% of activity volume and duplicate the GTM feed.
Two ingest gotchas: bulk CSV writes the literal string `null` for empties, and activities arrive
as envelope columns plus an `attributes` JSON blob — the same shape as GTM events, so the Raw
flattening pattern carries over. See [[gtm-medallion-build]].
