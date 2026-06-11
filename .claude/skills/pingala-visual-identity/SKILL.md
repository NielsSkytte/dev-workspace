---
name: pingala-visual-identity
description: Pingala's brand visual identity system — colors, fonts, and Microsoft Fabric icons. Use this skill whenever creating ANY visual output for Pingala, including presentations, Word documents, Excel files, PDFs, Figma designs, HTML pages, architecture diagrams, data flow visuals, or any deliverable that needs to look like a Pingala product. Trigger on any mention of Pingala colors, Pingala fonts, Pingala brand, Pingala styling, "our colors", "our brand", "make it look Pingala", "use the correct icons", "Microsoft Fabric icons", or any request to create a visual that should follow Pingala standards. Also trigger when creating architecture diagrams, data platform visuals, or Microsoft Fabric-related diagrams where Pingala branding should be applied. Even if the user doesn't explicitly ask for Pingala branding, use this skill whenever creating visuals in a Pingala project context.
---

# Pingala Visual Identity

This is the definitive reference for Pingala's visual identity. Apply these standards to ALL visual outputs — presentations, documents, web assets, diagrams, Figma designs, and any other deliverable.

## Color palette

Pingala uses a 5-row earthy/natural color palette. Each row has 4 shades progressing from darkest (left) to lightest (right). The leftmost color in each row is the base/primary color from that row.

### Row 1 — Teal / sage (primary brand teal)
| Role | Hex | Usage |
|------|------|-------|
| Base (dark) | `#60756E` | Primary teal, headers, key elements |
| Mid | `#8AA59F` | Secondary teal, supporting elements |
| Light | `#EEE4DE` | Warm light background, cards |
| Contrast | `#000000` | Black for maximum contrast text |

### Row 2 — Deep teal
| Role | Hex | Usage |
|------|------|-------|
| Base (dark) | `#4D7878` | Deep teal accents, data viz primary |
| Mid | `#6BA0A0` | Teal midtone, interactive states |
| Light | `#9BBCBC` | Light teal fills, chart areas |
| Lightest | `#C6DBDB` | Teal wash, subtle backgrounds |

### Row 3 — Burnt orange / terracotta (accent)
| Role | Hex | Usage |
|------|------|-------|
| Base (dark) | `#B5442A` | Primary accent, CTAs, highlights |
| Mid-dark | `#A7633E` | Warm mid-brown, secondary accent |
| Mid | `#BA7C4E` | Warm amber, tertiary accent |
| Light | `#E1A143` | Golden accent, warnings, emphasis |

### Row 4 — Warm gray / khaki
| Role | Hex | Usage |
|------|------|-------|
| Base (dark) | `#827560` | Warm gray text, muted elements |
| Mid | `#A1947F` | Warm mid-gray, borders, dividers |
| Light | `#BBA998` | Warm light, disabled states |
| Lightest | `#CBC4B9` | Warm wash, backgrounds |

### Row 5 — Cool gray / stone
| Role | Hex | Usage |
|------|------|-------|
| Base (dark) | `#726864` | Cool gray text, secondary content |
| Mid | `#908B84` | Cool mid-gray, supporting elements |
| Light | `#AEA8A4` | Cool light, subtle borders |
| Lightest | `#D0CCCA` | Cool wash, page backgrounds |

### Color usage rules

- **Primary brand colors**: Use Row 1 (teal/sage) and Row 2 (deep teal) as the dominant colors in any visual. These define the Pingala look.
- **Accent sparingly**: Row 3 (burnt orange/terracotta) is the accent palette. Use it for call-to-action elements, highlights, and emphasis — never as a dominant color.
- **Neutrals for structure**: Rows 4 and 5 (warm gray and cool gray) are for backgrounds, borders, body text, and structural elements.
- **Black (`#000000`)** is available for maximum-contrast headings and text on light backgrounds.
- **Charts and data viz**: Rotate through the base colors from each row: `#4D7878` (deep teal), `#B5442A` (burnt orange), `#60756E` (sage), `#827560` (warm gray), `#726864` (cool gray). Use lighter shades for fills and darker shades for strokes/labels.
- **Backgrounds**: Prefer `#EEE4DE` (warm cream from Row 1), `#C6DBDB` (light teal from Row 2), or `#D0CCCA` (cool stone from Row 5) for slide and card backgrounds. Avoid pure white — Pingala's palette is warm and earthy.

