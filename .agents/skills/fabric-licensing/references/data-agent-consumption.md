> Reference within the `fabric-licensing` skill: how a Fabric DATA AGENT specifically is consumed and metered (Teams, M365 Copilot vs Copilot Credits, publishing, residency, tenant gates). The broad Fabric capacity and per-user picture is in the parent `SKILL.md`; the CU / AI-Query compute monitoring lives in `fabric-data-agent-ops`.

# Licensing and consuming a Fabric data agent

This skill answers the money-and-access question: **once the agent is built, who needs which
licence to use it, where can it be consumed, and what gates that.** It is the licensing companion
to `fabric-data-agent` (design and build) and `fabric-data-agent-ops` (run it in production).

## Scope boundary (read this first)

This skill owns **seat and consumption licensing, publishing surfaces, data residency, and tenant
prerequisites.** It does not own the **CU / AI-Query compute cost model** (how many capacity units
a query burns, the 100/400 CU-second token rates, monitoring, baselines, runaway alerting). That
lives in `fabric-data-agent-ops`. When a question is "how much capacity does a query cost / how is
it metered in CU / how do I stop it blowing the capacity", route to `fabric-data-agent-ops` and do
not restate the numbers here.

The split in one line: **`fabric-data-agent-ops` = what the COMPUTE costs in CU; this skill = what
the SEAT and the CONSUMPTION SURFACE cost in licences and credits.**

## The licensing decision in one view

A data agent has two cost surfaces, billed independently:

1. **The Fabric capacity** that runs the agent and its AI queries. Always required. The CU
   mechanics are `fabric-data-agent-ops`; the seat rules around it are below.
2. **The consumption surface** the user reaches the agent through: the in-Fabric chat pane, a
   Power BI client, Teams / M365 Copilot, or a Copilot Studio agent. Each carries its own licence
   and, for the metered Teams path, its own currency (Copilot Credits).

## 1. Capacity to enable the agent

