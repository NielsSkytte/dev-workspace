---
id: tooling-promotion-customer-to-own
ts: 2026-07-31T08:05:00Z
type: procedural
scope: workspace
source: session:04e254a5
tags: [convention, projects, own, customers, tooling, promotion, skills, envdiscovery]
description: "Promoting reusable tooling built inside a customer project to own/: what moves, what stays, and the four wiring steps so it is actually found again"
status: distilled
---

Tooling often gets built inside the customer project that paid for the question. When it turns out
not to be customer-specific, it is promoted to `own/<Name>`. First worked example:
`customers/Matas/DataCompare/src/env-discovery/` -> `own/EnvDiscovery` (2026-07-31).

## What moves, what stays

- **Moves:** the code, its README, and any fixture data the owner designates as **test data**.
- **Stays:** run output produced *for that engagement* — it belongs to the customer project.
- The distinction is the owner's call, not a rule read off file names. At Matas the two real-tenant
  CSVs moved (they are the only verified input/output pair the scripts have) while future
  per-engagement runs stay with their customer.

## Four wiring steps — skip one and it is lost

1. **`lineage.from`** in the new project's `CLAUDE.md` points back at the origin project, and the
   origin's `CONTEXT.md` gains a "Related contexts" pointer forward. Both directions, or the trail
   breaks from whichever end is read first.
2. **A VS Code task** in `.vscode/tasks.json` (`Claude - own/<Name>`) — time tracking and the
   project context chain both depend on sessions being rooted at the project folder.
3. **Route it from a skill.** A tool nobody remembers is not a capability. Pick the skill that
   already owns the *question the tool answers*, not the one that owns the technology, and add
   both the content and the trigger phrasings. `EnvDiscovery` went into `fabric-project-access`
   (section 0) because it answers "what does this tenant already have" = Phase 1 of the playbook,
   not into `pingala-fabric-platform`, which is architecture guidance.
4. **Back-pointer.** The new project's `CONTEXT.md` names every skill that references it by path,
   so a later rename updates them.

## Repo mechanics

`own` and each `customers/<Customer>` are **local unit repos**; `C:\Dev/.gitignore` excludes
`/own/` and `/customers/` from the workspace repo. `ops/bin/heal-repos.ps1` is the sanctioned way
to init/heal a unit — hand-rolling a `.gitignore` there fights a harness-managed block. A
cross-repo move is copy + `git rm`, since `git mv` cannot cross a repo boundary; verify the
landed files against the origin's `HEAD` blobs by hash before committing the deletion.
