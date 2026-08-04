---
id: eval-2026-08-04-provider-before-skill
ts: 2026-08-04T00:45:00Z
type: evaluative
scope: project:customers/ElementLogic/LineageDocumentation
source: session:a77891ac
tags: [skills, claude-api, ollama, adr-001, evaluation]
status: distilled
description: "Invoked claude-api before the provider question was settled and built a cloud backend the owner then had to redirect; the workspace already carried the local-first doctrine (ADR-001) and a working Ollama install"
---

**The miss.** The task was "generate business descriptions from lineage". I loaded the
`claude-api` skill because the task was LLM-shaped and the provider was unstated, and built
a Message Batches backend on `claude-opus-5`. The skill did its job well — the batch path is
correct and still ships as `--backend anthropic`. But the provider was the wrong default,
and the owner had to say so: *"can we try to use our local model for this? this is not
complex thinking."*

**Everything needed to propose local first was already in hand.** `ADR-001 > Local Model
Offload` names the two drivers verbatim — *cost* for "documentation generation" and
*privacy* for "tasks involving client-sensitive data that should not leave the local
network" — and this task is both. Ollama was already installed and already in production in
this workspace (the memory capture hook summarises every turn with it). I even raised the
egress concern myself, correctly listing what would leave the machine, but framed it as an
**approval question for the owner** rather than as a reason to choose a different provider.
Surfacing a risk is not the same as acting on it.

**Rule earned: settle the provider before invoking a provider-specific skill.** A skill
named for one vendor will not ask whether that vendor is the right choice — `claude-api`
explicitly scopes itself to Claude code and says nothing about legitimate local backends,
which is correct behaviour for the skill and exactly why the question has to be answered
upstream of it. For any bulk, low-complexity, customer-data workload, check ADR-001 first.

**Cost of the miss was low** and partly recovered: the batch backend remains the fallback,
and the local pivot dissolved the credentials-and-egress blocker entirely rather than
routing it through an approval conversation. But the owner did the thinking the workspace's
own ADR should have done for me.

**Also observed:** `claude-api`'s guidance was sound where it applied and its API-drift table
was worth having. No skill fired automatically this session; both invocations were by
context or by hand.
