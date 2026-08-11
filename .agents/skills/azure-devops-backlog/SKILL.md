---
name: azure-devops-backlog
bundle: custom
description: >
  Use this skill whenever the user wants to create, plan, or structure an Azure DevOps backlog
  from a project brief or document. Triggers on phrases like "create a backlog", "set up backlog",
  "generate work items", "plan my sprint", "break this into Azure DevOps items", or any mention of
  turning a project description into structured work items for Azure DevOps. Also trigger when the
  user shares a project brief (Word doc, PDF, or pasted text) and wants it turned into Epics,
  Features, Work Packages, or Tasks. Use this skill even if the user only mentions one part of the
  workflow (e.g. "draft some epics from this brief" or "push my backlog to DevOps").
---

# Azure DevOps Backlog Skill

Turn project briefs into a complete Pingala Datahub backlog and push it to Azure DevOps in one
go via a Python helper script. The skill is built around a small **parameters YAML** that captures
only the customer-specific variables — the full backlog (including all generic epics, features,
and standard work packages) is expanded by the script at push time.

---

## Files in this skill

```
azure-devops-backlog/
├── SKILL.md                                     # this file
├── scripts/
│   └── push_backlog.py                          # main helper script (CLI)
└── templates/
    ├── backlog_parameters.example.yaml          # commented schema / template
    └── data_excellence_description.html         # HTML for the Data Excellence epic
```

Run the script with Python 3.10+. Dependencies: `pip install requests pyyaml python-dotenv`.

---

## Standard Backlog Template (reference)

Every Datahub project produces the same shape. **[GENERIC]** parts are built automatically by the
script. **[CUSTOMER-SPECIFIC]** parts are driven by the parameters YAML.

```
Project
├── Epic: Business area: [X]                           [CUSTOMER-SPECIFIC — one per business area]
│   ├── Feature: Power BI Reports: [X]
│   │   └── Work Package: Report [name]
│   ├── Feature: Semantic model: [X]
│   │   ├── Work Package: [X]: Relationships
│   │   │   └── Task: [DimTable] -> [FactTable]
│   │   ├── Work Package: [X]: Business measures
│   │   │   └── Task: [X] measures: [Measure name]
│   │   └── Work Package: [X]: Row-level-Security
│   └── Feature: Curated: [X]
│       ├── Work Package: Dimension table: [Name]
│       ├── Work Package: Fact table: [Name]
│       └── Work Package: Bridge table: [Name]
│
├── Epic: Shared masterdata                             [GENERIC]
│   ├── Feature: Curated: Shared masterdata
│   │   ├── Work Package: Dimension table: Department
│   │   └── Work Package: Dimension table: Calendar
│   └── Feature: Semantic Model: Shared masterdata
│       ├── Work Package: Shared masterdata: Relationships
│       ├── Work Package: Shared masterdata: Business measures
│       └── Work Package: Shared masterdata: Row-level security
│
├── Epic: Data platform                                 [GENERIC — driven by data_sources list]
│   ├── Feature: Landing zone
│   │   └── User Story: Landing zone: [DataSource] (+ 3 standard tasks)
│   ├── Feature: Raw
│   │   └── User Story: Raw: [DataSource] (+ 3 standard tasks)
│   ├── Feature: Enriched
│   │   └── Work Package: Enriched: [DataSource]
│   │       └── Task: [DataSource]: [EntityName]
│   └── Feature: Util & platform
│       ├── Work Package: Workspaces (+ data/reporting workspace task per business area)
│       ├── Work Package: Azure DevOps & Deployment pipelines
│       ├── Work Package: Roles and groups
│       └── Work Package: Environments (Dev / Test / Prod)
│
└── Epic: Data excellence                               [GENERIC — HTML maturity-journey description]
    ├── Feature: 1. Automate
    ├── Feature: 2. Align & elaborate
    ├── Feature: 3. Validate
    ├── Feature: 4. Adopt
    ├── Feature: 5. Integrate
    └── Feature: 6. Transform
```

---

## One-time setup

