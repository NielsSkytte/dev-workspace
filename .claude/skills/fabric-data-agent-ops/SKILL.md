---
name: fabric-data-agent-ops
bundle: custom
description: >
  How to operate a Microsoft Fabric Data Agent in production: capacity and cost (the token-based
  "AI Query" billing model, monitoring via the Capacity Metrics app, baselines and alerting so
  usage doesn't run away), usage logging (the reality that Fabric has no native prompt log, the
  Microsoft Purview DSPM-for-AI path, and SDK-fronted logging), and lifecycle (CI/CD/ALM
  promotion and keeping the agent in sync with its semantic model so a model change triggers a
  re-test — Git serialization mechanics themselves live in `fabric-data-agent`). Use this skill whenever someone asks how much a Fabric data agent costs, how to see
  what users are asking it, whether usage is logged, how to monitor capacity / set spend alerts,
  how to stop a data agent from blowing the capacity, how to version or deploy a data agent
  through dev/test/prod, or how to keep the agent and model in sync in Git. Trigger on "data
  agent cost / capacity / CU", "how much does the data agent use", "log what users ask the
  agent", "data agent usage / telemetry / monitoring", "Purview data agent", "deploy / promote /
  CI/CD the data agent", "git the data agent", "agent vs model out of sync". Companion to
  `fabric-data-agent` (design/build) and `fabric-data-agent-testing` (evaluation). Use even if
  the user only asks about one piece (e.g. just "can I see the prompts" or "how is it billed").
---

# Operating a Fabric Data Agent in Production

Three operational concerns decide whether a data agent is safe to put in front of real users:
**cost/capacity**, **usage visibility**, and **lifecycle/sync**. Fabric covers the first well,
the second poorly (plan for it), and the third is solid via Git. This skill is the operational
companion to `fabric-data-agent` (build) and `fabric-data-agent-testing` (evaluate).

## 1. Capacity & cost

### How it's billed

Data agent usage is **token-based**, metered as **"AI Query"** at the standard Copilot rates:

| Operation | Unit | Rate |
|---|---|---|
| AI Query — input prompt | per 1,000 tokens | **100 CU-seconds** |
| AI Query — output completion | per 1,000 tokens | **400 CU-seconds** |

Worked example from the docs: 2,000 input + 500 output tokens =
(2,000×100 + 500×400)/1,000 = **400 CU-seconds ≈ 6.67 CU-minutes** — for the LLM portion only.

