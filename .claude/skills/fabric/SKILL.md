---
name: fabric
bundle: custom
description: Index to Pingala's Microsoft Fabric skills, which are not auto-loaded. Use for any Fabric or data-pipeline work (pipelines, notebooks, warehouse in git, deployment, renames, data agents, licensing, customer access, Atomic platform, migration checks, timestamps), then read the matching skill file it names.
---

# Fabric skill index

The twelve Fabric skills below carry `disable-model-invocation: true` (decided 2026-10-22) so their
long descriptions stay out of every session's startup context. The Skill tool will not load them.
**Read the file instead:** `.claude/skills/<name>/SKILL.md`, then any `references/` file it points to.
The path resolves from `C:\Dev` and from every project root (the `skills` folder is junctioned in).
Niels can still type `/<name>` to load one by hand.

Any of these names mentioned inside another skill or agent means: read that file. Read the whole
SKILL.md before acting; its frontmatter `description` holds the full trigger list and scope edges.

| Skill | Read it when |
|---|---|
| `pingala-fabric-platform` | Pingala's delivery architecture: workspaces LZ/Raw/Enriched/Curated, Atomic (Particles/Atoms/Molecules), branch model, environment strategy, Master Pipeline, Views-to-Tables, gateway, GDPR. Atomic reference docs in its `references/`. |
| `fabric-pipeline-notebook` | Pipelines that run notebooks; JSON ingestion; silent data loss; interactive vs pipeline run differences; hand-editing `pipeline-content.json` (`notebookId` = `.platform` `logicalId`); "Missing Dependencies" on Update from git. |
| `fabric-warehouse-git` | Any warehouse schema change through git; Update-from-git failures (ObjectNotFoundInCollection, "Invalid column name", "data will be deleted", empty table); `xmla.json`, `.sqlproj`, DacFx. A table name with `(1)` belongs HERE, not to rename-entity. |
| `fabric-deployment` | Promoting items DEV -> TEST -> PROD; first deploy into an empty workspace; first push to a customer repo; variable libraries; portability review; ownership and schedules that stop. |
| `fabric-rename-entity` | Renaming or moving a git-connected Fabric ITEM (notebook, lakehouse, warehouse, pipeline, model); an item `(1)` import suffix. |
| `medallion-migration-validation` | Migration go-lives, row-count reconciliation, QC queries, watermark and tracking tables, backfills after a bug or gap. |
| `timestamp-timezone-pipelines` | Timestamps across system boundaries; watermarks; date filters sent to APIs; missing records or drift from timezones. |
| `fabric-project-access` | Phase 1 of a customer project: Entra groups, guest/ext_ accounts, SPNs, Key Vault, workspace/capacity roles, admin-portal settings, access-request email; Dataverse "Link to Fabric" access problems (section 8.5); tenant discovery (section 0). |
| `fabric-licensing` | What Fabric costs; which licence (Free/Pro/PPU); F SKU sizing; F64 rule; reserved vs pay-as-you-go; pause; Copilot/AI metering; pricing an offer. Cited, dated facts. |
| `fabric-data-agent` | Designing, grounding, building a Fabric data agent; agent vs data-source instructions; Prep for AI vs agent layer; wrong table/measure; git/config-as-code for the agent. |
| `fabric-data-agent-testing` | Ground-truth Q&A sets, `evaluate_data_agent`, LLM judge, few-shot validation, regression after a model change. |
| `fabric-data-agent-ops` | Data-agent cost and capacity (AI Query), usage logging (Purview, SDK), CI/CD promotion, model-agent sync. |

Owning agents: `fabric-back` (platform, pipeline, warehouse, deployment, rename, medallion,
timestamp, access), `semantic` (data-agent trio, rename, platform). Licensing is read by whoever
prices or sizes, including `content` for offers.
