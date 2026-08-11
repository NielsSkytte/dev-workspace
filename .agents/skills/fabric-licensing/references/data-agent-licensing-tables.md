# Licensing tables and citations - Fabric data agent

The detail layer for `fabric-licensing`. Every figure here is grounded in MS Learn.
Where the docs do not state a number, this file says so rather than inventing one.

> Licensing facts verified against MS Learn on 2026-06-24. Re-verify before any priced commitment
> and at least quarterly (preview surfaces and dated list facts decay).

---

## 1. SKU and threshold table

| Item | Value | Source (verified 2026-06-24) |
|---|---|---|
| Minimum capacity to ENABLE a data agent | Paid **F2 or higher**, or **P1+** Power BI Premium per capacity with Microsoft Fabric enabled | [concept-data-agent#prerequisites](https://learn.microsoft.com/fabric/data-science/concept-data-agent#prerequisites) |
| Same prerequisite on the create page | F2+/P1+ | [how-to-create-data-agent](https://learn.microsoft.com/fabric/data-science/how-to-create-data-agent) |
| Data agent supported on F and P SKUs | F SKU yes, P SKU yes (not on trial capacity unless stated) | [fabric-features](https://learn.microsoft.com/fabric/enterprise/fabric-features) |
| Why P1+ needs "Fabric enabled" | P SKU has Fabric items disabled until an admin enables the Fabric switch | [licenses](https://learn.microsoft.com/fabric/enterprise/licenses) |
| SKU equivalence | **F64 = P1** (8 v-cores) | [licenses](https://learn.microsoft.com/fabric/enterprise/licenses) |
| Power BI viewing **below F64** | Each viewer needs **Pro, PPU, or individual trial** | [licenses](https://learn.microsoft.com/fabric/enterprise/licenses) |
| Power BI viewing **at F64+** | **Free** licence + viewer role can view | [licenses](https://learn.microsoft.com/fabric/enterprise/licenses) |
| PPU and Fabric capacity | PPU does **not** provision a Fabric capacity; cannot run non-Power BI Fabric items alone (so PPU alone will not enable a data agent) | [licenses](https://learn.microsoft.com/fabric/enterprise/licenses) |
| Minimum org licence for Power BI in Fabric | At least one **Pro or PPU** user | [licenses](https://learn.microsoft.com/fabric/enterprise/licenses) |
| Querying a Power BI semantic-model source via the agent | **Read** on the model (Build not required, no workspace access) | [data-agent-sharing](https://learn.microsoft.com/fabric/data-science/data-agent-sharing#sharing-permission-models-and-required-source-access) |

The **CU / AI-Query compute cost** (100 CU-s per 1,000 input tokens, 400 per 1,000 output) is NOT
in this skill. It lives in `fabric-data-agent-ops`. Do not restate it here.

---

## 2. Two licensing models for Teams / M365 Copilot consumption (PREVIEW)

Consumption in Teams / M365 Copilot is **preview**. ([data-agent-microsoft-365-copilot](https://learn.microsoft.com/fabric/data-science/data-agent-microsoft-365-copilot), verified 2026-06-24)
The agent is grounded in tenant data, which is the trigger that meters non-Copilot users.

| | Model A - user holds M365 Copilot | Model B - no full Copilot licence (pay-as-you-go) |
|---|---|---|
| Licence | M365 Copilot licence (or O365 commercial) + a user licence per individual | No full Copilot licence; reaches the agent via **Copilot Chat** |
| Reaches an agent grounded in tenant data? | Yes, included by the licence | Yes, but **metered** because the agent is grounded in tenant data |
| Cost of using this agent | **Zero-rated** - does not draw the meter or a message pack | **Metered in Copilot Credits** (pay-as-you-go), billed to an Azure subscription via a billing policy; or prepaid Copilot Credit packs |
| Setup needed | Already in place via the Copilot licence | **Azure subscription + billing policy** in the M365 admin center |
| Source (verified 2026-06-24) | [extensibility/prerequisites](https://learn.microsoft.com/microsoft-365/copilot/extensibility/prerequisites); [billing-licensing](https://learn.microsoft.com/microsoft-copilot-studio/billing-licensing) | [extensibility/prerequisites](https://learn.microsoft.com/microsoft-365/copilot/extensibility/prerequisites); [billing-licensing](https://learn.microsoft.com/microsoft-copilot-studio/billing-licensing) |

Copilot Credit currency and packs (Model B detail):

| Fact | Value | Source (verified 2026-06-24) |
|---|---|---|
| Common currency | **Copilot Credits**, via pay-as-you-go meters, prepurchase plans, and prepaid Copilot Credit pack subscriptions | [billing-licensing](https://learn.microsoft.com/microsoft-copilot-studio/billing-licensing) |
| Currency change | From **1 Sep 2025** the currency for agents changed from messages to Copilot Credits (no change to pack quantity or PAYG rate) | [billing-licensing](https://learn.microsoft.com/microsoft-copilot-studio/billing-licensing) |
| Per-credit list price | **$0.01 per Copilot Credit** | [pay-as-you-go-meters#how-do-meters-work](https://learn.microsoft.com/power-platform/admin/pay-as-you-go-meters#how-do-meters-work); confirmed in [copilot-credit-p3](https://learn.microsoft.com/azure/cost-management-billing/reservations/copilot-credit-p3#determine-the-right-size-to-buy) |
| Prepaid capacity pack size | **25,000 credits per month per pack**, used first, no carryover | [copilot-capacity-packs](https://learn.microsoft.com/microsoft-365/copilot/pay-as-you-go/copilot-capacity-packs); [billing-licensing](https://learn.microsoft.com/microsoft-copilot-studio/billing-licensing) |
| Overflow past the pack | Billed at the per-credit PAYG rate | [copilot-capacity-packs](https://learn.microsoft.com/microsoft-365/copilot/pay-as-you-go/copilot-capacity-packs) |
| Credits per response | **Variable - depends on task complexity** (use the estimator) | [billing-licensing](https://learn.microsoft.com/microsoft-copilot-studio/billing-licensing); [requirements-messages-management](https://learn.microsoft.com/microsoft-copilot-studio/requirements-messages-management) |
| Usage estimator tool | `https://microsoft.github.io/copilot-studio-estimator/` | [billing-licensing](https://learn.microsoft.com/microsoft-copilot-studio/billing-licensing); [agent-usage-estimator](https://learn.microsoft.com/microsoft-copilot-studio/agent-usage-estimator) |
| PAYG billing-policy setup | M365 admin center -> Copilot -> Billing & usage: add policy (name, Azure subscription, resource group, region), accept terms, optional users/budget, create | [pay-as-you-go-setup-copilot](https://learn.microsoft.com/microsoft-365/commerce/services/pay-as-you-go-setup-copilot) |

---

## 3. Publishing surfaces

| Surface | Status | Channel validated for end users | Key licence / gate | Source (verified 2026-06-24) |
|---|---|---|---|---|
| **Publish to Agent Store** (M365 Copilot) | Available; appears in store, used from Teams | **Teams** | M365 admin must confirm **Copilot extensibility** enabled | [data-agent-microsoft-365-copilot](https://learn.microsoft.com/fabric/data-science/data-agent-microsoft-365-copilot) |
| **Copilot Studio** (connected agent) | **Preview** | **Microsoft Teams only** (not M365 Copilot; other channels untested) | **M365 Copilot licence** per builder; generative AI orchestration on; agent published with a rich description | [data-agent-microsoft-copilot-studio](https://learn.microsoft.com/fabric/data-science/data-agent-microsoft-copilot-studio) |
| **In-Fabric chat pane** | GA | In Fabric | Fabric access + source Read access | [concept-data-agent](https://learn.microsoft.com/fabric/data-science/concept-data-agent) |

Shared prerequisites for both Teams paths: same tenant + same account; cross-geo processing and
storing for AI enabled; at least one supported source (warehouse, lakehouse, Power BI semantic
model, KQL database, mirrored database, ontology) with read access; recipients of a shared agent
need access to **both** the agent and the underlying data sources. ([data-agent-microsoft-365-copilot](https://learn.microsoft.com/fabric/data-science/data-agent-microsoft-365-copilot); [data-agent-microsoft-copilot-studio](https://learn.microsoft.com/fabric/data-science/data-agent-microsoft-copilot-studio), verified 2026-06-24)

In Copilot Studio you set the connected agent's auth to **User authentication** (users must have
access to the agent and its sources) or **Agent author authentication.** ([data-agent-microsoft-copilot-studio](https://learn.microsoft.com/fabric/data-science/data-agent-microsoft-copilot-studio), verified 2026-06-24)

---

## 4. Tenant settings and data residency

| Setting | Required when | Source (verified 2026-06-24) |
|---|---|---|
| Users can use Copilot and other features powered by Azure OpenAI | Always (enables the data agent feature) | [data-agent-tenant-settings](https://learn.microsoft.com/fabric/data-science/data-agent-tenant-settings) |
| Cross-geo **processing** for AI | Capacity region outside the EU data boundary and the US | [data-agent-tenant-settings](https://learn.microsoft.com/fabric/data-science/data-agent-tenant-settings) |
| Cross-geo **storing** for AI | Same condition, for storage | [data-agent-tenant-settings](https://learn.microsoft.com/fabric/data-science/data-agent-tenant-settings) |
| Conversation history stored cross-geo (optional) | Only for fully conversational/agentic use (history up to 28 days) | [data-agent-tenant-settings](https://learn.microsoft.com/fabric/data-science/data-agent-tenant-settings) |

Data residency: when consumed in M365 / Copilot Studio, responses may leave Fabric's compliance
boundary or region and be processed/stored under the consuming product's terms; cross-geo
processing may place data in any region where Azure OpenAI is available. ([data-agent-microsoft-365-copilot](https://learn.microsoft.com/fabric/data-science/data-agent-microsoft-365-copilot); [data-agent-microsoft-copilot-studio](https://learn.microsoft.com/fabric/data-science/data-agent-microsoft-copilot-studio); [data-agent-consumption#region-mapping](https://learn.microsoft.com/fabric/fundamentals/data-agent-consumption#region-mapping), verified 2026-06-24)
RLS/CLS apply at query time under the requesting user's identity; a Power BI model source needs only
Read. ([concept-data-agent](https://learn.microsoft.com/fabric/data-science/concept-data-agent); [data-agent-sharing](https://learn.microsoft.com/fabric/data-science/data-agent-sharing#sharing-permission-models-and-required-source-access), verified 2026-06-24)

---

## 5. What is and is NOT priced

**Priced (explicit list value on MS Learn):**

- Copilot Studio pay-as-you-go meter = **$0.01 per Copilot Credit.** ([pay-as-you-go-meters#how-do-meters-work](https://learn.microsoft.com/power-platform/admin/pay-as-you-go-meters#how-do-meters-work), verified 2026-06-24)
- Prepaid capacity pack = **25,000 credits per month per pack** (a count, not a dollar price). ([copilot-capacity-packs](https://learn.microsoft.com/microsoft-365/copilot/pay-as-you-go/copilot-capacity-packs), verified 2026-06-24)
- In-Fabric CU rate (100/400 CU-s per 1k in/out tokens) is priced too, but **owned by `fabric-data-agent-ops`**, not restated here.

**NOT priced in these docs (do not invent):**

- The **dollar price of a Copilot Studio prepaid pack or prepurchase tier.** The billing-licensing
  page defers to external guides (Copilot Studio Licensing Guide, Copilot Credit Guide); any tier
  dollar figure in the docs is an illustrative example, not a list price. ([copilot-credit-p3#determine-the-right-size-to-buy](https://learn.microsoft.com/azure/cost-management-billing/reservations/copilot-credit-p3#determine-the-right-size-to-buy), verified 2026-06-24)
- **How many Copilot Credits a given agent response costs** - explicitly variable; this is what the
  estimator forecasts. ([requirements-messages-management](https://learn.microsoft.com/microsoft-copilot-studio/requirements-messages-management), verified 2026-06-24)

**UNVERIFIED (could not be confirmed on MS Learn):**

- Any specific dollar list price for a named Copilot Studio prepaid pack tier or the standalone
  Copilot Studio subscription SKU. The pages point to fwlink licensing/credit PDFs, not a learn.microsoft.com
  price, so none is asserted.

---

## 6. Full citation list (grouped by topic)

**Capacity / per-user / SKU**
- https://learn.microsoft.com/fabric/data-science/concept-data-agent
- https://learn.microsoft.com/fabric/data-science/how-to-create-data-agent
- https://learn.microsoft.com/fabric/enterprise/licenses
- https://learn.microsoft.com/fabric/enterprise/fabric-features

**Tenant settings / data residency / security**
- https://learn.microsoft.com/fabric/data-science/data-agent-tenant-settings
- https://learn.microsoft.com/fabric/fundamentals/data-agent-consumption
- https://learn.microsoft.com/fabric/data-science/data-agent-sharing
- https://learn.microsoft.com/fabric/security/security-overview
- https://learn.microsoft.com/fabric/iq/plan/planning-concept-row-level-security

**Consuming in Teams / M365 Copilot (preview)**
- https://learn.microsoft.com/fabric/data-science/data-agent-microsoft-365-copilot

**Publishing via Copilot Studio (preview)**
- https://learn.microsoft.com/fabric/data-science/data-agent-microsoft-copilot-studio

**Copilot Credits / billing / estimator**
- https://learn.microsoft.com/microsoft-365/copilot/extensibility/prerequisites
- https://learn.microsoft.com/microsoft-copilot-studio/billing-licensing
- https://learn.microsoft.com/microsoft-copilot-studio/agent-usage-estimator
- https://learn.microsoft.com/microsoft-copilot-studio/requirements-messages-management
- https://learn.microsoft.com/microsoft-365/commerce/services/pay-as-you-go-setup-copilot
- https://learn.microsoft.com/microsoft-365/copilot/pay-as-you-go/copilot-capacity-packs
- https://learn.microsoft.com/power-platform/admin/pay-as-you-go-meters
- https://learn.microsoft.com/azure/cost-management-billing/reservations/copilot-credit-p3

**Compute cost model (owned by `fabric-data-agent-ops`, listed for cross-reference only)**
- https://learn.microsoft.com/fabric/fundamentals/how-copilot-works
- https://learn.microsoft.com/fabric/fundamentals/copilot-fabric-consumption
- https://learn.microsoft.com/fabric/enterprise/fabric-operations

---

## 7. Worked offer section - "Licensing & consumption" (advisor-led, F4)

A reusable template for `pingala-offer`. Advisor-led: one committed spec, no mechanics, the only
customer decision is the data-residency sign-off. Adjust names and figures per engagement; run the
`pingala-offer` and `writing-voice` self-checks before it ships.

> ### Licensing & consumption
>
> Required for the agent, verified against Microsoft documentation (June 2026).
>
> **<Customer> to confirm in place:**
>
> | Requirement | Detail |
> |---|---|
> | Fabric capacity | Paid capacity (F4) runs the agent and the subset model. |
> | Power BI Pro or PPU | Per user consuming the agent's model content, on capacities below F64. On F64 and above, free users can consume. |
> | Tenant settings | Fabric Data Agent setting on, Copilot extensibility enabled, cross-geo AI processing and storage enabled. |
>
> **Consuming the agent in Teams** (preview, June 2026). Cost follows the licence the user already
> holds:
>
> | User holds | Cost of agent use |
> |---|---|
> | Microsoft 365 Copilot (paid add-on) | Included. Nothing extra to buy or meter. |
> | Standard M365/O365, no Copilot | Reached via Copilot Chat. Each use is metered to <Customer> in Copilot Credits (pay-as-you-go or prepaid packs). |
>
> Pingala sizes any metered usage with the Copilot Credits estimator at the question-types session.
>
> **Publishing and access.** Publishing to a named group is immediate and fits Phase 1; org-wide
> publishing needs M365 admin approval. Each user sees only what their permissions allow.
>
> **Data residency (EU).** When the agent is used in Teams, the questions and answers may be
> processed or stored by Microsoft outside the EU region. The Fabric source data does not move; only
> the Copilot conversation may leave the region. <Customer> confirms before Phase 1: accept the Teams
> terms, or keep the agent in the in-region Fabric chat pane. Pingala obtains written confirmation
> from Microsoft if required.

The data-residency line is the single legitimate customer decision (a compliance sign-off); every
other line is Pingala's committed call. Keep the $0.01 rate, the 25,000-credit pack, the CU
mechanics, and the admin steps OUT of the offer - they are technical-note material.
