---
id: link-to-fabric-views-and-dataverse-access
ts: 2026-10-28T12:00:00Z
type: procedural
scope: workspace
source: /log session 16910ea9
tags: [dataverse, link-to-fabric, sql-endpoint, views, permissions, vestforbraending]
status: distilled
description: "Views over Link to Fabric tables: filter IsDelete, labels from OptionsetMetadata/GlobalOptionsetMetadata/StateMetadata/StatusMetadata (lang 1030); display names are NOT in the link (need Dataverse metadata access); schema-only access = item share with no boxes + GRANT SELECT ON SCHEMA"
---

From building `bi` views in lh_KURS_Serving (2026-10-26/27):

- Link to Fabric rows carry `IsDelete` (bit, NULL when live): views filter `ISNULL(IsDelete,0)=0`.
- Option set labels: `OptionsetMetadata` / `GlobalOptionsetMetadata` (EntityName, OptionSetName,
  Option, LocalizedLabelLanguageCode, LocalizedLabel), `StateMetadata` (State), `StatusMetadata`
  (State, Status). Shortcut them next to the data tables. Join on bigint columns only.
- Column **display names are not in the link**. They need the Dataverse Web API
  (EntityDefinitions); a guest with no Dataverse role gets an empty global discovery list.
- A view whose names strip the publisher prefix can collide (`account.vf_nummer` vs `nummer`):
  keep the logical name on collision.
- Schema-only access for a BI user: share the lakehouse with no boxes ticked (connect only), then
  `GRANT SELECT ON SCHEMA::bi TO [upn]` on the SQL endpoint. The GRANT works before the share
  exists. Item share has no API we found; it is done in the UI.
- pyodbc prints varchar UTF-8 as mojibake in the console; `UNICODE()` showed the data is correct.
