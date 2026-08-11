---
name: pingala-stream-maturity-matrix
bundle: custom
description: Standardized methodology and visual template for Agent M & Agent Q to track, evaluate, and present overall data platform progress across customer projects. Generates an executive-ready Data Stream Maturity Matrix & Solution Architecture Overview HTML report following Pingala Visual Identity standards, tracking 6 Medallion pipeline stages with live data counts, neutral progress grays, and strict 4-color status semantics (Green = PROD Live ONLY, Neutral = DEV/TEST Active, Yellow = Stale >30d, Red = Documented Blocker).
---

# Pingala Data Stream Maturity Matrix & Architecture Overview

This skill defines the canonical methodology for **Agent M** (Head of Operations & Continuity) and **Agent Q** (System Architect) to evaluate, track, and visually report implementation progress across all Pingala data platform projects.

---

## 1. Core Architectural & Visual Principles

1. **One Stream Per Ingest Source System & Two-Way Stream Support:**  
   * **Standard One-Way Streams:** Distinct origin systems render as single rows.  
   * **Two-Way Integration Streams (e.g., Marketo Sync):** Systems with bi-directional flow (Inbound Ingestion $\leftrightarrow$ Outbound Reverse-ETL Write-Back) expand row height cleanly and render **2 stacked sub-cards** across the 7 pipeline columns:
     - ⬇️ **Inbound Ingestion Track:** (Marketo REST API $\rightarrow$ Fabric Medallion Bronze/Silver/Gold).
     - ⬆️ **Outbound Write-Back Track:** (Fabric Gold $\rightarrow$ Reverse-ETL $\rightarrow$ Marketo API).

2. **Two-Section Architecture Structure (Pipelines vs Data Models & Activation):**  
   * **Section 1: Ingestion & Data Stream Pipelines Overview (Stages 1 to 5):**  
     Tracks independent data engineering ingestion streams from origin source through Curated storage (`1. Source`, `2. Landing Zone`, `3. Raw`, `4. Enriched`, `5. Curated`).  
   * **Section 2: Data Models & Activation Overview (Stages 6 to 7):**  
     Tracks semantic data models and activation delivery where streams join together (e.g. AX 2009 Sales + CVR Register joined into `Enterprise Sales & Customer Analytics Model`). Columns: `6. Semantic Model (Data Model)` and `7. Activation (Reports & Delivery)`. Allows separate tracking of BI/analytics work done by separate colleagues.

3. **Single Live Data Metric with Highest-Environment Pointer Badge:**  
   To prevent metric clutter across multiple environments, every stage node renders **ONE single volume number** accompanied by an explicit **Environment Pointer Badge** (`(DEV)`, `(TEST)`, or `(PROD)`) indicating the highest environment that generated that data count:
   * **`324M Staged (DEV)`**: Data volume comes from DEV (because TEST ingestion run is pending).
   * **`27.1M Delta Rows (TEST)`**: Data volume verified in TEST.
   * **`56M Rows (PROD)`**: Data volume live in PROD.

4. **Environment Readiness Track `[ DEV | TEST | PROD ]` & Dynamic Workspace Scope:**  
   * **Custom Environment Scope:** Supports customers operating with `[ DEV | PROD ]` only (automatically hides the TEST chip when a customer has no TEST workspace).
   * **Live Fabric vs Git Repo Distinction:** Stage status is marked `"done"` (`DEV ✓`) ONLY when deployed and live in the Fabric workspace. If notebook/python code exists in the local git repository (`src/`, `fabric/`) but has not been deployed to Fabric, it remains marked `"pending"` (`DEV ⏳`) with an explicit note *"Code in Git repo, pending deployment to Fabric"*.
   * **Chip States:**
     - `DEV ✓`: Live and active in Fabric workspace.
     - `DEV 🔨`: Active coding in progress.
     - `TEST ⚡`: Code deployed to TEST workspace, initial ingestion run pending.
     - `DEV ⏳` / `PROD ⏳`: Pending.

5. **Executive Title & Screenshot Readiness Standards:**  
   * **Title Standard:** Main header MUST be **`Solution Architecture & Progress Overview`** and Section H2 MUST be **`Data Stream Progress Overview`** (never use "Data Stream Maturity Matrix" or internal slang in customer deliverables!).
   * **Zero Instructional Text:** Do NOT include click instructions (e.g. *"Click Any Box to Drill Down"*) or debugging notes. The page must be 100% clean, executive, and screenshot-ready for emailing directly to the customer. The click-to-drilldown drawer operates silently in the background.

