---
id: feedback-closed-questions
ts: 2026-08-11T16:50:00Z
type: semantic
scope: workspace
source: session:carlras-datahub-2026-08-11
tags: [feedback]
status: distilled
description: "When a question IS warranted, pose it closed: recommendation first, named options with concrete values, and state what a bare yes triggers; open prompts with no recommendation hand the work back"
---

**An open prompt with no recommendation is the failure mode.** When a decision genuinely belongs
to Niels, the question is posed **closed**, in this order:

1. **The recommendation, one sentence** - what I would do, and why. Never a bare menu.
2. **The options, named and mutually exclusive**, two or three at most, each carrying its
   **concrete values**: the item names, the dates, the row counts, the duration, the cost.
   Never an abstract either/or.
3. **What a bare "yes" triggers** - the exact next action, so that "yes" (or "ja") is a complete
   answer needing nothing added to it.

One decision per question. Banned shapes, all observed in one session: *"your call whether to
..."*, *"I'd rather you pick: A, or B"*, *"want me to X, or Y?"* with no recommendation, *"let me
know how you want to proceed"*, and any *"should I also ...?"* about work already inside the agreed
scope - that last one is not a question at all, it is work to just do
([[feedback-act-then-report]] rules 1-3).

**Why:** 2026-08-11 (Carl Ras / datahub). Niels: *"you need to be a bit more specific on what i
should do or decide on, your questions are somewhat open, this is a major problem going forward."*
Four examples in one session, including *"Want me to fix all four the same way and push?"* (an
obvious yes - it should have been done) and *"Want me to run Phase 1 and 2 once you've done the
Update from git, or push items 10-13 into ops/TODO.md?"* (two decisions, no recommendation, no
values). An open question transfers the analysis back to the person who asked for the work.

**How to apply:** All agents, all sessions. Canonical home: `AGENTS.md` > Conventions ("Ask
closed"). Applies to the ask categories in [[feedback-act-then-report]] (rules 4-7) and to any
real fork in scope.

**Not a mandate for choice cards.** [[feedback-design-dialogue]] stands: architecture and strategy
stay open conversational prose, not AskUserQuestion cards - but they **close on a stated
recommendation**, never on a bare "what do you think". [[feedback-interview-one-question]] stands
too: one question at a time, and a card is the right vehicle once a discussion has reached
enumerable, already-scoped implementation choices. This record governs the *content* of a question
(recommendation, values, what yes means); those two govern its *vehicle* and *pacing*.
