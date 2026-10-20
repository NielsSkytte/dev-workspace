---
id: metaatomic-fabric-app-spike-20261020
ts: 2026-10-20T13:30:00Z
type: semantic
scope: project:own/MetaAtomic
source: distilled
tags: [project, metaatomic, carl-ras, fabric-apps, rayfin, hosting, decision]
status: distilled
description: "Carl Ras gets MetaAtomic (DQ, lineage, portal) as a Fabric App, Matas keeps SWA; three spikes pass in Pingala NielsWorkspace_Dev: SSO + static page, delegated SQL connector with actor by column default, daily run's pages served from OneLake by a function (25.9 MB in 6.5 s), headless smoke via externalEntraExchange"
---

**Decision (Niels, 2026-10-20):** MetaAtomic and all its modules stay deployable as either a Fabric App or an
Azure Static Web App, chosen per deployment. Carl Ras: Fabric App. Matas DataCompare: SWA. Recorded in
`own/MetaAtomic/CONTEXT_DECISIONS.md`; design in `own/MetaAtomic/docs/app-hosting-pattern.md` sections 6 and 7a.

**Tested facts (Rayfin CLI 1.36.2, F8 West Europe), project `own/MetaAtomic/fabric-app`:**
- Static MetaAtomic page + Fabric SSO work; `assetAccess: protected` gives 401 anonymous.
- `fabric-sqldatabase` connector with `auth: delegated` (set by hand; default is application) stores the user's UPN
  through `actor DEFAULT ORIGINAL_LOGIN()`.
- Views only keyless (`primaryKey: []`); a key on a view fails deploy with `InvalidKeyFieldsForEnforcedKeySource`.
  `connector add` discovers tables only.
- The `dataapp` template needs `rayfin/tsconfig.json` from `todoapp` and SWC `decoratorVersion: "2022-03"` for entities.
- A function `page(path)` with `ctx.Tokens.Storage` (app identity) serves `Files/MetaAtomic/out/` from a lakehouse:
  no redeploy for daily pages. 5.4 MB 1.3 s, 25.9 MB 6.5 s.
- Headless test: `services.auth.fabric.externalEntraExchange: true`, token scope
  `https://analysis.windows.net/powerbi/api/Item.Execute.All` from the rayfin CLI cache, POST
  `<api>/api/auth/v1/brokered/token`; the `api.fabric.microsoft.com` audience gets 401. `scripts/probe-pages.mjs`.
- Browser sign-in to the app is not something Claude can do; the headless exchange replaces it for checks.

**Open:** client-sent actor (spoofing), `checkPack` port to TypeScript, Carl Ras tenant setting "Fabric Apps (preview)".
