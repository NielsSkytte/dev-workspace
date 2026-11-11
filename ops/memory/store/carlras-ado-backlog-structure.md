---
id: carlras-ado-backlog-structure
ts: 2026-11-11T10:00:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: session 01c65527 2026-11-11; decisions in datahub/CONTEXT_DECISIONS.md
tags: [carl-ras, devops, backlog, process-insight]
status: distilled
description: "Carl Ras ADO structure since 2026-11-11: Epic 41 Data platform (Feature per source), Epic 842 Process insight (Feature per process), Business-area Epics deliver; one WP per Feature with one SyncToPingala booking Task"
---

Two ways in, one delivery: Data platform (bottom up, Niels) and Process insight (top down, Mads +
Niels) have Successor links into Business-area Features (Mads). A data source is an area path; a
Feature is a finite deliverable. One WP per Feature; exactly one SyncToPingala booking Task per WP;
other Tasks untagged. A request between Niels and Mads is an untagged Task tagged Request in the
other's WP. Page: datahub/design/ado-restructure.html. EXT_NSKC lacks rights to create area paths
(TF50309) and to write Shared Queries (TF401256). az for Carl Ras runs with
AZURE_CONFIG_DIR=~/.azure-carlras (separate from the Matas default profile).
