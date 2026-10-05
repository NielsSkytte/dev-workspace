# Pingala Atomic — overview

> What Atomic is, what it solves, and which components it consists of. Component level only:
> no procedures, file paths or customer detail. Implementation evidence and file references are in
> `atomic.md`. Status 2026-10-05; statements marked *(to confirm)* await owner confirmation.

## 1. What Atomic is

Pingala Atomic is Pingala's accelerator for building a data platform on Microsoft Fabric from ERP
data. It is a set of pre-built, tested components that take ERP tables from the moment they land in
Fabric to a star-schema model that reports and semantic models read from.

It was designed for Microsoft Dynamics 365 Finance & Operations (F&O). It also runs on Dynamics AX
2009, which has the same table shape, and it takes non-ERP sources (REST APIs, marketing platforms,
event streams) through the same layers where their data has a key.

## 2. What it solves

| Problem without Atomic | What Atomic provides |
|---|---|
| Most project time (60-80%) goes to building data transformations before anything can be tested | Ingestion, history and transformation patterns that already exist and are tested |
| Every ERP table needs its own load logic, change detection and history handling | One generic ingestion that handles any keyed table the same way |
| Business logic is spread across notebooks, pipelines and procedures | Business logic lives in one place: SQL views, one per output table |
| Adding a table means changing pipelines | Adding a view is enough; orchestration finds it |
| Each project invents its own layers, names and keys | Fixed layers, naming, key and history columns, the same on every project |
| Moving between DEV, TEST and PROD breaks hard-coded ids | All environment-dependent ids are held in variable libraries |

## 3. Architecture at a glance

Data moves through five layers, each with one job:

```
Source systems
   │
Landing Zone ── staging copy of the source, untransformed
   │
Raw (Particles) ── full change history of every source table
   │
Enriched (Atoms) ── cleaned, joined business entities per source
   │
Curated (Molecules) ── one star schema: dimensions, facts, bridges, outbound
   │
Semantic model (Measures) ── measures, calculation groups, security
   │
Reports, data agents, outbound feeds
```

| Layer | Atomic name | Medallion | Fabric store | One per |
|---|---|---|---|---|
| Landing Zone | - | - | Lakehouse | source |
| Raw | Particles | Bronze | Lakehouse | source |
| Enriched | Atoms | Silver | Warehouse | source |
| Curated | Molecules | Gold | Warehouse | platform (one) |
| Semantic model | Measures | - | Power BI semantic model | platform |

Supporting all layers: a **Util** store for shared reference data and configuration.

## 4. Components

### 4.1 Landing Zone
- A staging lakehouse per source, kept apart in its own workspace and shared across environments.
- For F&O, Microsoft's Dataverse "Link to Fabric" delivers the tables; Atomic adds nothing here.
- For other sources, a source adapter fills it (see 4.8).

### 4.2 Raw — the history layer
- **Generic ingestion engine.** Two steps that work for every source table: detect which landed
  tables have changed, then read only the changed rows and merge them in.
- **Change detection** reads the change feed of the landed tables, so no per-table watermark logic
  is written.
- **Full history (SCD type 2)** on every table: each row carries current-flag, valid-from and
  valid-to columns, so any past state can be reconstructed.
- **Key handling**: the ERP record id where it exists; a key map for other sources.
- Source tables keep their source names; technical columns added by the source link are removed.
- Delivered as a Pingala Python library (Spark) plus two shared notebooks.

### 4.3 Enriched — the business-entity layer
- One warehouse per source.
- **Transformation views**: each business entity is one SQL view that reads current Raw rows,
  joins, renames and derives columns. The views are produced from a standard template by Pingala's
  view generator.
- **Materialisation procedure**: one generic stored procedure turns each view into a table of the
  same name, rebuilt in full every run.
- **Standard lineage columns** (`PIN_*`) on every row: source system, primary table, company,
  record id, timestamp, row check.

### 4.4 Curated — the star schema
- One warehouse for the whole platform; sources meet here.
- **Dimensions, facts and bridges**, each defined as a view and materialised by its own generic
  procedure, in the same pattern as Enriched.
- **Surrogate keys** on every dimension, with an "unknown" member so facts never lose rows on a
  missing reference.
- **Outbound schema** *(where used)*: projections of curated data shaped for systems that receive
  data back (CRM, marketing, partner exchange).

### 4.5 Semantic model
- One model over the curated star schema: tables, relationships, measures, calculation groups and
  row-level security.
- Refreshed as the last step of each run.

### 4.6 Util — shared reference and configuration
- Calendar and time tables.
- ERP enum labels (turns ERP code values into readable text).
- Key maps and ingestion status tables that drive the Raw layer.
- Seeded once per environment by a set-up routine.

### 4.7 Orchestration
- **One master pipeline** runs the layers in order — Raw, Enriched, Curated, semantic model — and
  runs sources in parallel within a layer.
- **Self-configuring transforms**: each layer's pipeline asks the warehouse which views exist and
  materialises all of them. The set of views is the configuration.
- Optional steps around the run: capacity scale-up and scale-down, outbound exports.

### 4.8 Source adapters
| Source type | How it reaches the Landing Zone |
|---|---|
| D365 F&O (and Dataverse/CRM) | Microsoft-managed Link to Fabric |
| Dynamics AX 2009 | Pingala copy pipeline through the on-premises data gateway |
| REST APIs (e.g. company registers) | Pingala ingestion notebook |
| Marketing platforms (e.g. Marketo) | Pingala bulk-extract notebook |
| Event streams (e.g. web analytics) | OneLake shortcut to captured event files |
| Spreadsheets (e.g. SharePoint Excel) | Dataflow |

From Raw onwards all keyed sources use the same components. Event data without a key uses an
append-only path instead of history tracking.

### 4.9 Environment and deployment components
- **Variable libraries** hold every workspace, store, connection and model id per environment, so
  the same items run unchanged in DEV, TEST and PROD.
- **Git-serialised items**: pipelines, notebooks, warehouse schemas and the semantic model are
  stored as code.
- **Promotion**: a Fabric deployment pipeline or Atomic's SQL deployment routine moves items
  between environments. *(to confirm: which is standard)*
- **Workspace preparation** routine that sets up a new environment for Atomic.

### 4.10 Conventions (the contract between components)
- Fixed name prefixes for items (`PL_` pipeline, `NB_` notebook, `VL_` variable library, `SM_`
  semantic model) and stores (`Lakehouse_Raw_<Source>`, `Warehouse_Enriched_<Source>`,
  `Warehouse_Curated`, `Lakehouse_Util`). A component knows a store's layer from its name.
- Fixed schema triples: a view schema holds the logic, a table schema holds the result, a
  procedure schema holds the materialiser.
- Fixed columns: `PIN_*` for lineage and keys, `SCD*` for history, `SurrogateKey` in Curated.

## 5. Related products
- **MetaAtomic** — Pingala's metadata product, run against an Atomic platform: lineage down to
  column level, a maturity matrix per data stream and environment, data-quality rules, and a portal.
  It relies on the conventions in 4.10.

## 6. Open points *(to confirm)*
- Whether Atomic is sold as a product, a method, or both.
- Whether a canonical, customer-independent Atomic codebase exists.
- Where the view generator lives and how it is versioned.
- Whether "Particles / Atoms / Molecules" is used beyond presentations (the code uses Raw /
  Enriched / Curated).
