---
title: Carl Ras - kundesegmenter og dim.CustomerTermsGroup
status: done
created: 2026-10-13
project: customers/Carl-Ras/datahub
owner: fabric-back
priority: normal
blocked_by:
fno_task: none
customer_ask: none
waiting_on:
resume_on:
source: direct
---

## What
Vise hvor mange forskellige kundegrupper Carl Ras' kunder falder i (rabat-, pris- og betalingsgrupper m.fl.) i dim.Customer, og give en gruppenoegle pr. kunde. Done when: view i Warehouse_Curated og et overblik over de mest interessante 5-kolonne-kombinationer.

## Why
En kollega ville se kundernes gruppesammensaetning; gaet var over 10.000 aktive kombinationer.

## Progress
**Now (2026-10-13):** dim.CustomerTermsGroup er committet og pushet (Fabric-ETL c37647e) og findes i DEV: 5.451 grupper for 63.188 aabne kunder, 10.907 for alle (15 terms-kolonner). Dashboard design/customer_segments_dashboard.html og SQL design/customer_terms_groups.sql er lavet.
**Tried and dropped:** Update from git mod DEV fra denne session blev ikke koert (konflikt paa NB_DataQuality); workspacet blev synket til c37647e fra en anden session.
**Next:** ingen.

## Needs from customer
- none

## Context
design/customer_segments_dashboard.html, design/customer_terms_groups.sql, Fabric-ETL/01 - Curated/Warehouse_Curated.Warehouse/dim/Views/CustomerTermsGroup.sql

## Log
- 2026-10-13 - created; view og dashboard leveret
