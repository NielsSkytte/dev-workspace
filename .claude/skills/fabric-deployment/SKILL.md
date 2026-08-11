---
name: fabric-deployment
bundle: custom
description: >
  What breaks when Microsoft Fabric items are promoted between environments, and the
  release procedure that prevents it. Use this skill whenever an item moves DEV -> TEST
  -> PROD through a Fabric deployment pipeline, whenever a deployment or a first run in
  the new environment fails, and whenever authoring an item that will later be promoted.
  Trigger on "deploy to TEST", "promote to PROD", "deployment pipeline failed", "the
  deployment succeeded but it doesn't work in TEST", "Invalid object name" or
  "DmsImportDatabaseException" on a warehouse deploy, "already exists" on a redeploy,
  a pipeline failing at submit with "BadRequest" and zero activity runs, VariableNotFound,
  a variable library / value set that differs between stages, a notebook that wrote to
  the wrong workspace, a missing seeded table in a new environment, or a scheduled run
  that stopped when someone's account was disabled. Also trigger on "is this item
  portable", "can I hardcode this id", item ownership / LastModifiedBy / takeover, and
  on reviewing a change for environment portability before it ships.
  This skill owns deployment MECHANICS and FAILURE MODES. The delivery architecture
  around it - workspace structure, branch model, three-stage strategy, roles, and the
  git-not-fab-import authoring rule - lives in `pingala-fabric-platform`. Renaming a
  git-connected item is `fabric-rename-entity`. Post-migration data reconciliation is
  `medallion-migration-validation`.
---

# Deploying Fabric Items Between Environments

## Core principle: a deployment copies definitions, not environments

A Fabric deployment pipeline copies **item definitions** from one workspace to the next.
It does not carry the four things that actually make an item work there:

| Not carried | Consequence |
|---|---|
| **Data** | A lakehouse or warehouse item arrives empty. Seeded/reference tables are gone. |
| **Per-environment configuration** | Variable library *value sets* are per workspace. Connections are not workspace items at all. |
| **Identity** | Who an item runs as (`LastModifiedBy`, schedule owner, warehouse owner) is not preserved the way you expect. |
| **Anything hardcoded inside the definition** | A literal workspace or item GUID is copied verbatim and keeps pointing at the source environment. |

**So a release is four steps, not one: deploy -> seed -> re-stamp identity -> check value
sets.** Anything short of that produces an item that either fails cryptically on its first
run, or - worse - succeeds against the wrong environment.

Reference implementation: `customers/Carl-Ras/datahub/tools/fabric_release.py` runs all four
in order against the Fabric REST API, audit-by-default (`--apply` to write). Its companion
`fabric_identity.py` does step 3. Read them before writing a new one; the per-customer names
they use (seed pipeline, variable library names, deployment pipeline names) belong in that
customer's `CLAUDE.md`, not here.

---

## Failure catalogue

Every entry below was diagnosed the hard way. The symptoms are cryptic and none of them
name their real cause, which is why they belong in a skill rather than in a runbook.

### 1. Warehouse deploy fails: `DmsImportDatabaseException` / `Invalid object name 'X.dbo.y'`

**Symptom.** Deploying a warehouse to the next stage fails with a DMS import exception naming
an object that plainly exists in the source, e.g.
`Invalid object name 'Lakehouse_Raw_GTM.dbo.events'`.

**Cause.** A warehouse view that reaches across databases with a **three-part name** binds
that name at `CREATE VIEW` time. The import replays the DDL in the target, where the
referenced lakehouse table does not exist - because the deployment copied the lakehouse
**item** without its **data**, and an empty lakehouse has no tables.

**Cure.** The dependency has to exist in the target *before* the warehouse import runs.
Either deploy and populate the upstream lakehouse first (run its ingest, or the seeding
pipeline), or promote in dependency order: landing -> raw -> enriched -> curated, running
each layer once before the next is deployed.

**Generalises to:** any cross-database reference - warehouse views over a lakehouse SQL
endpoint, or over another warehouse. If a view names a database other than its own, the
deployment has an ordering constraint.

### 2. The retry fails with "already exists"

**Symptom.** After a failed deploy you re-run it and the target complains that an item with
that display name already exists.

**Cause.** The failed import **left the item behind in the target, unpaired**. The deployment
pipeline tracks pairing per stage item; on the orphan the stage item shows
`targetItemId: null`. Because the pipeline sees no pairing, it tries to *create* rather than
*update*, and collides on display name.

