---
id: tenant-scoped-cli-auth
ts: 2026-08-11T12:00:00Z
type: semantic
scope: workspace
source: session:5bbffdc6-903f-456e-9d01-a37807792a96
tags: [harness, fabric, security, guardrail]
status: distilled
description: "fab tenant auth resolves automatically from cwd via a PATH shim (ops/bin/tenant_shim.py); per-customer profiles in %LOCALAPPDATA%\\fab-profiles; plus three verified traps — Claude's shells do NOT load user profiles, `fab auth status` exits 0 when logged out, and a bare customer login from C:\\Dev clobbers the default profile"
---

`fab` hardcodes its state directory to `expanduser("~/.config/fab/")` (`fabric_cli/core/fab_state_config.py:13-17`) — no `--config-dir` flag, no config-dir env var (the only `FAB_*` vars are `FAB_SPN_CLIENT_ID`/`FAB_SPN_CERT_PASSWORD`, both SPN inputs). So one Windows user gets one Fabric tenant, and two customers overwrite each other's `auth.json` + `cache.bin`. That produced Guardrail 11 on 2026-07-31, when a `fab ls` in a Matas session returned the Carl Ras estate.

## Mechanism (2026-08-11)

**Shims on PATH ahead of the real `fab.exe`** → `ops/bin/tenant_shim.py` → real `fab.exe` in a child process with `USERPROFILE` pointed at `%LOCALAPPDATA%\fab-profiles\<Customer>`. Windows' `ntpath.expanduser` reads `USERPROFILE` and **never** consults `HOME`, so redirecting it moves `~/.config/fab` per customer.

- Resolution: **explicit (`TENANT_PROFILE_HOME`) > cwd's customer node > default**. "Default" means *no redirection at all* — the real `~/.config/fab`, holding Niels's own Pingala user, used for `C:\Dev` and `own/…`.
- **Per-invocation, not per-session.** `USERPROFILE` is set only in the `fab` child process, so `git`/`gh`/`az` in the same shell are unaffected. This is why a session-wide env var or a settings `env` block was rejected: `USERPROFILE` is a blunt instrument that moves `~` for everything.
- Shims live in `~/.local/bin`, which is **already** on PATH ahead of the Python Scripts dir (index 29 vs 43 in git-bash, 21 vs 22 in PowerShell) — no PATH change needed. `heal-repos.ps1 > Install-TenantShims` writes them at top level, so every `/log` self-heals them.
- `PYTHONIOENCODING=utf-8` is set by the shim (fab dies with a charmap error printing its own checkmark).

**Rejected — junctioning `~/.config/fab` per session via a SessionStart hook.** Tempting (no wrapper, no PATH change, matches the `Link-Harness` junction idiom) but it is global mutable state: a second session starting at `C:\Dev` repoints the junction and silently breaks a live customer session. That automates the exact failure Guardrail 11 exists to prevent.

**Coexists with `ops/bin/fab-as.ps1`** (2026-08-04), which stays the *onboarding and inspection* tool: lists customers with tenant + cached-login state, reads `tenant_id:`/`account:` from the customer node, builds the login. Same profile directory, so a login via either is visible to both. `fab-as.ps1` calls bare `fab`, which the shim now shadows — hence `TENANT_PROFILE_HOME`, so an explicitly named customer is not silently overridden by the current directory.

**Onboarding is one interactive login** in a real console. `fab auth login -t <tenant>` with no `-u`/`-p` falls to `prompt_select_item` → questionary → prompt_toolkit (`fab_auth.py:58-61`), which needs a real Windows console: it fails with "Found xterm-256color, while expecting a Windows console" in a pty and "No Windows console found" in an agent shell. **Never assume an SPN exists** — SPN (`-u <client_id> -p <secret> -t <tenant>`) is the only non-interactive path and is an optimisation available at *some* customers, never a prerequisite. The default is our own user at the customer.

## Three traps worth remembering

1. **Claude's Bash and PowerShell tools do NOT load the user's shell profile.** Verified by writing marker functions to `~/.bashrc` and `$PROFILE.CurrentUserAllHosts` and calling both tools fresh: neither loaded. The Bash tool's own description claims "the shell is initialized from the user's profile" — **false in this environment**. Any mechanism built on shell profile functions works in Niels's terminal and silently does nothing for agent-run commands. This is why the design is a PATH shim, not a shell function.
2. **`fab auth status` exits 0 even when logged out.** Parse its output; never gate on the exit code.
3. **A bare `fab auth login -t <customer tenant>` run from outside a customer folder overwrites the default Pingala profile.** Observed live on 2026-08-11: `~/.config/fab/auth.json` held the Carl Ras tenant. Log in from inside the customer folder, or via `fab-as.ps1`.

**Implementation trap:** the resolver must exclude the directory holding the *shim* from its PATH search, not the directory holding *itself* — otherwise it re-finds the shim and recurses until the caller times out. Fixed with `--shim-dir` (`$(dirname "$0")` / `%~dp0.`) plus a `TENANT_SHIM_ACTIVE` re-entry guard.

## Scope

`fab` only. `az` was deliberately excluded: `AZURE_CONFIG_DIR` would scope it precisely without touching `USERPROFILE`, but shadowing `az` needs a shim dir ahead of PATH **index 2** (`C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin`), i.e. a real user-PATH change. `pac` has native named auth profiles, a different mechanism. Both stay manual under Guardrail 11.

Related: [[fabric-cu-quota]], [[customer-project-two-tier]]
