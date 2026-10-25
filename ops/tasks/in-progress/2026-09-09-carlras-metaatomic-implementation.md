---
title: Carl Ras — MetaAtomic implementation (lineage, stream matrix and portal running on a schedule in Fabric)
status: in-progress
created: 2026-09-09
project: customers/Carl-Ras/datahub
owner: self
priority: normal
blocked_by:
activity:
fno_task: CarlRData-666
customer_ask: none
source: direct
---

## What
Run MetaAtomic for Carl Ras inside their Fabric tenant, on a schedule, with nothing depending
on a workstation: `NB_MetaAtomic` clones the three DevOps repos, builds lineage, the stream matrix
and the portal from `metaatomic.pyz` in `Lakehouse_Util`, and publishes the pages to
`Files/MetaAtomic/out/`. `PL_UpdateLineage` triggers it daily at 05:30. The stream matrix
document lives in `Fabric-ETL/MetaAtomic/design/`.

## Progress

**Now (2026-10-25):** Pingala base `PL_UpdateLineage` runs end to end in Fabric (13:17-17:31, Completed): clone of AtomicBase via `GIT_PAT_FILE` (Lakehouse_Util `Files/MetaAtomic/git_pat.txt`, stopgap until SPN `d26a0ca0...` is in PingalaGlobal), lineage, DQ. Fixes on the way: publish copy falls back to `fs.put` when azcopy fails (`c52c741`), NB_MetaAtomic on 8 vCores via a first `%%configure` cell, the default node segfaulted (`b2b34ef`); AtomicBase `790a6a6`, `08aa5b4`. Next: SPN into PingalaGlobal then back to `GIT_SPN_SECRET`; Change buttons on CustTable.

**Earlier (2026-10-23):** Carl Ras DEV on engine `dc73fff` (Fabric-ETL `9ed9ae0` pushed, Niels's go; DEV Lakehouse_Util;
app redeployed). Lineage now sees sources in the same or another workspace (shortcuts with hot/cold schema, ingest
pipelines via variable libraries -> `datastore_location`); DQ reaches them in their own workspace and falls back to raw
`hot` (own repo `8d11dcb`, `dc73fff`). Fixes the empty Pingala-base check set (CustTable missing). Base AtomicBase
(Development `4104a4a`) at `Fabric/00 - Services/MetaAtomic`, app item moved there by Niels. Online lineage now takes a
fresh Fabric token per call (`7ba5140`, a long run hit 401); base lineage + DQ rerun in progress. Open: the base
pipeline's git clone has no credential - Niels has no Azure DevOps admin; recommended a read-only PAT in `kvpingaladata`.

