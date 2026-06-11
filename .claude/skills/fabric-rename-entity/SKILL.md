---
name: fabric-rename-entity
description: How to safely rename (or move) a Microsoft Fabric item — notebook, lakehouse, warehouse, data pipeline, semantic model — when the workspace is connected to Git, without breaking references from other items. Use this skill whenever renaming or cleaning up the name of any Fabric item that is serialised to a Git repo (folders like `<Name>.Notebook`, `<Name>.Lakehouse`, `.platform` files), removing an import-artifact suffix (e.g. a trailing `(1)`), or whenever an item rename needs to survive a Fabric Source-control "Update" with no broken pipeline activities, notebook dependencies, or connection bindings. Also use when a rename via `git mv` produced a folder/displayName mismatch or a reference stopped resolving after a rename.
---

# Renaming Fabric Items Under Git Integration

## Core Principle: Identity is the `logicalId`, not the name

When a Fabric workspace is connected to Git, every item is serialised as a folder
`<DisplayName>.<Type>/` containing a `.platform` file. The `.platform` holds a stable
**`logicalId`** (a GUID). That `logicalId` — not the display name — is the item's
identity. Fabric matches Git ↔ workspace by `logicalId`, and **cross-item references
are stored by GUID**, not by name.

```json
// .platform
"metadata": { "type": "Notebook", "displayName": "nb_A_build_metadata" },
"config":   { "logicalId": "25811ead-71ac-a11b-4e97-c1f313fc6a19" }
```

A pipeline activity that calls this notebook references the **GUID**, so the name is
free to change:
```json
"type": "TridentNotebook",
"typeProperties": { "notebookId": "25811ead-71ac-a11b-4e97-c1f313fc6a19" }
```

**Therefore the safe rename is:** change `displayName` + rename the folder to match,
and **never touch `logicalId`.** GUID-based references survive untouched.

---

## The safe rename procedure

1. **Pre-flight: rule out name-based references.** GUID references are safe; *name*
   references are not. Grep the whole repo before renaming:
   ```
   notebookutils.notebook.run("OldName")   # by display name — WOULD break
   mssparkutils.notebook.run("OldName")
   %run OldName
   runMultiple([... "OldName" ...])
   ```
   For lakehouses/warehouses also check notebook `.platform` `dependencies`
   (`default_lakehouse_name`) and any abfss paths or `connectionSettings.name` that
   use the display name rather than an `artifactId`/GUID. If a name-based reference
   exists, you must update it in the same change.

2. **Edit `displayName`** in the item's `.platform` to the new name.

3. **Rename the folder** to match — `<NewName>.<Type>/`. The folder name MUST equal
   `displayName`, or Fabric's Git sync will flag a mismatch.

4. **Leave `logicalId` alone.**

5. **Commit, push, then in Fabric → Source control → Update.** Fabric matches by
   `logicalId`, renames the item in place — no duplicate is created.

6. **Verify:** a test-run of any pipeline that calls the item should stay green.

---

## Critical gotcha: `git mv` drops your `.platform` edit

This is the failure this skill exists for. If you **edit `.platform` first and then
`git mv` the folder**, git stages the rename of the *original indexed content* and
leaves your `displayName` edit **unstaged**. `git status` shows `RM` (renamed +
modified). Committing then ships the folder rename with the **old** `displayName` →
folder/name mismatch, and your edit silently sits in the working tree.

**Symptom in the commit:** `rename (100%)`, `0 insertions(+), 0 deletions(-)` — i.e.
no content actually changed.

**WRONG — edit then `git mv`, then commit:**
```bash
# edit .platform displayName ...
git mv "Old(1).Notebook" "Old.Notebook"
git commit -m "rename"        # ships OLD displayName; edit left unstaged
```

**RIGHT — choose one:**
```bash
# Option A: git mv FIRST, edit the .platform at its new path, then commit
git mv "Old(1).Notebook" "Old.Notebook"
# ... edit "Old.Notebook/.platform" displayName ...
git add "Old.Notebook/.platform"
git commit -m "rename + align displayName"

# Option B: if you edited first, explicitly re-add after the mv
git mv "Old(1).Notebook" "Old.Notebook"
git add "Old.Notebook/.platform"     # picks up the displayName edit
git commit -m "rename + align displayName"
```

**Always verify the committed content, not just the tree:**
```bash
git show HEAD:"Old.Notebook/.platform" | grep displayName   # must be the NEW name
git status --short                                          # must be clean
```

---

## Reference-resolution by item type — an extensible registry

Fabric has **many** item types (and the list keeps growing): Notebook, Lakehouse,
Warehouse, Data Pipeline, Dataflow Gen2, Semantic Model, Report, Eventstream,
Eventhouse / KQL Database, KQL Queryset, ML Model, ML Experiment, Environment,
Mirrored Database, GraphQL API, Datamart, Spark Job Definition, and more. **Each
serialises to its own file layout and may reference other items differently.** The
identity principle (`logicalId` = identity; GUID references survive; *name* references
break) holds across all of them — but *how* and *where* a name might leak into a
reference is type-specific.

**Do not generalise from one type. Before renaming a type you haven't verified,
open its serialised files and confirm how it is referenced.** When you verify a new
type in real work, **add a row below and mark it verified** — this table is meant to
grow.

| Item type | Referenced by others via | Name-based reference risk | Status |
|-----------|--------------------------|---------------------------|--------|
| Notebook | `notebookId` (= `logicalId`) in pipeline `TridentNotebook` activities | `%run` / `notebookutils.notebook.run("name")` between notebooks — **by name** | ✅ verified (Tystofte 2026-06-02) |
| Lakehouse | `artifactId`/GUID in notebook `.platform` `dependencies`, pipeline `connectionSettings` | `default_lakehouse_name`, abfss paths, `connectionSettings.name` may embed the name | ⚠️ inspect files |
| Warehouse | connection bindings / dataset references | T-SQL three-part names, semantic-model source bindings | ⚠️ inspect files |
| Data Pipeline | `pipelineId`/GUID in `InvokePipeline` activities | low, but confirm | ⚠️ inspect files |
| Semantic Model | dataset binding from reports | report `definition` source name; TMDL expressions referencing source names | ⚠️ inspect files |
| Report | bound to a semantic model | model name in `definition.pbir` / connection | ⚠️ inspect files |
| Dataflow Gen2 | consumed downstream by pipelines/notebooks | mashup queries referencing source names | ⚠️ inspect files |
| Eventstream / Eventhouse / KQL DB | destinations/sources by id | DB/table names in KQL — **likely by name** | ⚠️ inspect files |
| _(other types)_ | _verify_ | _verify_ | ❓ unverified |

> Only the notebook ↔ pipeline GUID behaviour and the `git mv` gotcha are verified from
> a live repo. Everything marked ⚠️/❓ is a *hypothesis to check*, not a fact — the
> name-risk column lists where to look, not what is true. Treat an unverified type as
> "inspect first, rename second."

---

## Quick checklist
- [ ] Grep repo for by-name references (`%run`, `notebookutils`, `default_lakehouse_name`, abfss, `connectionSettings.name`)
- [ ] Edit `displayName` in `.platform`
- [ ] Rename folder to match `displayName`
- [ ] `logicalId` untouched
- [ ] `git add` the `.platform` after `git mv` (the gotcha)
- [ ] `git show HEAD:.../.platform` confirms new name committed; tree clean
- [ ] Push → Fabric Source control → Update → test-run a dependent pipeline
