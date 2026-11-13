---
id: aeven-fabric-connections
ts: 2026-11-11T20:40:00Z
type: semantic
scope: project:customers/Aeven/AtomicServiceNow
tags: [aeven, fabric, connection, gateway, environments]
status: distilled
description: "Aeven ITSM-ETL-Dev connections: ServiceNow_Test_BasicAuth_http_v2 (494578c4, WebForPipeline) reads ServiceNow; CON_Fabric_SQL (d7263d88) reads SQL_Util; production ServiceNow_Prod_BasicAuth_http_v2 (9d0cd0a3)"
---

- ServiceNow: `ServiceNow_Test_BasicAuth_http_v2` = `494578c4-e2c3-4aab-a8f0-469c008795d1`, WebForPipeline,
  Basic, Aeven gateway AevenDW_... Verified by Niels 2026-11-11; named in `tooling/config/environments.json` (room `35eb6e7`).
  On 2026-10-02 only the id was pasted; the name was not recorded until 2026-11-11.
- The other ServiceNow connections at Aeven (`_http` HttpServer, `_REST` RestService) are not used by the load.
- `CON_Fabric_SQL` = `d7263d88-ce3a-44e5-9f91-881c5969a077` reads the plan config from SQL database `SQL_Util` (added by Kresten).
- Production: Niels cannot create connections at Aeven; asked 2026-11-11. Aeven's production connection id = `9d0cd0a3-58ee-4e48-bbe0-324729a2b1ef` (given by Niels 2026-11-12), name `ServiceNow_Prod_BasicAuth_http_v2`. Recorded as `_aeven-prod` in `environments.json` (room `3f27450`, not pushed); the underscore keeps it out of `build_variables.py` until the PROD workspace and LZ lakehouse ids exist.
- There is no access to Aeven from Niels's machine, only to the MasterDataPlan repo. Never query Aeven's Fabric (az/fab/REST); ask Niels. See memory `aeven-repo-access-only`.
- Lesson: when a connection id is pasted, record its display name beside it in `environments.json`.
