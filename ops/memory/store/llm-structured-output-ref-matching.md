---
id: llm-structured-output-ref-matching
ts: 2026-08-06T09:00:00Z
type: procedural
scope: workspace
source: session:a77891ac
tags: [llm, structured-output, json-schema, ollama, anthropic, prompt-design]
status: distilled
description: "Match batched LLM output by an opaque ref you assign, never by a human-readable name - models qualify names with other fields in the payload and the mismatch silently discards good output"
---

When you send a model N objects and ask for N results back, **give each object an
opaque `ref` and have the model echo it**. Do not match results to inputs by name.

**The failure, observed 2026-08-04.** A request carried `{"group": "columns/
DimAccountHierarchies", "objects": [{"name": "TotalAccountNameLevel1", ...}]}`.
`mistral-small3.2:24b` returned the name as
`"columns/DimAccountHierarchies/TotalAccountNameLevel1"` — it had helpfully
qualified the name with the group field sitting next to it. Six of twenty
descriptions failed to match and were **silently discarded**. The generated text
was good; only the join was broken. `gemma4:12b` never did this, so the defect
looked like a model-quality difference until the returned names were printed.

Three rules that follow:

1. **Opaque ref.** `"ref": "o0"` carries no semantics for the model to improve on.
   Instruct explicitly: *copy the ref back verbatim, it is an identifier not a
   name, never qualify it or tidy it up.*
2. **Report unmatched results, never drop them.** Any result you cannot join is
   generated output you are throwing away — it must reach a log or stderr. A
   silent drop looks identical to a successful run.
3. **Progress output must count what was WRITTEN, not what came back.** The
   original line printed `len(items)` (results returned) while the total counted
   successful joins, so per-group output summed to 20 while the run reported 14.
   The discrepancy was visible only in the final total.

A fallback that strips a qualifying prefix is worth having as a safety net, but it
is a net — the ref is the fix. Note this is a *payload design* problem, not a
model defect: putting a `group` field beside a `name` field invites exactly this.
