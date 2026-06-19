# Grounding a data agent on a Fabric IQ Ontology (preview)

An ontology gives the agent **formal business meaning** — entity types, properties, and
relationships — instead of making it infer structure from column names. It's a supported data
agent source today. The wider **Fabric IQ platform reached GA at Build 2026** (Graph, Operations
Agents), but the **Ontology *item* itself is still public preview** and the data-binding story is
fragile. Use it with eyes open. (Also note: like semantic models, **ontologies don't support
example queries** on the agent.)

## Which "ontology" — disambiguation

There are two different Fabric features that both use the word "ontology":

- **Fabric IQ → Ontology (preview)** — *this is the one for data agents.* Announced at Ignite
  (Nov 2025), part of the **Fabric IQ** semantic layer. Defines entity types/properties/
  relationships/rules, binds them to OneLake data, exposes an **NL2Ontology** query layer, and
  uses the separate **Graph in Microsoft Fabric** item under the hood.
- **Digital Twin Builder ontologies** — a different, older capability in the Real-Time
  Intelligence workload for industrial/IoT digital twins. **Not** a data agent source. Don't
  confuse the two.

When someone says "ground the agent on our ontology," they mean the **Fabric IQ Ontology item**.

## Creating one

Two paths when you create the Ontology item:

1. **Generate from an existing Power BI semantic model** — auto-creates the ontology item,
   entity types from tables, static properties + bindings from columns, and relationship types
   from the model's relationships. The headline on-ramp ("jumpstart from your existing models").
2. **Build from OneLake (from scratch)** — manually define entity types and bind properties
   directly from OneLake tables. Use when there's no model or you want full control.

## The data-binding limitations (the real pain)

The ontology **can** bind to live data, but binding is gated. These are the constraints that
turn an ontology into a "schema-only, no data behind it" shell if you trip them:

- **Refresh is manual/scheduled, not live.** New rows upstream aren't visible until refresh —
  even when bound to an Eventhouse.
- **Semantic-model storage mode decides whether *data* binds at all:**
  - Entity/property/relationship **definitions** generate from Import, Direct Lake, and DirectQuery.
  - Entity-type **data bindings**: **Import — not supported. DirectQuery — not supported. Direct
    Lake — supported only if the backing lakehouse workspace has inbound public access enabled.**
    Otherwise you get definitions with **no data bindings**.
  - Querying via bindings works only in Direct Lake, and **without measures or calculated columns**.
  - → An **Import-mode** model yields a **conceptual ontology with no live data**. This is the
    limitation most people hit.
- **`Decimal` returns null.** Fabric Graph doesn't support `Decimal`; properties bound to Decimal
  columns return null on every query (common for money). Workaround: recreate as `Double`.
- **Lakehouse table constraints for binding:** tables must be **managed** (not external), must
  **not** have **OneLake security** enabled, and must **not** have **column mapping** enabled
  (auto-enabled when column names contain special characters/spaces, and on delta tables backing
  import-mode models — silently breaks the graph).
- **One static binding per entity type** (multiple time-series bindings allowed).
- **Property names** must be unique across entity types unless data types match.
- Graph refresh **consumes capacity** and can exceed limits — concretely, **one MVP exhausted and
  throttled an F4** just testing the Graph item backing an ontology
  ([Ilic, 2026](https://community.fabric.microsoft.com/t5/IQ-Community-Blog/Fabric-IQ-and-Ontology-when-your-data-speaks-the-language-of/ba-p/5176825)).
  Requires the Graph tenant setting; no `My workspace`; no built-in versioning yet.
- **Source data must live in OneLake.** External sources need migrating, and even shortcuts copy
  data in — so an ontology is not a thin overlay on wherever your data already is.

## Using it from a data agent

- Add the Ontology item as one of the agent's (≤5) data sources.
- Responses reference **entity types and relationships** rather than raw tables (NL2Ontology).
- **Known issue:** aggregation/group-by is off by default — add the agent instruction
  `Support group by in GQL`. The first query or two may fail while the agent initializes.
- The same ontology can also ground **Copilot Studio** and **Foundry IQ** agents — useful if you
  want one shared business-meaning layer across surfaces.

## Recommendation for a production PoC

If the customer's model is **Direct Lake** and the lakehouse can have inbound public access, an
ontology is worth piloting — it materially improves how the agent reasons about relationships.
If the model is **Import-mode**, or money columns are `Decimal`, or OneLake security is required,
expect a schema-only ontology and **lean on a well-prepped semantic model instead** for this PoC,
revisiting the ontology as the preview matures. Document the choice either way.

Two senior practitioners independently reach the same verdict for *today*: Teo Lachev notes the
Direct-Lake-only data binding "rules out pretty much 99.9% of existing semantic models," and that
building an ontology is labour-intensive (workshops/governance, not auto-generated)
([Lachev, 2025](https://prologika.com/first-look-at-fabric-iq-the-good-the-bad-and-the-ugly/));
Nikola Ilic's hands-on test hit the F4 capacity burnout above. Net: treat ontology as a
forward-looking bet for the PoC's "what's next," not the backbone of the first deliverable.

## Sources

- Fabric IQ overview: https://learn.microsoft.com/en-us/fabric/iq/overview
- Ontology overview: https://learn.microsoft.com/en-us/fabric/iq/ontology/overview
- Generate from a semantic model (binding support matrix): https://learn.microsoft.com/en-us/fabric/iq/ontology/concepts-generate
- Bind data: https://learn.microsoft.com/en-us/fabric/iq/ontology/how-to-bind-data
- Consume from a data agent (group-by gotcha): https://learn.microsoft.com/en-us/fabric/iq/ontology/tutorial-4-create-data-agent
- Troubleshooting: https://learn.microsoft.com/en-us/fabric/iq/ontology/resources-troubleshooting
