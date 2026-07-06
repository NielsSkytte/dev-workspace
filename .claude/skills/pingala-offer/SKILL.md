---
name: pingala-offer
description: >-
  The trusted-advisor doctrine and structure for writing a Pingala customer
  offer - Statement of Work (SoW), proposal, work order, quote, or engagement
  letter. Use this skill WHENEVER drafting, writing, revising, or reviewing any
  offer document Pingala will put in front of a customer, even when the request
  is only "write the offer", "draft the SoW", "the Melbye proposal", "tidy up the
  work order", or names an offer file. Its core rule: in an offer Pingala makes
  the calls - the customer is never handed a question or a decision - and
  implementation/technical detail (security mechanics, billing internals, admin
  steps, SDK/DAX) stays out, because an offer states value, scope, and price, not
  how it is built. Composes with writing-voice (how the prose reads / AI-smell)
  and email-outlook-ready (the cover email). Trigger even if the user only
  mentions one offer or one section.
bundle: custom
---

# Writing a Pingala offer

An offer - a SoW, proposal, or work order - is a confident commitment from a trusted advisor: the value, the scope, the deliverables, the price. It is not a technical design, not a menu of options, and not a list of the customer's homework. Pingala is the expert, and the offer reads like it.

This skill carries the **stance** and **structure** of an offer. For **voice** (how the prose reads, and stripping the AI smell), it builds on `writing-voice` and its `references/business-offers.md` strict layer. For the **cover email**, `email-outlook-ready`. For where an offer sits in the engagement, `pingala-project-playbook`.

## The trusted-advisor stance (the part that matters most)

1. **Never ask the customer a question. The "?" count in an offer is zero.** A question mark means a decision has been pushed onto the customer that Pingala should have made. If you have written one, you have failed as the trusted advisor. State the answer instead.

2. **Never hand the customer a decision.** Where there is a choice, Pingala makes the recommendation and states it as the plan: "We recommend X, and we will do X" - not "you can choose X or Y", and not "one decision for you is...". The customer's only decision is the commercial one: to accept and sign.

3. **The single legitimate exception is a sign-off only the customer can legally give** - a compliance, data-residency, or budget acceptance. Name it as one clear prerequisite ("subject to Melbye's compliance sign-off on X"), with Pingala's recommendation already stated and a fallback already chosen. Never as "which do you prefer".

4. **Make the call with confidence.** State what Pingala will do and why, decision already made. A spec is "F4", not "F2 minimum, sized later" (writing-voice business-offers rule 3). Confidence reads as expertise; options read as indecision.

5. **Do not promise to find out.** State what is true; never write a vague future action ("Pingala will arrange / obtain / confirm X with Microsoft"). If you know it, state it as fact; if you do not, leave it out. A promise to go and check reads as not knowing, which is the opposite of the trusted advisor.

## Know the customer before you write

An offer is shaped by the relationship behind it, and the same engagement reads completely differently for a new customer than for one whose platform Pingala already built and runs. Before drafting - and if you do not know, ask - establish the customer's current state:

- **New or existing customer?**
- **What has Pingala already delivered or built** for them: the semantic model, the Fabric workspaces, pipelines, prior solutions?
- **What does Pingala already operate or own**, versus what the customer holds and controls?
- **What agreements are already in place** (DPA, General Terms, MSA)?
- **Who is the audience** - the budget holder, the sponsor, a technical lead?

This drives **prerequisites and scope** above all. For an existing customer where Pingala built the semantic model and runs the Fabric setup, the offer must not list those as "the customer provides..." prerequisites, or re-scope them as new work - Pingala already has them. Prerequisites then narrow to the genuinely customer-side items: a named SME, an access approval the customer controls, a tenant setting their admin owns, a budget decision. Listing things Pingala already delivered as customer obligations makes the offer read as if it was written by someone who does not know the account. If the current state is unclear, ask before drafting rather than emitting generic "customer provides X" boilerplate.

## Write for the budget holder (keep the build out)

The reader who matters is the person with the **budget and the decision**, not the engineer who will implement. Pitch every section to a business decision-maker: what they get, what it costs, what they commit to, what they must decide. An offer thick with technical mechanics talks past the person who signs it.

So an offer states the **outcome and the commercial frame**. *How* it is built belongs in a technical or design document. Move the following out of the offer:

- How row- and column-level security behaves at query time, and other security mechanics.
- Billing mechanics (pay-as-you-go vs prepaid credit packs, metering internals, credit rates).
- Admin-portal steps (the "Built by your org" approval flow, which switch sits where).
- Tenant-setting toggles beyond *naming* them as a prerequisite.
- SDK/API internals, DAX, schema specifics.
- **Where the Fabric capacity sits.** Name the capacity the engagement needs (e.g. "F4"), never its region, workspace, or placement. Where capacity lives is a setup decision for the design phase, not offer content.

The test: does the budget holder need this to decide to buy, or only to understand value and scope? If it answers "how we will build it" or "where it will sit", it is design-doc material. Relocate it; do not lose the knowledge.

