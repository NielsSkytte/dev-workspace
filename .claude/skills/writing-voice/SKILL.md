---
name: writing-voice
description: >-
  Niels's business writing voice for ANY prose drafted on his behalf - client
  emails, offers, Statements of Work, proposals, executive briefs, customer
  notes, web or LinkedIn copy - in Danish or English. Use this skill WHENEVER
  you write or rewrite text that Niels (or Pingala) will send, publish, or hand
  to a customer, even when the request is only "draft an email", "write the
  offer section", "tidy up this paragraph", or "make this sound better". It
  strips the AI smell (em dashes, tricolons, "leverage/robust/seamless/holistic",
  meta-narration, throat-clearing, hedge-leaks) and bends the text to how Niels
  actually writes: warm but strict, purpose-first, and as short as the content
  allows. The reader is always a Danish/Nordic business customer. Composes with
  the email-outlook-ready skill (that one keeps the FORMATTING intact on paste
  into Outlook; this one keeps the VOICE). Trigger even when the user never says
  "voice" or "style" - any customer-facing or business prose qualifies.
bundle: custom
---

# Writing in Niels's voice

## When this applies

Any prose you draft for Niels to send or publish: client emails, offers, Statements of Work, proposals, executive briefs, internal notes, web copy. Danish or English. This skill governs **voice**; `email-outlook-ready` governs **formatting** - use both when the deliverable is an email.

The voice was reverse-engineered from Niels's own writing (a Danish master's thesis and his real sent mail). The full evidence sits in `references/voice-profile.md`. This file is the operational core: the rules and the self-check. Read the references when you need the detail or you are writing something substantial.

## The reader is always a Danish/Nordic business customer

- **Plain, clear language.** The reader is often a non-native English speaker (Melbye, for instance, is Swedish). Avoid idiom, heavy phrasal verbs, and cultural references that do not travel.
- **EU context is real, not noise.** GDPR, data residency, and European number/date formats are points the reader cares about. Treat them as substance.
- **Danish business norms** even at senior level: "Hej" greeting, direct "du/I", "Mvh" sign-off. He never opens with "Kære". See `references/danish.md`.

## The two things that make it him

1. **Warmth plus argument.** Thanks-first opener, first-person ownership of a recommendation ("jeg mener" / "my recommendation is"), honest about risk rather than relentlessly upbeat. A senior consultant with a point of view, not a faceless report.
2. **Economy.** He says it once, plainly, and stops. Half of sounding like him is what you *do not* write. When in doubt, cut.

## Register map - match the section, not just the document

Niels's natural voice reasons out loud; his *business* voice is stricter. Pick the stance per section:

| Section type | Stance |
|---|---|
| Warm / relationship: greeting, cover note, overview framing, the close | Voice-forward. Thanks-first, first person, at most one rhetorical-question hinge. Still tight. |
| Precise / technical: licensing, scope, requirements, prerequisites, estimates, data residency, anything with numbers or obligations | **Strict and declarative.** State requirements as requirements. List- or table-first. No narration, no hedging, no rhetorical questions. |

Emails lean warm. Offers and SoWs lean precise. Never let a precise section drift into reasoning-out-loud - that is where the Melbye draft went wrong. The strict layer and a full before/after live in `references/business-offers.md`.

## Universal rules (every register)

