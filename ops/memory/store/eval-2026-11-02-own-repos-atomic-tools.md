---
id: eval-2026-11-02-own-repos-atomic-tools
ts: 2026-11-02T12:00:00Z
type: evaluative
scope: workspace
source: session fff04b8f
tags: [skill-eval, own-repos]
status: distilled
description: "own-repos fired for 'sync to Pingala Atomic Tools' but only knows AAI; the ADO Atomic Tools repo had to be found by search"
---

Skill: `own-repos`. Trigger: "sync that folder to the repo Pingala Atomic Tools where we already
have CapacityManager". The skill describes AAI (GitHub) and the post-commit hook only. Pingala
Atomic Tools (ADO, the staff-facing tools repo) is named in MetaAtomic ADR 0011 and the session
log, not in the skill. Three searches were spent locating it. Gap: add Atomic Tools (URL, folders,
no local clone, publish by hand) to the skill.