The agent needs a **paid F2 or higher Fabric capacity, or a Power BI Premium per capacity (P1 or
higher) with Microsoft Fabric enabled.** ([concept-data-agent](https://learn.microsoft.com/fabric/data-science/concept-data-agent#prerequisites), verified 2026-06-24)
Same prerequisite on the create page. ([how-to-create-data-agent](https://learn.microsoft.com/fabric/data-science/how-to-create-data-agent), verified 2026-06-24)

F2 is the floor to *turn the feature on*, not a sizing recommendation. Production sizing (F4+ for
Pingala, driven by measured CU) is an ops decision, covered in `fabric-data-agent-ops`.

A P SKU has Fabric items **disabled until an admin enables Fabric** via the Fabric switch, which is
why P1+ carries the "Microsoft Fabric enabled" clause. ([licenses](https://learn.microsoft.com/fabric/enterprise/licenses), verified 2026-06-24)
For translating between SKUs, **F64 equals P1** (8 v-cores). ([licenses](https://learn.microsoft.com/fabric/enterprise/licenses), verified 2026-06-24)

## 2. Power BI per-user licensing (the F64 threshold)

This rule governs **who can view Power BI content** under the capacity. It does not gate *building*
the agent (that is F2+/P1+), and querying a Power BI semantic-model source through the agent needs
only **Read** on the model (see RLS/CLS below). But if the agent's answers surface Power BI content
to users, the per-user rule applies:

- **Below F64:** every user viewing Power BI content needs **Pro, PPU, or an individual trial.**
  ([licenses](https://learn.microsoft.com/fabric/enterprise/licenses), verified 2026-06-24)
- **F64 or larger:** a **Free** licence with a viewer role can view Power BI content.
  ([licenses](https://learn.microsoft.com/fabric/enterprise/licenses), verified 2026-06-24)
- **PPU does not provision a Fabric capacity** and cannot, on its own, run non-Power BI Fabric
  items, so PPU alone will not enable a data agent. ([licenses](https://learn.microsoft.com/fabric/enterprise/licenses), verified 2026-06-24)
- Every org using Power BI within Fabric needs **at least one Pro or PPU user.** ([licenses](https://learn.microsoft.com/fabric/enterprise/licenses), verified 2026-06-24)

The F64 threshold is the single biggest lever on per-seat cost for a mid-size team: below it, every
viewer is a paid Pro/PPU seat; at or above it, viewers can be Free. See the SKU/threshold table in
[`data-agent-licensing-tables.md`](data-agent-licensing-tables.md).

## 3. Consuming in Teams / M365 Copilot (PREVIEW)

> Consuming a Fabric data agent inside Microsoft 365 Copilot / Teams is **in preview.** ([data-agent-microsoft-365-copilot](https://learn.microsoft.com/fabric/data-science/data-agent-microsoft-365-copilot), verified 2026-06-24)

This is the path with the most licensing nuance, because the agent is **grounded in tenant data**,
which is exactly the thing that triggers metering for users who do not hold a full Copilot licence.
There are **two licensing models**:

**Model A - the user holds Microsoft 365 Copilot.** A Microsoft 365 Copilot licence (or an Office
365 commercial subscription) plus a user licence per individual using the agent in M365 Copilot.
([data-agent-microsoft-365-copilot](https://learn.microsoft.com/fabric/data-science/data-agent-microsoft-365-copilot), verified 2026-06-24)
That licence already **enables usage of agents grounded in tenant data** (SharePoint, Microsoft
Graph) and is required for authoring agents in Copilot Studio. ([extensibility/prerequisites](https://learn.microsoft.com/microsoft-365/copilot/extensibility/prerequisites), verified 2026-06-24)
Using agents in Copilot Chat, Teams, or SharePoint for tenant grounding under this licence is
**zero-rated** - it does not draw on the meter or a message pack. ([billing-licensing](https://learn.microsoft.com/microsoft-copilot-studio/billing-licensing), verified 2026-06-24)
For these users, **consuming the agent is included; nothing extra to buy or meter.**

**Model B - the user does not hold a full Copilot licence (pay-as-you-go).** Such users can still
reach the agent through **Copilot Chat**, but **usage billing applies specifically to agents
grounded in tenant data**; agents grounded in public data or instructions are free. ([extensibility/prerequisites](https://learn.microsoft.com/microsoft-365/copilot/extensibility/prerequisites), verified 2026-06-24)
Because a Fabric data agent is grounded in tenant data, **its use by a non-Copilot user is metered.**
Consumption is measured in **Copilot Credits**, and the pay-as-you-go path **requires an Azure
subscription and a billing policy** set up in the Microsoft 365 admin center. ([extensibility/prerequisites](https://learn.microsoft.com/microsoft-365/copilot/extensibility/prerequisites), verified 2026-06-24)
Copilot Credits are the common currency across Copilot Studio capabilities, available through
**pay-as-you-go meters, prepurchase plans, and prepaid Copilot Credit pack subscriptions.** ([billing-licensing](https://learn.microsoft.com/microsoft-copilot-studio/billing-licensing), verified 2026-06-24)
A prepaid capacity pack is **25,000 credits per month per pack**, used first, with overflow billed
at the pay-as-you-go rate; unused credits **do not carry over.** ([copilot-capacity-packs](https://learn.microsoft.com/microsoft-365/copilot/pay-as-you-go/copilot-capacity-packs), verified 2026-06-24; [billing-licensing](https://learn.microsoft.com/microsoft-copilot-studio/billing-licensing), verified 2026-06-24)

**The metered rate that is published:** the Copilot Studio pay-as-you-go meter is billed at
**$0.01 per Copilot Credit.** ([pay-as-you-go-meters](https://learn.microsoft.com/power-platform/admin/pay-as-you-go-meters#how-do-meters-work), verified 2026-06-24)
**What is NOT published:** how many credits a given agent response costs (it depends on task
complexity), and the dollar list price of a named prepaid pack or prepurchase tier (the docs defer
to external licensing guides). Do not invent these. See "What is and is not priced" in
[`data-agent-licensing-tables.md`](data-agent-licensing-tables.md).

**Forecasting credit volume:** Microsoft publishes the **Copilot Studio agent usage estimator** to
forecast an agent's Copilot Credit volume by agent type, traffic, orchestration, knowledge, and
tools. Tool: `https://microsoft.github.io/copilot-studio-estimator/` ([billing-licensing](https://learn.microsoft.com/microsoft-copilot-studio/billing-licensing) / [agent-usage-estimator](https://learn.microsoft.com/microsoft-copilot-studio/agent-usage-estimator), verified 2026-06-24)
Because the per-response credit count is variable, the estimator is the right way to size Model B,
not a back-of-envelope token calculation.

Other Teams/M365 prerequisites: enable **cross-geo processing and cross-geo storing for AI** (see
tenant settings below); at least one supported data source (warehouse, lakehouse, Power BI semantic
model, KQL database, mirrored database, or ontology) with read access; the data agent and M365
Copilot on the **same tenant**, signed in with the **same account.** ([data-agent-microsoft-365-copilot](https://learn.microsoft.com/fabric/data-science/data-agent-microsoft-365-copilot), verified 2026-06-24)

## 4. Publishing surfaces

There are two validated routes to put the agent in front of users outside the Fabric chat pane.

**Publish to Agent Store (M365 Copilot).** As part of publishing, you can make the agent available
to the M365 Copilot **Agent Store** by selecting **Publish to Agent Store**; once published it
appears in the store and users interact with it directly from Teams. ([data-agent-microsoft-365-copilot](https://learn.microsoft.com/fabric/data-science/data-agent-microsoft-365-copilot), verified 2026-06-24)
If agents do not appear, the **M365 admin must confirm Copilot extensibility is enabled** for the
account. ([data-agent-microsoft-365-copilot](https://learn.microsoft.com/fabric/data-science/data-agent-microsoft-365-copilot), verified 2026-06-24)

**Copilot Studio (connected agent).** The Fabric data agent is added to a custom Copilot Studio AI
agent as a **connected agent** (agent-to-agent collaboration); generative AI orchestration must be
enabled. ([data-agent-microsoft-copilot-studio](https://learn.microsoft.com/fabric/data-science/data-agent-microsoft-copilot-studio), verified 2026-06-24)
This path is **preview**, and the channel matters: a custom agent with a connected Fabric data agent
**is not currently supported in M365 Copilot and is only validated for Microsoft Teams** (other
channels may work but are not formally tested). ([data-agent-microsoft-copilot-studio](https://learn.microsoft.com/fabric/data-science/data-agent-microsoft-copilot-studio), verified 2026-06-24)
Authoring custom agents in Copilot Studio needs a **Microsoft 365 Copilot licence** per builder.
([data-agent-microsoft-copilot-studio](https://learn.microsoft.com/fabric/data-science/data-agent-microsoft-copilot-studio), verified 2026-06-24)
The agent must be **published with a rich description**, both items on the **same tenant**, signed
in with the **same account** that has access; you set the connected agent's authentication to
**User authentication** or **Agent author authentication.** ([data-agent-microsoft-copilot-studio](https://learn.microsoft.com/fabric/data-science/data-agent-microsoft-copilot-studio), verified 2026-06-24)

So today **Teams is the only validated end-user channel** for a published data agent, whether via
the Agent Store or via Copilot Studio. See the publishing-surface table in
[`data-agent-licensing-tables.md`](data-agent-licensing-tables.md).

## 5. Tenant settings (the gate)

Three tenant settings must be on (Admin Portal -> Tenant settings; changes can take up to an hour):

1. **Users can use Copilot and other features powered by Azure OpenAI** - the Copilot / Azure
   OpenAI switch that enables Copilot-powered features including the data agent. ([data-agent-tenant-settings](https://learn.microsoft.com/fabric/data-science/data-agent-tenant-settings), verified 2026-06-24)
2. **Cross-geo processing for AI** - required when the capacity's region is outside the EU data
   boundary and the US. ([data-agent-tenant-settings](https://learn.microsoft.com/fabric/data-science/data-agent-tenant-settings), verified 2026-06-24)
3. **Cross-geo storing for AI** - same condition, for storage. ([data-agent-tenant-settings](https://learn.microsoft.com/fabric/data-science/data-agent-tenant-settings), verified 2026-06-24)

An optional fourth setting stores **conversation history** outside the region (up to 28 days),
needed only for fully conversational/agentic experiences. ([data-agent-tenant-settings](https://learn.microsoft.com/fabric/data-science/data-agent-tenant-settings), verified 2026-06-24)
The data-agent prerequisite pages name settings 2 and 3 collectively as "enable cross-geo
processing and cross-geo storing for AI." ([concept-data-agent](https://learn.microsoft.com/fabric/data-science/concept-data-agent#prerequisites), verified 2026-06-24)

## 6. Data residency

When the agent is consumed inside Microsoft 365 or Copilot Studio, **responses may leave Fabric's
compliance boundary or geographic region** and be processed or stored under the consuming product's
terms.

- M365 Copilot / Teams: responses "may be sent outside of Fabric's compliance boundary or
  geographic region, and processed and/or stored according to the Microsoft 365's terms." ([data-agent-microsoft-365-copilot](https://learn.microsoft.com/fabric/data-science/data-agent-microsoft-365-copilot), verified 2026-06-24)
- Copilot Studio: the same caveat under "the Microsoft Copilot Studio's applicable terms." ([data-agent-microsoft-copilot-studio](https://learn.microsoft.com/fabric/data-science/data-agent-microsoft-copilot-studio), verified 2026-06-24)
- Cross-geo processing lets data be processed in a region where Azure OpenAI is available, possibly
  outside the user's region, compliance boundary, or national cloud. ([data-agent-consumption](https://learn.microsoft.com/fabric/fundamentals/data-agent-consumption#region-mapping), verified 2026-06-24)

The practical point for an EU customer: the **Fabric source data does not move**, but the **Copilot
conversation** (the question and the answer) may leave the region. That is a customer compliance
sign-off, not a Pingala decision.

## 7. Security at query time (RLS / CLS)

Licensing grants access to the surface; **RLS and CLS still decide what each user sees.** The agent
runs under the **requesting user's credentials** for least-privilege, read-only access, and honours
all permissions including Row-Level and Column-Level Security. ([concept-data-agent](https://learn.microsoft.com/fabric/data-science/concept-data-agent), verified 2026-06-24)
For a Power BI semantic-model source, the user needs only **Read** on the model (no workspace
access), and RLS/CLS continue to apply. ([data-agent-sharing](https://learn.microsoft.com/fabric/data-science/data-agent-sharing#sharing-permission-models-and-required-source-access), verified 2026-06-24)
When you share the agent, recipients must have access **both to the agent and to the underlying
data sources.** ([data-agent-microsoft-365-copilot](https://learn.microsoft.com/fabric/data-science/data-agent-microsoft-365-copilot), verified 2026-06-24)
This means a licence alone never over-shares: two users on identical licences can get different
answers because RLS/CLS filter to each identity.

## Offer translation layer

When these facts go into a customer offer, the **stance and structure are governed by
`pingala-offer`** and the **voice by `writing-voice`**. Defer to them; this section only maps which
facts surface and which stay internal.

**Surfaces in the offer** (advisor-led, one committed spec, no mechanics):

- The **single capacity spec** Pingala commits to (state "F4", not "F2 minimum, sized later"; F2 is
  the enable floor, the production size is an ops call).
- The **per-user licence position**: Pro/PPU below F64, Free viewers at F64+, stated as the plan for
  this customer, not as a menu.
- **Consuming in Teams** as one line per licensing model: M365 Copilot holders are included;
  everyone else is metered to the customer in Copilot Credits. Pingala sizes the metered usage with
  the estimator; the customer is not handed the choice.
- **Data residency** as a named compliance sign-off (the one legitimate customer decision): the
  Copilot conversation may leave the region; the source data does not. This is the single exception
  where the customer legally must decide.
- **Tenant settings** named as a prerequisite the customer satisfies, not explained switch by switch.

**Stays internal / in a technical note** (not in the offer):

- The CU / AI-Query compute mechanics and token rates (`fabric-data-agent-ops`).
- Billing internals: pay-as-you-go vs prepaid pack mechanics, the $0.01 per-credit rate, the 25,000
  credit pack size, the Azure billing-policy setup steps.
- Admin-portal steps, RLS/CLS query-time mechanics, the Agent Store vs Copilot Studio publish flow,
  SDK/DAX detail.

For the worked, advisor-led "Licensing & consumption" offer section that `pingala-offer` can reuse,
see [`data-agent-licensing-tables.md`](data-agent-licensing-tables.md). Run the `pingala-offer`
self-check (zero question marks, no decisions handed over, no build mechanics) before any offer
ships.

**This skill replaces the licensing facts** previously single-sourced in
`writing-voice/references/business-offers.md`. That file keeps its before/after licensing passage
as a **voice demonstration only** and points here for the facts. If the facts and that demo ever
disagree, **this skill is authoritative.**

## Re-verify

These facts decay. Two of the consumption surfaces (Teams/M365 Copilot and Copilot Studio) are
**preview**, the Copilot Credit currency changed on 1 September 2025, and the F64 threshold and
$0.01 rate are dated list facts. **Re-verify against MS Learn before any priced commitment, and at
least quarterly.** When you re-verify, update the "(verified YYYY-MM-DD)" stamps inline and the
citation list in [`data-agent-licensing-tables.md`](data-agent-licensing-tables.md).

Highest-decay items to check first: preview status of the two Teams paths, the per-credit list
price, the prepaid pack credit count, and the F2/F64 thresholds.

> **Licensing facts verified against MS Learn on 2026-06-24.**
