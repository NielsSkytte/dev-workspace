---
name: fabric-data-agent
bundle: custom
description: >
  How to design, build, ground, and ship a production-grade Microsoft Fabric Data Agent
  (the conversational natural-language-to-data feature, formerly "AI Skill"). Use this skill
  whenever someone is creating, configuring, grounding, or troubleshooting a Fabric data
  agent: choosing data sources (Power BI semantic model, lakehouse, warehouse, KQL/Eventhouse,
  ontology, mirrored DB, Microsoft Graph), writing agent vs data-source instructions and
  example queries, deciding what belongs in the semantic model's "Prep for AI" versus on the
  agent itself, diagnosing an agent that "ignores" table selection or instructions, picking
  the wrong table/measure, or planning a data-agent proof of concept for production. Trigger
  on "Fabric data agent", "data agent", "AI skill in Fabric", "NL2SQL / NL2DAX / NL2KQL",
  "ground an agent on my semantic model", "prep for AI", "verified answers", "the agent picks
  the wrong measure", "chat over my data in Fabric", or any request to build a conversational
  analytics experience on Fabric data. Use this even if the user only mentions one part (e.g.
  just "how do I write the instructions" or "why does deselecting tables do nothing"). Git
  serialization and config-as-code for the agent are covered here
  (`references/git-and-config-as-code.md`). For building the validated test set and running the
  evaluation harness see `fabric-data-agent-testing`; for capacity, cost, usage logging, and
  CI/CD promotion see `fabric-data-agent-ops`.
---

# Building Production-Grade Fabric Data Agents

A **Fabric data agent** is a conversational agent that answers natural-language questions by
generating and running read-only queries against Fabric data sources. It is generally
available (the preview name was "AI Skill"). This skill is the spine for **building one we
would put in front of real users** — not a toy demo. It covers the mental model, what belongs
where, the limits that shape every design decision, and the delivery workflow. Two sibling
skills go deeper:

- **`fabric-data-agent-testing`** — the Python evaluation harness, the validated ground-truth
  Q&A set (distinct from the agent's own "crib sheet"), and CI regression.
- **`fabric-data-agent-ops`** — capacity/cost baselines, the (poor) state of native usage
  logging and the workarounds, and CI/CD promotion plus keeping the model and agent in sync.

Git serialization and config-as-code (folder layout, SDK/REST item definitions, `fab` CLI)
live in this skill — see `references/git-and-config-as-code.md`. For other deep dives, read the
reference files in `references/` (pointers are inline below).

---

## The one thing that explains most confusion

> **For a Power BI semantic model source, the agent's DAX generator uses *only* the model's
> metadata + its "Prep for AI" configuration. It ignores everything you configure at the data
> agent level** — agent instructions, data-source instructions, and the agent's own table
> checkboxes do **not** steer DAX generation.

This single fact explains the two things people hit first:

1. *"Writing instructions on the agent doesn't change how it queries my semantic model."* —
   Correct. Those instructions only affect cross-source **routing** and response formatting.
   The query itself is driven by Prep for AI on the model.
2. *"Deselecting tables in the agent does nothing."* — Also essentially correct for semantic
   models. The authoritative table selection is the **AI data schema** in Prep for AI; the
   agent's checkboxes are a coarse second layer. Microsoft's own guidance is to **make the two
   match**, and to do the real trimming on the model.

For **lakehouse / warehouse / KQL** sources it is the opposite: there is no Prep-for-AI layer,
so the agent's table selection and data-source instructions **are** the controls.

This asymmetry is the heart of the design. Full treatment, with the routing-vs-generation
breakdown and the exact selection rules, is in
[`references/prep-for-ai-vs-agent.md`](references/prep-for-ai-vs-agent.md) — read it before
configuring any semantic-model-backed agent.

---

## Mental model: orchestrator + per-source query tools

An agent has two moving parts:

- **Orchestrator** — reads the user question plus the *agent instructions*, *data-source
  descriptions*, and schema, and decides **which source** to use. This is where cross-source
  routing lives.
- **Per-source query tool** — once a source is chosen, a source-specific tool generates the
  query: **NL2SQL** (lakehouse, warehouse), **NL2DAX** (semantic model), **NL2KQL** (KQL/
  Eventhouse, can call UDFs), and a Graph/ontology query tool. All are **read-only** — no
  create/update/delete, no triggering jobs.

So agent-level text influences *routing and tone*; what actually shapes each query depends on
the source type (Prep-for-AI for semantic models; agent-side config for the rest).

---

## Field reality check — what practitioners learn the hard way

The docs read as more deterministic than the product behaves. Four things hands-on builders
report repeatedly — design for them:

- **Query generation is non-deterministic.** The same question can produce different DAX/SQL on
  re-run — sometimes an elegant single query, sometimes an absurd plan (Chris Webb saw NL2DAX
  issue *five separate queries, one per customer*, for a question it solved in one query the next
  run). **Always inspect the generated query, and pin high-value questions** with verified answers
  / example queries rather than trusting fresh generation.
- **Instructions are honoured *intermittently*, even when correctly placed.** Multiple users
  report the agent ignoring valid AI instructions, with a manual **retry** often fixing it — a
  signal that instruction text is interpreted, not enforced. Prefer **structural** fixes (AI data
  schema, explicit measures) over prose when correctness matters.
- **Over-trimming the schema causes hallucination, not graceful "I don't know."** Removing a
  needed column (e.g. COGS) from the AI data schema made an agent *invent* a number rather than
  admit it lacked the data. Test the questions your trimmed schema can no longer answer.
- **Multi-source agents silently blend mismatched data.** A lakehouse (2001–2004) + semantic model
  (2016) merged into a nonsensical "sales over time" until an example query pinned the right
  source. This is why narrow, specialized agents beat one broad agent.
- **Capacity contention shows up as *wrong answers*, not "slow."** Above ~70% capacity utilization,
  the same agent/prompt/data returns materially different results at different times of day — and
  there's no "system busy" signal, just inconsistency. Size for peak + headroom (see
  `fabric-data-agent-ops`).
