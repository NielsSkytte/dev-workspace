---
id: feedback-bang-commands-are-bash
ts: 2026-10-23T12:00:00Z
type: semantic
scope: workspace
source: manual
tags: [feedback]
status: distilled
description: "A command handed to Niels to run with the ! prefix runs in Git Bash: /c/... paths, &&, VAR=value cmd; never $env:, ;-chained PowerShell or backslash paths"
---

Any command given to Niels to run himself with the `!` prefix is **bash** (Git Bash,
`/usr/bin/bash`), not PowerShell, even on this Windows machine.

- Paths: forward slashes, `/c/Dev/...`.
- Chain with `&&`.
- Environment variables inline: `VAR=value cmd`.
- Never `$env:X='y'`, `;`-chained PowerShell, or `C:\...` backslash paths.
- If it truly needs PowerShell: `! powershell -NoProfile -Command "..."`.
- Read the command once as bash before sending.

**Why:** recurring defect, Niels 2026-10-23: "you always do this, bash and run error fix it".
Sent: `! cd C:\Dev\own\MetaAtomic\fabric-app; $env:STORE_WORKSPACE_ID='x'; ... npx rayfin login ...`.
Bash ate the backslashes (`cd: C:DevownMetaAtomicfabric-app: No such file`), each `$env:` line
failed with "command not found", and the command ran in the wrong folder.
Correct form: `! cd /c/Dev/own/MetaAtomic/fabric-app && STORE_WORKSPACE_ID=x STORE_ITEM_ID=x npx rayfin login --tenant ...`.

**How to apply:** every `!` command in a reply. Rule also in `C:\Dev\CLAUDE.md` > Behaviour.
See [[bash-tool-limits-heredoc-backslashes-8kb]].