6. **Progressive Environmental Outline & Tint Rules:**  
   To provide immediate visual clarity on environmental depth across DEV, TEST, and PROD:
   * **`DEV Only Done`**: **Ragged Orange/Yellow Outline (`border: 2px dashed #D97706`)** with Crisp White Fill. *(Marketo Sync & GTM Web Events).*
   * **`DEV + TEST Both Done (No Blockers)`**: **Ragged Green Outline (`border: 2px dashed #059669`)** with Crisp White Fill. Signals *"Code & Testing validated across DEV and TEST!"* *(AX 2009 & CVR streams).*
   * **`ALL Envs Done (PROD Live)`**: **Solid Green Outline (`border: 2.5px solid #059669`) PLUS Soft Emerald Tint Fill (`background: #E6F4EA`)**.
   * **`🔴 Blocked Stage`**: **Red Outline (`border: 2px solid #DC2626`) + Light Red Tint (`background: #FEF2F2`)**. (Reserved strictly for active failing runtime errors or blocked external dependencies).
   * **`⚪ Planned Stage`**: **Dashed Gray Outline (`border: 1px dashed #CBD5E1`) + Muted Background (`#F8FAFC`)**.

7. **Top Executive Production Progress Banner:**  
   Every matrix document MUST include a top Production Progress Banner showing the overall environment stage distribution:
   * **`PRODUCTION GO-LIVE PROGRESS: X% LIVE IN PROD`** (e.g. `0 of 24 Medallion Stages Live in PROD`).
   * A multi-segment visual progress bar displaying the exact distribution across PROD (Green), TEST (Indigo), DEV (Blue), Blocked (Red), and Planned (Gray).

7. **Strict Deliverable & Styling Rules:**
   * **No Agent Names:** Internal agent persona names (`Agent M`, `Agent Q`, `Sentinel`, etc.) MUST NEVER appear in customer-facing HTML files, headings, or callout boxes.
   * **Pingala Typography:** Headings in `Aptos Display`, body & matrix grid in `Aptos`. NEVER use cursive/script fonts (`Ink Free`) for technical callouts or architecture notes.
   * **Pingala Color Palette:** Primary Teal (`#60756E`), Deep Teal (`#4D7878`), Terracotta Accent (`#B5442A`), Warm Cream Background (`#F5EFEA`).

---

## 2. Automated Inspection & Update Protocol Going Forward

When Agent M or Agent Q is asked to update or refresh the matrix for ANY project, follow this 4-step inspection protocol:

### Step 1: Discover Structure in Target Environments (DEV / TEST / PROD)
Query Fabric workspaces via `fab` CLI, git repository state, or Azure SQL endpoints to verify structure presence:
* **Lakehouse / Warehouse Tables:** Verify table or CTAS view exists (`fab items list`, pyodbc query).
* **Notebooks & Pipelines:** Check if artifact `.py` / `.json` exists in `Landingzone-ETL` or `Fabric-ETL` repos.

### Step 2: Data Population Verification (The Core Validation Rule)
Query actual row counts, file logs, or event counts:
* **`Structure Exists + 0 Rows`**: Mark stage as `DEV 🔨` / `TEST 🔨` (**Structure Created, Ingestion Pending**).
* **`Structure Exists + >0 Rows`**: Mark stage as `DEV ✓` / `TEST ✓` (**Structure & Data Verified!**).

### Step 3: Master Pipeline Orchestration Check (Automated Blocker Detector)
Check if the item is registered in master execution pipelines (`PL_Execute_Raw` / `PL_Execute_Enriched`):
* **`Structure Exists + Data Exists BUT NOT Registered in Master Pipeline`**: Flag stage as **`🔴 Blocked`** with explicit blocker reason (*"Awaiting registration in master pipeline PL_Execute_*"*).

### Step 4: Auto-Update Sidecar & Re-Render Visual Deliverable
1. Update `customers/<Customer>/<Project>/design/stream_matrix_data.json`.
2. Re-render `customers/<Customer>/<Project>/design/carlras_architecture_overview.html`.
3. Serve local HTTP preview URL (`http://127.0.0.1:8080/customers/<Customer>/<Project>/design/carlras_architecture_overview.html`) and open browser.

