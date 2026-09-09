---
id: ado-service-principal-needs-org-membership-and-basic-seat
ts: 2026-09-09T11:00:00Z
type: semantic
scope: workspace
source: /log
tags: [azure-devops, service-principal, git, licence, TF401444, fabric, carl-ras]
status: distilled
description: "A service principal can clone from Azure DevOps with an Entra token (scope 499b84ac-1321-427f-aa17-267ca6975798/.default, passed as a git bearer header), but only once it is a member of the DevOps organization; until then DevOps answers TF401444. Membership with code access is a Basic seat, which is a paid licence beyond the five included"
---

Measured 2026-09-09 at Carl Ras with `Fabric_Datahub` (app id `aa462763-...`, object id
`f05f446a-...`): the client-credentials token for the DevOps resource minted fine, and both the REST
repositories call and `git ls-remote` with `http.extraheader=AUTHORIZATION: bearer <token>` were
refused with `TF401444: Please sign-in at least once as <tenant>\<object id>`. That message means the
identity is not in the organization, not that the token is wrong. Fabric workspace roles say nothing
about DevOps membership.

Adding it needs an organization admin and, for a private project's code, Basic access. Stakeholder
is free and cannot read code. The CarlRas organization had 10 Basic seats assigned against 5 included,
so the eleventh is one more paid seat at the standard Basic price. Interim at Carl Ras: a read-only
PAT (Code: Read) under Niels's account, made by `datahub/create_metaatomic_pat.ps1`, stored in
`KeyVaultDataHub` as `metaatomic-ado-pat`, which expires and dies with the account.

The notebook template `NB_MetaAtomic.py` supports both: `GIT_SPN_*` preferred, `GIT_PAT_SECRET` as the
fallback. Flip to the service principal the day it has its seat.
