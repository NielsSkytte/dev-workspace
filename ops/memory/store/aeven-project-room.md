---
id: aeven-project-room
ts: 2026-11-02T15:00:00Z
type: semantic
scope: project:customers/Aeven/AtomicServiceNow
source: session:9542bfec-b04f-4d91-86b1-1ce3453b49bd
tags: [project, reference]
status: distilled
description: "Aeven AtomicServiceNow is shared with Kresten via project-room/ (atompower4us/aeven-atomicservicenow-room); tooling, docs, decisions moved there 2026-11-02; older tools/ docs/ config/ paths are relative to project-room/tooling"
---

Since 2026-11-02 `customers/Aeven/AtomicServiceNow/project-room/` is a nested git repo
(`atompower4us/aeven-atomicservicenow-room`, Project Room spec v1, template in
`own/AtomicCortex/project-room-template`). It holds everything shared with Kresten:
`tooling/` (src, tools, tests, config, Fabric-ETL, Landingzone-ETL, Semantic-Model, Report;
`.env` and `data/` local, gitignored), `docs/`, `architecture/` (drawing, standard-to-Aeven layout
mapping, delivery progress per component), `decisions/` (architecture + delivery), `knowledge/`,
`now/<person>.md`, `inbox/`.

**How to apply:** Aeven memory records written before 2026-11-02 cite `tools/...`, `config/...`,
`docs/...`, `tests/...` relative to the old project root: read them as `project-room/tooling/...`
(docs: `project-room/docs/...`). `CONTEXT_DECISIONS.md` is frozen; new decisions go to
`project-room/decisions/`. Anything Kresten should see goes into the room on purpose (spec rule 6);
hours, preferences and secrets never do. `heal-repos.ps1` recognises a room by `SPEC.md` and does not
exclude its AGENTS.md/CLAUDE.md. Related: [[aeven-servicenow-deploy-state]], [[atomiccortex-vision]].
