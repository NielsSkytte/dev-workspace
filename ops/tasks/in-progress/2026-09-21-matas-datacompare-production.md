---
title: DataCompare after PoC approval (production)
status: in-progress
created: 2026-09-21
project: customers/Matas/DataCompare
owner: self
priority: normal
blocked_by:
activity: 110383        # consultant activity on Task-72114 -- F&O derives it from the task (owner, 2026-09-29; was 111953)
fno_task: Task-72114
customer_ask: dropped
waiting_on: Matas (Prod resource group, app registration, group)
resume_on:
source: checkin
---

## What
All DataCompare work after the PoC approval on 2026-09-14: move to production, the customer entity,
the master switch to GFO, and getting Matas's people onto the app.

## Progress

**Now (2026-11-11):** UAT app live since 2026-11-10: https://zealous-rock-09f016303.6.azurestaticapps.net
(swa-datacompare-uat, rg-datacompare-weu-uat, app reg bce553fe). Interim (owner): deployed `-Environment prod
-AppEnvironment uat`, so it shows Prod data; the UAT group is in dc_uat and dc_prod. Sign-in loop fixed (anonymous
redirect.html), MetaAtomic v2 design with a data-source badge, load about 6 s -> 3 s, Guide tab, method card removed;
fabric `dev` d3bf5c5 pushed. Sara Jeftic (non-admin) signed in and saw data 2026-11-10. Waiting on Matas for Prod.

**2026-10-18:** Prod released 2026-10-18: DB on schema v6 by migrate_v4/v5/v6.sql (the pipeline's SQLDB
step failed twice, CopyOverwriteResult.GenericError, cause unknown); GQL_DataCompare (0d80e0f3) + notebook by
pipeline; Prod run 12:41-12:43 UTC Completed (Vendor 11,609 matched, 40,909 open, 0 rules). Closed Static Web
App (Standard, Entra sign-in, managed identity as federated credential) tested end to end on leita.dk, test
resources deleted; code in GFOERPDataAnalysis `swa/` (dev e4aa606); go-live runbook in prototype/README.md.
Email 07 sent by the owner; awaiting Matas.

**Tried and dropped:** triggers behind GraphQL writes (a GraphQL create fails on a table with a trigger)
-> append-only rows + views. User Data Functions as the API (2026-10-16) -> core in the page.
pushing to `main` (Matas policy needs a PR) -> branch `dev`. `deploy_fabric.py`
upload -> code generated into the notebook. One accept rule per Excel line -> one mapping rule per field.
Pipeline release of SQLDB (fails with a generic error, 2026-10-18) -> migrate scripts against Prod.
SWA Free plan -> Standard (Matas requires a closed page, 2026-10-17).

**Next:**
1. On Matas's Prod resources (resource group, app registration, group): run the go-live runbook for the Prod app
   (prototype/README.md > Static Web App); check a non-admin user and an outsider refused.
2. CNAME `datacompare-uat.matasgroup.com` -> `zealous-rock-09f016303.6.azurestaticapps.net` (owner asks Matas IT);
   then add the custom domain to the SWA and its redirect URIs to the app registration.
3. After Link to Fabric for F&O UAT: UAT comparisons (compare_pair.environment = 'uat'), redeploy the UAT app with
   `-Environment uat`, drop the UAT group from dc_prod. Inference: the notebook may need source configuration for UAT.
4. Diagnose the pipeline's SQLDB deploy failure; until then schema changes reach Prod by migrate script.
5. Customer page with 0 matched: show the missing lists first and say why (offered 2026-10-09, not answered).
6. Rule builder slice 2: missing-record rules, conditions on other fields (DESIGN-custom-rules.md).
7. Master flag MFO -> GFO (agreed for 2026-11-01, not done).

## Needs from customer

- **Matas:** rulings on the big buckets (on-hold All->No 2,497; the `%1` address placeholder; bank
  accounts and person names not migrated; 90 vendors without a GFO address; 38 on-hold vendors not
  migrated). Each ruling becomes an acceptance rule. **Owed.**
- **Matas:** hosting (email 07, sent by 2026-10-18). UAT delivered 2026-11-10 (subscription, rg-datacompare-weu-uat,
  app reg bce553fe, group "DataCompare UAT users"). **Owed:** Prod resource group + Contributor, Prod app
  registration, Prod group; Link to Fabric for F&O UAT.

## Why
Task-72114 is the F&O task for all Matas work after 2026-09-14 (owner, 2026-09-21). Work up to and
including 2026-09-14 books to Task-65904.

## Context
- F&O: project 212-01, activity 110383 (consultant), Task-72114. Task-65904 books to 111953.
- Before this: `2026-09-08-matas-datacompare-engine-app` (Task-65904), closed 2026-09-21.

## Log
- 2026-11-11 - UAT app live (2026-11-10) on Prod data; sign-in loop fix, design v2 + data badge, load ~3 s, Guide tab, method card removed; fabric dev d3bf5c5.
- 2026-10-21 — Customer ask dropped: no longer relevant
- 2026-09-21 - created at check-in; the owner named Task-72114 for all work after 2026-09-14.
  Matas heartbeats on 2026-09-18 and 2026-09-21 before the re-tag carry the engine-app slug and are
  corrected to Task-72114 in the timesheet at /log, never in the heartbeats.
- 2026-10-09 - rule kinds, builder, mapping import and match keys released to Dev (21fdd13); Dev run Completed.
- 2026-10-16 - API split: dc_api.py (core) + relay.py (FastAPI) + udf_shell.py/build_udf.py (Fabric UDF);
  34 golden cases identical before/after; UDF_DataCompare_API live in Dev (fabric dev 586242b), all read
  and error cases identical over REST. Fabric App test not built: tenant setting state unknown, and a
  Fabric App page cannot call a UDF as the user (Rayfin session); route = app function with app identity.
- 2026-10-16 - hosting design: UAT app + Prod app (SWA Standard, custom Entra sign-in, bring-your-own
  Function App with managed identity); ask drafted in emails/07, not sent.
- 2026-10-18 - Prod release: pipeline deploy of SQLDB_DataCompare failed twice (CopyOverwriteResult.GenericError,
  nothing applied); Prod DB migrated with migrate_v4/v5/v6.sql (0 rules in Prod, so the new checks pass); pipeline
  released GQL_DataCompare + NB_DataCompare_Daily; Prod GQL whoami reads Prod DB (d230007f). Prod notebook run
  not started (held for owner). SQLDB pipeline failure cause unknown. swa/ pushed to dev (122f385); outer commit dd3bf12.
  Prod run 12:41-12:43 UTC Completed (Vendor 11,609 matched, 40,909 open, 0 rules). Closed SWA tested on leita.dk:
  setup/deploy scripts, anonymous redirect, managed-identity sign-in, MSAL token + GraphQL call; fixes: az.cmd,
  ID token issuance (AADSTS700054). swa/ e4aa606. Test resources deleted. Go-live runbook in README.
- 2026-10-17 - SWA without API server: JS core over GraphQL, schema v5/v6, 38/38 golden; cross-project findings in own/MetaAtomic/docs/app-hosting-pattern.md; SharePoint hosting superseded (owner).
