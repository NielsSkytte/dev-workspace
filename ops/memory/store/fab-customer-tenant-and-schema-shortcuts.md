---
id: fab-customer-tenant-and-schema-shortcuts
ts: 2026-10-28T12:00:00Z
type: procedural
scope: workspace
source: /log session 16910ea9
tags: [fab, fabric-cli, tenant, onelake, shortcuts, lakehouse-schemas, vestforbraending]
status: distilled
description: "fab: interactive 'auth login -t' kept the home tenant (fix: set the profile's auth.json to the guest tenant); login needs a real console; in a schema-enabled lakehouse create the schema via OneLake DFS and manage shortcuts via the REST API (CreateOrOverwrite), not fab mkdir/rm"
---

Observed 2026-10-26 (Vestforbraending, guest account nchristensen@pingala.eu):

- **Login needs a Windows console.** `fab auth login` fails under Git Bash and the PowerShell tool
  ("No Windows console found"). `Start-Process cmd -ArgumentList '/k fab auth login -t <tenant>'`
  opens one for Niels. Run it from the customer folder so the tenant shim picks that profile.
- **`-t` did not stick for a guest.** After the interactive login the profile's `auth.json` still
  held Pingala's tenant. Writing `fab_authority` / `fab_tenant_id` for the customer tenant into
  `%LOCALAPPDATA%/fab-profiles/<Customer>/.config/fab/auth.json` made fab get a guest token
  silently. Edit the customer profile, never `~/.config/fab` (the default Pingala profile).
- **Schemas:** `fab mkdir <lh>/Tables/<schema>` -> NotSupported. `fab api -A storage -X put
  "<wsId>/<lhId>/Tables/<schema>?resource=directory"` creates it (201).
- **Shortcuts in a schema:** `fab ln <lh>/Tables/<schema>/<t>.Shortcut --type oneLake --target
  <ws>/<lh>/Tables/<t>` works, but `fab rm` on that path returns NotFound. Use `POST
  workspaces/{ws}/items/{lh}/shortcuts?shortcutConflictPolicy=CreateOrOverwrite` with
  `{"path":"Tables/<schema>","name":..,"target":{"oneLake":{workspaceId,itemId,path}}}` - one call
  repoints a shortcut, which is how `Fabric-ETL/kurs-only/serving/set-source.sh` switches source env.
- Shortcuts to Link to Fabric tables (themselves shortcuts) read fine through the SQL endpoint
  after `refreshMetadata`.
