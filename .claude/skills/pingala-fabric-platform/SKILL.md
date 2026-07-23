---
name: pingala-fabric-platform
bundle: custom
description: >
  How Pingala delivers Microsoft Fabric data platforms: architecture, workspace
  structure (LZ/Raw/Enriched/Curated), Pingala Atomic (Particles/Atoms/Molecules),
  medallion layers, ETL pipelines, CI/CD, data modelling, and data services. Trigger
  on any question about Pingala's Fabric setup, OneLake, capacity sizing, D365 F&O
  extraction, Dataverse integration, Power BI semantic models, deployment pipelines,
  environment strategy (dev/test/prod), Master Pipeline pattern, Views-to-Tables,
  data gateway, or GDPR handling. Also trigger on phrases like "our Fabric setup",
  "our data architecture", "Atomic framework", "data hub", "landing zone",
  "workspace structure", "bronze silver gold", or Fabric best practices in a Pingala
  context. Complements the fabric-project-access and pingala-project-playbook skills.
  Use even if the user only asks about one component.
---

# Pingala Fabric Data Platform — Implementation Guide

This skill documents how Pingala designs, builds, and operates Microsoft Fabric data
platforms for its customers. It covers the end-to-end technical implementation: from
platform architecture and workspace design through data extraction, transformation
(using Pingala Atomic), data modelling, CI/CD, and delivery of data services.

For user provisioning, Entra ID groups, licences, and security setup, see the
**fabric-project-access** skill. For the overall project lifecycle and playbook, see
the **pingala-project-playbook** skill.

Each component is covered inline below at a working depth. The areas below are **candidates
for a deeper standalone reference later** — captured here so the gaps aren't lost:

| Area to explore later | What a deeper dive would add |
|-----------------------|------------------------------|
| Architecture & workspaces | Workspace naming, capacity sizing, environment strategy, OneLake layout |
| Pingala Atomic | Particles/Atoms/Molecules layers and the full D365 F&O table mapping |
| ETL & pipelines | Data extraction, ingestion patterns, transformation patterns, pipeline orchestration |
| Data modelling | Medallion layer design, star schema, semantic models, measures |
| CI/CD & deployment | Git integration, Azure DevOps, deployment pipelines, environment promotion |
| Data services | Power BI reports, Data Activator, scorecards, data-as-a-service delivery |

---

## Platform overview

Pingala delivers data platforms built on **Microsoft Fabric**, Microsoft's unified SaaS
analytics platform. Fabric consolidates data integration, data engineering, data
warehousing, data science, real-time analytics, and Power BI into a single platform
backed by **OneLake** — a single logical data lake per tenant.

### Why Fabric

Pingala chose Microsoft Fabric as its standard data platform because it:

- Is the only platform that covers the entire end-to-end data process and delivers
  data-as-a-service from a single SaaS offering
- Stores all data in **OneLake** using the open **Delta Parquet** format, enabling
  multiple engines (Spark, T-SQL, Analysis Services) to work on the same data without
  duplication
- Integrates natively with the broader Microsoft Business Applications Ecosystem:
  Dynamics 365 F&O, Dataverse, Power Platform, and Azure services
- Provides built-in governance, security (via Microsoft Entra ID and Purview), and
  capacity-based billing
- Supports shortcuts to external data sources (ADLS Gen2, S3, Dataverse) without
  copying data

### Where Fabric fits in the Microsoft ecosystem

