---
id: eval-2026-07-23-fabric-licensing-quota-gap
ts: 2026-07-23T00:00:00Z
type: evaluative
scope: workspace
source: session:36359848 (/log checkpoint, Carl-Ras fabric CapacityManager session 07-17)
tags: [skill-eval, fabric-licensing, memory-infra, sanitizer]
status: distilled
description: fabric-licensing consulted manually (helped, but did not auto-fire on "reserved capacity" trigger) and lacks quota coverage; capture-hook sanitizer violated its own rule 4 on /handoff
---

Session: Carl-Ras fabric, CapacityManager scale-up debugging (ran 2026-07-17).

1. **fabric-licensing - helped, but consulted manually and has a gap.** When the user asked
   whether a reserved capacity blocks scale-up, the answer came from grepping the skill's
   files directly (`references/capacity-and-per-user.md:82`, cited with verify date) - the
   skill was not invoked through the Skill tool despite "reserved vs pay-as-you-go capacity"
   being an explicit trigger phrase in its description. Outcome was right (fact-only, cited),
   so the knowledge worked; the trigger mechanism was bypassed. Gap found: the skill has **no
   Fabric CU quota coverage** - the session had to research online (now distilled as
   [[fabric-cu-quota]]). Candidate: add a quota section to fabric-licensing.
2. **microsoft-docs MCP tools fired and helped** (docs_fetch of fabric-quotas + region-
   availability grounded the quota answer).
3. **Memory-infra defect (not a skill):** the capture hook recorded the `/handoff` turn with
   the command's expanded help text as the User body - a direct violation of the sanitizer's
   own rule 4 (record the invocation, never the help text). Sentinel caught it at /log;
   truncated by hand. The sanitizer's command-turn detection evidently misses skill
   invocations that arrive as expanded prompts. TODO filed.
4. **Sentinel value confirmed:** 4/9 records flagged this /log, including one summary that
   falsely claimed the assistant "provided the password" (it had refused and handed sign-in
   to the user) - exactly the fabrication class the sentinel exists to stop from reaching
   the store.
