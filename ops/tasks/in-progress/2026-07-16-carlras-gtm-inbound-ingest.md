---
title: Carl Ras — GTM inbound ingest (Event Hub landing storage → Fabric LZ/Raw)
status: in-progress
created: 2026-07-16
project: customers/Carl-Ras/datahub
owner: fabric-back
priority: normal
blocked_by:
activity:
fno_task:
source: session
---

## What
Build the inbound import of the GA4/Stape event data from the Carl Ras-owned landing
storage account (`stcrdatabricksweprod/landing`, Event Hubs Capture Avro) into the
Fabric platform: new GTM source in the LandingZone (shortcut + ingest notebook →
`Lakehouse_Landingzone_GTM`), then the Raw layer per the house pattern.

## Why
The decided inbound architecture (2026-07-03): OneLake shortcut on the landing
container, rebuild the medallion in Fabric, retire Databricks. This is the first
build step of the datahub project.

## Context
- Project: `customers/Carl-Ras/datahub` (fno_code 230-02); CONTEXT.md holds the decided
  architecture; sample Avro in `datahub/data/`.
- Repos: `Landingzone-ETL` (LZ workspace; GTM folder goes here, alongside AX09/CVR) and
  `Fabric-ETL` (`03 - Raw\GTM` later). Both dev.azure.com/CarlRas/Datahub.
- Auth for now: Niels' guest account (prove it works), then switch to WI/SPN.

## Log
- 2026-07-16 — created + started (session task); scoped to the LZ ingest first
