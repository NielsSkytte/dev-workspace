---
id: customer-project-two-tier
ts: 2026-07-06T09:40:00Z
type: semantic
scope: workspace
source: session:b7e48af4-fad6-4297-a6b4-bb4650338135
tags: [project, workspace-design, continuity]
status: distilled
description: "customers/ is two-tier — a customer node (map: profile + project index, never billable) wraps its projects (the work unit); session walk is three-scoped"
---

`customers/` is **two-tier** (decided/rolled out 2026-07-06):

- **Customer node** = `customers/<client>/CLAUDE.md` + `CONTEXT.md`. The customer *map*: profile,
  key contacts, shared infrastructure (Fabric capacity, Entra tenant, DevOps org), and a **project
  index** (one row per project + status). `CONTEXT.md` = live customer-level state across projects.
  Scaffold from `_templates/customer/`.
- **Project** = `customers/<client>/<project>/…` — unchanged. The unit of work, and **the only thing
  time and tasks attach to.**

**A customer node is never a project and never a billing target** — no `type:`/`scale:`/`fno_code:`.
Work always bills to a project (and, for `customers/…`, a task within it). **Every** customer gets a
node, including single-project ones (index has one row). `own/` stays single-tier (an `own/<project>`
is just a project).

**Session walk is now three-scoped** (AGENTS.md > Continuity loop; Guardrail 8):
workspace root (workspace walk) → **customer root (customer walk: read node, surface projects +
statuses, prompt which project this session is for, hand to project walk)** → project (project walk).

Applied to all 6 customers. Tystofte was normalised from a project-style "umbrella engagement" to a
clean node + real per-project files for its tracks (Data-Discovery, Tystofte-Fabric) — the umbrella's
`type/scale/fno_code` on a customer was the anti-pattern this removes.

Related: [[workspace-design]]
