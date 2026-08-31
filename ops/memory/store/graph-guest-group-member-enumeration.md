---
id: graph-guest-group-member-enumeration
ts: 2026-08-31T10:30:00Z
type: semantic
scope: workspace
source: session:f17772e8-6514-4c38-b590-03daab4595e6
tags: [entra, graph, guest-account, technique, verification]
status: distilled
description: "As a guest in a customer tenant, Graph /groups/{id}/members returns an EMPTY list rather than an error - use the servicePrincipal cast or checkMemberGroups, never the bare call"
---

Measured 2026-08-31 in the Carl Ras tenant as `EXT_NSKC@carl-ras.dk` (guest).

## The trap

```
GET /v1.0/groups/{id}/members          -> {"value": []}     WRONG - looks like an empty group
GET /v1.0/groups/{id}/members/$count   -> 2                  (needs ConsistencyLevel: eventual)
GET /v1.0/groups/{id}/members/microsoft.graph.servicePrincipal?$count=true
                                       -> the actual 2 members
```

The bare `/members` call returns **HTTP 200 with an empty array**, not a 403. A guest account's
directory read is restricted for service-principal objects, and the restriction presents as absence.
This is the worst possible failure shape: it reads as a measurement.

It cost a wrong conclusion in this session — an agent reported `Fabric_Key_Vault_Users` as having
"0 members, not 2" and called the existing record wrong. The group has 2:
`c898431c-f141-4fe3-9a7b-3031618956b6` (Fabric-ETL-DEV) and
`fa075892-6394-415c-b0a9-a25105e2f1a8` (Fabric-ETL / PROD).

## What to use instead

- **To test one principal's membership** — `POST /v1.0/directoryObjects/{objectId}/checkMemberGroups`
  with `{"groupIds": ["..."]}`. Returns the group id if a member, `[]` if not. It also distinguishes
  "not a member" from "object does not exist": a bad object id returns `Request_ResourceNotFound`,
  so a plain `[]` is a real negative.
- **To enumerate** — add the `microsoft.graph.servicePrincipal` (or `.user`, `.group`) cast.
- **To sanity-check a count** — `/members/$count` with the `ConsistencyLevel: eventual` header.

## General rule

An empty collection from Graph under a restricted identity is not evidence of an empty collection.
Corroborate with a second call shape before recording an absence as a fact.
