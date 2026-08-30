---
id: carlras-wi-notebook-connection-per-environment
ts: 2026-08-30T00:00:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: /log
tags: [fabric, workspace-identity, connection, variable-library, key-vault, entra, carlras, deployment]
status: distilled
description: A workspace-identity notebook connection is per-environment by construction; an empty value-set override kills the whole activity at submit, and the identity needs the data-source grant on top of its workspace role.
---

TEST's `PL_MainExecution` failed every scheduled run with
`Failed to resolve connection ''` / `InvalidExternalReferenceConnection` /
`Invalid datasourceObjectId:  passed`. Cause: its `Scale Up` / `Scale Down` activities bind
`externalReferences.connection` to `VL_ConnectionId.CON-WI-Notebook`, and the `Test` and `Prod`
value sets override that variable with an **empty string on purpose** — no such connection existed
outside DEV. An empty override is not a fallback to the default value; it resolves to nothing and
fails the activity at submit.

**The connection is per-environment by construction.** A Fabric connection with
`credentialType: WorkspaceIdentity` carries no workspace in its own definition — the create payload
is just `{"credentials":{"credentialType":"WorkspaceIdentity"}}`. The token is minted at run time
for the workspace hosting the item that calls it, and MS Learn flags cross-workspace reuse as
"might not work". So one connection id shared across DEV/TEST/PROD is not an option; the per-stage
`VL_ConnectionId` value-set override is the only thing that makes the binding explicit.

**Two permission layers, both required, checked separately.**
1. The workspace identity needs its role on the workspace (Member/Contributor) — and the SPN that
   *triggers* the run needs `User` on the connection itself, or a scheduled run cannot use it even
   though a manual one can.
2. The workspace identity needs the grant on whatever the notebook actually touches.
   `NB_CapacityManager_Bootstrap` calls `notebookutils.credentials.getSecret`, which runs as the
   workspace identity, so it needs Key Vault Secrets User on `KeyVaultDataHub`. Fixing only the
   value set moves the failure from connection resolution into the notebook.

**Entra group membership takes the service principal OBJECT id, not the app id.** Verified against
the working DEV case: the group entry is `c898431c…` (servicePrincipalId), not `19efb836…`
(applicationId). Asking a customer for "the WI" without saying which id is how the wrong principal
gets added — Carl Ras added DEV and PROD and missed TEST on the first pass.

Concrete ids for this project are in `customers/Carl-Ras/datahub/CONTEXT.md` > *Completed
2026-08-27*.
