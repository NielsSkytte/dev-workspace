# Git serialization & config-as-code

A Fabric data agent is a first-class, **Git-serializable item** (like `.Notebook` /
`.SemanticModel`) and can be built **programmatically** with the Python SDK or the REST item
definition. This is what makes a production PoC reproducible and reviewable. Operational
concerns (capacity, logging, when to re-test) live in the `fabric-data-agent-ops` skill; this
file is the serialization + as-code surface.

## Git folder layout

In a Git-connected workspace the agent gets its own item folder. Every config change — schema
selection, AI instructions, data-source instructions, example queries, publish description —
shows as **uncommitted changes** in the Source control pane, so you get diff/history/revert and
PR review.

```
<DataAgentName>.DataAgent/        (item folder; plus a .platform metadata file)
└── files/
    └── config/
        ├── data_agent.json            # schema version, e.g. {"$schema":"2.1.0"}
        ├── publish_info.json          # publish description
        ├── draft/                     # EDIT HERE
        │   ├── stage_config.json       # {"$schema":..., "aiInstructions":"..."}  ← agent instructions
        │   ├── lakehouse-tables-<LHname>/
        │   │   ├── datasource.json      # dataSourceInstructions, displayName, elements[] (tables/cols, is_selected)
        │   │   └── fewshots.json        # [{id, question, query}]
        │   ├── warehouse-tables-<WHname>/ ...
        │   ├── semantic-model-<name>/    # NO fewshots.json (example queries unsupported for models)
        │   ├── kusto-<name>/ ...
        │   └── ontology-<name>/ ...
        └── published/                  # generated on publish — do NOT edit by hand
```

Folder prefixes: `lakehouse-tables-`, `warehouse-tables-`, `semantic-model-`, `kusto-`,
`ontology-`. Edit only `draft/`; `published/` is regenerated on `publish()`.

### What's diffable (and what isn't enforced)

- **Table selection is git-diffable**: each table in `datasource.json` `elements[]` carries
  `is_selected: true/false`. You can review exactly which tables an agent exposes in a PR.
- **Column-level `is_selected` is stored but NOT enforced** — selecting a table includes all its
  columns regardless of column flags. Don't rely on column deselection for security; use the
  source's own RLS/CLS/OneLake security.
- For semantic-model sources, remember the agent's selection is secondary to the model's **AI
  data schema** (see [`prep-for-ai-vs-agent.md`](prep-for-ai-vs-agent.md)).

## Review the agent and its model together

The semantic model is its own Git item in the same workspace. Put the agent's config and the
model's Prep-for-AI changes in the **same PR** so a reviewer sees a model change and its agent
impact at once. The operational rule — *model changed → re-run the test harness before merge* —
is in `fabric-data-agent-ops`; Git is what makes that change visible.

