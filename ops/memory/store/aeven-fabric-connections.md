---
id: aeven-fabric-connections
ts: 2026-11-11T20:40:00Z
type: semantic
scope: project:customers/Aeven/AtomicServiceNow
tags: [aeven, fabric, connection, gateway, environments]
status: distilled
description: "Aeven ITSM-ETL-Dev connections: ServiceNow_Test_BasicAuth_http_v2 (494578c4, WebForPipeline) reads ServiceNow; CON_Fabric_SQL (d7263d88) reads SQL_Util; production connection asked from Aeven"
---

- ServiceNow: `ServiceNow_Test_BasicAuth_http_v2` = `494578c4-e2c3-4aab-a8f0-469c008795d1`, WebForPipeline,
  Basic, Aeven gateway AevenDW_... Verified by Niels 2026-11-11; named in `tooling/config/environments.json` (room `35eb6e7`).
  On 2026-10-02 only the id was pasted; the name was not recorded until 2026-11-11.
- The other ServiceNow connections at Aeven (`_http` HttpServer, `_REST` RestService) are not used by the load.
- `CON_Fabric_SQL` = `d7263d88-ce3a-44e5-9f91-881c5969a077` reads the plan config from SQL database `SQL_Util` (added by Kresten).
- Production: Niels cannot create connections at Aeven; a production Web v2 connection was asked from Aeven 2026-11-11.
- Lesson: when a connection id is pasted, record its display name beside it in `environments.json`.
