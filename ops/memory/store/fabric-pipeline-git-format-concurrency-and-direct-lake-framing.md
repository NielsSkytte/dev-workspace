---
id: fabric-pipeline-git-format-concurrency-and-direct-lake-framing
ts: 2026-10-04T12:00:00Z
type: semantic
scope: global
tags: [fabric, pipeline, concurrency, git, direct-lake, framing, semantic-model-refresh]
status: distilled
description: "Fabric pipeline concurrency serialises as properties.concurrency; the designer drops empty defaults on save; Direct Lake refresh is framing, auto-update is model-level only; the refresh activity takes a table list"
---

- Pipeline Settings > Concurrency = 1 is stored as `"concurrency": 1` under `properties` in
  pipeline-content.json (read from an Aeven workspace commit, 2026-10-03). Overlapping runs queue
  (Fabric limit: 100 queued runs per pipeline).
- Saving a pipeline in the designer drops `"defaultValue": ""` on string parameters and an empty
  `"parameters": {}`; generated JSON should tolerate that or match it.
- Direct Lake "refresh" = framing (metadata only, seconds). "Keep your Direct Lake data up to date"
  is a model-level setting (on by default); Microsoft recommends it off when an ETL must finish before
  users see data. There is no per-table auto-update.
- The pipeline's Semantic model refresh activity can refresh selected tables/partitions, settable by
  expression (doc read 2026-10-03). Its git JSON shape was not found in the docs.
- An If Condition cannot contain another If Condition; nest via Execute Pipeline.
