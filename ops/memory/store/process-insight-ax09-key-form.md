---
id: process-insight-ax09-key-form
type: decision
scope: project:customers/Carl-Ras/process-insight
date: 2026-11-04
status: distilled
---
Entities bound to AX09 Enriched views use the Atomic house key `<DataAreaId>-<RecId>` (VARCHAR(151), unknown '-1', binding option `key_form: dataarea_recid`); every other source keeps the hash key. Niels chose this (option A) on 2026-11-04 and asked to revisit having two key forms later (note in own/ProcessInsight/docs/03-spec-schema.md 3.2).
