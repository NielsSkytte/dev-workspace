---
id: fab-token-cache-version-mismatch
ts: 2026-10-09T12:30:00Z
type: semantic
scope: workspace
source: /log
tags: [fab, msal, token, python, functions]
status: distilled
description: "Two fab/fabric_cli versions on one machine (2026-10-09: fab 1.7.0 under uv Python 3.12 does the login, fabric_cli 0.1.10 under Python 3.14 runs in the Functions worker) break silent token lookup: different client ids and auth.json keys; read fab's PersistedTokenCache directly and take the client id from the cached refresh token"
---

- Symptom 1: `acquire_token_silent` returns None although the cache holds a refresh token - the
  refresh token's client id (1950a258...) differs from the importing fabric_cli's (5814bfb4...).
- Symptom 2: under the 3.14 install `FabAuth()._get_app()` returns None - 0.1.10 reads `fab_auth_mode`,
  the 1.7 login writes `identity_type` in auth.json.
- Fix (`DataCompare/prototype/fabric_sql.py` sql_token, 9c43845): `PersistedTokenCache(FabAuth()._get_persistence())`,
  client id from the cached refresh token, authority = the tenant. Works under both Pythons.
- Azure Functions Core Tools runs its bundled Python 3.14 worker regardless of PATH order; the API's
  packages (openpyxl etc.) must be installed in the 3.14 site-packages too.
- Related: `fab-console-login-and-silent-sql-onelake-tokens`. An interactive sign-in cannot open from the
  agent shell (ODBC/WAM dialog cancels at once); the owner runs `fab auth login` in a console.
