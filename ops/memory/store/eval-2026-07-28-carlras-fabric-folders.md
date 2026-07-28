---
id: eval-2026-07-28-carlras-fabric-folders
ts: 2026-07-28T09:38:00Z
type: evaluative
scope: workspace
source: session:c79aa71b
tags: [evaluative, skill-pingala-fabric-platform, fabric, tooling]
status: distilled
description: "pingala-fabric-platform fired+helped for the GTM medallion design but had a GAP (item folder placement via fab CLI) that caused a real misplacement; gap now patched into the skill"
---

Carl Ras GTM medallion session (2026-07-28):

- **Fired + helped:** `pingala-fabric-platform` — carried the medallion shape, the
  Views-to-Tables discipline, Python-over-PySpark default, and the multi-source pattern;
  all directly shaped the build. Design decisions (DirectLake, windowed fact, shared
  Curated) landed cleanly on it.
- **Gap → real error → fixed:** the skill did not document that **`fab mkdir` creates items
  at the workspace ROOT** and that `fab ls` hides workspace folders — so the CLI-created
  `Lakehouse_Raw_GTM` and `Warehouse_Enriched_GTM` serialized to the repo root, breaking the
  house layout. Caught by the owner ("fix the folder issue and make sure it doesn't happen
  again, always prompt me if in doubt on folders"). Fixed via REST API (folders + item-move
  are API-only: `POST .../folders`, `POST .../items/{id}/move`). **Patched the skill** with an
  "Item folder placement (fab CLI gotcha)" subsection incl. the move routine and a
  prompt-when-unsure rule.
- **Pattern:** this is the **second** confirmed pingala-fabric-platform gap on Fabric
  *conventions the skill under-specifies* (cf. [[eval-2026-07-22-lineage-viewer]] — layer-ID
  conventions). Both were fold-into-skill updates, not new skills. The skill teaches the
  medallion *design* well but is thin on *operational/CLI conventions*; keep folding those in.
- **Correctly silent:** offer/email/writing skills (no customer-facing prose this session).