- **Purpose first.** Open each document and each section by stating what it is and why, in one plain declarative line. Not "The purpose can be briefly summarised as..." - just state it.
- **Concision is the default.** Cut any sentence that carries no information. Prefer a list or table to a paragraph whenever the content is enumerable. In offers, shorter is the goal, not a side effect.
- **Declarative for anything precise.** "As per current Microsoft licensing requirements, the following is required:" then a clean list. Never "To bring a complex topic back to something manageable, the following is stated for clarity...".
- **Commit to one answer in precise text.** State the single spec you recommend ("F4"), not the vendor minimum, a range, or a "depends / sized later" caveat. Ambiguity in a requirements or licensing line reads as indecision. If a value truly belongs to a later phase, state it in that phase's section, not in the requirement.
- **No meta-narration / throat-clearing.** Delete openers that announce what you are about to do: "In the following, X is walked through", "A point worth highlighting", "It is worth stressing/noting that", "It must be highlighted clearly here", "To close on the wider view". Present the content; do not narrate it.
- **No working notes leaking to the customer.** "(to confirm before kick-off)", "(confirm)", "worth confirming" sprinkled inline are internal hedges. Collect everything that needs confirming into one clean labelled block (a Prerequisites list, or "Melbye to confirm:"). Never pepper the prose with parenthetical uncertainty.
- **Own actions in the active voice.** "Pingala builds...", "we map...", "vi kortlaegger...". Not "a closer look is taken", "the following is stated", "it is expected that".
- **One hedge max, then commit.** Keep a single honest softener ("nok", "umiddelbart" / "typically", "in our experience") and strip it off the actual recommendation.
- **No breezy or "clever" phrasing.** The register is formal Nordic/Danish business language, not American sales punch. Strip lines that try to be quotable or wry: "built in an afternoon", "in a heartbeat", "the magic happens here", "easier said than done". State the fact plainly: "Setting up a data agent in Fabric takes only a few steps; the real work lies in instructing it correctly and validating its answers." Plain and factual beats catchy.
- **Label and heading words must name the technical property, not a vibe.** A section title or bold label states what the thing *is*, in terms the reader can check. Use "a validated data agent" (grounded on truth, tested for correctness), not "a proper / real / serious data agent" - vague qualifiers that could mean anything (how it talks back, how it looks). If you cannot say what the word verifies, it is the wrong word.

## Strip the AI tells first (subtraction beats imitation)

Trying to "write like Niels" produces caricature. The reliable method is to remove what he never does, then nudge what remains toward his markers. The top tells, all confirmed absent from his own prose:

- **Em dash as a connector** - he uses it **zero** times. Replace every `-` -style break with a colon, comma, parenthesis, or full stop.
- **Tricolons / rule-of-three** for cadence ("clear, concise, and compelling"). Make lists their real length.
- **The additive ladder**: "Derudover / Endvidere / Furthermore / Moreover / In addition". He uses essentially none. Injecting them is the fastest way to stop sounding like him.
- **"Not just X, it's Y"** used to hype. He only uses that contrast to downgrade or qualify.
- **Empty connectives**: "In conclusion", "Overall", "It is important to note that".
- **AI lexicon (zero tolerance):** delve, leverage, robust, seamless, navigate (figurative), holistic, underscore, unlock, elevate, foster, landscape, journey, world-class - and Danish equivalents (robust, holistisk, synergi, fremtidssikret). Their appearance means the draft has drifted off-voice.

The complete AVOID list with detection signals is in `references/voice-profile.md` (section 5).

## Self-check before you hand it over

Run this on every draft, in this order:

1. **Em dash count = 0?** Search the text. Replace each with colon / comma / parenthesis / full stop.
2. **Any meta-narration or "(to confirm)" leak?** Delete the narration; consolidate the confirmations into one labelled block.
3. **Could any paragraph be a tighter list or table?** Especially in an offer or a requirements section. And is any commercial fact (the phase split, the T&M basis, a scope boundary) stated more than once - if so, say it once and cross-reference.
4. **Is the purpose stated plainly, up front?**
5. **Register right?** Precise sections strictly declarative and committed to one answer (no stray range, minimum, or "sized later"); warm sections thanks-first and first person.
6. **AI-lexicon scan** (leverage / robust / seamless / holistic / delve / ...) - clean?
6b. **Register and label scan.** Any breezy/"clever" line ("built in an afternoon", "the magic happens")? Rewrite plain. Any heading or label using a vague qualifier ("proper", "real", "serious") instead of the verifiable property ("validated", "tested", "grounded")? Replace it.
7. **(English only)** Any "Mvh" or Danish word leaking in? Scrub it. Plain enough for a non-native reader?
8. **Read each sentence in one breath.** Any sentence you cannot - split it.

## Go deeper

- `references/voice-profile.md` - the full evidence-backed fingerprint: rhythm, diction, stance, the KEEP list, the complete AVOID list, calibrated before/after examples.
- `references/business-offers.md` - the strict offer/SoW layer, with the real Melbye licensing before/after and the meta-narration kill-list.
- `references/danish.md` and `references/english.md` - per-language specifics. Load the one for the language you are writing in.