---

## 2. Maintaining State via Data Sidecar (`stream_matrix_data.json`)

Store the stream definitions, stage metrics, and blocker descriptions in `customers/<Customer>/<Project>/design/stream_matrix_data.json`:

```json
{
  "customer": "Carl-Ras",
  "project": "Datahub",
  "environment_scope": "DEV & TEST WORKSPACES ONLY (PROD PENDING)",
  "last_updated": "2026-08-10",
  "streams": [
    {
      "id": "ax09",
      "name": "AX 2009 ERP",
      "icon": "🏢",
      "description": "Sales Transactions, Products, Orders & Customer Master",
      "stages": {
        "source": { "label": "AX 2009 Source", "status": "neutral", "metric": "27 Raw Tables (TEST)" },
        "landing": { "label": "LZ Storage", "status": "neutral", "metric": "27.1M Rows (TEST)" },
        "raw": { "label": "PL_Execute_Raw", "status": "neutral", "metric": "27.1M Delta (TEST)" },
        "enriched": { "label": "WH_Enriched", "status": "neutral", "metric": "28 CTAS Views (TEST)" },
        "curated": { "label": "WH_Curated", "status": "neutral", "metric": "28 Gold Tables (TEST)" },
        "delivery": { "label": "Power BI TEST", "status": "neutral", "metric": "27.1M Model (TEST)" }
      }
    },
    {
      "id": "gtm",
      "name": "GTM Web Events",
      "icon": "🌐",
      "description": "Stape sGTM → Event Hub (140M events/yr)",
      "stages": {
        "source": { "label": "eh-cr-ga4streaming", "status": "neutral", "metric": "140M Ev/Yr (TEST)" },
        "landing": { "label": "OneLake Shortcut", "status": "neutral", "metric": "324M Ingested (TEST)" },
        "raw": { "label": "NB_Raw_GTM", "status": "blocked", "metric": "324M Staged", "blocker_reason": "Awaiting pipeline registration in PL_Execute_Raw" },
        "enriched": { "label": "viewtransform", "status": "neutral", "metric": "21 Fields Typed (DEV)" },
        "curated": { "label": "Fact_GTM_Events", "status": "planned", "metric": "Planned" },
        "delivery": { "label": "Power BI Integration", "status": "planned", "metric": "Planned" }
      }
    }
  ]
}
```

---

## 3. Standard HTML Architecture Matrix Template

Generate the deliverable HTML file at `customers/<Customer>/<Project>/design/architecture_overview.html` using this exact Pingala visual structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Customer] Datahub — Solution Architecture Matrix</title>
  <style>
    @font-face { font-family: 'Aptos Display'; src: local('Aptos Display'), local('Calibri'); }
    @font-face { font-family: 'Aptos'; src: local('Aptos'), local('Calibri'); }

    :root {
      --pingala-bg: #F5EFEA;
      --pingala-card-bg: #FFFFFF;
      --pingala-teal-deep: #4D7878;

      /* 4-Color Status Palette */
      --status-prod-bg: #E6F4EA;
      --status-prod-text: #059669;

      --status-neutral-bg: #F1F5F9;
      --status-neutral-border: #475569;
      --status-neutral-text: #334155;

      --status-stale-bg: #FEF3C7;
      --status-stale-border: #D97706;
      --status-stale-text: #92400E;

      --status-blocked-bg: #FEF2F2;
      --status-blocked-border: #DC2626;
      --status-blocked-text: #991B1B;
    }
    /* Matrix styling */
  </style>
</head>
<body>
  <!-- Executive Matrix HTML -->
</body>
</html>
```

---

## 4. Summary Checklist for Agent M & Agent Q

When asked to provide a status update or review architecture progress for ANY customer project:
- [ ] Split all data sources into **one stream per source system**.
- [ ] Audit data metrics across the **6 Medallion stages**.
- [ ] Ensure **NO Green badges appear unless the stream/stage is active in PRODUCTION**.
- [ ] Use **Neutral Slate** by default for active DEV/TEST stages.
- [ ] Use **Yellow** if untouched for >30 days.
- [ ] Use **Red** ONLY for documented blockers (must include documented reason!).
- [ ] Render `architecture_overview.html` and serve local HTTP preview URL (`http://127.0.0.1:8080/...`).
