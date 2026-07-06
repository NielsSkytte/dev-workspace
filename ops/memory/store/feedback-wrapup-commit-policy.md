---
id: feedback-wrapup-commit-policy
ts: 2026-07-06T14:30:00Z
type: semantic
scope: workspace
source: session:8b788acf
tags: [feedback]
status: distilled
description: "At wrap-up//log: ALWAYS commit the internal (personal) repos touched this session; DevOps/customer-facing repos are NEVER auto-committed - always ask"
---

At session wrap-up (`/log`, `/exit`, or an explicit "wrap up"), commit handling splits by repo tier:

- **Internal ("personal") repos — commit without asking.** The workspace repo (`C:\Dev`) and the
  customer/own unit repos (`customers/<Client>/`, `own/`) are Niels's private continuity substrate;
  committing them at wrap-up IS the backup. Push where a remote exists (workspace repo →
  `github.com/NielsSkytte/dev-workspace`).
- **DevOps / customer-facing repos — always ask first.** Any repo with an external or company remote
  (Azure DevOps project repos, e.g. `PowerPortal-fabric`, wiki repos) is a delivery surface — a commit
  there is visible to others and may trigger syncs (Fabric Source control). Never auto-commit; prompt
  explicitly.

**Why:** Decided 2026-07-06 right after Gate 1 of the v1 review — the fno_code/rename edits sat
uncommitted across four unit repos minutes after backup was established, showing "commit only when
asked" leaves the substrate perpetually unbacked. The split mirrors Guardrail 10's two axes: internal
sharing (safe to automate) vs customer isolation (never automate).

**How to apply:** Canonical home: `AGENTS.md` > Conventions ("Wrap-up commits"). Wired into `/log`
step. Refines [[feedback-commit-to-test]] (that rule covers mid-session pushes that unblock testing;
this one covers the wrap-up gate).