```
┌─────────────────────────────────────────────────────────┐
│           Microsoft Business Applications Ecosystem      │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Dynamics 365  │  │  Power       │  │  Microsoft   │  │
│  │ F&O           │◄─►│  Platform    │◄─►│  Fabric      │  │
│  │               │  │              │  │              │  │
│  │ Finance       │  │ Power Apps   │  │ Power BI     │  │
│  │ SCM           │  │ Power Auto.  │  │ OneLake      │  │
│  │ HR            │  │ Co-pilot St. │  │ Data Factory │  │
│  │ Commerce      │  │ AI builder   │  │ Data Eng.    │  │
│  └──────┬───────┘  └──────┬───────┘  │ Data Science │  │
│         │                  │          │ Data WH      │  │
│         └────────►┌────────┴───┐◄────│ Real-Time    │  │
│                   │ Dataverse  │     │ Data Activ.  │  │
│                   └────────────┘     └──────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────────┐│
│  │                    Azure Platform                     ││
│  │ Logic Apps · Service Bus · Azure Functions · Key Vault││
│  │ Entra ID · DevOps · Cost Mgmt · App Insights         ││
│  └──────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

### Integration pathways

- **D365 F&O → Dataverse → Fabric**: Two-way integration using linked services and
  virtual entities; primary path for structured ERP data
- **D365 F&O → Fabric (direct)**: Via Dataverse shortcuts or Fabric's native D365
  link; used for table-level extraction
- **Dataverse → Power Platform**: Native application layer; Power Apps, Power
  Automate, Co-pilot Studio
- **Fabric → Power BI**: Native embedding; Direct Lake mode for zero-copy reporting
- **Azure Service Bus → D365 F&O**: For data-heavy asynchronous integrations

---

## Architecture principles

Pingala follows these core principles when implementing Fabric:

1. **Medallion architecture** — All data flows through Bronze → Silver → Gold layers,
   with clear separation of concerns at each stage
2. **Workspace isolation** — Each medallion layer and each environment (Dev/Test/Prod)
   gets its own workspace for governance and access control
3. **Pingala Atomic acceleration** — For D365 F&O sources, Pingala Atomic pre-built
   transformations dramatically reduce the ETL effort, mapping raw tables through
   Particles → Atoms → Molecules
4. **Data-as-a-service** — The platform exists to deliver data services (reports,
   AI models, integrations, scorecards), not just to store data
5. **MVP mindset** — Start with the minimum viable data services, prove value early,
   and expand incrementally
6. **Standard over custom** — Use Pingala Atomic and proven patterns to avoid the
   "uniqueness bias" that plagues IT projects
7. **Modular independence** — Each data service should function independently and
   create value, allowing gradual integration
8. **Stock data in advance** — Because OneLake storage is extremely cheap, extract
   data before you need it so it's ready when business requirements emerge; don't
   wait for a use case to start ingesting

---

## Workspace structure

Pingala organises Fabric workspaces into three functional layers, each deployed across
three environments. The naming convention follows the pattern:
`{CustomerPrefix}-Fabric-{Layer}-{Environment}`

### Workspace layers

| Layer | Purpose | Key Fabric artifacts |
|-------|---------|---------------------|
| **LandingZone** | Ingestion and staging of raw data from source systems | Master Pipeline, Copy Activities, Shortcuts, one **LZ Lakehouse** per source system |
| **ETL** | Transformation and modelling of data through all medallion layers | Master Pipeline (Raw → Enriched → Curated → Model sub-pipelines), **Raw Lakehouse** (per source), **Enriched Warehouse** (per source), **Curated Warehouse** (shared), Notebooks, Environments |
| **DataService** | Consumption-ready data services delivered to the business | Semantic Models, Power BI Reports, Power BI Apps, Scorecards, Data Activator (Reflex) |

### Environment matrix

| | DEV | TEST | PROD |
|---|-----|------|------|
| **LandingZone** | LandingZone-DEV | LandingZone-TEST | LandingZone-PROD |
| **ETL** | ETL-DEV | ETL-TEST | ETL-PROD |
| **DataService** | DataService-DEV | DataService-TEST | DataService-PROD |

This results in **9 workspaces** per customer project. All workspaces are assigned to
a shared Fabric capacity and secured via Entra ID security groups (see the
fabric-project-access skill for the full group matrix).

### Workspace role mapping

Each workspace layer uses a consistent Admin / Member / Contributor pattern:

- **Admin**: Pingala solution architect (full control)
- **Member**: All Pingala consultants (can create and modify artifacts)
- **Contributor**: Customer resources (DEV and TEST only — no direct PROD access)
- **Viewer / App viewer**: End users consuming published data services (DataService only)

Production workspaces have no Contributor access — all changes flow through CI/CD.

---

## Medallion architecture — Pingala implementation

Pingala implements the medallion architecture using separate Fabric artifacts for each
layer. The standard Pingala artifact naming maps to the medallion terminology and
(for D365 F&O sources) the Pingala Atomic framework:

| Pingala artifact name | Medallion layer | Atomic name | Fabric artifact type | Purpose |
|----------------------|----------------|-------------|---------------------|---------|
| **LZ Lakehouse** | (Landing zone) | — | Lakehouse | Raw data landed from source systems via Copy Activity or Shortcuts |
| **Raw Lakehouse** | **Bronze** | **Particles** | Lakehouse | Auto-loaded from LZ with type-2 history tracking; no business logic |
| **Enriched Warehouse** | **Silver** | **Atoms** | Data Warehouse | Standardised views → tables: uniform types, chosen columns, surrogate keys, null handling, date dimension |
| **Curated Warehouse** | **Gold** | **Molecules** | Data Warehouse | Business-customised dimensional model: facts and dimensions for reporting and analytics |
| **Semantic Model** | **Measures** | — | Semantic Model (Power BI) | DAX measures, time intelligence, KPIs on top of the Curated layer via Direct Lake |

### Multi-source pattern

When a customer has multiple source systems (e.g. two Dynamics AX instances plus
Navision), each source gets its own isolated set of artifacts in the Landing Zone and
ETL workspaces. All sources converge into a single shared Curated Warehouse:

```
Source A ──► LZ Lakehouse (A) ──► Raw Lakehouse (A) ──► Enriched Warehouse (A) ──┐
Source B ──► LZ Lakehouse (B) ──► Raw Lakehouse (B) ──► Enriched Warehouse (B) ──┼──► Curated Warehouse (shared) ──► Semantic Model
Source C ──► LZ Lakehouse (C) ──► Raw Lakehouse (C) ──► Enriched Warehouse (C) ──┘
```

This pattern ensures each source system's ingestion and transformation logic is
isolated (one failing source doesn't break others), while the Curated layer provides
a single unified dimensional model across all sources.

### Layer details

**Landing Zone (LZ Lakehouse):**
- Data lands from source systems via Copy Activity (batch) or Shortcuts (near real-time)
- One LZ Lakehouse per source system
- No transformations applied — pure staging area
- For on-premises sources (legacy Dynamics AX, Navision, on-prem SQL), a **data gateway**
  must be installed on the customer's server; Copy Activity connects through this gateway

**Raw Lakehouse (Bronze / Particles):**
- Auto-loaded from the LZ Lakehouse
- Type-2 slowly changing dimension (SCD2) history is built at this layer to preserve
  a complete audit trail
- **GDPR opt-out**: SCD2 can be selectively disabled per table for tables containing
  personally identifiable information — these tables are overwritten instead of
  historised, ensuring GDPR compliance
- Transformations are defined as **views** first, then materialised into **Delta tables**
- Typical D365 F&O project: 40–80 raw tables extracted
- No business logic — only structural operations (type casting, history tracking)

**Enriched Warehouse (Silver / Atoms):**
- Tables are combined, merged, and joined into standardised business entities
- Transformations are defined as **SQL views** first, then materialised into **tables**
- Uniform data types applied across all tables
- Only chosen/relevant columns retained
- Surrogate keys generated between all tables where relationships are possible
- Missing values, blanks, and nulls handled consistently
- Date dimension table created
- One Enriched Warehouse per source system
- For D365 F&O: the 40–80 Particle tables are consolidated into roughly 20–30 Atom
  tables (e.g., a unified Customer table, a unified Item table, a unified Sales
  Transaction table)

**Curated Warehouse (Gold / Molecules):**
- The Enriched tables from all source systems are modelled into a unified dimensional
  star schema in a single shared Curated Warehouse
- Transformations defined as **views**, then materialised into **tables**
- Typical project: 13–17 dimension tables and 8–15 fact tables
- Customised to the customer's business domain and reporting needs
- This is where customer-specific business rules, hierarchies, and aggregations live
- The Curated layer is the primary consumption layer for all data services

**Semantic Model (Measures):**
- DAX measures built across the fact and dimension tables
- Complex time intelligence (YTD, QTD, MTD, YoY, rolling averages)
- KPIs aligned to the customer's business objectives
- Delivered via Power BI semantic models connected to the Curated Warehouse using Direct Lake

---

## Pingala Atomic framework

Pingala Atomic is Pingala's proprietary accelerator for transforming Dynamics 365 F&O
data into analytics-ready data models in Microsoft Fabric. It exists because D365 F&O
has approximately 23,000 tables, and even a simple reporting requirement (e.g., "what
items did we sell to which customers") can require joining 30+ raw tables.

### The problem Atomic solves

Without Atomic, a typical data platform project spends 60–80% of its time on data
transformations and modelling — identifying which of the 23,000 tables are needed,
understanding their relationships, joining them correctly, and handling D365 F&O's
complex data structures (dimension attributes, financial tags, inventory dimensions,
etc.).

### How Atomic works

Pingala Atomic provides **pre-built, tested transformation logic** that maps the raw
D365 F&O tables (Particles) through standardised intermediate views (Atoms) into
business-ready dimensional models (Molecules). The transformations cover:

- Table identification: Which of the 23,000 tables are needed for each domain
- Join logic: How tables relate to each other (including D365 F&O's non-obvious
  relationships like DimensionAttributeValueCombination, InventDim, etc.)
- Type-2 history: SCD2 tracking on extracted tables (with per-table opt-out for
  GDPR-sensitive tables containing personal data)
- Data type standardisation: Consistent types across all columns
- Surrogate key generation: Integer keys for all table relationships
- Null/blank handling: Consistent treatment of missing data
- Date dimension: Standard calendar table with fiscal period support
- Star schema modelling: Pre-defined fact and dimension structures

### Key D365 F&O tables handled by Atomic

Atomic covers tables including (non-exhaustive): DimensionFinancialTag, CategoryTable,
ProjCategory, CompanyInfo, CustTable, DirPartyTable, LogisticsElectronicAddress,
DimensionAttributeValueSet, OMOperatingUnit, DimensionAttributeValueCombination,
ProjFundingSource, ProjGrant, MainAccount, EcoResProduct, EcoResProductTranslation,
InventItemGroupItem, InventTable, ProjTable, WrkCtrTable, and many more.

### Atomic value proposition

| Aspect | Traditional project | With Pingala Atomic |
|--------|--------------------|--------------------|
| Time allocation | 60–80% on transformations | Majority on data services and value |
| Risk | High — custom ETL is error-prone | Low — pre-tested standard logic |
| Testing speed | Slow — must build ETL before testing | Fast — Atomic accelerates ETL, enabling earlier testing |
| Budget model | Mostly time & materials | Significant portion as fixed fee |
| Worst case | 50%+ cost overrun (IT project average) | Even worst case delivers in half the time of traditional |

> **Area to explore later:** a deeper dive into the Atomic framework — the full table
> mapping and transformation specifications — is a candidate for a standalone reference doc.

---

## Data extraction patterns

Pingala uses different extraction methods depending on the data source:

### Dynamics 365 F&O (primary source for most customers)

Two approaches exist for getting data out of D365 F&O:

1. **Entity-based approach** (upper path): D365 F&O → Entities → Dataverse → Fabric
   Curated Warehouse. Requires a D365 developer to build/maintain entities. Simpler but
   limited flexibility.

2. **Table-based approach** (lower path — Pingala's preferred): D365 F&O → Dataverse
   Tables → LZ Lakehouse → Raw Lakehouse → Enriched Warehouse → Curated Warehouse →
   Power BI. Extracts raw tables directly, giving full control over transformation
   logic. This is the path Pingala Atomic is designed for.

### On-premises sources (legacy Dynamics AX, Navision, on-prem SQL)

For non-cloud sources, a **Microsoft on-premises data gateway** must be installed on
a server within the customer's network. Data Pipelines use Copy Activity through
the gateway to extract data into the LZ Lakehouse. This is common — many Pingala
customers have legacy Dynamics AX or Navision instances running on-prem.

### Other data sources

- **ServiceNow**: Connected via Data Pipelines in Fabric Data Factory; relevant tables
  extracted to LZ Lakehouse
- **Confluence / Azure DevOps**: API-based extraction
- **CSV / Excel / flat files**: Uploaded to Lakehouse Files area, then loaded to
  Delta tables
- **Streaming sources**: Eventstream → Eventhouse for real-time data

### Extraction tooling

| Tool | When to use |
|------|-------------|
| **Dataverse Shortcuts** | D365 F&O / Dataverse data; zero-copy, near real-time |
| **Data Pipeline (Copy Activity)** | External sources requiring scheduled batch loads |
| **Dataflow Gen2** | Low-code transformations during ingestion |
| **Eventstream** | Real-time / streaming data sources |
| **Notebook (Python or PySpark)** | Complex extraction logic, API calls, custom connectors |

> **Notebook default — Python over PySpark.** Default to plain **Python notebooks**
> (single-node: pandas/polars/duckdb) for notebook logic. Reach for **PySpark/Spark
> notebooks only when a concrete compute requirement has been identified** (data
> volumes or distributed processing that a single node can't handle). Python notebooks
> start faster and consume far fewer CUs — on small capacities (F4–F8) this matters.
> Owner preference (Niels, 2026-07-16): always Python unless the Spark-scale need is proven.

---

## CI/CD and deployment

Pingala implements CI/CD using the combination of Azure DevOps Git integration and
Fabric's built-in deployment pipelines.

> **Role requirement — CI/CD needs Workspace Admin.** Connecting a workspace to Git
> and creating/assigning deployment pipelines both require the **Workspace Admin**
> role. Member and Contributor can commit/update against an *already-connected* repo,
> but cannot connect the workspace to Git or create/assign deployment pipelines.
> Whoever sets up CI/CD on a workspace must be Admin on it — on smaller engagements
> where the delivering consultant also does the CI/CD setup, that consultant needs
> Admin, not just Member.

### Source control

- All Fabric workspaces are connected to an **Azure DevOps Git repository**
- The DEV workspace is connected to a `develop` branch
- Changes are committed from the DEV workspace to the develop branch
- Pull requests promote changes from `develop` → `main`
- The `main` branch represents production-ready code

### Deployment flow

```
DEV workspace ──commit──► develop branch ──PR──► main branch
                                                      │
                          TEST workspace ◄────────────┘
                               │
                          PROD workspace ◄── deploy from TEST
