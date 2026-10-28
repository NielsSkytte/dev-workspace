---
id: eval-2026-10-28-kurs-memory-recall
ts: 2026-10-28T12:00:00Z
type: evaluative
scope: workspace
source: /log session 16910ea9
tags: [evaluation, skills, memory, fabric, capture-hook]
status: distilled
description: "KURS session: fabric index skill fired but no sub-skill fitted the shortcut/view work; memory record link-to-fabric-late-tables answered 'we dealt with this before'; sentinel found capture_turn mojibake in assistant bodies"
---

- `fabric` index skill fired; none of the twelve sub-skills covered schema shortcuts or views over
  Link to Fabric, so the work ran on CLI probing. Two new procedural records fill that gap.
- Memory store record `link-to-fabric-late-tables-and-endpoint-lag` answered Niels's "believe we
  have dealt with this before" correctly (Track changes, Manage tables, Refresh Fabric tables).
  The tables still took ~a day to appear, longer than the hour recorded there.
- Sentinel (2026-10-28): assistant bodies in daily/2026-10-26..28 carry mojibake (UTF-8 read as
  cp1252, e.g. "VestforbrÃ¦nding"); user lines are fine. Defect in the capture path
  (`.claude/hooks/capture_turn.py`), not fixed this session.
