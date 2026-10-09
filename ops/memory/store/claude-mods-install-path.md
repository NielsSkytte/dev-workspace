---
id: claude-mods-install-path
ts: 2026-10-09T12:30:00Z
type: semantic
scope: workspace
source: /log
tags: [claude-code, mods, plugins, settings]
status: distilled
description: "A Claude Code mod built in a session lives in ~/.claude/dev-mods/<session>/ and loads only there; to load it in every session copy it to C:\Dev\.claude\mods\<name> and add the path to CLAUDE_CODE_PLUGIN_DIRS in ~/.claude/settings.json (';'-separated, inference), then run claude-accounts.ps1"
---

- Found 2026-10-09: `work-view` (hides code and tool output) was built 2026-10-07 in session f8e8b854
  but never installed, so other sessions showed code. `hours-chart` was installed the documented way.
- Installed: `C:\Dev\.claude\mods\work-view`, `CLAUDE_CODE_PLUGIN_DIRS` =
  `...\mods\hours-chart;...\mods\work-view`, settings re-synced to `~/.claude-priv`. Takes effect in
  new sessions. The `;` separator is not verified - if hours-chart disappears, the separator is wrong.