**The one thing you must not thin out: cost and licensing exposure.** Less technical does not mean vague on money. State clearly, in business terms, what the customer must license and budget for, and any cost that scales with use, so there is no surprise later that lands on Pingala. The discipline is business-level clarity, not mechanics: "users are licensed through their existing Microsoft 365 plan; users without it are billed per use, which Pingala sizes up front" - not the credit rates, meters, and Azure billing-policy steps behind it (those live in `fabric-licensing`). Protect Pingala from a licensing or cost gap without turning the offer into a technical manual.

**No reassurance, no meta-framing.** State the fact; do not pad it with comfort ("this is routine, not a blocker", "so the running cost is known up front", "this is straightforward"). A budget holder reads reassurance as filler at best, and as a hint of hidden risk at worst. Cut meta-framing too ("the cost picture below is stated in business terms", "the following is verified against...") - just give the facts.

## What an offer does contain

Value and outcome, scope (in and out), deliverables, estimates, prerequisites (what the customer provides), commercial terms, and a clear path to start. Pingala's SoW structure (Overview, Purpose, Scope, Activities, Areas Not in Scope, Estimates, Prerequisites, Criteria of Delivery, Signatures) is the working template; follow the existing customer SoW as the pattern. State each commercial fact once and cross-reference (writing-voice business-offers rule 6).

## Required sections (do not drop the furniture)

An offer built from scratch tends to lose the *contractual* sections that a polished one keeps - and some of those carry real go-live blockers, not just formality. Every Pingala SoW includes, at minimum:

- **Document History** - versioned, with business-language change rows.
- **Overview** - the value and a one-paragraph scope summary.
- **Delivery** - commercial basis (e.g. Time & Material), the estimate basis, and how out-of-scope work is handled (Change Request).
- **Documents** - this SoW, the Pingala General Terms and Conditions, and the **DPA**.
- **Purpose**, **Scope** (in-scope data/scope plus related/companion work), **Activities** (per phase), **Areas Not in Scope**.
- **Licensing & consumption** - advisor-led and at business altitude; facts sourced from the `fabric-licensing` skill.
- **Organisation** - the roles and named contacts on each side.
- **Prerequisites** - including the technical go-live blockers the customer must satisfy: access and the **XMLA endpoint** on the model, agent and model in the **same region**, the required tenant settings, a named SME, and a current DPA. Missing any of these stalls kick-off, so they belong in every offer.
- **Estimates** - hours, itemised per activity where the scope supports it.
- **Criteria of Delivery** (acceptance) and **Signatures**.

A from-scratch draft that silently drops the DPA, the General Terms, the Organisation section, status reporting, or the XMLA / same-region prerequisites is not signable, however well it reads. Run this list before handing over.

**Keep Areas Not in Scope short.** List only boundaries a customer could reasonably expect to be in scope - adjacent domains, changes to their model, ongoing operation and support. Drop the obvious (no bulk export, no third-party support, no data migration). A long negative list reads as "look at everything we are not doing" and undersells the offer; the genuine boundaries should be a handful, not a page.

## Before / after - the trusted-advisor reframe

A real Melbye SoW licensing passage failed the stance on both counts:

> **Before:** "One decision for Melbye: which users hold M365 Copilot, and for the rest, is the metered per-use cost acceptable? ... Publishing and access. ... Row-level and column-level security on the data always applies: each user sees only what their own permissions allow, exactly as in Power BI, and answers respect the asking user's permissions at query time."

Two failures: a **question** that hands Melbye a licensing decision, and a paragraph of **security and publishing mechanics** that belongs in a design doc.

> **After:** "The agent runs on a Fabric F4 capacity and is used in Microsoft Teams. Each user is covered by their existing Microsoft 365 plan; users without Microsoft 365 Copilot are billed per use."

Pingala made the call, asked nothing, added no reassurance, and moved the mechanics to a technical note.

## Self-check before the offer goes out

1. **Customer state confirmed?** New or existing, and what Pingala already built or runs. Do the **prerequisites list only genuinely customer-side items** - not the semantic model, workspaces, or setup Pingala already delivered?
2. **Search for "?" - the count must be zero.** Each one is a decision Pingala should have made.
3. **Is the customer handed any choice or decision?** Replace it with Pingala's recommendation stated as the plan. The only exception is a named legal/compliance sign-off, framed as a prerequisite.
4. **Written for the budget holder?** Is any section pitched at an engineer rather than a decision-maker? Are build/technical mechanics (security internals, billing, admin steps, SDK/DAX, **capacity location**) moved to a technical note?
5. **Cost and licensing exposure stated in business terms** - clear enough that no licensing gap or scaling cost surprises anyone later, without the mechanics?
6. **No reassurance, no vague promises, no meta-framing?** Cut "this is routine / not a blocker / so the cost is known", any "Pingala will arrange / obtain / confirm X", and framing like "the cost picture below is...". State facts.
7. **Areas Not in Scope short?** Only what a customer could reasonably expect in scope; the obvious dropped.
8. **Does every recommendation read as Pingala's expert call**, not a hedge or an option?
9. Then run the `writing-voice` self-check (em dashes, meta-narration, concision, commit-to-one-answer).