> **Prep for AI is a manual gate in any otherwise-as-code pipeline.** The AI data schema, verified
> answers, and AI instructions can be **read** programmatically (e.g. via the Power BI MCP
> `GetSemanticModelSchema`) but **not set** as code — they're UI-only today
> ([Pawar, 2026](https://fabric.guru/programmatically-retrieve-prep-data-for-ai-configuration-of-semantic-models)).
> So even a fully scripted agent build still has a human step on the model side; account for it.

## Building it as code — Python SDK (runs inside a Fabric notebook)

Package: `fabric-data-agent-sdk`. Verified API (sample notebooks + MS Learn). The SDK is
**notebook-only** (not local).

> **⏰ The data-plane (consumption) client uses the OpenAI Assistants API, which shuts down
> 26 Aug 2026.** Microsoft will migrate this to the Responses API "in a future update" but hasn't
> shipped the sample yet. The **management/config-as-code** calls below are unaffected; only the
> `FabricOpenAI(...)` *consumption* path carries this deadline. Don't hard-bake Assistants-API
> consumption you can't revisit.
>
> Today's consumption shape: `FabricOpenAI(artifact_name=..., ai_skill_stage="sandbox"|"production")`
> (the `ai_skill_stage` toggle picks draft vs published — handy for A/B-ing config changes) →
> `threads.create` → `messages.create` → `runs.create` → **poll** `runs.retrieve` (~2s; 300s
> default timeout) → read the assistant message. The **forward path** is the agent's **MCP server**
> (preview): a published agent exposes a downloadable `mcp.json`, runs under the *caller's* Entra
> identity, appears as a single tool, and keeps RLS/CLS/Purview — but **responses may leave
> Fabric's compliance/geo boundary** per the MCP client's policies, so vet it for regulated data.

```python
%pip install fabric-data-agent-sdk

from fabric.dataagent.client import (
    FabricDataAgentManagement, create_data_agent, delete_data_agent,
)

# Create + bind
agent = create_data_agent("ProductSalesAgent")          # returns a management handle
# (or bind to an existing one: agent = FabricDataAgentManagement("ProductSalesAgent"))

# Agent-level AI instructions (cross-source routing, tone, glossary)
agent.update_configuration(
    instructions="You answer product-sales questions. Route financial KPIs to the semantic "
                 "model and row-level lookups to the lakehouse. 'sales' means Net Sales."
)

# Add a data source
agent.add_datasource("AdventureWorksLH", type="lakehouse")   # type: "lakehouse" | "warehouse" | "kusto" | "semantic_model" | ...
ds = agent.get_datasources()[0]

# Select tables (schema, table); unselect to remove
for t in ["dimcustomer", "dimdate", "factinternetsales"]:
    ds.select("dbo", t)
# ds.unselect("dbo", "dimdate")

# Data-source-level instructions (lakehouse/warehouse/KQL only) — stored as additional_instructions
ds.update_configuration(
    instructions="Revenue = SUM(factinternetsales.SalesAmount). Exclude test rows (CustomerType<>'TEST')."
)
# read back: ds.get_configuration()["additional_instructions"]

# Example queries (few-shot) — dict of {question: SQL}; lakehouse/warehouse/KQL only
ds.add_fewshots({
    "How many employees are there?": "SELECT COUNT(*) AS n FROM dbo.dimemployee",
})
# ds.get_fewshots(); ds.remove_fewshot("<fewshot-id>")   # removal is singular, by id

agent.publish()
```

Verified building blocks: `create_data_agent(name)`, `delete_data_agent(name)`,
`FabricDataAgentManagement(name)`, `.get_configuration()`, `.update_configuration(instructions=)`,
`.add_datasource(name, type=)`, `.get_datasources()`, `.publish()`; datasource `.select(schema,
table)`, `.unselect(schema, table)`, `.update_configuration(instructions=)`,
`.add_fewshots(dict)`, `.get_fewshots()`, `.remove_fewshot(id)`, `.pretty_print()`.

**Not verified — do not assume:** a whole-datasource removal method
(`remove_datasource`/`delete_datasource`) is **absent from the PyPI changelog (all releases) and
all four sample notebooks as of 0.1.25a0 (Jun 2026)** — a confirmed negative, not just an
oversight. Datasource management surfaces only `add_datasource`, `get_datasources`, `select`,
`unselect`. To drop an entire source as code, verify the method first or do it in the portal/Git.
There is no separate "description" setter and no `set_instructions` — instructions are set via
`update_configuration`.

## Building it as code — REST item definition (config-as-code)

Data agents are items (`"type": "DataAgent"` from `GET /workspaces/{id}/items`). The full config
serializes as an **item definition** of base64-encoded JSON "parts" matching the Git layout
(`data_agent.json`, `draft/stage_config.json` with `aiInstructions`, per-source `datasource.json`
with `elements[]` + `dataSourceInstructions`, `fewshots.json`). Create/update via the standard
Create/Update-Item-With-Definition APIs, and the **Import/Export Item Definitions Batch APIs
(preview)** for bulk dev→test→prod promotion. This is the surface to use from an Azure DevOps
pipeline.

## CLI (`fab`) and CI/CD

- The **Fabric CLI (`fab`)** has *generic* `fab import` / `fab export` for item definitions, so a
  DataAgent definition can be round-tripped. There is **no documented dedicated `fab create
  data-agent` verb** — treat generic import/export as the supported CLI route.
- **`fabric-cicd`** (Microsoft's open-source Python deploy library) **explicitly supports the
  `DataAgent` item type** for code-first dev→test→prod promotion from a Git repo — a more concrete
  route than raw `fab import`/`export`, and the usual way teams parameterize what deployment
  pipelines can't (below).
- A **Terraform provider** resource (`fabric_data_agent`) is in progress on the same item-
  definition surface — a signal the documented JSON layout is stable, though not yet shipped.
- Microsoft's recommended automation is the **Azure DevOps Pipelines extension for Fabric**,
  which runs `fab` CLI tasks; pair with **deployment pipelines** for environment promotion —
  **with a big caveat:**

> **⚠️ Deployment pipelines promote the *item* but do NOT re-point a data agent's data-source
> bindings.** Practitioners (confirmed by MS support) found an agent promoted Test→Prod kept
> querying the **Test** lakehouse, because deployment-rule support doesn't yet cover data agents
> (preview). Plan to externalize environment-specific connections via **variable libraries** and/or
> re-point post-deploy. Also: **only the item *owner* can promote** via deployment pipelines —
> Member/Contributor isn't enough.
> ([Fabric Community + MS support, 2025](https://community.fabric.microsoft.com/t5/Fabric-platform/Deployment-of-notebooks-and-data-agent-via-Fabric-pipelines/m-p/4894049/highlight/true))
- **Auth caveat:** service principals are fully supported for **ALM** (Git/deployment pipelines).
  Runtime querying historically required a **user identity**, but **SPN runtime auth is now in
  preview** (custom apps / Foundry; KQL "coming soon"). So automated provisioning/promotion is
  solid; automated *asking the agent questions* via SPN is becoming viable but is preview —
  verify before relying on it.

## Sources

- Source control / CI/CD / Git: https://learn.microsoft.com/en-us/fabric/data-science/data-agent-source-control
- REST item definition schema: https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/definitions/data-agent-definition
- SDK overview: https://learn.microsoft.com/en-us/fabric/data-science/fabric-data-agent-sdk
- Fabric CLI: https://microsoft.github.io/fabric-cli/