1. Create a Personal Access Token in Azure DevOps with **Work Items: Read, write, & manage** scope.
2. Create a `.env` file (anywhere — typically next to the backlog YAML):
   ```
   AZDO_ORG_URL=https://dev.azure.com/pingala
   AZDO_PROJECT=CustomerX-Datahub
   AZDO_PAT=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
3. Install deps once: `pip install requests pyyaml python-dotenv`.

Don't put the PAT in the YAML file or check it into Git.

---

## Phase 1 — Draft the parameters YAML

### Step 1: Read the brief

- If the user uploads a `.docx` or `.pdf`, read it using available tools.
- If pasted as text, use it directly.
- Extract these customer-specific variables:
  - **Business areas** (e.g. Sales, Finance, Procurement)
  - For each business area: **Power BI reports**, **dimension tables**, **fact tables**,
    **bridge tables** (if any), **relationships**, **business measures**
  - **Data sources / source systems** (e.g. AX09, SAP) and their **entities**
  - Any **shared masterdata** relationships or measures beyond the default Department + Calendar

If any of the above are unclear or missing from the brief, **ask before drafting**.

### Step 2: Write the parameters YAML

Produce a single `backlog.yaml` file following the schema in
`templates/backlog_parameters.example.yaml`. Keep it compact — one list entry per report, table,
relationship, measure, entity, etc. The full backlog will be expanded automatically.

### Step 3: Preview the tree

Run a dry-run so the user can see the full expanded backlog before anything is pushed:

```bash
python scripts/push_backlog.py --yaml backlog.yaml --dry-run
```

Share the tree output with the user. Iterate on the YAML — add/remove/rename entries — until the
user approves. Do **not** proceed to Phase 2 until explicitly confirmed.

---

## Phase 2 — Push to Azure DevOps

### Step 4: Run the script

```bash
python scripts/push_backlog.py --yaml backlog.yaml --execute --env .env
```

What the script does:

1. Expands the parameters YAML into the full backlog tree (same as `--dry-run`).
2. Queries Azure DevOps via WIQL for all existing non-removed items in the project.
3. Marks any item whose title already exists as **skipped** (and reuses its ID so later children
   still get linked to the real parent).
4. Creates the remaining items **level by level**, with up to 10 parallel workers per level.
   Parents always finish before their children start, so the hierarchy links are always valid.
5. Retries on HTTP 429 with exponential backoff.
6. Prints a summary table: counts of created / skipped / failed, a markdown table of new IDs,
   and details of any failures.

The script is **idempotent**: re-running after adding a new business area or measure just creates
the new items. Nothing duplicates.

### Step 5: Report results

Share the script's summary output with the user. If any items failed, offer to retry (fix the
error, then re-run — skipped items stay skipped).

---

## How parameters map to work items

| Parameter                        | Produces                                                             |
|----------------------------------|----------------------------------------------------------------------|
| `business_areas[].name`          | Epic `Business area: {name}` + three Features (Reports / Semantic / Curated) |
| `business_areas[].power_bi_reports[]` | Work Package `Report: {name}` under Power BI Reports feature    |
| `business_areas[].dim_tables[]`  | Work Package `Dimension table: {name}` under Curated feature         |
| `business_areas[].fact_tables[]` | Work Package `Fact table: {name}` under Curated feature              |
| `business_areas[].bridge_tables[]` | Work Package `Bridge table: {name}` under Curated feature          |
| `business_areas[].relationships[]` | Task under the `{area}: Relationships` work package                |
| `business_areas[].measures[]`    | Task `{area} measures: {name}` under the Business measures work package |
| `data_sources[].name`            | User Stories for Landing zone & Raw, Work Package for Enriched       |
| `data_sources[].entities[]`      | Task `{source}: {entity}` under Enriched work package                |
| `business_areas[].name` (again)  | `{area} data workspace` and `{area} reporting workspace` tasks in Util & platform |
| `shared_masterdata.relationships[]` | Tasks under `Shared masterdata: Relationships`                    |
| `shared_masterdata.measures[]`   | Tasks `Shared measures: {name}` under `Shared masterdata: Business measures` |
| `extra_items[]`                  | Appended verbatim to the backlog (use for one-off additions)         |

---

## Tips

- Default acceptance criteria are auto-generated for Report work packages and Row-level-Security
  work packages. To override, add the item to `extra_items` with your own `acceptance_criteria`.
- For a mid-project addition (new measure, new entity), edit the YAML and re-run with `--execute`.
  Existing items are skipped automatically.
- The script sets `System.AreaPath` and `System.IterationPath` to the project name by default.
  Override in the YAML under `project.area_path` / `project.iteration_path` if you need to file
  items under a specific area or sprint.
- Use `--workers N` to change parallelism (default 10). Lower it if you hit rate limits on a
  large backlog; raise it if your ADO instance is fast and you're pushing 500+ items.

---

## Troubleshooting

| Error                                    | Likely cause / fix                                                   |
|------------------------------------------|----------------------------------------------------------------------|
| `Missing credential(s)`                  | `.env` file not loaded or env vars not set                           |
| `HTTP 401`                               | PAT expired, wrong, or missing **Work Items: Read, write & manage**  |
| `HTTP 404` on WIQL                       | Wrong `AZDO_PROJECT` or `AZDO_ORG_URL`                               |
| `HTTP 400 ... field ... invalid`         | Work item type not enabled in the project process template           |
| Parent creation failed (cascades)        | Fix the parent error, re-run — children get retried automatically    |
| Rate-limited after 5 attempts            | Lower `--workers` (e.g. `--workers 4`) and re-run                    |

---

## Fallback: pure REST API (no script)

If Python isn't available, the same logic can be done manually via REST:

```
POST {orgUrl}/{project}/_apis/wit/workitems/${type}?api-version=7.1
Authorization: Basic {base64(":" + PAT)}
Content-Type: application/json-patch+json

[
  { "op": "add", "path": "/fields/System.Title", "value": "..." },
  { "op": "add", "path": "/fields/System.Description", "value": "..." },
  { "op": "add", "path": "/fields/Microsoft.VSTS.Common.AcceptanceCriteria", "value": "<ul>...</ul>" },
  { "op": "add", "path": "/relations/-", "value": {
      "rel": "System.LinkTypes.Hierarchy-Reverse",
      "url": "{orgUrl}/_apis/wit/workitems/{parentId}"
  }}
]
```

Create top-down so each child can link to its parent's real ID. This is what the script automates.
