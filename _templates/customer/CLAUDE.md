# [Customer] — CLAUDE.md (customer node)

> **Customer node, not a project.** This file is the customer *map*: who they are and the
> projects under them. **Tasks attach only to projects** — time normally bills to a project; a session left at
> this node is tracked at the customer level (Proj ID `UNSET`, resolved at review). All work lives in the projects listed
> below, each with its own `CLAUDE.md` + `CONTEXT.md`. Live customer-level state is in
> `CONTEXT.md` beside this file.

## Customer
name:
status: active | prospect | paused | closed
owner: customers/[client]
contacts:            # key people — customer-side and partners
infra:               # shared across projects: Fabric capacity, Entra tenant, Azure DevOps org, ...
tenant_id:           # Entra tenant GUID — verify before any fab/az/pac command (Guardrail 11)
account:             # the identity we sign in as, normally an account created in their tenant
language: da | en

## About
<!-- Who they are, the relationship, the shared picture. One short paragraph. -->

## Projects
| Project | Folder | Type | Status | One-line |
|---|---|---|---|---|
| | ./ | content \| function | active \| planned \| paused \| delivered | |

<!-- List non-project inputs (read-only sources, wikis) below the table if useful. -->
