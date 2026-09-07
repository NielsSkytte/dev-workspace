---
id: fab-console-login-and-silent-sql-onelake-tokens
ts: 2026-09-07T12:00:00Z
type: procedural
scope: workspace
source: distilled
tags: [fabric, fab-cli, auth, tenant-shim, onelake, duckdb, sql-database, pyodbc, deltalake]
status: distilled
description: "fab auth login only works from a real console window (the Claude shells have no Windows console); once the per-customer profile holds a login, its MSAL cache silently serves tokens for OneLake (DuckDB delta_scan reads Link-to-Fabric tables that the deltalake package cannot) and for the SQL scope (pyodbc token auth to a Fabric SQL database, no browser prompt)"
---

**Login.** `fab auth login -t <tenant>` fails from both Claude shells: Git Bash prints "Found
xterm-256color, while expecting a Windows console", PowerShell prints "No Windows console found".
It has to run in a Windows Terminal / cmd window, **from a folder under `C:\Dev\customers\<Name>`**
so the tenant shim routes the credentials into `%LOCALAPPDATA%\fab-profiles\<Name>`. A login that
did not finish leaves an 86-byte `auth.json` (mode only) and no `cache.bin`; a finished one writes
`cache.bin` (~37 kB). Check the profile folder before trusting "logged in" (2026-09-07, Matas).

**Silent tokens from the same cache.** With `USERPROFILE` pointed at the profile folder *before*
importing `fabric_cli`, `FabAuth()._get_app()` is fab's MSAL public client (client id
`1950a258-227b-4e31-a9cf-717495945fc2`, the Azure PowerShell app) over fab's persisted cache, and
`acquire_token_silent` returns tokens for scopes fab itself never asks for:

- OneLake: `FabAuth().get_access_token(con.SCOPE_ONELAKE_DEFAULT, interactive_renew=False)`;
  DuckDB then reads delta tables straight from OneLake with
  `CREATE SECRET (TYPE azure, PROVIDER access_token, ACCESS_TOKEN '<tok>', ACCOUNT_NAME 'onelake')`
  and `delta_scan('abfss://<ws>@onelake.dfs.fabric.microsoft.com/<lh>.Lakehouse/Tables/<t>')`.
  Do not set ENDPOINT (the https form breaks the list request). The Python `deltalake` package
  refuses these tables ("reader features: deletionVectors ... not yet supported"); DuckDB's delta
  extension reads them. `fab table schema` and recursive `fab cp` both fail on shortcut tables.
- SQL: `app.acquire_token_silent(["https://database.windows.net/.default"], account=...)`, passed to
  pyodbc as `attrs_before={1256: struct.pack("<i", len(tok)) + tok}` with the token UTF-16-LE
  encoded, against a Fabric SQL database's `serverFqdn` from `fab get <item> -q properties`.
  Connects as the signed-in user, no browser prompt. Helper: `customers/Matas/DataCompare/prototype/fabric_sql.py`.

**Why it matters.** Local prototyping against customer Fabric data needs no service principal,
no `az login` (which the shim deliberately does not isolate), and no copying of secrets: one
console login per customer profile carries reads and writes for the session.
