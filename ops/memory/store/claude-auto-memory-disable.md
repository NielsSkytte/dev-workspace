---
id: claude-auto-memory-disable
ts: 2026-06-22T10:05:00Z
type: semantic
scope: workspace
source: session:e642cd4e-5e1c-4a28-a96c-9d9f9a890aa7
tags: [reference]
status: distilled
description: "Why we disable Claude native auto-memory: it stops the rogue WRITES (the real collision with ops/memory) but not the ~11-16k-token preamble (open bug #63903); Simon layers, we disable+replace"
---

We run `autoMemoryEnabled: false` (in `.claude/settings.json`) on purpose. The reasoning, verified 2026-06-22:

**The collision is on the WRITE side, not the read side.** Claude's native auto-memory (`~/.claude/projects/<project>/memory/`) *reads and writes* during a session — the docs confirm "Claude reads and writes memory files during your session" ("Writing memory" / "Recalled memory"). Left ON, Claude autonomously drops new learnings into `~/.claude` = a **second memory home** accumulating in parallel to `ops/memory/`, fragmenting knowledge our system never sees (split-brain). Disabling it keeps `ops/memory/` the single home — the point of the whole build.

**The disable is partial (known bug).** `autoMemoryEnabled: false` **stops the writes** (what we need) but does NOT suppress the hardcoded memory *preamble* in the system prompt — measured ~**11-16k tokens on Opus** even with an empty memory dir. Open bug **[#63903]** (filed May 2026, no maintainer response; re-file of closed #44829). So we don't reclaim those tokens until Anthropic fixes it; minor on a 1M window. `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` overrides all settings but hits the same preamble bug. The read-side double-load of `MEMORY.md` is separately neutralized by our 3-line stub at the old location.

**Simon Scrapes does NOT disable.** He (and the agentic-OS crowd) *layer on top* — keep Claude's working parts, write summaries to memory.md at wrap-up. Our **disable + replace with one agnostic home in `ops/`** is a deliberate divergence that fits our goals (LLM-agnostic, one home, no duplicate functionality) better than layering on a Claude-specific store. So this was our call, not his recommendation.

**Why:** prevents a split-brain where Claude's autonomous memory-writes land outside our system.
**How to apply:** keep `autoMemoryEnabled: false`; accept the preamble token cost until #63903 is fixed; re-check the bug on Claude Code upgrades (a fix would reclaim ~11-16k tokens/session). Relates to [[memory-arch-three-jobs]], [[skill-usage-evaluation]].

Sources: Claude Code memory docs (code.claude.com/docs/en/memory); GitHub anthropics/claude-code issue #63903 (also #23544, #23750).
