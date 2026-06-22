---
id: memory-arch-three-jobs
ts: 2026-06-19T14:03:58Z
type: semantic
scope: workspace
source: session:e642cd4e-5e1c-4a28-a96c-9d9f9a890aa7
tags: [reference]
status: distilled
description: "Reference - Simon Scrapes 'best Claude memory system' video; Storage/Injection/Recall framing, cherry-picks Hermes/MemArch/GBrain, company-brain RLS for teams"
---

Source: YouTube "I Built The Best Claude Memory System (Beats Hermes)" by **Simon Scrapes** (id `H9BUkgDf5Y4`). The user's stated basis for our memory direction. Related: [[skill-usage-evaluation]], [[atomiccortex-vision]].

Core model — Claude memory does **three jobs**, each with variable choices; he surveyed ~20 frameworks and cherry-picks the best per job into one portable, plug-and-play system (works across Claude Code / Codex / any harness):

- **Storage** — who triggers save (hook vs agent) × form (verbatim vs summarized). Fix: keep summarized + add an **automatic per-turn hook (MemSearch)** — a cheap model (Haiku) summarizes each turn into a **daily log**, no agent opinion about what matters. (Claude OOTB = agent-decided + summarized = *leaky*; if the agent doesn't flag it, it's never saved.)
- **Injection** — hook-loaded vs agent-pulled × capped vs uncapped. Fix: **Hermes frozen snapshot** at session start (identity / user profile / most important recent memories), ~1,300 tokens, **cached** (pay once/session). (Claude OOTB = hook-loaded but *uncapped* = bloat.)
- **Recall** — keyword vs semantic vs hybrid. Biggest gap (Claude OOTB = **no search at all**). Fix: **MemArch** local **vector index** (zero API cost) + **hybrid** (semantic+keyword), **multi-tier** (tier 0 = check the injected snapshot first, then go deeper) + **GBrain** (Gary Tan / YC) **re-ranker** + **cited sources**. Principle: *"a good memory system admits what it doesn't know; a confident answer with no source is worse than useless for client work."*
- **Team scale** (his June feature) — Gary Tan's **"company brain"**: one central store (Postgres on Supabase + **row-level security**), every row tagged by client/project/department, every query filtered by the asking user's token. Simpler alt = one DB per person, but that yields *isolated* (not shared) brains.

**Decision (2026-06-19):** adopt his **mechanics as the foundation** (per-turn/daily capture, capped+cached injection snapshot, hybrid recall with cited sources, company-brain RLS for the team horizon), with **skill-evaluation layered on top** as the first *evaluative* use case (the video doesn't cover the evaluative layer — judging the system's own skills — see [[skill-usage-evaluation]]).

**A database is NOT ruled out** — it's a *sequencing* call, not a principle. A lightweight DB is fine once the system is up and running; the user's earlier "overkill" was timing, not rejection. **For now: work on structure.** Design a **storage-agnostic record shape** — markdown+git now (still the LLM-agnostic substrate, Guardrail 7), but shaped so a lightweight DB / vector index drops in later as an accelerator without reshaping (any index is rebuildable from the markdown, which stays source of truth). Add a **`scope` field** (workspace/project/client) to every record from day one so the future company-brain RLS is a tag-and-filter, not a re-architecture.
