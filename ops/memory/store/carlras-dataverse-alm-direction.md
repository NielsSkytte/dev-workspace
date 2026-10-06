---
id: carlras-dataverse-alm-direction
ts: 2026-10-05T14:00:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: /log
tags: [carl-ras, dataverse, alm, ado, cicd, environments, decision]
status: distilled
description: "Carl Ras Dataverse ALM direction (2026-10-05): AX 2009 stays one PROD source in a shared landing zone; Dataverse in/out splits per environment (Dev/Test/Prod exist, one region); the Customer Service developers are a separate Pingala team; ADO drives releases with a shared schema contract, the Fabric deployment pipeline stays the copy step"
---

- **Scope is Dataverse only for now.** AX 2009 (not D365 F&O; on-prem SQL `Dynamics_Addon` via gateway)
  stays a single PROD source in one shared Landingzone read by every stage. Dataverse outbound, and
  later inbound via Link to Fabric, splits per environment: Dev, Test and Prod Dataverse exist, all in
  one region (Niels, 2026-10-05).
- **Why ADO at all:** the Power Platform / Customer Service developers are a separate Pingala team with
  their own dev cadence; Fabric changes (columns, data) must be coordinated with them by PR and
  release, not by manual deployment-pipeline clicks (Niels). Kasper (Carl Ras CIO/CTO) is not the
  counterpart for this; the information is internal to Pingala.
- **Proposal (not built):** ADO YAML drives the Fabric deployment-pipeline API + `fabric_release.py`
  per stage with approvals; a Dataverse schema contract file reviewed by both teams;
  `dataverse_preflight.py` gates every push against it. fabric-cicd deferred: it creates an empty
  Warehouse item and does not deploy the schema. Detail: `design/ADO_CICD_RESEARCH.md`, ALM page
  https://claude.ai/artifact/QyvURNCeEAXusaNj2BawUu.
- **Landed:** `VL_ConnectionId.Dataverse_Url` (Fabric-ETL `7d4a8ab`, not pushed at 10-05): default
  empty, Dev = `org8a074fed.crm4`, Test/Prod empty so those runs stop instead of writing into DEV.
  Crm4 vs crm17 as the Dev value not confirmed.
- **Prerequisite:** pipeline SPN `ca6cc2d2` is not in the CarlRas ADO organisation (TF401444).