```

Fabric Deployment Pipelines provide the UI-based promotion mechanism across
environments. The pipeline has three stages: Development, Test, and Production.

### Key CI/CD practices

- No direct changes in TEST or PROD workspaces
- All changes originate in DEV and flow through Git
- Service principals are used for automated deployments where possible
- Connection parameters are managed via deployment rules (different data sources per
  environment)
- Fabric items are version-controlled: Notebooks, Pipelines, Semantic Models,
  Reports, Lakehouses, Warehouses

---

## Fabric capacity and cost

Pingala typically starts customers on a **Fabric F4 capacity** (North Europe region),
which provides a cost-effective entry point for initial projects.

### Typical monthly cost structure (list prices, example)

| Component | Approximate monthly cost |
|-----------|------------------------|
| Power BI Pro licences (e.g., 250 users × $10) | ~17,000 DKK |
| Power BI Premium Per User (e.g., 20 users × $20) | ~2,700 DKK |
| Fabric F4 capacity (North Europe) | ~3,700 DKK |
| OneLake storage | ~30 DKK |
| **Total** | **~23,400 DKK/month** |

OneLake storage is extremely cheap (approximately 0.154 DKK per GB/month), which
supports the "stock data in advance" philosophy — extract data before you need it
so it's ready when business requirements emerge.

### Capacity sizing guidance

- **F4**: Suitable for small-to-medium projects; 1–3 concurrent data services
- **F8–F16**: Medium projects with multiple concurrent workloads
- **F32+**: Large enterprises with heavy ETL and many concurrent users
- Capacity can be paused/resumed to control costs during off-hours
- Fabric provides elastic burst capacity — workloads can temporarily exceed the
  base SKU

---

## Data services — delivering value

The entire purpose of the platform is to deliver **data services** to the business.
The Fabric platform is the enabler; data services are the value.

### Types of data services Pingala delivers

| Service type | Fabric artifact | Example |
|-------------|----------------|---------|
| **Financial reporting** | Power BI Report | Finance and budget reporting with financial dimensions |
| **Project reporting** | Power BI Report | Project cost, grants, limits, categories, resources |
| **Sales reporting** | Power BI Report | Products, sales, customers across time |
| **OKR & strategy execution** | Power BI Scorecard | Rolling out corporate strategy with automated follow-up |
| **Real-time price adjustments** | Data Activator (Reflex) | Price elasticity + daily turnover → automated pricing updates |
| **Churn prediction** | Data Science + Dataverse | ML model identifies at-risk customers; alerts in CRM |
| **AI agents** | Co-pilot Studio + Azure AI | Case resolution assistance, knowledge search, case routing |

### AI data platform capabilities

For customers requiring AI alongside analytics (e.g., the Pandora AI data platform
pattern), Pingala extends the Fabric platform with:

- **Microsoft Co-pilot Studio & Azure OpenAI**: Custom AI agents using RAG and
  fine-tuning on support data
- **Azure AI Search**: Knowledge article and case history indexing
- **Azure AI Foundry**: Enterprise-grade AI model hosting and management
- **Microsoft Fabric as the data backbone**: All relevant data extracted, transformed,
  and made available for both analytics and AI consumption

The AI solution canvas methodology (Why / What / How) is used to define each AI
use case before implementation. See the Pandora AI data platform presentation for
the full canvas template and example.

---

## Proposed implementation process

A standard Pingala Fabric implementation follows this timeline:

| Phase | Activity | Typical estimate | Timeline |
|-------|----------|-----------------|----------|
| 1 | AI/data solution definition workshops (3 workshops) | 40 hours | Weeks 1–4 |
| 2 | Setup of Microsoft Fabric (capacity, workspaces, medallion architecture, CI/CD, security) | 70 hours | Weeks 3–4 |
| 3 | Connect to and extract source data into Fabric | 40 hours | Weeks 4–5 |
| 4 | Transform and model data (apply Pingala Atomic or custom ETL) | 125–175 hours | Weeks 6–10 |
| 5 | Build data services (reports, AI solutions, integrations) | Varies | Weeks 8+ |
| 6 | Go-live, training, and handover | Included | Final weeks |

With Pingala Atomic, phases 2–4 are significantly accelerated compared to traditional
data platform projects, allowing more time and budget to be spent on phase 5 (data
services that create actual business value).

---

## Quick reference — key technology choices

| Decision | Pingala standard |
|----------|-----------------|
| Data platform | Microsoft Fabric (SaaS) |
| Storage layer | OneLake (ADLS Gen2, Delta Parquet) |
| Architecture pattern | Medallion: Landing Zone → Raw → Enriched → Curated → Measures |
| Accelerator for D365 F&O | Pingala Atomic (Particles/Atoms/Molecules) |
| Landing Zone artifact | LZ Lakehouse (one per source system) |
| Raw / Bronze artifact | Raw Lakehouse (one per source system) |
| Enriched / Silver artifact | Enriched Warehouse (one per source system) |
| Curated / Gold artifact | Curated Warehouse (single shared across sources) |
| Measures artifact | Power BI Semantic Model (Direct Lake mode) |
| Transformation pattern | Views → Tables at every layer |
| Pipeline orchestration | Master Pipeline → sub-pipelines (Raw, Enriched, Curated, Model) |
| SCD2 history | Built in Raw layer; per-table GDPR opt-out supported |
| Source control | Azure DevOps Git |
| CI/CD | Fabric Deployment Pipelines + Azure DevOps |
| Security model | Entra ID security groups per workspace layer |
| Capacity entry point | Fabric F4 (North Europe) |
| Transformation language | Python (Notebooks) and T-SQL; PySpark only on identified compute need |
| Orchestration | Fabric Data Pipelines (Master + sub-pipelines) |
| On-prem connectivity | Data Gateway for non-cloud sources |
| AI platform (when needed) | Azure AI Foundry + Co-pilot Studio + Fabric |

---

## Related skills

- **pingala-visual-identity** — apply Pingala's palette and the correct Microsoft Fabric icons
  whenever the architecture diagrams above are rendered as real visuals (slides, docs, HTML).
- **e2e-medallion-architecture** (Microsoft) — the generic build mechanics for the
  Bronze/Silver/Gold stack. This skill is the Pingala *methodology* (Atomic, workspace naming,
  GDPR opt-out); that one is the *execution*.

(See also **fabric-project-access** and **pingala-project-playbook**, referenced at the top.)
