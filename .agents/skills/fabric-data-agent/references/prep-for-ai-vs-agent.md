# Prep for AI vs. the Data Agent — the two-layer model

This is the most misunderstood part of building a Fabric data agent, and the source of the two
complaints people hit first: *"my agent instructions don't change anything"* and *"deselecting
tables does nothing."* Both are explained by one rule.

## The rule

> When the source is a **Power BI semantic model**, the agent's **DAX generation tool relies
> solely on the semantic model's metadata and its Prep for AI configuration. It ignores any
> instructions you set at the data agent level.**

So there are two layers, and which one controls behavior depends on the **source type**:

| | Semantic model source | Lakehouse / Warehouse / KQL source |
|---|---|---|
| What generates the query | NL2DAX tool | NL2SQL / NL2KQL tool |
| What it reads | **only** model metadata + Prep for AI | the agent's table selection + data-source instructions + example queries |
| Agent-level instructions affect the query? | **No** (routing/formatting only) | They affect routing; per-source instructions affect the query |
| Authoritative table selection | **AI data schema** (on the model) | the agent's table **checkboxes** |
| Where business rules/terms go | **Prep for AI → AI instructions** | data-source instructions |
| Few-shot example queries | **not supported** | supported (≤100/source) |

## Why "instructions on the agent do nothing" (for semantic models)

Agent instructions are consumed by the **orchestrator** — the part that decides *which source*
to use and how to format the reply. They are **not** passed to the DAX generator. If you write
"always use the Net Sales measure" in agent instructions, the DAX tool never sees it. The fix is
to encode that in **Prep for AI → AI instructions** (or, better, resolve it structurally in the
**AI data schema** so the ambiguous measure isn't even a candidate).

Rule of thumb: **agent instructions should only contain guidance that applies across all
sources** — routing rules, cross-cutting acronyms, tone, response format. Anything specific to a
semantic model belongs in Prep for AI.

## Why "deselecting tables does nothing" (for semantic models)

There are two table-selection surfaces:

1. **AI data schema** (Prep for AI, on the model) — *the* control the DAX tool uses.
2. The data agent's own table **checkboxes** (when you add the model as a source) — a coarser
   layer.

Because the DAX tool reads the AI data schema and ignores agent-level config, trimming tables on
the *agent* feels inert. Microsoft's guidance, verbatim in spirit: configure the schema in Prep
for AI first, then **select the same tables in the data agent** so the two are consistent
("very important" in the official checklist). Do the real trimming on the model.

Caveat the docs are silent on: whether deselecting a table on the agent (while it stays in the
AI data schema) fully blocks the DAX tool. The safe operating assumption is **the model layer
wins — make both match** rather than relying on agent-side deselection.

For lakehouse/warehouse/KQL there is no AI data schema, so the agent's checkboxes *are* the
control and deselection works as expected.

## What goes where — decision table

| You want to… | Semantic model | Lakehouse / Warehouse / KQL |
|---|---|---|
| Limit which tables the AI considers | AI data schema (then mirror in agent) | agent table checkboxes |
| Disambiguate a measure/column | AI data schema (+ descriptions/synonyms) | data-source instructions |
| Encode a business rule ("peak season = Nov–Jan") | Prep for AI → AI instructions | data-source instructions |
| Pin a known question to a trusted answer | verified answer (model) | example query (few-shot) |
| Demonstrate a hard query pattern | verified answer / AI instructions | example query with "leading words" |
| Tell the agent which source to use | agent instructions + data-source description | agent instructions + data-source description |
| Set tone / response format | agent instructions | agent instructions |

## The three parts of Prep for AI (semantic model)

Configured on the model (Power BI Desktop or Service; needs **Write** on the model):

1. **AI data schema** ("Simplify data schema"): pick the tables/columns/measures the DAX tool
   should prioritize. Include **dependent objects** for any measure you keep (a measure that
   references other measures/columns needs them present) — Semantic Link Labs'
   `get_measure_dependencies` helps. Exclude helper/duplicate measures that create ambiguity.
   **But don't over-trim:** removing a column a question genuinely needs makes the agent
   *hallucinate* a confident wrong answer rather than say "I don't have that"
   ([Jurado Cortés, MS, 2025](https://medium.com/data-science-at-microsoft/microsoft-fabric-taming-ais-wild-side-with-smarter-data-prep-fb1fc9647e99)).
   Test the questions your trimmed schema can no longer answer.
2. **Verified answers**: approved question→visual pairs, stored at **model level** so every
   agent using the model benefits. The agent uses the visual's columns/measures/filters to steer
   DAX and checks for a match before generating fresh DAX. Tips: 5–7 trigger questions per
   answer, ≤3 filters, won't work on hidden fields. (A Microsoft data-agent PM confirms a verified
   answer captures the visual's **projections** — tables/columns/measures/filters — **not** the
   DAX query itself — [Pawar, 2026](https://fabric.guru/programmatically-retrieve-prep-data-for-ai-configuration-of-semantic-models).)
3. **AI instructions**: free-text business logic/terminology ("top performer = ≥110% of quota").
   Interpreted by the LLM — influential but not guaranteed; prefer structural fixes (schema,
   explicit measures) when correctness matters.

Plus model hygiene the generator leans on: **descriptions** on tables/columns/measures, clean
**star schema**, **explicit measures**, business-friendly names, and report **visual metadata**
(the DAX tool also reads visual titles/columns/measures/filters). Practitioner nuances (Tabular
Editor's [AI-readiness guide, 2026](https://tabulareditor.com/blog/ai-readiness-and-best-practices-for-semantic-models-a-comprehensive-guide)):

- **Implicit / report-scoped measures and auto-sum fields are invisible to the agent.** Every
  AI-facing metric must be an **explicit DAX measure** — a hard rule, not a nicety.
- **Synonyms are low-ROI on their own.** They help only for genuinely irreducible naming clashes;
  prefer *fixing inconsistent names*. Don't expect synonyms alone to move the needle.
- **Context is a budget, not a pile.** Over-describing causes "context rot" (useful signal drowns
  in noise), and an auto-generated description the model could infer from the schema adds nothing.
  Describe only where it encodes **business logic the schema doesn't reveal**.
- **Display folders don't scope the agent** — it sees every measure regardless of folder.

## Recommended sequence (semantic model)

1. Optimize the model (star schema, explicit measures, names).
2. Set the **AI data schema** (the subset).
3. Add **descriptions + synonyms**.
4. Add **verified answers** for the highest-value known questions.
5. Add the model to the agent, **mirror the table selection**, and test — inspect the generated
   DAX, not just the answer.
6. Add **AI instructions** to fix what the DAX inspection revealed.
7. Only then set **agent-level** instructions (routing/tone/cross-source terms).
8. Validate with the test harness (`fabric-data-agent-testing`) and version with Git
   (`fabric-data-agent-ops`).

## Source

- Semantic model best practices (the authoritative page):
  https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices
- fabric-toolbox checklist:
  https://github.com/microsoft/fabric-toolbox/blob/main/samples/data_agent_checklist_notebooks/Semantic%20Model%20Data%20Agent%20Checklist.md
