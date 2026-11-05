---
id: aeven-metadata-driven-views
ts: 2026-11-05T18:30:00Z
type: semantic
scope: project:customers/Aeven/AtomicServiceNow
source: /log
tags: [aeven, servicenow, atomic, views, metadata, decision]
status: distilled
description: "AtomicServiceNow views (2026-11-04): metadata says what a view holds, shared generator writes plain SQL, only changed views are altered, marked block for columns in hand-owned views; decision file in the room"
---

- Decision file: `customers/Aeven/AtomicServiceNow/project-room/decisions/2026-11-04-metadata-driven-views-in-git.md`.
- Metadata in SQL_Util states what a view contains; the shared generator writes plain SQL. Views are generated when the pipeline runs, so a table or column change needs no code deployment. A run builds every view's text and changes only those that differ.
- A hand-owned view takes generated columns through a marked block: the person owns the view, the generator owns only the lines between the markers.
- The local-build proposal of 2026-11-04 was dropped; do not read it as the design.
- Pushed to Aeven's repo as MasterDataPlan `6a43619` on 2026-11-04. Later state at Aeven: see the project room `now/`.