**Earlier (2026-10-22, 01:00 Copenhagen):** engine-suggested exceptions (`f25bdc6`) released: Fabric-ETL `5294652` pushed,
pyz in DEV + TEST `Lakehouse_Util`, both apps redeployed (lyric-dove, game-dove). Tonight's runs (`f44edda0` DEV green,
`d35b456e` TEST notebooks green, mail parked) loaded the engine before the upload, so a TEST run `3af465cd` on `f25bdc6`
was started at 00:48 for the first suggestions. **Check builder** built (Niels: a guided interface to create and modify
rules): own repo `1f93be7` + `873b672`, 211 tests; All checks + `#build` wizard, overlay/own-check saving, out-of-date
proposals brought up to date (`packs.replay`). Not released: needs a pyz push to Fabric-ETL + upload + a run (Niels's go).
Local preview: relay on `127.0.0.1:8097` over the DEV run with a scratch store.

**Earlier (2026-10-20):** DEV runs daily and is level with Fabric-ETL main at `f627fb6` (10-19). Lineage is whole: the
10-18 DEV store has raw -> enriched 2,528 and enriched -> curated 881 column edges (the "all views partial" finding was a
stale 10-12 snapshot). `NB_DataQuality` profiles entry, enriched and curated with the AX09 pack, reconciles row counts from
the Delta log, and the run mail arrives (Niels, 10-20). Weighted score made the headline with the mean over tables beside
it (Niels's yes, 10-20): own repo `816661e`, pyz `0.7.0+20261020.816661e` uploaded to Lakehouse_Util and written to the
Fabric-ETL clone, not committed.

**Fabric App (2026-10-20):** tests 1-2 pass in Pingala `NielsWorkspace_Dev` (`own/MetaAtomic` `88ea59f`, findings in
`docs/app-hosting-pattern.md` section 7a): static MetaAtomic page + Fabric SSO; delegated `fabric-sqldatabase` connector
to a separate store, actor = the user's UPN by column default; views read keyless only. Sizing (estimate, inference):
1 page delivery from the daily run into the app (unknown, spike first); 2 one app shell over portal, lineage, stream
matrix, DQ, packs (~1 d); 3 DQ editor writes through the connector, store reshaped to single-row appends, `checkPack`
ported to TypeScript (~2-4 d); 4 Carl Ras store DB + an Entra group with SELECT/INSERT (~0.5 d plus their admin);
5 Carl Ras gates: "Fabric Apps (preview)" tenant setting, sharing "Run and interact". Total ~5-8 days.
Test 3 passes (10-20): a function reads the run's pages from `Files/MetaAtomic/out/` as the app identity, up to 25.9 MB in
6.5 s, so page delivery needs no redeploy and item 1 drops to ~0.5 d (inference); total ~4-7 days.

**Tried and dropped:** cloning as the `Fabric_Datahub` service principal -> `TF401444`, not an org member
(needs a paid Basic seat, org admin required); Graph for the SharePoint publish -> a Copy activity under
Niels's account (09-09); the pyz in the lakehouse plus an upload script -> the pyz travels in the
`Fabric-ETL` repo and comes with the clone (09-09 afternoon); DevOps Basic seat for `Fabric_Datahub` ->
staying on PAT (09-21); the engine path for `NB_DataQuality` through the `/lakehouse/default` mount (`8d41e79`, 10-12) ->
the notebook has no default lakehouse, replaced by an `abfss://` copy (`d7f2424`).

**Next:**
1. Pyz pushed to Fabric-ETL main `0b52618` (10-20); no Update from git needed (the notebook diff is a comment). Check the
   next run's page and mail show the weighted headline and compare with the previous run's weighted score.
2. Fabric App build: plan in `own/MetaAtomic/docs/fabric-app-build-plan.md` (6 phases, ~6.5 d + Carl Ras admin);
   decided 10-20: app in Fabric-ETL-DEV for now, pack check in browser JS, develop against Carl Ras real data and show
   them early. `service_drift.py` now never commits a new item of a type the branch does not hold. **Phase 1 live at
   Carl Ras (10-21):** item `MetaAtomic` in Fabric-ETL-DEV, https://lyric-dove-2894621aef-westeurope.webapp.fabricapps.net ,
   showing the daily run's index, lineage (28 MB), data quality (7.7 MB) and stream matrix (own `fcc0f6a`). Not yet seen
   in a browser. Parity test (`fabric-app/scripts/parity.mjs`): 0 differences between the app and the pages on their
   own (DQ 8 views 188 checks, index, stream matrix, lineage); `#` links fixed (`19bceba`, `8394570`).
   **Phase 2 done (10-21, own `53d3c64`):** DQ store schema 4 is append-only (events + state views), pack overlays
   added as the customer level beside Pingala's versions (Niels 10-21); a schema-3 store reads the same after
   migration on SQLite and the Pingala Fabric SQL store. Plan now ~7.5 d (phase 3 +1 d for overlays).
   **Phase 3 done (10-21, own `62cb1fe`):** `packcheck.js` = `packs.check` on 106 golden cases; overlays run store ->
   `design/dq_packs/<name>.overlay.json` -> engine.
   **Phase 4 done (10-21, own `a9ce7ca`):** in the Pingala app the DQ page writes the store through the app (delegated
   connector); `scripts/e2e-dq.mjs` ran each call once, every row's actor the signed-in user. **Phase 5 done (own
   `984d85a`):** role `metaatomic_page` (read + append only, trigger sets who/when/status); tested with a throwaway
   principal, removed after. **Phase 6 started (10-21, Niels's go):** `MetaAtomic_Store` in Fabric-ETL-DEV Util/Data
   (schema 4), app item moved to Util; engine `0.7.0+20261021.984d85a` in Lakehouse_Util and pushed with
   `PL_UpdateLineage` STORE = MetaAtomic_Store (Fabric-ETL `abd16e6`). Next: Update from git (Niels's go; PL_UpdateLineage
   conflicts with workspace noise, take the branch), a run loads the store, Carl Ras rayfin login, app redeploy against
   the Carl Ras store. Entra group later (Niels; not via Kasper, who is CIO).
   **Store loaded (10-21):** the manual PL_UpdateLineage run failed in NB_DataQuality (Python kernel segfault, exit -11,
   in `profile._is_date` strptime after 46 min, before anything was written); a rerun of NB_DataQuality alone passed and
   loaded run 2026-10-21 02:27 into MetaAtomic_Store (score 68.3, 1,740 findings). Both apps read it. Watch whether the
   crash recurs on the 05:30 schedule.
   **UI v2 (10-21, Niels's ask, own `accd9e5`):** redesign of layout, navigation and wording for business users,
   deployed beside v1 as item `MetaAtomic_v2` (https://fast-quay-164f388232-westeurope.webapp.fabricapps.net), same
   pages and store. **Niels chose v2 (10-21):** v2 is the app default (own `71e46d8`), deployed to both items; sidebar
   folds to icons; Power BI layer renamed Semantic. The 05:30 scheduled run on 10-21 completed (no DQ crash). Open:
   whether to delete the now-duplicate `MetaAtomic_v2` item; engine rendering v2 natively (later). Noted for later
   (Niels): a browser's saved sign-in is refused after a redeploy (401 / connector error until a new profile); fix =
   drop the saved session on 401 (build plan, own `64be47e`).
   **Engine renders v2 (10-21, Niels's yes):** own `76ffa01`, pyz `0.7.0+20261021.76ffa01` pushed to Fabric-ETL main
   `c7e468b` and uploaded to Lakehouse_Util; PL_UpdateLineage run `d50ff763` started 13:2x. `MetaAtomic_v2` item to be
   deleted by Niels in the portal (API refuses app items). Known-limitation round trip still to show.
   Runs from 13:00 fail in NB_MetaAtomic: AADSTS50076 (MFA) on the owner's (Niels's) user token; a pipeline runs as its
   LastModifiedBy, not the caller. Re-stamp to the SPN is refused: Outlook connections cannot be shared ("not allowed to
   add principals for MicrosoftOutlook"). Copy Lineage removed (DEV + Fabric-ETL `dbb40db`; no SharePoint, Niels).
   Simpler DQ page (Niels's feedback, own `3c6bff7`): 5 views, overview > table > issue, Timeliness counted where
   inherited. Deployed (Niels's go): pyz `0.7.0+20261021.3c6bff7` (Fabric-ETL `74081a3`, Lakehouse_Util), app
   redeployed. Run `b2f898e6` (13:08-14:23 local): both notebooks Succeeded, all three pages engine-v2, store run 13:19
   loaded; "Send DQ mail" Failed (connection 67345190 not resolved, DMTS_EntityNotFoundOrUnauthorized). Mail and the
   pipeline's owner/MFA problem parked by Niels ("deal with it later").
   **TEST release (10-21 evening, Niels's go, option A = one MetaAtomic per stage):** PL_UpdateLineage + both notebooks
   resolve `{workspace}`/`{Lakehouse_Util}` and the stage (from ENVIRONMENTS) where they run (Fabric-ETL `f525ccd`, own
   `ffbf747`); DEV updated from git and its run passed both notebooks. TEST's old copy had run daily into DEV's
   Lakehouse_Util; its schedule is off until a green TEST run. Deployed DEV -> TEST (`fabric_release.py`, "Test" OrgApp
   items excluded): PL_UpdateLineage refused for the SPN (Outlook connection), so deployed as Niels and runs as him; rest
   re-stamped to the SPN. Pre-existing in TEST: seed GetEnums fails (Key Vault in Pingala's tenant, since 10-12),
   `VL_ConnectionId.Dataverse_Url` empty. TEST store `88bb93b1`, pyz in TEST Lakehouse_Util, TEST app item `e2d2e985`
   https://game-dove-a742e1b587-westeurope.webapp.fabricapps.net . Run mail now fails on
   `DMTS_OAuthTokenRefreshFailedError` (the Outlook connection's own sign-in expired; Niels to re-enter).
   **Check editing A + AX09 (10-21, Niels's yes):** own `7167b9a` (editor saves only the customer's changes as an
   overlay on Pingala's version; clash screen keep-yours/take-Pingala's and rebase), ax09 is Pingala's pack 1.0
   (AX 2009 wording, own `0445c26`, `1e7b61f`); Carl Ras's differences in `ax09.overlay.json` (Fabric-ETL `280b028`,
   pyz `1e7b61f` in DEV). DEV store: Pingala ax09 1.0 + overlay `1.0+local.1` standard; the stale published
   `design/dq_packs/ax09.json` in DEV Lakehouse_Util deleted (NB_MetaAtomic copies but never removes pack files:
   fix in the notebook later, needs an Update from git). Same release in TEST (Niels's go): pyz `1e7b61f` in TEST Lakehouse_Util, TEST store
   switched the same way, stale published ax09.json deleted; run `fcfcaff1` started before it, so the next TEST run is
   the first on the new engine. Outlook connection "MicrosoftOutlook EXT_NSKC" re-signed by Niels (10-21 evening).
   TEST run `fcfcaff1` (old engine): both notebooks Succeeded, mail Failed `DMTS_EntityNotFoundOrUnauthorized` (TEST's
   pipeline principal has no access to the connection; inference: the item was created by the SPN). DEV run `b5a8798c`
   failed: `KeyError '_same_as_engine'` with an overlay in force; fixed own `9370171`, pyz to DEV + TEST and Fabric-ETL
   `785a284`. NB_MetaAtomic now removes published pack files no longer in git (Fabric-ETL `ccd206b`, own `24c315f`):
   DEV updated from git (Niels's go), notebook deployed to TEST as the SPN. Reruns DEV `e151c12c`, TEST `e30b4941`.
   **Green in both (10-21 21:47):** DEV `e151c12c` and TEST `e30b4941` ran both notebooks on engine `9370171` with
   ax09 1.0+local.1 (overlay on Pingala 1.0) for 90 tables; TEST store run 19:43 loaded (score 73.9, 159 tables). DEV
   mail succeeded after the re-sign; TEST mail still `DMTS_EntityNotFoundOrUnauthorized`. TEST 05:30 schedule re-enabled
   (owner SPN). Released after the runs: own `a166b27` (score card bands; Report impact scores along the lineage; a
   stale row check fails every row, DEV headline 68.4 -> 53.2 on the same data, Niels's yes), pyz in DEV + TEST,
   Fabric-ETL `a0a6a6e`; shows from the 05:30 runs.
   **Issue quality (10-21 late, Niels's yeses):** impact follows use for general rules (own `8f503af`: a generic
   finding on a column used nowhere past raw is low; notes recognised by content; plain "why" texts). AX09 check set 1.1
   from a review of the rules (own `d4e1da3`, `62ef018`, `5e66e88`; report in the session scratchpad): AX general noise
   rules low/accept, new field checks (company, cust/vendtrans, invoice voucher/account/currency, unit per company,
   exchange rate > 0, names, country, payment terms, VAT number), SALESID check on ORIGSALESID; financial dimensions
   open (engine change). Exceptions as data (`exempt_when`); a draft local adjustment is a proposal the customer
   confirms on the page. Released: pyz `5e66e88` DEV + TEST, Fabric-ETL `e6d5968` (ax09.overlay.json = 1.1+local.1).
   Both stores: ax09 1.1 + 1.1+local.1 standard, 1.1+local.2 (customer group 989 may have no VAT number) a draft
   waiting for Carl Ras, the separate VATNUM expectation retired. Runs DEV `f44edda0`, TEST `d35b456e`.
   **Rule (Niels, 10-21):** analytics of actual data is always the engine; agents build the engine but never create a
   customer rule (memory `feedback-engine-not-agent-finds-exceptions`). The handwritten 989 draft (1.1+local.2) was
   withdrawn in both stores. In flight at session end: a fork building engine-suggested exceptions (failures
   concentrated in one value of a low-cardinality column, live counts, Confirm/Dismiss, stored per run; synthetic
   tests only) in own repo; runs DEV `f44edda0` / TEST `d35b456e` on AX09 1.1. Suggestions built: own `f25bdc6`
   (`suggest.py`: >= 80 % of >= 10 failures in up to 3 values of a 2-50 distinct column, >= 99 % pass elsewhere, values
   cover <= 50 % of rows; Confirm writes an `exempt_when` local adjustment, Dismiss is an event; `dq.suggestion` table;
   205 tests). Next: check those runs and pages; release `f25bdc6` (pyz DEV + TEST, Fabric-ETL push) and redeploy both
   apps (Dismiss needs it) on Niels's go. Open: suggestions only for check-set checks with an id.
   **Mail parked (Niels, 10-21):** "easy fix later"; focus on deployment and functionality. A run counts as green when
   both notebooks succeed, whatever the mail step does.
3. **Copy Lineage** is parked: Niels will replace it with something else once the main work is implemented (10-20).
4. `Landingzone-ETL` contributes 0 nodes — engine work, tracked in `own/MetaAtomic`.

## Needs from customer

- None.


## Why
The pages are the customer-facing record of what the platform holds and how far each stream has
come. A copy that ages on a laptop is not that record.

## Context
- `customers/Carl-Ras/datahub/CONTEXT.md` > MetaAtomic section (prerequisites, blockers, the GTM gap)
- `own/MetaAtomic/README.md` > Running it in Fabric
- Engine work that this deployment drove is R&D and is logged in `own/MetaAtomic/CONTEXT.md`
- Related: 2026-08-11-carlras-operation-hardening (the daily run must stay green)
- **Hosting (2026-10-20): at Carl Ras MetaAtomic incl. DQ and lineage is hosted as a Fabric App** (Niels). MetaAtomic
  stays deployable to either host, chosen per deployment (Matas: SWA). Design base:
  `own/MetaAtomic/docs/app-hosting-pattern.md` (SWA vs Fabric App, the module schema is the API, tested facts),
  `customers/Matas/DataCompare` (the SWA build and Matas Dev GraphQL/SSO tests), `datahub/INBOX.md` 2026-10-17 note.
  Test app: `own/MetaAtomic/fabric-app` (Rayfin `dataapp` template). Carl Ras capacity is West Europe (Fabric Apps
  available there per the pattern doc); whether the "Fabric Apps (preview)" tenant setting is on at Carl Ras is unknown.

## Log
- 2026-09-09 — created, in progress: deployed, first run by hand completed, schedule set
- 2026-09-09 — time: 39 min of session f0ca3d4e (05:40-08:00 UTC, rooted in own/MetaAtomic) attributed here by Niels; the remaining 52 min of that session go to 2026-08-11-carlras-operation-hardening. Apply when 2026-09-09 is rolled up: the heartbeats carry own/MetaAtomic.
- 2026-09-16 — brought onto the Progress shape (Progress + Needs from customer, `fno_task` / `customer_ask` set, `activity` blanked per CLAUDE.md task-always rule); no facts changed. Card: `customers/Carl-Ras/datahub/CONTEXT.md`.
- 2026-09-21 — check-in: staying on PAT; DevOps seat ask dropped. Engine 0.7.0 available locally (2026-09-18). Next: upload to Lakehouse_Util.
- 2026-10-13 — engine 0.7.0 deployed (`3069ba9`); `NB_DataQuality` made to run in Fabric (`8d41e79`, `d7f2424`, `e371d83`); run `a1d06a51` Completed, 92 tables, score 95.0; sqlglot 30.22 regression found (fixed in the own repo, not deployed).
- 2026-10-20 — Progress brought up to date (lineage whole, DQ over three layers, mail works); weighted score made the headline (`816661e`), engine uploaded to Lakehouse_Util; Copy Lineage parked.
