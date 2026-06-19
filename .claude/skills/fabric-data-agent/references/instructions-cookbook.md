# Instructions & example-queries cookbook

Concrete patterns for the agent's authoring surfaces. Reminder of where each applies (see
[`prep-for-ai-vs-agent.md`](prep-for-ai-vs-agent.md)): data-source instructions, descriptions,
and example queries work for **lakehouse / warehouse / KQL / SQL DB only** — for **semantic
models** the equivalents live in Prep for AI on the model, and **ontologies** also don't support
example queries.

> **Tip (preview): the Creator Agent** can auto-draft your agent instructions, data-source
> guidance, and example queries (currently for **SQL and Eventhouse** sources), with iterative
> validation. Treat its output as a strong first draft to refine with the patterns below — not a
> substitute for understanding what belongs where.

## Agent instructions template (≤15,000 chars)

**Write instructions like you're onboarding a new analyst, not writing API docs** — encode the
*business* meaning, not field lists. A practitioner's example that measurably improved output:
*"Revenue means net revenue after returns and discounts, not gross. Returns are in the Returns
table with transaction type 'RT'. Discounts are negative line items in Sales Detail."* That level
of business context is most of the battle — practitioners estimate **~60–70% of answer quality
comes from configuration**, not raw model power ([Tejwani, 2026](https://pub.towardsai.net/fabric-data-agents-just-hit-ga-94f459c68dcc)).

Keep it lean — long instructions add latency and dilute focus. Microsoft's recommended sections:

```markdown
## Objective
You answer questions about <domain> for <audience>. You are read-only and return concise,
conversational insights (max 25 rows).

## Data sources
- <Semantic model name>: financial/aggregated metrics (revenue, margin, KPIs). Prefer for
  "how much / how many / trend" questions.
- <Lakehouse name>: raw transactional detail. Prefer for row-level lookups.
- <KQL DB name>: event/telemetry/time-series. Prefer for "when / how often / by minute".

## Key terminology
- "GMV" = Gross Merchandise Value.
- "active customer" = ordered in the last 90 days.
- Fiscal year starts 1 July.

## Response guidelines
- Lead with the number, then a one-line explanation.
- Show currency with the ISO code. Use the user's date format (DD-MM-YYYY).
- If a question is ambiguous, ask one clarifying question before querying.

## Handling common topics
- "sales" means Net Sales (the Net Sales measure), never Gross Sales.
- Always exclude test accounts (CustomerType = 'TEST').
```

The **Data sources** and **Key terminology** sections are doing the heavy lifting: routing and
cross-cutting glossary. Everything here is global — source-specific guidance goes below.

## Data-source instructions template (lakehouse/warehouse/KQL)

```markdown
## General knowledge
This source holds <what>. Granularity is <grain>. Time zone is UTC.

## Table descriptions
- dbo.factsales: one row per order line. Join to dbo.dimdate on DateKey.
- dbo.dimcustomer: customer master. Filter test accounts with CustomerType <> 'TEST'.

## When asked about...
- "revenue": SUM(factsales.NetAmount). Revenue is net of returns (ReturnFlag = 0).
- "region": use dimcustomer.Region, values are two-letter codes ('NA','EU','APAC').
```

## "Leading words" — nudging query shape

The generator can't see row values before querying, so spell out value formats and seed query
fragments. Embedding small SQL/DAX/KQL fragments in data-source instructions steers the output:

- "When filtering products by name, use `WHERE ProductName LIKE '%<term>%'` (names are free-text)."
- "State is stored as the two-letter code (`'CA'`), not the full name (`'California'`)."
- "Status values are exactly: `'Open'`, `'Closed'`, `'Pending'` (case-sensitive)."

This is the single highest-leverage technique for getting correct filters, because the model
otherwise guesses at value formats.

**Encode relationships the agent keeps misreading.** When the generator can't infer a business
relationship from the schema, state it as a plain rule. Chris Webb fixed an agent that kept
misjudging "which customers bought a product" with one line: *"You can tell a customer has bought
a product when the Count of Sales measure is greater than 0."*
([Webb, 2025](https://blog.crossjoin.co.uk/2025/04/06/fabric-data-agents-unlocking-the-full-power-of-dax-for-data-analysis/))

**Why this matters (war story):** consuming an agent as a function, Sandeep Pawar saw NL2SQL
*invent* a merged `FullName` concept from `FirstName`+`LastName` and return **dates as strings** —
only fixed by adding value/format context and several SQL few-shots. Two takeaways: spell out
value formats and identity columns, and **validate types downstream** — don't assume the agent
returns clean typed values. ([Pawar, 2024](https://fabric.guru/quick-test-fabric-ai-skills-as-a-function))

## Example queries (few-shot) — lakehouse/warehouse/KQL only

Up to 100 per source; the agent retrieves the top ~3–4 by vector similarity per question and
injects them. So **distinct coverage** beats volume — don't add 30 variations of one pattern.

```text
Q: What was total net revenue for product 'Alpha' in Q1 2024?
A: SELECT SUM(NetAmount) FROM dbo.factsales s
   JOIN dbo.dimproduct p ON s.ProductKey = p.ProductKey
   JOIN dbo.dimdate d ON s.DateKey = d.DateKey
   WHERE p.ProductName = 'Alpha' AND d.FiscalYear = 2024 AND d.FiscalQuarter = 1
     AND s.ReturnFlag = 0;
```

Guidance:
- One clear question → one correct query. Add a `-- comment` explaining any non-obvious join.
- Demonstrate the **hard** patterns (multi-table joins, window functions, fiscal calendars), not
  the trivial ones the model already gets right.
- Validate them with the few-shot validator (`evaluate_few_shots`, SQL-only today) to catch
  conflicting or low-quality pairs before they degrade generation — see `fabric-data-agent-testing`.

## Grounding on a business glossary / reference material

Unstructured docs (.pdf/.docx/.txt) are **not** supported. Three patterns:

1. **Small, cross-cutting** terms/acronyms → agent instructions "Key terminology". For a
   semantic model, put them in **Prep for AI → AI instructions** instead.
2. **A real glossary to query** → materialize as a table, e.g.
   `BusinessGlossary(term STRING, definition STRING, owner STRING)` in a lakehouse/warehouse,
   select it, and add a data-source instruction: *"For questions about what a term means, query
   BusinessGlossary by term."*
3. **Large doc corpora / true RAG** → out of scope for the data agent; offload to **Foundry IQ**
   or **Copilot Studio** and keep the Fabric agent as the structured-data tool in a multi-agent
   setup.

## Anti-patterns

- Putting semantic-model query guidance in agent instructions (the DAX tool ignores it).
- One big general-purpose agent over 5 sprawling sources — split into specialized agents.
- Telling the agent only what *not* to do; be explicit about what *to* do.
- Treating example-query count as the goal — coverage and correctness matter, not volume.

## Sources

- Configurations & templates: https://learn.microsoft.com/en-us/fabric/data-science/data-agent-configurations
- Best practices (leading words, ≤25 tables, where to place definitions): https://learn.microsoft.com/en-us/fabric/data-science/data-agent-configuration-best-practices
- Example queries: https://learn.microsoft.com/en-us/fabric/data-science/data-agent-example-queries
