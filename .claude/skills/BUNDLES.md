# Skill Bundles

Skills are organized into bundles matching Microsoft's `marketplace.json` in the upstream repo.
Each skill's `bundle:` frontmatter field records its bundle membership.

Upstream source: `.claude/vendor/skills-for-fabric` (git submodule)
Update procedure: `/update-skills`

---

## fabric-authoring
*Create and modify Fabric items via CLI*

| Skill | Description |
|---|---|
| `sqldw-authoring-cli` | DDL/DML, COPY INTO, schema changes on Warehouse/SQLEP |
| `spark-authoring-cli` | Create and manage notebooks, Spark job definitions |
| `eventhouse-authoring-cli` | Author KQL databases and tables |
| `eventstream-authoring-cli` | Create and configure Eventstreams |
| `activator-authoring-cli` | Author Activator items (rules, actions) |
| `semantic-model-authoring` | Develop Power BI semantic models |
| `dataflows-authoring-cli` | Create and modify Dataflows Gen2 |
| `dataflows-save-as-authoring-cli` | Convert Dataflows Gen1 → Gen2 |
| `e2e-medallion-architecture` | Build end-to-end Bronze/Silver/Gold architectures |
| `check-updates` | Version check for this skill collection |

---

## fabric-consumption
*Read-only queries and exploration via CLI*

| Skill | Description |
|---|---|
| `sqldw-consumption-cli` | T-SQL queries against Warehouse, Lakehouse SQLEP, Mirrored DB |
| `spark-consumption-cli` | Interactive PySpark analysis and Livy sessions |
| `eventhouse-consumption-cli` | Execute read-only KQL queries |
| `eventstream-consumption-cli` | List and inspect Eventstream items |
| `activator-consumption-cli` | Inspect Activator items |
| `semantic-model-consumption` | Execute DAX queries against semantic models |
| `dataflows-consumption-cli` | Inspect and execute Dataflows queries |
| `search-consumption-cli` | Find and discover items across workspaces |
| `check-updates` | Version check for this skill collection |

---

## fabric-operations
*Diagnose performance and health issues*

| Skill | Description |
|---|---|
| `sqldw-operations-cli` | DW performance diagnostics via queryinsights |
| `spark-operations-cli` | Spark job and Livy session triage |
| `check-updates` | Version check for this skill collection |

---

## fabric-migrations
*Migrate from legacy Azure data platforms*

| Skill | Description |
|---|---|
| `databricks-migration` | Port Azure Databricks Spark code to Fabric |
| `synapse-migration` | Migrate Azure Synapse Analytics to Fabric |
| `hdinsight-migration` | Port Azure HDInsight Spark workloads |

---

## powerbi-authoring
*Create and manage Power BI reports and semantic models*

| Skill | Description |
|---|---|
| `semantic-model-authoring` | Develop Power BI semantic models (also in fabric-authoring) |
| `powerbi-report-planning` | Plan and orchestrate report delivery |
| `powerbi-report-design` | Generate report designs and layouts |
| `powerbi-report-authoring` | Create and modify reports |
| `powerbi-report-management` | Manage report lifecycle |

---

## custom
*Workspace-specific skills not in the upstream collection*

| Skill | Description |
|---|---|
| `fabric-data-agent` | Design, ground, and ship production-grade Fabric Data Agents (Prep-for-AI vs agent layer, sources, instructions, lifecycle) |
| `fabric-data-agent-testing` | Evaluate a data agent with the SDK harness — ground-truth Q&A, LLM-judge, few-shot validation, regression |
| `fabric-data-agent-ops` | Operate a data agent — capacity/cost, usage logging (Purview/custom), git/CI/ALM, model↔agent sync |
| `pingala-fabric-platform` | Pingala's Fabric delivery platform context |
| `pingala-project-playbook` | Pingala project setup and delivery playbook |
| `pingala-visual-identity` | Pingala brand and visual identity |
| `fabric-pipeline-notebook` | Best practices for pipeline-orchestrated notebooks |
| `fabric-project-access` | Setting up access rights for Fabric projects |
| `fabric-rename-entity` | Safely rename Fabric items |
| `medallion-migration-validation` | Validate medallion layer migrations |
| `azure-devops-backlog` | Create and manage Azure DevOps backlog items |
| `email-outlook-ready` | Draft and send emails via Outlook |
| `timestamp-timezone-pipelines` | Timestamp and timezone handling in pipelines |
| `writing-voice` | Niels's business writing voice (DA/EN) - strip the AI smell, match his voice; strict offer layer |
| `pingala-offer` | Trusted-advisor doctrine and structure for writing Pingala customer offers / SoWs |
| `fabric-licensing` | Microsoft Fabric licensing & cost (capacity SKUs, Free/Pro/PPU, the F64 rule, buy/reserve/pause, Copilot metering; data-agent consumption in a reference), cited to MS Learn |