## Typography

Pingala uses three fonts with distinct roles:

| Font | Role | Usage |
|------|------|-------|
| **Aptos Display** | Headings | All headings (H1–H4), slide titles, section headers, document titles. Use bold or semibold weight. |
| **Aptos** | Body text | All body copy, paragraphs, bullet points, table content, captions, footnotes. Use regular weight; bold for emphasis within text. |
| **Ink Free** | Standout / creative | Callout boxes, pull quotes, handwritten-style annotations, creative highlights, informal labels. Use sparingly for personality and to draw attention. |

### Typography rules

- Never use Ink Free for body text or headings — it's reserved for accent/standout moments only.
- Aptos Display and Aptos are from the same family but Aptos Display is optimized for larger sizes. Always use Aptos Display at 18pt+ and Aptos for text below 18pt.
- When a font is not available in the target format (e.g., web), fall back to: Aptos Display → Calibri → sans-serif; Ink Free → Segoe Print → cursive. Never use Comic Sans MS — it is not permitted in Pingala visuals.
- Headings: Aptos Display, 24–40pt depending on context, semibold or bold.
- Subheadings: Aptos Display, 18–24pt, regular or semibold.
- Body: Aptos, 10–14pt, regular.
- Captions/footnotes: Aptos, 8–10pt, regular or italic.

## Microsoft Fabric icons

Pingala uses the official Microsoft Fabric icon set (v6.1.0) for all Fabric-related visuals. The icons are bundled in `assets/icons/svg/` as SVGs (32px and 48px sizes).

### Icon naming convention

Icons follow this pattern: `{name}_{size}_{variant}.{ext}`

- **Sizes**: 12, 16, 20, 24, 28, 32, 40, 48, 64
- **Variants**: `filled`, `regular`, `color`, `item`, `non-item`
- **Preferred size for diagrams**: 32px or 48px
- **Preferred variant**: Use `color` when available, then `filled`, then `item`

### Key Fabric icons for Pingala projects

When building architecture diagrams or Fabric-related visuals, use these correct icons:

| Component | Icon file (32px) | Notes |
|-----------|-----------------|-------|
| Microsoft Fabric | `fabric_32_color.svg` | Overall platform |
| Power BI | `power_bi_32_color.svg` | Reports and dashboards |
| Lakehouse | `lakehouse_32_item.svg` | Lakehouse items |
| Data Warehouse | `data_warehouse_32_item.svg` | Warehouse items |
| Data Factory | `data_factory_32_color.svg` | ETL/ELT platform |
| Pipeline | `pipeline_32_item.svg` | Data pipelines |
| Dataflow Gen2 | `dataflow_gen2_32_item.svg` | Dataflow items |
| Notebook | `notebook_32_item.svg` | Spark notebooks |
| OneLake | `one_lake_32_color.svg` | OneLake storage |
| Semantic Model | `semantic_model_32_item.svg` | Power BI datasets |
| Report | `report_32_item.svg` | Power BI reports |
| Dashboard | `dashboard_32_item.svg` | Power BI dashboards |
| Eventstream | `eventstream_32_item.svg` | Real-time streams |
| KQL Database | `kql_database_32_item.svg` | Real-time analytics |
| SQL Database | `sql_database_32_item.svg` | SQL databases |
| Data Engineering | `data_engineering_32_color.svg` | Engineering workload |
| Data Science | `data_science_32_color.svg` | ML workload |
| Spark Job | `spark_job_direction_32_item.svg` | Spark jobs |
| Environment | `environment_32_item.svg` | Environments |

