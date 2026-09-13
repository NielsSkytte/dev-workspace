---
id: pbir-report-as-code-microsoft-plugin-and-rest-create
ts: 2026-09-13T21:00:00Z
type: procedural
scope: project:customers/Aeven/AtomicServiceNow
source: /log
tags: [power-bi, pbir, report, fabric-rest, skills-for-fabric, node, aeven]
description: A Power BI report is authored as PBIR files and created by the Fabric REST create-with-definition call; Microsoft's skills-for-fabric plugin (powerbi-authoring) carries the templates and a validator CLI that needs Node
status: distilled
---

Report-as-code route proven on Aeven 2026-09-13 (`tools/build_report.py`, `tools/deploy_report.py`).

- Files: `definition.pbir` (schema `definitionProperties/2.0.0`, version `4.0`, `byConnection` with
  `connectionString: semanticmodelid=<id>`), `definition/version.json` (`versionMetadata/1.0.0`,
  `2.0.0`), `definition/report.json` (`report/3.1.0`, base theme `CY25SU12`), `definition/pages/pages.json`
  (`pagesMetadata/1.0.0`), one `page.json` (`page/2.1.0`, 1280x720) and one `visual.json` per visual
  (`visualContainer/2.9.0`). Names are 20 lowercase hex chars; role projections sit under
  `query.queryState`; a measure binds to the measures table entity (`01 - Global Measures`).
- Deploy: `POST workspaces/{ws}/reports` with every file as an `InlineBase64` part (dotfiles out);
  202 + `x-ms-operation-id`, poll `operations/{id}`; update = `.../updateDefinition` with all parts.
  The report opened and answered correctly on the first create.
- Tooling: Microsoft's first-party plugin `microsoft/skills-for-fabric` > `powerbi-authoring`
  (skills report-authoring / design / planning / management, plus a modeling MCP server) is
  installed at user scope, so every project under `C:\Dev` has it. Its validator
  `powerbi-report-author validate <dir>` and the MCP server need Node 20+; Node 22 is installed
  without admin at `%LOCALAPPDATA%\Programs\nodejs` (portable zip, on the user PATH) with
  `@microsoft/powerbi-report-authoring-cli` and `powerbi-desktop-bridge-cli` global.
- Q's verdict: adopt, do not write a house PBIR skill; `fabric-front` points at the plugin.
- Browser check of a report in another tenant: append `?ctid=<tenant id>` to the app URL.
