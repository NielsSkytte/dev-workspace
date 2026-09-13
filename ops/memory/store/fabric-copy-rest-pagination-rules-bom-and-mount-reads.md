---
id: fabric-copy-rest-pagination-rules-bom-and-mount-reads
ts: 2026-09-13T21:00:00Z
type: semantic
scope: project:customers/Aeven/AtomicServiceNow
source: /log
tags: [fabric, pipeline, copy-activity, rest, pagination, json, bom, notebookutils, landing]
description: Fabric Copy REST: a paginationRules block holding only supportRFC5988 loops until stopped; the JSON sink writes a UTF-8 BOM; a mounted lakehouse path can read back empty, so pull files with notebookutils.fs.cp before parsing
status: distilled
---

Three Fabric-only findings from the first ServiceNow pipeline runs (Aeven, 2026-09-13):

- A Copy activity with `paginationRules: {supportRFC5988: true}` and nothing else re-requested the
  same page 6,955 times in 23 minutes. Give the count copy no rules at all; pages use
  `QueryParameters.{offset}: RANGE:0::<page>` with `EndCondition:$.result: Empty`.
- The JSON-as-is sink writes a UTF-8 BOM; read landed files as `utf-8-sig`.
- A lakehouse mounted with `notebookutils.lakehouse` read a folder back empty from the mount
  path; copying each file with `notebookutils.fs.cp` to `/tmp` and parsing there is reliable.
- Notebook bool parameters arrive as strings through the job scheduler; coerce.
