---
id: eval-2026-11-13-own-repos-worktree-hook
ts: 2026-11-13T08:30:00Z
type: evaluative
scope: workspace
source: session e7a5320e
tags: [skill-eval, own-repos, git, worktree, aai-sync]
status: distilled
description: "own-repos: the post-commit AAI push fails for a commit made in a git worktree (GIT_DIR inherited); the skill also still lacks Atomic Tools"
---

Skill: `own-repos`. Context: a SoWSkill commit made on `master` in a worktree (`C:\Dev\own-wt-sow`),
to keep the checked-out feature branch untouched.

- The post-commit hook ran but `sync-aai.ps1` failed: `'origin' does not appear to be a git
  repository` on `git -C <aai cache> fetch`. Cause (inference): git exports `GIT_DIR` to hooks in a
  worktree, so `git -C` in the script uses the worktree's repo. Workaround that worked:
  `env -u GIT_DIR -u GIT_WORK_TREE powershell -NoProfile -File ops/bin/sync-aai.ps1 '<worktree>\SoWSkill'`.
  Fix candidate: clear `GIT_DIR`/`GIT_WORK_TREE` in the hook or at the top of `sync-aai.ps1`.
- Second time (after eval-2026-11-02-own-repos-atomic-tools) that a publish to ADO Pingala Atomic
  Tools needed the memory store, not the skill. The skill still names AAI only.
