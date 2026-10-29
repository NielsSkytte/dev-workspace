---
id: eval-20261022-fabric-skill-index
ts: 2026-10-22T15:50:00Z
type: evaluative
scope: workspace
source: /log
tags: [eval, skills, fabric, capture-hook, auto-mode]
status: distilled
description: "2026-10-22: 12 Fabric skills moved behind a `fabric` index skill (listing ~10k -> ~6.1k); watch that Fabric work still reaches them; probes and mojibake polluted the capture; auto mode blocked the workspace push"
---

- Niels found the Fabric skill descriptions (~4k tokens) needless at startup. Q set `disable-model-invocation: true`
  on 12 Fabric skills and added one index skill `fabric`. Agent `skills:` preload was rejected: it only takes
  model-invocable skills. Watch (m.md WATCH): does Fabric work still find the right skill through the index?
- Q's `claude -p` listing probes were captured as turns in daily/2026-10-22.md (4 dropped by sentinel). Probe runs
  from a subagent pollute the memory stream.
- Sentinel: capture_turn.py still writes mojibake (UTF-8 read as cp1252) and expanded skill bodies / harness
  mid-turn text in User lines (2 truncated in daily/2026-10-21.md). Fix is still open.
- Auto-mode classifier blocked `git commit`/`git push` of the workspace repo (ops/ memory + tasks to the GitHub
  remote) as sensitive / out-of-place publication; /log step 8 may need Niels to run it or an allow rule.