### How to use icons

- **In presentations**: Read the SVG from `assets/icons/svg/` and embed it. Use the 48px variant for slide content, 32px for smaller elements.
- **In documents**: Convert the SVG to an image when embedding in Word/PDF. Use 32px for inline, 48px for featured.
- **In diagrams**: Use the SVG versions at 32px for node icons. Place them inside or adjacent to boxes in architecture diagrams.
- **In HTML/web**: Use the SVG files inline or as `<img>` sources.

The bundled set includes 32px and 48px variants (the most useful sizes for diagrams and documents). Only SVG format is included to keep the skill lightweight. If you need other sizes or PNG format, they can be sourced from the Microsoft Fabric Icons npm package (`@fabric-msft/svg-icons` v6.1.0).

To find the right icon, check `assets/icons/svg/` and search by the component name. Icons are always lowercase with underscores.

## Dynamics 365 icons

Pingala also uses the official Microsoft Dynamics 365 scalable icon set for all D365-related visuals. These are bundled in `assets/icons/d365/` as SVG files.

### D365 icon reference

| Component | Icon file | Notes |
|-----------|----------|-------|
| Dynamics 365 (brand) | `Dynamics365_scalable.svg` | Overall D365 logo/family icon |
| Finance & Operations | `FinanceOperations_scalable.svg` | F&O combined icon |
| Finance | `Finance_scalable.svg` | D365 Finance standalone |
| Supply Chain Management | `SupplyChainManagement_scalable.svg` | SCM module |
| Commerce | `Commerce_scalable.svg` | Retail/commerce module |
| Human Resources | `HumanResources_scalable.svg` | HR module |
| Sales | `Sales_scalable.svg` | CRM sales |
| Sales Insights | `SalesInsights_scalable.svg` | AI-powered sales insights |
| Customer Service | `CustomerServices_scalable.svg` | Service module |
| Customer Insights | `CustomerInsights_scalable.svg` | CDP / customer data |
| Customer Voice | `CustomerVoice_scalable.svg` | Survey / feedback |
| Field Service | `FieldService_scalable.svg` | Field operations |
| Project Operations | `ProjectOperations_scalable.svg` | Project management |
| Business Central | `BusinessCentral_scalable.svg` | SMB ERP |
| Contact Center | `ContactCenter_scalable.svg` | Contact center module |
| Intelligent Order Management | `IntelligentOrderManagement_scalable.svg` | Order orchestration |

### When to use D365 icons vs Fabric icons vs Azure icons

- **Fabric icons** (`assets/icons/svg/`): Use for Microsoft Fabric components — Lakehouse, Pipeline, Data Warehouse, Power BI, OneLake, etc.
- **D365 icons** (`assets/icons/d365/`): Use for Dynamics 365 applications — F&O, Finance, SCM, Sales, Customer Insights, etc.
- **Azure icons** (`assets/icons/azure/`): Use for Azure platform services — Key Vault, Entra ID, Azure SQL, Storage Accounts, DevOps, networking, etc.
- **Combined diagrams**: In end-to-end architecture visuals (e.g., D365 F&O → Azure Data Factory → Fabric Lakehouse → Power BI), use each icon set for its respective layer.

## Azure service icons

Pingala uses the official Azure Public Service Icons (v23) for Azure infrastructure and platform services. These are bundled in `assets/icons/azure/` as SVGs.

### Azure icon reference

