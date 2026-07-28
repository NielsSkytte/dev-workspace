---
id: eval-2026-07-28-datacompare-build
ts: 2026-07-28T12:00:00Z
type: evaluative
scope: project:customers/Matas/DataCompare
source: session:1f323a74
tags: [evaluative, skills, pingala-fabric-platform, feedback-interview-one-question, agents]
status: distilled
description: "Evaluative: pingala-fabric-platform + its new Python-over-PySpark default fired+helped on the DataCompare build; one-card interview pattern worked for 15 decisions; workspace agent roster (sentinel) unavailable in project-rooted sessions"
---

DataCompare architecture + Parts 1–2 build session (07-16 → 07-28):

- **pingala-fabric-platform: fired + helped.** The project-scoped copy loaded by context and
  grounded the Fabric SQL DB / OneLake mirroring / Link-to-Fabric design work. The
  **Python-over-PySpark default added 2026-07-25** demonstrably steered Part 2 the same
  session arc: the canonical layer shipped as a plain-Python notebook (pandas/duckdb/deltalake)
  with no Spark, exactly the intended effect.
- **feedback-interview-one-question: applied + worked.** The 15-decision architecture interview
  ran as sequential AskUserQuestion cards (after the batched-list correction that created the
  record); Niels answered all 15, several via the Other/free-text springboard. The pattern holds.
- **microsoft-docs MCP: helped twice** — Fabric SQL DB platform limits (Part 1 DDL) and
  Link-to-Fabric F&O export behaviors (Part 2 IsDelete / inheritance / valid-time / enums),
  each caught facts that would otherwise have been guessed.
- **Gap: workspace agent roster doesn't load in project-rooted sessions** — the `sentinel`
  agent (mandatory pre-distill review at /log) was not an available agent type in this session
  (rooted at `customers/Matas/DataCompare/...`); vetting done by hand per the README recipe.
  Same root-cause family as [[hooks-subdir-session-gap]] (per-root registration, no cascade).
