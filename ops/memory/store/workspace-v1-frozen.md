---
id: workspace-v1-frozen
ts: 2026-07-06T17:00:00Z
type: semantic
scope: workspace
source: session:8b788acf
tags: [project, milestone]
status: distilled
description: "Workspace tagged v1.0 (2026-07-06) - setup phase OVER; freeze rule in force: no new agent/skill/command without a demonstrated failure; success metric = INTERNAL-RND share collapsing in /time"
---

The workspace was tagged **v1.0** on 2026-07-06 (remote: `github.com/NielsSkytte/dev-workspace`)
after a full review closed three gates: survivability (remote + OneDrive time mirror + fno_codes),
drift (root cleanup, broken refs, tracker reconciliation), and decisions (evaluation layer
committed, assisted-triage cancelled, sanitizer + sentinel for local-model output).

**The setup phase is over.** The freeze rule is in force (AGENTS.md > Building new capabilities is
now binding): no new agent, skill, or command without a demonstrated failure as evidence. Sessions
in `C:\Dev` "improving the setup" without a failure in hand violate the freeze.

**Success metric:** the share of `Dev`/`INTERNAL-RND` time in `/time` reports should collapse from
"most of the time" (June) to minutes per day; billable hours land on real F&O codes (Matas 212-01,
Carl-Ras/datahub 230-02, Tystofte/Data-Discovery 4048-1). If setup time does not collapse, v1
failed its purpose regardless of design quality.
