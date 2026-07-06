---
id: skill-fabric-licensing
ts: 2026-06-25T10:50:00Z
type: semantic
scope: workspace
source: /log
tags: [project, skill, reference, fabric]
status: distilled
description: "fabric-licensing skill - broad MS-Learn-cited Fabric licensing (capacity SKUs, Free/Pro/PPU, F64 rule, buy/reserve, Copilot metering; data-agent consumption in refs); owns the licensing facts"
---

`.claude/skills/fabric-licensing/` is the **cited** authority for Microsoft Fabric licensing and
cost. `SKILL.md` covers: the two stacking licence types; the F2-F2048 SKU ladder (F64 = P1);
Free/Pro/PPU and the **F64 viewing threshold** (below F64 every viewer needs Pro/PPU; at F64+ Free
viewers can view) - the biggest per-seat cost lever; capacity purchase (pay-as-you-go F SKUs vs a
1/3-year reservation; pause/resume; **P-SKU retirement**); Copilot-in-Fabric metering (consumes
CUs, no per-user licence). References: `capacity-and-per-user.md`, `data-agent-consumption.md`
(Teams / M365 Copilot vs Copilot Credits, publishing, residency), `data-agent-licensing-tables.md`.

**Every fact carries a MS Learn URL + a "(verified YYYY-MM-DD)" stamp** (grounded via the
`microsoft-docs` MCP); dollar prices are flagged "not on MS Learn -> quote from the calculator".
Re-verify quarterly (P-SKU transition, Copilot rates "subject to change").

Origin/lesson: first built as the too-narrow `fabric-data-agent-licensing`, then **generalized to
`fabric-licensing`** (data-agent consumption demoted to a reference). It exists because a
build-from-skills test exposed that those consumption-licensing facts had been **single-sourced in
a `writing-voice` worked example** - a style sample acting as a licensing authority. That example is
now a voice demo only and points here; **this skill is authoritative**. The CU/AI-Query compute
*monitoring* stays in `fabric-data-agent-ops`. See [[skill-pingala-offer]].