**Cure.** Delete the orphan item in the target workspace, then re-deploy. Check pairing
before assuming, via `GET /deploymentPipelines/{id}/stages/{stageId}/items` - a null
`targetItemId` on an item that visibly exists in the target workspace is the signature.

**Rule.** A failed deployment is not a no-op. Inspect the target before retrying.

### 3. Pipeline fails at submit: `BadRequest`, seconds, zero activity runs

**Symptom.** A deployed pipeline fails almost immediately - `RequestExecutionFailed` /
`BadRequest`, ~8 seconds, zero activity runs recorded, and no message naming the offending
variable. Nothing in the error points at variable libraries.

**Cause.** An unresolved **variable library alias**. A pipeline binds library variables under
aliases in its `libraryVariables` block (e.g. `SourceLakehouseId` ->
`VL_DatastoreId.Lakehouse_Landingzone_Marketo`). If the referenced variable does not exist in
the target workspace's libraries, validation kills the whole pipeline before any activity
starts. Nothing in the error says "variable".

**Cure.** Diff the variable libraries between stages first, before reading any activity log.
Reading a library's definition is a **202 long-running operation**: `POST
/workspaces/{ws}/items/{id}/getDefinition`, then poll `Location`, then `GET Location/result`.
`fab api` does not follow the LRO for you.

**Rule.** Variable libraries are the environment contract. Adding a stream means adding its
variables **and** deploying the libraries to every stage **and** filling that stage's
value-set override. A variable with no override falls back to the library default - correct
for a shared resource, wrong for anything per-environment.

**Related symptom:** `VariableNotFound` naming a specific variable is the same class of
failure, stated more helpfully.

### 4. The deployment succeeds, the run succeeds, and it wrote to the wrong environment

The most dangerous failure, because there is no error.

**Cause.** A literal workspace or item GUID in **notebook code**. Verified 2026-08-11: three
notebooks pinned the DEV workspace id, so a TEST run read and wrote DEV and reported success.
One of them ran as an activity inside a pipeline, so it happened on every TEST run.

**Do not trust the notebook's `default_lakehouse` META as evidence.** The deployment pipeline
remaps that binding correctly - verified: TEST's copy pointed at TEST's lakehouse while the
code inside pointed at DEV. Code that calls `lakehouse.get(..., workspaceId=<literal>)` never
reads the META.

> **Method rule.** The declared binding and the runtime behaviour are different artifacts, and
> in Fabric they routinely disagree: the META block is what the deployment pipeline rewrites,
> the code is what executes. Checking the one that gets rewritten is checking the thing least
> likely to be wrong. **Config that a deploy step rewrites is never evidence about code that
> ignores it.** Before declaring an item safe to run in an environment, read the code that
> resolves its targets.

**Detection.** Reviewing an item for portability = grep it for GUIDs and account for *every*
one. Each hit is either resolved at runtime, or justified as environment-invariant.

**Fixes.**
- Destination (a per-environment lakehouse/warehouse in this workspace) -> resolve at runtime
  with `runtime.context["currentWorkspaceId"]`, or take it from a variable library.
- A genuinely shared, environment-invariant source workspace -> a pinned id is correct.
  That is the only exception, and it must be stated as such where it appears.
- Where the id sits in a **parameters cell**, keep the parameter but default it to `""` and
  resolve after the imports (`x = x or runtime.context["currentWorkspaceId"]`) -
  `notebookutils` is not imported yet inside a parameters cell, and deliberate cross-workspace
  targeting stays possible.

### 5. Missing reference/seeded table in the new environment

**Symptom.** First run in the new environment fails on a table that exists in DEV - key maps,
date dimensions, enum/metadata tables. Typically
`[TABLE_OR_VIEW_NOT_FOUND] <Lakehouse>.<reference_table>`.

**Cause.** The deployment copied the lakehouse item, not its data.

**Cure.** A **seeding pipeline** that recreates reference data with `CREATE OR REPLACE`, safe
to re-run, executed once per environment as step 2 of the release. Running the individual
notebooks by hand is the fallback, not the procedure.

**Rule.** If a table is written by a notebook rather than by ingest, it needs seeding in every
environment. Track which those are.

### 6. Scheduled work stops when a person's account is disabled

**Cause.** Fabric binds several identity fields to whoever created or last touched an item,
and a deployment does not move them to a service principal for you. `LastModifiedBy` decides
which principal an item runs as, so a newly deployed pipeline or notebook can run as a person.

**Fields, and how each is set** (from `fabric_identity.py`, verified 2026-08-11):

| Field | How it moves to an SPN |
|---|---|
| Schedule owner | `PATCH /jobs/{jobType}/schedules/{id}` - caller becomes owner |
| Pipeline `LastModifiedBy` | `POST /dataPipelines/{id}/updateDefinition` - byte-identical write, caller becomes last modifier |
| Warehouse owner | `POST` powerbi `/datawarehouses/{id}/takeover` |
| Lakehouse identity | `POST /items/{id}/identities/default/assign?beta=true` - cascades to child items such as the SQL analytics endpoint |

**No API accepts a service principal for these** - portal takeover, user only:
- the "Owner" column on pipelines and notebooks
- the lakehouse SQL endpoint via `lhdatamarts/takeover`

**Connections are not workspace items.** They carry their own access list, so no workspace
role reaches them. A value set can name a connection that was never created in this
environment, or one the SPN has no role on - neither surfaces until a pipeline runs and fails.
Grant with `POST /connections/{id}/roleAssignments`, which must be called as an owner (the SPN
cannot grant to itself).

**Unverified, flagged for test:** a semantic model has its own owner (`configuredBy`) which
`fabric_identity.py` does not move. A TEST refresh POST returned 403 for an SPN that could
read the dataset and its refresh history, on a model whose `configuredBy` was a user account.
Model ownership is the leading hypothesis, not a proven cause; the test is
`POST /datasets/{id}/Default.TakeOver` as the SPN, then re-run. Semantic-model refresh
behaviour otherwise belongs to the `semantic` agent.

---

## Pre-flight: before promoting anything

1. **Grep the item for GUIDs.** Account for every one (failure 4).
2. **Do its variable references exist in the target?** New variables must be added to the
   library, the library deployed to that stage, and the stage's value-set override filled
   (failure 3).
3. **Do its upstream dependencies exist and hold data in the target?** Cross-database views
   have an ordering constraint (failure 1).
4. **Does it read a seeded table?** Then the target needs seeding (failure 5).
5. **Will it run on a schedule?** Then it must be re-stamped to the service principal
   (failure 6).

## Post-deploy: what to check before promoting further

- Value sets in the target: every variable non-empty, and every connection id actually
  resolvable by the principal that will run the job (`GET /connections/{id}` - 200 usable,
  403 exists but no role, 404 not present in this tenant; back off on 429 rather than report a
  false negative).
- Identity re-stamped.
- One smoke run of the deployed item, and check *where* it wrote, not just that it succeeded.

## Audit before you write

Both reference tools default to audit and require `--apply` to change anything. Keep that
property in anything new: a deployment audit that lists which items exist only in the source
(and would therefore be *created*) is cheap, and it is the last point at which a bad promotion
is still free. Everything not newly created is **overwritten in place; nothing in the target is
deleted** - so a stale item in the target survives every deployment until someone removes it.

---

## Boundaries

- **How new items get into a git-connected workspace** (author -> commit -> push -> Update from
  git, never `fab import`; `logicalId`; the normalising commit that follows) - that is
  authoring, not promotion: `pingala-fabric-platform` > *Never `fab import` an item that
  belongs in a git-connected workspace*.
- **Workspace structure, branch model, three-stage strategy, workspace roles, the Admin
  requirement for connecting git and creating deployment pipelines** - `pingala-fabric-platform`
  > *CI/CD and deployment*.
- **Renaming or moving a git-connected item safely** - `fabric-rename-entity`.
- **Reconciling row counts and validating a go-live after data moves** -
  `medallion-migration-validation`.
- **Semantic model refresh, processing, and Direct Lake behaviour** - the `semantic` agent.
- **Which tenant the `fab` CLI is authenticated against** - the auth substrate under all of
  this, not part of it: memory record `tenant-scoped-cli-auth` (Guardrail 11). Two traps worth
  carrying anyway: `fab auth status` exits 0 even when logged out, so parse its output rather
  than gate on the exit code; and a bare `fab auth login -t <tenant>` run from outside a
  customer folder overwrites the default profile.

## Notes

- A deployment pipeline carries **its own access list**. An SPN that is workspace admin
  everywhere still cannot deploy until it is admin on the *pipeline*. Falling back to the
  signed-in user account is the workaround; making the SPN a pipeline admin is the fix, and it
  is what makes a release schedulable with nobody's account in it.
- Stage display names and value-set names are not the same words, and libraries do not
  necessarily agree with each other on case. Map stage -> value set explicitly; do not infer it
  from a prefix.