| Component | Icon file | Notes |
|-----------|----------|-------|
| Azure Data Factory | `10126-icon-service-Data-Factories.svg` | ADF pipelines |
| Azure Synapse Analytics | `00606-icon-service-Azure-Synapse-Analytics.svg` | Synapse workspace |
| Azure Databricks | `10787-icon-service-Azure-Databricks.svg` | Databricks workspace |
| Azure Data Explorer | `10145-icon-service-Azure-Data-Explorer-Clusters.svg` | ADX clusters |
| Event Hubs | `00039-icon-service-Event-Hubs.svg` | Streaming ingestion |
| Stream Analytics | `00042-icon-service-Stream-Analytics-Jobs.svg` | Real-time analytics |
| Power BI Embedded | `03332-icon-service-Power-BI-Embedded.svg` | Embedded analytics |
| Power Platform | `03335-icon-service-Power-Platform.svg` | Power Platform suite |
| Data Lake Storage | `10090-icon-service-Data-Lake-Storage-Gen1.svg` | ADLS |
| SQL Database | `10130-icon-service-SQL-Database.svg` | Azure SQL DB |
| SQL Server | `10132-icon-service-SQL-Server.svg` | SQL Server |
| Azure SQL | `02390-icon-service-Azure-SQL.svg` | Azure SQL family |
| PostgreSQL | `10131-icon-service-Azure-Database-PostgreSQL-Server.svg` | Postgres |
| Cosmos DB | `10121-icon-service-Azure-Cosmos-DB.svg` | NoSQL database |
| Database Migration | `10133-icon-service-Azure-Database-Migration-Services.svg` | DMS |
| Storage Accounts | `10086-icon-service-Storage-Accounts.svg` | Blob/file storage |
| Key Vaults | `10245-icon-service-Key-Vaults.svg` | Secrets management |
| Entra Connect | `02854-icon-service-Entra-Connect.svg` | Identity sync |
| Entra Domain Services | `10222-icon-service-Entra-Domain-Services.svg` | Managed AD |
| Groups | `10223-icon-service-Groups.svg` | Security groups |
| Defender for Cloud | `10241-icon-service-Microsoft-Defender-for-Cloud.svg` | Security |
| Azure DevOps | `10261-icon-service-Azure-DevOps.svg` | CI/CD pipelines |
| Logic Apps | `02631-icon-service-Logic-Apps.svg` | Workflow automation |
| API Management | `10042-icon-service-API-Management-Services.svg` | API gateway |
| Event Grid | `10206-icon-service-Event-Grid-Topics.svg` | Event routing |
| Virtual Networks | `10061-icon-service-Virtual-Networks.svg` | VNets |
| Resource Groups | `10007-icon-service-Resource-Groups.svg` | Resource grouping |
| Subscriptions | `10002-icon-service-Subscriptions.svg` | Azure subscriptions |
| Policy | `10316-icon-service-Policy.svg` | Azure Policy |
| Automation | `00022-icon-service-Automation-Accounts.svg` | Runbooks |

## Applying the brand

### Presentations (PowerPoint)
- Title slides: Deep teal (`#4D7878`) background, white text in Aptos Display
- Content slides: Warm cream (`#EEE4DE`) or white background, dark text
- Accent elements: Burnt orange (`#B5442A`) for highlights, icons, and emphasis
- Use Fabric icons from the bundled set for any Microsoft Fabric content

### Documents (Word/PDF)
- Headings: Aptos Display in teal (`#60756E`) or deep teal (`#4D7878`)
- Body: Aptos in dark gray (`#726864`) or black
- Accent callouts: Ink Free for pull quotes or creative elements
- Table headers: Deep teal background with white text

### Diagrams and architecture visuals
- Use the Pingala color palette for all nodes and connections
- Apply Microsoft Fabric icons from `assets/icons/svg/` for Fabric components
- Apply Dynamics 365 icons from `assets/icons/d365/` for D365 source systems
- Apply Azure icons from `assets/icons/azure/` for Azure infrastructure (Key Vault, Entra ID, DevOps, networking, etc.)
- Primary flow arrows: Deep teal (`#4D7878`)
- Secondary flows: Warm gray (`#A1947F`)
- Highlight/emphasis: Burnt orange (`#B5442A`)

### Web and HTML
- Apply the Pingala palette as CSS variables or direct hex values
- Use the font stack: `'Aptos Display', Calibri, sans-serif` for headings
- Use `'Aptos', Calibri, sans-serif` for body
- Use `'Ink Free', 'Segoe Print', cursive` for standout elements