> **Heads-up — treat that 400 CU as a floor, not a typical cost.** Microsoft support has confirmed the
> docs' figure is "illustrative only." In the field, a single data-agent/Copilot question commonly
> costs **5,000–10,000 CU** — because the real token count includes the semantic-model schema
> grounding, report metadata, and *multiple* internal LLM calls (query generation, then result
> summarization), not just the user's words. One practitioner measured **~5,129 CU even on a
> trivial 3-table/1,000-row model**, and a real report-generation action billed **~$0.57 in ~10
> minutes on an F2**. Cost-model from measured pilot usage, never from the textbook number.
> ([Fabric Community, 2026](https://community.fabric.microsoft.com/t5/Service/High-consumption-rate-of-Copilot-usage-in-Microsoft-Fabric/m-p/5133845);
> [MS Q&A, 2026](https://learn.microsoft.com/en-us/answers/questions/5821847/clarification-on-microsoft-fabric-copilot-charges))

**The query execution is billed separately.** The "AI Query" charge is the LLM call. When the
agent generates and runs a SQL/DAX/KQL query, that execution is billed to the underlying engine
too. So **one user question = two charges**: AI/LLM tokens + the data-engine execution. Budget
for both.

It's classified as a **background job, smoothed over 24h**, so a ~6.67 CU-minute request is
~1 CU-minute/hour. That makes per-request cost look tiny — but at scale, and with the separate
query cost, it adds up, and **when capacity is exhausted, operations shut down.**

> Effective **17 Mar 2026**, new operation entries for Fabric AI functions/AI services started
> appearing in the Capacity Metrics app. The **data agent AI Query rate is unchanged** (still
> 100/400 CU-s per 1k in/out) — this is a metrics-reporting/naming change, not a price change.

### Real total cost of ownership (set CFO expectations early)

The headline "F2, $X/month" badly understates production cost. Grounded numbers from a real
deployment ([Tejwani, 2026](https://pub.towardsai.net/fabric-data-agents-just-hit-ga-94f459c68dcc)):

- **F2 is the minimum to *enable* the feature, rarely the right size to *run* it.** Between
  existing Power BI workload contention and AI headroom, real deployments land at **F4–F8** —
  2–4× the headline.
- **Capacity contention degrades AI quality above ~70% utilization** (inconsistent answers, not a
  "slow" warning), so **size to peak + ~30%** — if F4 covers your average day, run **F8** for
  production reliability.
- Rough annual TCO: **F4 ≈ $10–12k**, **F8 ≈ $20–24k**; **per-user Pro/PPU** for content
  consumers below F64 can add **$10–20k** for a mid-size team (often matching the capacity cost);
  initial configuration is **100–200 hours** of practitioner time. **First-year, production-grade,
  ~50 users: roughly $30–60k** depending on SKU and licensing mix.

### Monitoring & baselines

- Use the **Fabric Capacity Metrics app** — data agent LLM usage appears under operation **AI
  Query** (general Copilot shows as **Copilot in Fabric**); the item kind is **LlmPlugin**.
- **Pilot small and extrapolate — and don't pilot on a small SKU.** Deploying broadly without
  measuring can exhaust capacity fast. Field stories: **~20 questions exhausted an F2** (24h
  throttle), and **~15 concurrent Copilot users overwhelmed an F64 in ~10 minutes** — so sizing
  is driven by *peak concurrency*, not average per-request CU. Run the PoC with a small group,
  read per-activity CU in the Metrics app, then project before opening up.
  ([F2 story](https://community.fabric.microsoft.com/t5/Service/High-consumption-rate-of-Copilot-usage-in-Microsoft-Fabric/m-p/5133845);
  [F64 story](https://community.fabric.microsoft.com/t5/Data-Warehouse/High-Copilot-and-AI-cost/m-p/4881683))
- **Watch for phantom/ambient Copilot CU.** Since the May 2025 expansion, some Copilot features
  are **on by default and consume CU with no intentional use** — notably Warehouse/SQL DB
  auto-complete (a Lakehouse SQL endpoint has *no* item-level toggle; you disable it only
  tenant/capacity-wide). Your baseline includes CU you didn't trigger — know the toggles before
  cost-modeling. ([Fabric Community, 2025](https://community.fabric.microsoft.com/t5/Fabric-platform/Copilot-using-capacity-despite-not-being-active/m-p/4682989))
- **Monitoring infrastructure is non-optional for production** (and is exactly what separates the
  PoCs that work from the prod deployments that struggle): capacity-utilization monitoring, query-
  log review, output-validation routines, and behavior-drift detection (the recurring baseline
  battery in `fabric-data-agent-testing`). A PoC can skip these; production cannot.

### Stopping runaway usage

- There is **no per-agent spend cap or request quota.** Governance is capacity **smoothing +
  progressive throttling** (delays kick in when the capacity has spent its next-10-minutes of CU)
  — a blunt, capacity-wide backstop, not per-agent.
- **Real alerting is custom — working recipe:** in the **Capacity Metrics app**, open a CU visual
  → **More actions → Trigger action** → set the measure + threshold (e.g. AI Query / autoscale CU
  > N) → email/Teams. Two field gotchas: you usually must **request access to the Metrics app's
  semantic model** from a Fabric admin before you can build on it, and the **Activator/reflex item
  itself consumes CU** (your monitor has a cost and shows up in the Metrics app).
- **Cost isolation:** assign a **Fabric Copilot capacity** to absorb all Copilot + Data Agent
  usage for a named user set (intended for sub-F64 users; needs ≥F2/P1; one per user; home-region
  only; not on Embedded). Use it to ring-fence and watch AI spend on a dedicated capacity.
- **"Pause to save money" is a trap.** Smoothing *defers* cost, it never cancels it — **pausing a
  capacity immediately tallies all outstanding smoothed CU and bills it to Azure on the spot**, and
  idle capacities still draw down carry-forward overnight. Don't plan testing around pausing.

## 2. Usage logging — what users actually ask

**The hard truth: Fabric has no native prompt-log dashboard.** There is no built-in report of
the questions users ask, by whom, how often, inside the agent item or the Monitoring Hub.
Conversation history may not even persist across service updates. The agent docs only offer vague
"monitor through available logging/audit capabilities."

What's actually available:

| Need | Reality |
|---|---|
| CU / volume per agent | **Capacity Metrics app** (AI Query / Copilot in Fabric / LlmPlugin) — volume & cost, **not** prompt content |
| The actual prompts & responses, by user, over time | **Microsoft Purview DSPM for AI** (preview) — the only supported way *inside the Fabric/M365 boundary* (see below) |
| Per-call telemetry (latency, status, errors) | **Microsoft Foundry observability** (preview) — if the agent is consumed as a Foundry tool, each call emits telemetry. Not prompt content, but the closest thing to native call-level monitoring. |
| Prompts in Fabric **workspace monitoring** / Eventhouse | **No** — data agents/Copilot are **not** a captured log source there |
| Rich custom prompt analytics, real-time | **Custom** — front the agent via the SDK / MCP server / Copilot Studio / Foundry and log it yourself |

### The supported prompt-logging path: Purview DSPM for AI (preview)

With it enabled, Purview captures, per interaction, the **full prompt text**, the **full response**
(natural-language + generated queries), plus **timestamp, user identity, app** (`Fabric-Data
Agent`). Records are typed **"Copilot Interaction"** in the M365 unified audit log, viewed in
**Purview → DSPM for AI → Activity Explorer**.

Enable all three (it's off by default): (1) activate **Purview Audit** for the tenant; (2) enable
the Purview policy **"DSPM for AI — Capture interactions for Copilot experiences"** (the policy
name says "Copilot experiences" but it covers data agents); (3) in the **Fabric Admin Portal**
turn on **"Allow Microsoft Purview to secure AI interactions."** Caveats: **preview**; it's a
security/compliance surface (Purview), **not** a Fabric analytics dashboard; basic audit is in
M365 E5, some advanced Purview features carry extra licensing.

**Enablement gotcha — two independent pipelines.** Prompts reach Purview Activity Explorer two
different ways: M365 Copilot interactions flow from the **unified audit log regardless of any DSPM
policy**, but **Copilot-in-Fabric and data-agent interactions require an active DSPM collection
policy with "capture content."** Consequences both directions: to *capture* Fabric data-agent
prompts you specifically need the collection policy (audit alone isn't enough); to *fully stop*
capture you must also disable Copilot auditing at tenant level (the policy goes to
"PendingDeletion" for ~1h+, and historical events linger) — people have hit "policies disabled but
still collecting." ([MS Q&A, 2026](https://learn.microsoft.com/en-us/answers/questions/5827720/purview-dpsm-for-ai-collection-policies-disabled-b))
Don't hand-toggle it for a real deployment: Microsoft ships a spec-driven
[Data and Agent Governance and Security Accelerator](https://github.com/microsoft/Data-and-Agent-Governance-and-Security-Accelerator)
that automates DLP, sensitivity labels, audit export, and Defender-for-AI telemetry across M365
Copilot, Foundry, and Fabric from one config (with a troubleshooting guide for missing
interactions).

**Purview now also enforces at query time (not just logs).** Beyond DSPM logging, Purview can
**truncate or block** an agent's response over sensitive data: **DLP policies in Fabric
Warehouse are GA**, and **access-restriction policies for KQL DB, SQL DB, and Warehouse are in
preview**. So a governed agent may legitimately return less than the raw query would — design and
test with these policies on, not off.

### Custom logging (when you need a real usage dashboard)

Front the agent through your own app/orchestrator — the SDK's OpenAI-compatible client
(`FabricOpenAI(artifact_name=...)`), the agent's **MCP server** (preview; consumed via VS Code
Agent Mode today), **Copilot Studio**, or **Microsoft Foundry** — and **log every prompt/response
yourself** into a lakehouse/Eventhouse, then build a Power BI report on it. This is the only way
to get prompt-level analytics inside Fabric today.

- **Auth:** historically runtime querying ran only as a **user identity**. **Service-principal
  auth is now in preview**, but narrowly: it covers exactly **two scenarios — direct calls from
  custom apps, and Foundry agents using the data agent as a knowledge source.** Known gaps
  practitioners hit: **KQL-DB-backed agents are "coming soon" (not yet)**, and client-credentials
  SPN has been reported **unsupported for external REST API integrations**. "SPN is supported"
  ≠ every path works — verify the exact path before promising it.
  ([MS PMs, 2026](https://community.fabric.microsoft.com/t5/Fabric-Updates-Blog/Service-Principal-Support-for-Data-Agents-in-Fabric-Preview/ba-p/5181634))
- **Compliance caveat (MCP):** when consumed via the MCP server, responses may leave Fabric's
  compliance/geo boundary depending on the MCP client's policies. Factor this into any regulated
  deployment.

The two halves of a homegrown observability setup, from practitioners:
- **Prompt side:** wrap the SDK consumption loop — `FabricOpenAI(artifact_name=..., ai_skill_stage=
  "production")` → `threads.create` → `messages.create` → `runs.create` → poll `runs.retrieve` →
  read the assistant message — and persist each prompt+response to a Lakehouse table. (No
  practitioner has published a turnkey prompt-logger, which itself confirms there's no native one.)
  ([Pawar, 2026](https://fabric.guru/programmatically-comparing-draft-vs-production-fabric-data-agent-responses))
- **CU side:** query the **Capacity Metrics semantic model directly from a notebook** (SemPy
  `fabric.evaluate_dax`, filtering `TimePoint`/`CapacitiesList` with `TREATAS`) to attribute CU to
  an operation without the Metrics-app UI. Operational gotcha: **operations take ~6 minutes to
  appear** in the Metrics model, so automation must wait.
  ([bits2BI, 2025](https://bits2bi.com/2025/10/05/tracking-capacity-unit-consumption-for-dax-queries-with-fabric-notebooks/))

> **Time-sensitive — plan for it.** The data agent's programmatic interface still uses the
> **OpenAI Assistants API, which shuts down 26 Aug 2026** (no extensions). Microsoft says it
> "will migrate this programmatic interface to the Responses API in a future update" but has
> **not yet shipped a migration sample**. Existing code keeps working until then. Any PoC that
> promises SDK/MCP/programmatic consumption must budget for this migration — track the updated
> sample and don't hard-bake Assistants-API calls you can't revisit.

## 3. Lifecycle: Git, CI/CD, and model↔agent sync

- The data agent is a **Git-serialized item**; every config change (schema selection, instructions,
  few-shots, publish description) is diffable. Full layout and the as-code SDK/REST/`fab` paths
  are in [`../fabric-data-agent/references/git-and-config-as-code.md`](../fabric-data-agent/references/git-and-config-as-code.md).
- **Keep the agent in sync with its semantic model.** Both are Git items in the same workspace.
  Review them in the **same PR** so a model/Prep-for-AI change and its agent impact are visible
  together. The operating rule:

  > **A change to the semantic model (or its Prep for AI) can silently move the agent's answers.
  > Treat any model change as a trigger to re-run the evaluation harness** (`fabric-data-agent-testing`)
  > **before merge/publish.** Likewise re-test on any agent-config change.

- **Promotion:** use **deployment pipelines** (dev→test→prod) and/or the REST **Import/Export Item
  Definitions Batch APIs**; automate with the **Azure DevOps Pipelines extension for Fabric**
  (runs `fab` CLI tasks).
- **Auth:** service principals have long been supported for **ALM** (Git/deployment automation).
  **Runtime querying** ran as a user identity only — but **SPN runtime auth is now in preview**
  (custom apps / Foundry; KQL "coming soon"). So as-code provisioning/promotion is solid, and
  app-identity invocation is becoming viable; treat the runtime path as preview until GA.

## Quick reference — out of the box vs custom

| Capability | OOB? |
|---|---|
| Cost/volume per agent | **Yes** — Capacity Metrics app |
| Published billing model | **Yes** — token-based AI Query (100/400 CU-s per 1k in/out) |
| See actual prompts & responses by user | **Yes, but** — Purview DSPM for AI only (preview, 3 enablement steps, Purview surface) |
| Prompts in workspace monitoring / Eventhouse | **No** |
| Per-agent rate limit / spend cap | **No** — only capacity smoothing/throttling + Copilot-capacity isolation |
| Spend alert before runaway | **Custom** — Activator on Capacity Metrics |
| Rich prompt/usage dashboard | **Custom** — SDK-fronted invocation + your own logging |
| Versioning / diff / promotion | **Yes** — Git + deployment pipelines + batch import/export |

## Sources

- Data agent consumption (billing): https://learn.microsoft.com/en-us/fabric/fundamentals/data-agent-consumption
- Copilot consumption: https://learn.microsoft.com/en-us/fabric/fundamentals/copilot-fabric-consumption
- Purview governance for data agents: https://learn.microsoft.com/en-us/fabric/data-science/data-agent-purview-governance
- Concept (governance, limitations): https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent
- Workspace monitoring (what it captures): https://learn.microsoft.com/en-us/fabric/fundamentals/workspace-monitoring-overview
- Fabric Copilot capacity: https://learn.microsoft.com/en-us/fabric/enterprise/fabric-copilot-capacity
- Throttling: https://learn.microsoft.com/en-us/fabric/enterprise/throttling
- Source control / CI/CD: https://learn.microsoft.com/en-us/fabric/data-science/data-agent-source-control
- Data agent as MCP server (preview): https://learn.microsoft.com/en-us/fabric/data-science/data-agent-mcp-server
- Foundry Fabric tool (observability, identity passthrough): https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/fabric
- Responses-API migration note (end-to-end tutorial): https://learn.microsoft.com/en-us/fabric/data-science/data-agent-end-to-end-tutorial
- Billing updates — new AI operations (Mar 2026): https://blog.fabric.microsoft.com/en-GB/blog/billing-updates-new-operations-for-fabric-ai-functions-and-ai-services/
- June 2026 feature summary: https://community.fabric.microsoft.com/t5/Fabric-Updates-Blog/Fabric-June-2026-Feature-Summary/ba-p/5190690