- **Truncation is silent and misleads users.** Past ~30–40 rows the response is trimmed with no
  clear warning — the agent may answer "top 10 customers" when the user asked "all above $50K."
  Business users won't notice; shape questions/instructions to avoid large result sets.

Sources: [Webb, 2025](https://blog.crossjoin.co.uk/2025/04/06/fabric-data-agents-unlocking-the-full-power-of-dax-for-data-analysis/);
[Tejwani, Towards AI, 2026](https://pub.towardsai.net/fabric-data-agents-just-hit-ga-94f459c68dcc);
[Jurado Cortés (MS), 2025](https://medium.com/data-science-at-microsoft/microsoft-fabric-taming-ais-wild-side-with-smarter-data-prep-fb1fc9647e99);
[Fabric Community, 2025](https://community.fabric.microsoft.com/t5/Fabric-platform/Microsoft-Fabric-Data-Agent-Ignores-Its-Own-AI-Instructions-Also/m-p/4715105).

## Data sources, and the limits that shape the design

Supported sources: **Power BI semantic model, lakehouse, warehouse, SQL database, KQL database
(Eventhouse — preview support now also covers UDFs, materialized views, and shortcut tables),
mirrored database, ontology (the Fabric IQ Ontology *item* is still preview, though the wider
Fabric IQ platform went GA at Build 2026), and Microsoft Graph.**

The limits below are not trivia — design around them from day one:

| Limit | Value | Design consequence |
|---|---|---|
| Data sources per agent | **up to 5** | Don't try to make one agent know everything. Build **narrow, specialized agents.** |
| Response size | **25 rows × 25 columns** (default) | It's for conversational insight, **not bulk export.** The **Preview Fabric Data Agent Runtime** toggle raises this — enable it for PoCs that need larger results. |
| Tables per source (recommended) | **≤ 25** | Trim hard. Fewer, well-described tables beat a giant schema. |
| Example queries per source | **up to 100** (top ~3–4 retrieved per question by vector similarity) | Few-shots are retrieval-ranked, so coverage and distinctness matter more than volume. |
| Agent instructions length | **up to 15,000 characters** | Plenty for routing + glossary, but keep it lean — bloated instructions add latency and confusion. |
| Unstructured data | **not supported** (no .pdf/.docx/.txt) | A glossary/reference doc must become **instruction text or a queryable table** — see below. |
| Language | English for best performance | Flag for non-English customers. |
| Region | source capacity region must match the agent's | Cross-region grounding fails. Check capacities early. |

Earlier schema-size caps (the old "< 1,000 tables / < 100 columns") have been **lifted** for
KQL/semantic-model/lakehouse/warehouse — large schemas are allowed, but the ≤25-table *practice*
still holds for quality.

**Prerequisites:** F2+ capacity (or P1+ with Fabric enabled), the cross-geo AI tenant settings +
Copilot tenant switch + Fabric data agent tenant setting on, and read access to at least one
source. A semantic model needs only **Read** (not Build, not workspace membership) **and XMLA
endpoints enabled**; RLS/CLS still apply at query time. **Below F64**, every user consuming the
related Power BI content also needs an individual **Pro/PPU** license — a per-user cost that
often surprises teams (real TCO is in `fabric-data-agent-ops`).

---

## The four authoring surfaces — and what belongs on each

| Surface | Scope | Put here | Works for |
|---|---|---|---|
| **Agent instructions** (≤15k chars) | whole agent | objective; **cross-source routing** ("finance → semantic model, raw events → KQL"); cross-cutting terminology/acronyms; tone; response formatting | all sources |
| **Data-source instructions** | one source | which tables to prefer, join logic, filters, value formats, "leading words" (SQL/DAX/KQL fragments) | lakehouse / warehouse / KQL **only** |
| **Data-source description** | one source | one-paragraph summary used for **routing** | all sources |
| **Example queries** (few-shot) | one source | question→query pairs that demonstrate hard logic | lakehouse / warehouse / KQL **only** |

**Critical asymmetry:** data-source instructions, descriptions, and example queries are **not
supported for semantic-model sources.** For a semantic model, everything that shapes the query
must live in **Prep for AI** on the model (AI data schema, verified answers, AI instructions) —
not on the agent. Putting semantic-model query guidance in agent instructions is a common
mistake; the DAX generator never sees it. (This asymmetry is the single most common source of
confusion in the Fabric community — set expectations about it early with anyone building on a
semantic model.)

Recommended instruction structure, leading-words technique, and glossary/reference-material
patterns (including how to ground on a business glossary when unstructured docs aren't allowed)
are in [`references/instructions-cookbook.md`](references/instructions-cookbook.md).

---

## Grounding on a semantic model: Prep for AI (the real control surface)

Prep for AI is configured **on the model** (Power BI Desktop/Service, needs Write) and has
three parts the DAX generator actually consumes:

1. **AI data schema** — the subset of tables/columns/measures the DAX tool prioritizes;
   resolves ambiguity (e.g. "sales" → the right measure). *This is the authoritative table
   selection.*
2. **Verified answers** — approved question→visual pairs (stored at model level). The agent
   doesn't return the visual; it uses the visual's columns/measures/filters to steer DAX, and
   checks for a match before generating fresh DAX. Use 5–7 trigger questions each, ≤3 filters,
   no hidden fields.
3. **AI instructions** — business logic/terminology on the model ("top performer = ≥110% of
   quota"). Interpreted, not guaranteed.

Plus model hygiene that feeds the generator: **descriptions** on tables/columns/measures,
**synonyms**, a clean star schema, explicit measures, business-friendly names.

Workflow detail and the full "what belongs in Prep for AI vs the agent" decision table:
[`references/prep-for-ai-vs-agent.md`](references/prep-for-ai-vs-agent.md).

---

## Grounding on non-model context (glossary, rules, reference material)

There is **no upload-a-document knowledge base** — unstructured files are unsupported. Options:

- **Short, cross-cutting terms/rules** → agent instructions ("Key terminology" section). For a
  **semantic model**, term/rule definitions must instead go into **Prep for AI → AI instructions**.
- **A real glossary that must be queried** → materialize it as a **lakehouse/warehouse table**
  (e.g. `BusinessGlossary(term, definition)`), select it, and use data-source instructions to
  tell the agent when to consult it.
- **Larger doc/RAG needs** → offload to **Foundry IQ** or **Copilot Studio** in a multi-agent
  setup; keep the Fabric data agent as the structured-data tool.

## Grounding on an ontology (Fabric IQ, preview)

A **Fabric IQ Ontology** is a supported source and can be generated from an existing semantic
model — it gives the agent formal entities/relationships instead of guessing from column names.
It's real but immature: live-data binding is gated (Direct Lake + public inbound access only;
Import/DirectQuery give schema-only), `Decimal` columns can return null, refresh is manual, and
group-by needs the agent instruction `Support group by in GQL`. Treat as "use with eyes open."
Details and gotchas: [`references/ontology-grounding.md`](references/ontology-grounding.md).

---

## When it fits (and when it doesn't)

A grounded read from production engagements ([Tejwani, 2026](https://pub.towardsai.net/fabric-data-agents-just-hit-ga-94f459c68dcc)):

- **Fits:** a **mature, well-governed Fabric estate** (clean tables, documented models, consistent
  naming, active capacity management); **bounded, repetitive questions** ("revenue by region last
  month", "customers who grew >20% this quarter"); scaling analytics access to **non-technical
  users** without growing the analytics team.
- **Doesn't fit (yet):** an **immature data foundation** (raw files, inconsistent models, weak
  governance) — the agent will confidently answer *wrong*, and fixing that is the same work you
  owe the foundation anyway; **mission-critical financial/regulatory reporting** where
  confident-but-wrong is unacceptable; workloads needing **strict multi-year reproducibility**
  (mapping drift means the same question can answer differently over time — see below).
- **Budget honestly:** a demo agent stands up in ~30 minutes; a **production-grade agent is
  100–200 hours** of configuration + validation, and **~60–70% of answer quality comes from
  configuration**, not raw model power. Plan the PoC accordingly.

## Delivery workflow for a production PoC

Build in this order — it front-loads the work that actually determines answer quality:

1. **Scope one question domain and one user group.** Narrow beats broad (≤5 sources, ≤25
   tables/source). Write down 15–30 real questions users will ask — these become both the
   design target and the seed of the test set.
2. **Prepare the source(s) first.**
   - Semantic model: optimize the model → set the **AI data schema** → add descriptions/
     synonyms → add **verified answers** → add **AI instructions**. Mirror the same table
     selection later in the agent.
   - Lakehouse/warehouse/KQL: trim to ≤25 well-named tables; plan the data-source instructions
     and example queries.
3. **Create the agent and add sources** (portal: *+ New item → Fabric data agent*, or
   programmatically via the SDK — see `fabric-data-agent-ops` for config-as-code).
4. **Configure the right surfaces** (per the table above). Verify generated queries in the test
   pane; for semantic models, inspect the generated DAX.
5. **Write the validated test set and evaluate** → `fabric-data-agent-testing`. This is the
   gate: a held-out question→answer set scored by the harness, separate from the few-shots the
   agent learns from.
6. **Connect Git** — serialize the agent as config-as-code (folder layout, SDK/REST item
   definitions: `references/git-and-config-as-code.md`). **Set capacity baselines and logging**
   → `fabric-data-agent-ops`. The agent and its model are both Git items: review them
   **together** so a model change triggers a re-test.
7. **Publish**, pilot with a small group, watch capacity, iterate.

A ready-made checklist + utility notebooks exist in Microsoft's `fabric-toolbox`
(`samples/data_agent_checklist_notebooks`) — worth cloning as a starting harness.

---

## Common failure modes (and where they're solved)

| Symptom | Cause | Fix |
|---|---|---|
| Agent instructions don't change DAX | DAX tool ignores agent-level config for semantic models | Move guidance to Prep for AI → AI instructions ([prep ref](references/prep-for-ai-vs-agent.md)) |
| Deselecting tables in the agent "does nothing" | AI data schema is authoritative for semantic models | Trim the AI data schema on the model; mirror in agent |
| Picks the wrong measure ("sales") | ambiguous measures, no AI data schema | Disambiguate in AI data schema; add verified answers |
| Wrong source chosen | weak routing signal | Improve agent instructions + data-source **descriptions** |
| Bad SQL/KQL joins or filters | no per-source guidance | Add data-source instructions + example queries (leading words) ([cookbook](references/instructions-cookbook.md)) |
| Ontology aggregation fails | GQL group-by off by default | Add agent instruction `Support group by in GQL` ([ontology ref](references/ontology-grounding.md)) |
| "Can't I just upload our PDF policies?" | unstructured unsupported | Instruction text, queryable table, or Foundry IQ/Copilot Studio |

---

## Moving target — preview features to watch (mid-2026)

Data agents change monthly. The core agent is GA (and is now also GA inside Microsoft 365
Copilot), but these are live in **preview** and shift the calculus for a PoC — enable them
deliberately and call them out in any plan:

- **Preview Fabric Data Agent Runtime** (toggle in agent settings): higher result limits (lifts
  the 25×25 cap) plus an improved NL2SQL engine (better example-query use, asks clarifying
  questions on ambiguous intent, smarter filter mapping, run-step visibility). Slated to become
  the default.
- **GPT-5.X upgrade** under the agent and its query tools — ~20% accuracy gain on Microsoft's
  internal benchmarks (Build 2026).
- **Creator Agent**: AI-assisted setup that auto-drafts agent instructions, data-source guidance,
  and example queries (currently scoped to SQL and Eventhouse sources).
- **Code Interpreter tool**: runs Python inside the agent for stats/forecasting/cohort analysis
  and Python visuals.
- **Consumption beyond the chat pane**: the agent can be exposed as an **MCP server** (consumed
  via VS Code Agent Mode today), a **Copilot Studio** tool, and a **Microsoft Foundry** tool with
  identity passthrough and per-call observability.
- **Service-principal auth** (preview): run an agent under an app identity for custom apps/Foundry
  (KQL "coming soon") — this **softens the old "SPN can't query at runtime" limit** (see
  `fabric-data-agent-ops` and [git ref](references/git-and-config-as-code.md)).
- Roadmap: **in-agent visualizations** ("coming soon"); ontology GA (no date).

> **Time-sensitive:** the programmatic interface still uses the OpenAI **Assistants API, which
> shuts down 26 Aug 2026**, and Microsoft has not yet shipped the Responses API migration sample.
> Any PoC promising SDK/programmatic consumption must plan for this — details in
> `fabric-data-agent-ops`.

## Authoritative sources

- Concept (sources, limits, governance): https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent
- Create (portal flow, 15k instructions): https://learn.microsoft.com/en-us/fabric/data-science/how-to-create-data-agent
- Configurations (the instruction surfaces + templates): https://learn.microsoft.com/en-us/fabric/data-science/data-agent-configurations
- Best practices: https://learn.microsoft.com/en-us/fabric/data-science/data-agent-configuration-best-practices
- Semantic model best practices (Prep for AI vs agent — the key page): https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices
- Example queries / few-shot validator: https://learn.microsoft.com/en-us/fabric/data-science/data-agent-example-queries
- fabric-toolbox checklist: https://github.com/microsoft/fabric-toolbox/tree/main/samples/data_agent_checklist_notebooks
- What's new in Fabric: https://learn.microsoft.com/en-us/fabric/fundamentals/whats-new
- June 2026 feature summary: https://community.fabric.microsoft.com/t5/Fabric-Updates-Blog/Fabric-June-2026-Feature-Summary/ba-p/5190690
- Data agent as MCP server (preview): https://learn.microsoft.com/en-us/fabric/data-science/data-agent-mcp-server
