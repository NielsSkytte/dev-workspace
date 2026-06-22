---
id: skill-creator-trigger-eval-limitation
ts: 2026-06-19T08:53:25Z
type: semantic
scope: workspace
source: session:e852ca0e-aafa-426f-823b-ec72e9210346
tags: [reference]
status: distilled
description: "skill-creator's description-optimization loop gives no valid triggering signal on this Windows setup; also crashes on emoji in SKILL.md"
---

The `skill-creator` plugin's description-optimization loop (`scripts/run_loop.py` →
`run_eval.py`) does **not** produce a usable triggering signal on this Windows + Claude Code
setup. It detects "triggering" by writing a command stub into `.claude/commands/` and watching
whether a nested `claude -p <query>` autonomously calls the `Skill`/`Read` tool — but a command
isn't an auto-loading skill, so the nested model just answers directly and detection reads
**0 triggers for every on-topic query**. Tell-tale sign: every skill scores exactly the
should-NOT-trigger count (e.g. 4/8 test, 6/12 train identically across different skills). Treat
its "best == original, no improvement" output as **no signal**, not as validation.

Second gotcha: `parse_skill_md` reads `SKILL.md` with the default Windows codec (cp1252) and
**crashes on any emoji whose UTF-8 contains byte 0x8f** — notably ⏰ (U+23F0) and ⚠️ (the U+FE0F
variation selector). Keep SKILL.md files ASCII-safe (the workspace ASCII-only convention already
implies this).

Practical path for these skills: **hand-author thorough, "pushy" descriptions** with explicit
`Trigger on "…"` phrase lists and sibling cross-references, and refine reactively if real usage
shows under/over-triggering. The full draft→eval→iterate parts of `skill-creator` still work; only
the automated *description-triggering* benchmark is unreliable here. See [[agent-framework]].
