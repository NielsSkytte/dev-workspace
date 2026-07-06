# Memory Store — Index

Distilled, curated memory records (`ops/memory/store/`). Grouped by `tags` category.
This index is rebuildable from the records' frontmatter (`id` + `description`). Newest jobs
and the record shape live in [`../README.md`](../README.md).

## User
- [user-work-profile](user-work-profile.md) — solo consultant, Fabric/data platforms, Pingala A/S, context-switches frequently

## Feedback
- [feedback-design-dialogue](feedback-design-dialogue.md) — in architecture/strategy talks, discuss in prose; don't force AskUserQuestion cards
- [feedback-response-style](feedback-response-style.md) — terse/brief/full sticky keywords; default brief; no edit narration unless asked
- [feedback-commit-to-test](feedback-commit-to-test.md) — proactively offer commit+push when a push unblocks testing/deploy; user still approves (convention canonical in AGENTS.md)
- [feedback-version-bump-revisions](feedback-version-bump-revisions.md) — on a major revision to a versioned client doc (SoW/offer), bump the version + add a Document History row, unprompted
- [feedback-time-attribution-dev-to-project](feedback-time-attribution-dev-to-project.md) — project-rooted time always stays; Dev-rooted time clearly a project's gets reassigned to it (out of Dev only)

## Project
- [workspace-design](workspace-design.md) — two buckets (own/customers), two types (content/function), focus field, scale
- [customer-project-two-tier](customer-project-two-tier.md) — customers/ is two-tier: customer node (map, never billable) wraps projects (work unit); session walk three-scoped
- [agent-framework](agent-framework.md) — 7 agents (fabric-back/semantic/fabric-front + content, architect, M, Q); fabric split at the semantic model; frontmatter required for invocation; skill=verb vs agent=role
- [knowledge-flow](knowledge-flow.md) — /brief command + INBOX.md for cross-project knowledge transfer
- [atomiccortex-vision](atomiccortex-vision.md) — LLM second brain; full-ICOR, portability-first (tool + scale), markdown+git, three horizons (solo->team of 10->org of 150)
- [skill-usage-evaluation](skill-usage-evaluation.md) — core goal: capture which skills fire/don't-fire/help and feed back into skill revision; the evaluative layer this memory system enables
- [time-tracking-system](time-tracking-system.md) — per-project time tracking at ops/time/; heartbeat+15/5 idle model, deterministic rollup, F&O codes, data gitignored (ADR-002)
- [skill-writing-voice](skill-writing-voice.md) — writing-voice skill (DA/EN); subtraction-first AI-smell removal; built from Niels's thesis + email voice
- [skill-pingala-offer](skill-pingala-offer.md) — pingala-offer skill; trusted-advisor doctrine (no questions/decisions, build out, customer-state interview, budget-holder altitude, no capacity location)
- [skill-fabric-licensing](skill-fabric-licensing.md) — fabric-licensing skill; broad MS-Learn-cited Fabric licensing; owns the licensing facts (replaces the voice-example single-source)

## Reference
- [memory-arch-three-jobs](memory-arch-three-jobs.md) — Simon Scrapes video; Storage/Injection/Recall framing, cherry-picks Hermes/MemArch/GBrain, company-brain RLS; our memory direction
- [skill-creator-trigger-eval-limitation](skill-creator-trigger-eval-limitation.md) — its description-optimization loop gives no valid triggering signal on this Windows setup; crashes on emoji in SKILL.md
- [claude-auto-memory-disable](claude-auto-memory-disable.md) — why we disable native auto-memory: stops its rogue writes (the real collision with ops/memory) but not the ~11-16k-token preamble (open bug #63903); we disable+replace, Simon layers
- [workflow-large-return-timeout](workflow-large-return-timeout.md) — Workflow synthesis returning two big files via schema times out; files write to disk first (recoverable); prefer agent-Write or smaller returns
