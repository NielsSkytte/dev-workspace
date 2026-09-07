---
id: datacompare-shared-backend-two-hosting-tracks
ts: 2026-09-07T12:00:00Z
type: semantic
scope: project:customers/Matas/DataCompare
source: distilled
tags: [project, matas, datacompare, fabric, fabric-apps, rayfin, graphql, sql-database, static-web-app, application-insights, architecture, decision]
status: distilled
description: "DataCompare review app: one Fabric SQL database schema (Rayfin-constrained), one notebook, one App Insights emitter and one page with two thin adapters serve both hosting tracks, Fabric App (preview) and Azure Static Web App; the single non-equal is that a Fabric App creates its own database and cannot attach an existing one. Verified 2026-09-07: page -> local relay -> dc.accept_rule in Fabric, rule application and all counting in SQL"
---

**The loop the customer wants (Thomas at Matas):** daily compare in Fabric -> events in Application
Insights -> alert -> open the app pre-filtered -> accept a value pair with a reason -> rule stored
with who/when -> next run applies it -> resolved event. Consumers are therefore no longer
Pingala-only in v1 (changes [D13]); a Matas reviewer writes rules with identity and audit.

**Facts checked on Microsoft Learn, 2026-09-07:**

- *Fabric Apps (preview)*, built on the Rayfin SDK: TypeScript entities (`@entity`, `@text`, ...)
  generate a **child Fabric SQL database**, a GraphQL API and static hosting on OneLake; deployed
  apps authenticate with **Fabric SSO only**; `@role` policies on claims give row/field rules;
  UUID `id` keys only, `<x>_id` foreign keys, no composite keys, no many-to-many. Needs the
  "Fabric Apps (preview)" tenant setting; **not available in North Europe** (West Europe OK; Matas's
  visible capacities are West Europe). No documented way to attach an existing database.
- *Fabric API for GraphQL*: browser apps sign in with PKCE and the delegated
  `GraphQLApi.Execute.All` permission (admin consent not required); SSO mode passes the user's
  identity to the data source, so Fabric item and database permissions decide who may write;
  mutations on Fabric SQL database supported.
- *Fabric SQL database* mirrors itself to OneLake read-only; docs are mixed on preview vs GA.

**Decision: two tracks on one backend.** Schema `dc` designed under the Rayfin constraints so it
can be declared as entities unchanged; `load_sql.py` / the future notebook write through a
connection string; `appinsights.py` computes events in SQL (run summary, new, resolved, accepted
findings across the two latest runs) and posts to the track endpoint; the page calls only
`Adapter.load / addRule / retireRule / whoami`, so `adapter-local.js` (relay), a GraphQL+MSAL
adapter (static track) and a Fabric App adapter are swappable. Non-equal items to discuss with the
owner: the database moves with the app in the Fabric App track; authorization is entity policies
there vs Fabric permissions in the static track.

**Rules of the backend (owner):** logic lives in the data, the page renders (status and counters
are set by SQL at run time and on accept/retire); rules are **retired, never deleted**, and a
finding keeps its `rule_id`, so accepted findings stay reviewable with reason, who and when;
composite fields are marked as such and grouped Atomic-style (`09 Calculated`).

**Verified end to end** in the browser on real data: accept -> rule row in `dc.accept_rule` with
the Matas account as author -> 5,890 findings accepted by SQL -> agreement 87.1 -> 88.9% ->
retire reopens them. Local run: `pull.py` -> `load_sql.py` -> `relay.py` (FastAPI, contract in
`prototype/API.md`) -> http://127.0.0.1:8080. Target: accessible to people by 2026-11-01, the day
GFO becomes master for vendors and customers.
