---
id: repo-vs-project-vs-task
ts: 2026-07-28T12:50:00Z
type: semantic
scope: workspace
source: session:carlras-merge-task-first-attribution
tags: [project, decision]
status: distilled
description: "A project is ONE F&O Project ID (repos live inside it, several allowed); distinct workstreams are TASKS at user-story/ADO-work-item granularity — not projects, not folders"
---

The rule that settles "is this a project or a task", decided 2026-07-28 (ADR-003):

**A project is one F&O Project ID.** If two folders bill to the same `fno_code`, they are one project.
Testable, and it resolves the argument without debate.

- **A repo is not a project.** Repos live *inside* a project; a project may hold several. Never promote a
  repo to a project just because it is a repo.
- **Distinct workstreams inside a project are tasks**, carrying `activity:` and `fno_task:`. That is what
  the F&O dimensions (Project ID -> Activity -> Task) exist for.
- **Task granularity = the user story / Azure DevOps work item** that `fno_task:` names. Sub-steps of one
  story ("create the datastore", "type-2 history", "build the semantic model") are deliberately NOT
  modelled — F&O has no dimension below Task, so modelling them produces detail nothing can receive.
- **A task need not be finishable in one sitting.** The tag is stamped per turn, so a task can span weeks
  and a session can span two tasks (`/switch-task` splits the time where you switch).
- **`own/` is for reusable assets, not customer delivery.** A tool built inside a customer's repo to solve
  that customer's problem is billable customer work; productizing it for reuse is `own/` and non-billable.
  CapacityManager is both at different moments (its `own/` record still holds all 4.75 h as internal —
  open question, not resolved).

**The case that forced it — Carl Ras.** It broke the old folder=project assumption in both directions at
once: one project across two repos (`Landingzone-ETL` + `Fabric-ETL`, both under the customer's single ADO
project `Datahub`), and one repo hosting three workstreams (GTM ingest, capacity scale-up, CapacityManager).
`Carl-Ras/fabric` and `Carl-Ras/datahub` had been separate projects purely because each held a repo — and
both already carried `fno_code: 230-02`, proving they were never two billing units. Merged 2026-07-28;
the merge was billing-neutral for exactly that reason. **The remote is the tell:** both repos sit at
`dev.azure.com/CarlRas/Datahub/_git/...` — the customer already filed them under one project.

**Rejected: a folder per task.** Task identity already lives in `ops/tasks/*.md`; folders fork it into two
places that drift, give folders to tasks needing no artifacts, and answer "am I tracking correctly?" only
at launch. The real requirement is continuous visibility (statusline), not directory structure.
