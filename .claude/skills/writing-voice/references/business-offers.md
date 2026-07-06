# Business offers, SoWs and proposals - the strict layer

> Niels's offer voice is **stricter and leaner** than his natural reasoning voice. Offers and Statements of Work are where "AI smell" does the most damage, because the reader is deciding whether to trust and pay. The rules below override the warmer guidance in `voice-profile.md` wherever they conflict.

> **Stance before voice.** In an offer, Pingala never hands the customer a question or a decision, and build/technical mechanics stay out (that is design-doc material). That doctrine lives in the `pingala-offer` skill - load it whenever you write an offer. The rules here are the voice layer on top of it.

## The offer rules

1. **Purpose first, plainly.** Every document and every section opens with one declarative line: what this is and why it exists. State it; do not summarise that you are about to state it.
2. **Strict and declarative for precise topics.** Licensing, scope, requirements, prerequisites, estimates, data residency, security: state them as facts and obligations. "As per current Microsoft requirements, the following is required:" then a clean list. No reasoning-out-loud, no rhetorical questions, no editorialising.
3. **Commit to one answer. No ambiguity in precise text.** State the single value you recommend - "F4", not "minimum F2, Pingala specifies F4, sized later in Phase 2". A range, a vendor minimum, or a "depends / sized later" caveat in a requirements or licensing line reads as indecision and invites a question you did not need to open. If a value genuinely belongs to a later phase, state it there, in that phase's section, not in the requirement. His natural voice hedges once then commits; in offer specs, drop the hedge and state the number. Committing to one value means the vendor minimum, the range, and any "sized later" caveat are intentionally dropped - that is a voice decision, not a lost fact, so a later review or audit should not "restore" them.
4. **Shorter is the goal.** Prefer a table or list to a paragraph for anything enumerable. A licensing section is a tight structure, not three paragraphs. Cut every sentence that does not carry information.
5. **Confirmations live in one place.** Anything the customer must confirm goes into a single labelled block (Prerequisites, or "<Customer> to confirm:"). Never sprinkle "(to confirm before kick-off)" through the prose, and never put it in a heading.
6. **State a fact once, then cross-reference.** A commercial point (the phase split, the Time & Material basis, a scope boundary) belongs in one place, stated in full. Repeating it across three or four sections reads as padding and bloats the offer - the fastest way an SoW gets too long. After the canonical statement, point back to it ("see Overview") instead of restating it.
7. **Version-history rows speak to the customer, not the tooling.** When you bump a version on a customer-facing document, describe the change in business terms ("tightened language; committed the capacity to F4; clarified data residency"), never the editing method ("applied the writing-voice skill; removed em dashes and meta-narration"). The changelog is part of the deliverable the customer reads. (Niels bumps the version and adds a Document History row on every major revision to a versioned client document.)

## Meta-narration kill-list (harvested from a real draft)

These all appeared in a real Pingala SoW and all must go. They announce content instead of delivering it. Recognise the shape, then delete the opener and keep only the substance:

- "In the following, the activities are walked through phase by phase."
- "Before the activities are walked through, the load-bearing goals are summarised here:"
- "A point on expectations, because this is where the value sits."
- "A principle is worth highlighting here:"
- "It is worth stressing that..." / "It is a fact that..." / "It must be highlighted clearly here:"
- "To bring a complex topic back to something manageable, the following is stated for clarity..."
- "To close on the wider view:"
- "The purpose can be briefly summarised as..." (just give the purpose)

Passive, agentless forms in the same family - rewrite into active, owned actions:

- "a closer look is taken at..." -> "this section covers..." or just the content
- "the following is stated" -> state it
- "it is expected that Melbye holds..." -> "Melbye holds... (confirm)" in the confirm block

## Before / after - the licensing section

This is the calibration example. Same facts, ~40% the length.

> **This is a VOICE demonstration, not a licensing reference.** The licensing *facts* in this passage are owned and kept current, cited to MS Learn, by the `fabric-licensing` skill - load that for anything factual about capacity, per-user licences, Copilot vs Copilot Credits, Teams consumption, data residency, or pricing. This example exists only to show how a dense licensing passage tightens into Niels's offer voice. If the facts here and the licensing skill ever disagree, the skill is authoritative.

### Before (AI-smelling)

> ### Licensing & consumption surface (to confirm before kick-off)
>
> To bring a complex topic back to something manageable, the following is stated for clarity, verified against Microsoft's documentation (current as of June 2026). It is expected that Melbye already holds the standard Power BI licences; the Teams consumption route is the one with dependencies worth confirming.
>
> [three dense paragraphs on Teams licensing, each opening with a meta phrase, em dashes throughout, "It must be highlighted clearly here:" framing the data-residency point, "to confirm" repeated inline]

Problems: a heading that hedges, a throat-clearing opener, "is stated for clarity" passive, em dashes as default connectors, the data-residency point buried under "It must be highlighted clearly here", confirmations scattered through the prose.

### After (Niels's offer voice)

> ### Licensing & consumption
>
> Required for the agent, verified against Microsoft documentation (June 2026).
>
> **Melbye to confirm in place:**
>
> | Requirement | Detail |
> |---|---|
> | Fabric capacity | Paid capacity (F4) runs the agent and the subset model. |
> | Power BI Pro or PPU | Per user consuming the agent's model content, on capacities below F64. On F64 and above, free users can consume. |
> | Tenant settings | Fabric Data Agent setting on, Copilot extensibility enabled, cross-geo AI processing and storage enabled. |
>
> **Consuming the agent in Teams** (preview, June 2026). Cost depends only on the licence the user already holds:
>
> | User holds | Cost of agent use |
> |---|---|
> | Microsoft 365 Copilot (paid add-on) | Included. Nothing extra to buy or meter. |
> | Standard M365/O365, no Copilot | Reached via Copilot Chat (free). No per-seat cost. Each use is metered to Melbye in Copilot Credits (pay-as-you-go or prepaid packs). |
>
> One decision for Melbye: which users hold M365 Copilot, and for the rest, is the metered per-use cost acceptable? Pingala sizes this with the Copilot Credits estimator at the question-types session.
>
> **Publishing and access.** Link-publishing to a named group is immediate and fine for Phase 1. Org-wide publishing needs M365 admin approval. Row- and column-level security always applies: each user sees only what their permissions allow.
>
> **Data residency (EU/Sweden).** When the agent is used in Teams, the questions and answers may be processed or stored by Microsoft outside the EU region. The Fabric source data does not move; only the Copilot conversation may leave the region. Melbye decides before Phase 1: accept the Teams terms, or keep the agent in the in-region Fabric chat pane. Pingala obtains written confirmation from Microsoft if required.

What changed: the heading lost its hedge, the opener became a single declarative line, the dependency lists became scannable tables, "to confirm" was consolidated into one labelled block and one explicit decision, em dashes are gone, and the data-residency point is stated as a crisp decision rather than introduced with "It must be highlighted clearly here".

## What survives into offers

The strict layer trims, but the parts that make it *him* stay:

- Thanks-first in the cover note and the email that carries the offer.
- First-person ownership where Pingala takes a position ("Pingala specifies F4", "Pingala recommends implementing both").
- Honest edges over false certainty: name the preview status, the dependency, the assumption. He is candid about risk, not relentlessly upbeat.
- The occasional value-framing line in a warm section (Overview, Vision) - kept to one, never in a precise section.

When unsure whether a sentence belongs, ask: does the customer need this fact to decide or to act? If not, cut it.
