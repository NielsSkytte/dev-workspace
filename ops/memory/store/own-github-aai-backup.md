---
id: own-github-aai-backup
ts: 2026-10-04T12:00:00Z
type: semantic
scope: project:own/MetaAtomic
tags: [github, backup, aai, metaatomic, sowskill, git-filter-repo, own-repo]
status: distilled
description: "C:\\Dev\\own is ONE git repo (all own projects) with no remote; selected folders are backed up with history to the private GitHub repo atompower4us/AAI by ops/bin/sync-aai.ps1, manual only"
---

- `C:\Dev\own` is a single git repo holding every own project (MetaAtomic, SoWSkill, DeployFabric,
  ...). It has no remote. `git rev-parse --show-toplevel` from a project folder says `C:/Dev/own`.
- 2026-10-02: private repo `https://github.com/atompower4us/AAI` created (org admin: NielsSkytte,
  `gh` 2.102.0 installed via winget, keyring login). Folders `MetaAtomic/` (131 commits) and
  `SoWSkill/` pushed with history; `main` at `ff9beb9`.
- Private because the MetaAtomic history names customers (22 tracked files). The Pingala ADO repo
  keeps the customer-free published subset (`build.py publish`); AAI is the full backup.
- Sync: `powershell -NoProfile -File C:\Dev\ops\bin\sync-aai.ps1 <folder>...` (`-List`, `-NoPush`,
  `path=Name`). It extracts each folder from a throwaway clone with `python -m git_filter_repo`
  (pip package; the `git filter-repo` subcommand does not spawn on this machine), merges into a
  script-owned clone at `%LOCALAPPDATA%\aai-sync\AAI`, pushes `main`. The extract is deterministic,
  so a re-sync adds only new commits. Committed work only.
- Not automatic: a post-commit hook in `C:\Dev\own\.git\hooks` was blocked by the auto-mode
  classifier (unauthorized persistence); Niels holds the hook text and installs it himself.
- Gotcha met while writing the script: a PowerShell function named `Git` shadows `git.exe`, and a
  `ValueFromRemainingArguments` param needs `[CmdletBinding(PositionalBinding = $false)]` when
  other string params follow, or the positional value binds elsewhere.
