# Capacity SKUs and per-user licensing - tables (reference)

The detail layer for `fabric-licensing`. Every figure is grounded in MS Learn. Where MS Learn does not publish a number (notably dollar prices), this file says so rather than inventing one.

> Verified against MS Learn on 2026-06-25. Re-verify before any priced commitment and at least quarterly (the P SKUs are being retired and CU rates can change).

---

## 1. The F-SKU ladder

The F number equals the SKU's Capacity Units (CUs). ([licenses](https://learn.microsoft.com/fabric/enterprise/licenses), verified 2026-06-25)

| SKU | Capacity Units | Power BI v-cores | Note |
|---|---|---|---|
| F2 | 2 | 0.25 | Floor to enable Fabric features (incl. data agents, Copilot) |
| F4 | 4 | 0.5 | Pingala default starting capacity |
| F8 | 8 | 1 | |
| F16 | 16 | 2 | |
| F32 | 32 | 4 | |
| F64 | 64 | 8 | **= P1.** The free-viewing threshold |
| F128 | 128 | 16 | |
| F256 | 256 | 32 | |
| F512 | 512 | 64 | |
| F1024 | 1024 | 128 | |
| F2048 | 2048 | 256 | |

CUs translate to consumption over a 30-second evaluation window (CU count x 30 = CUs per 30s; F64 = 1,920). ([plan-capacity](https://learn.microsoft.com/fabric/enterprise/plan-capacity), verified 2026-06-25)

---

## 2. Per-user capability matrix

Source for the whole table: [licenses](https://learn.microsoft.com/fabric/enterprise/licenses) (verified 2026-06-25)

| Capability | Free | Pro | PPU |
|---|---|---|---|
| Access the Fabric web app | Yes | Yes | Yes |
| Create non-Power BI Fabric items (in an F/Trial-capacity workspace) | Yes | Yes | Yes |
| Share non-Power BI Fabric items | Yes | Yes | Yes |
| Create/update/manage Power BI items outside *My workspace* | No | Yes | Yes |
| Create Pro or Premium (P) workspaces | No | Yes | Yes |
| Create PPU workspaces | No | No | Yes |
| View Power BI content in a Pro workspace or a sub-F64 capacity | No | Yes | Yes |
| View content with a viewer role on F64+ or a P capacity | Yes | Yes | Yes |

Key constraints:

- **PPU does not provision a Fabric capacity.** It is a per-user feature set, not a capacity; non-Power BI Fabric items still need an F or Trial capacity. ([licenses](https://learn.microsoft.com/fabric/enterprise/licenses), verified 2026-06-25)
- **PPU sharing:** PPU content can be shared only with other PPU users, unless it sits in a Premium/F64+ capacity. Model size limit 100 GB. ([PPU FAQ](https://learn.microsoft.com/power-bi/enterprise/service-premium-per-user-faq), verified 2026-06-25)
- **PPU is positioned as more cost-effective than a Premium capacity when Premium features are needed for fewer than 250 users.** ([licenses](https://learn.microsoft.com/fabric/enterprise/licenses), verified 2026-06-25)

---

## 3. The F64 rule (per-seat cost lever)

- **Below F64** (and all A SKUs): every user **viewing** Power BI content needs **Pro, PPU, or an individual trial**. ([licenses](https://learn.microsoft.com/fabric/enterprise/licenses), verified 2026-06-25)
- **F64 or larger** (or a P capacity): a **Free** licence with a viewer role can view Power BI content. ([licenses](https://learn.microsoft.com/fabric/enterprise/licenses), verified 2026-06-25)
- F64 = 64 CU = 8 v-cores = the old P1/A4. ([licenses](https://learn.microsoft.com/fabric/enterprise/licenses), verified 2026-06-25)

The decision: for a large viewer audience, F64 (Free viewers) can beat a smaller SKU plus many Pro seats; for a small audience, a smaller SKU plus Pro/PPU is cheaper. Model both at offer time against live prices.

---

## 4. Trials

- **Fabric (capacity) trial:** free for **60 days**, acts like an **F64** for viewing (Trial SKU = 64 CU / 8 v-cores), and includes a per-user entitlement "similar to PPU" (a Power BI individual trial with PPU-equivalent rights). ([fabric-trial](https://learn.microsoft.com/fabric/fundamentals/fabric-trial); [licenses](https://learn.microsoft.com/fabric/enterprise/licenses), verified 2026-06-25)
- The individual trial gives PPU-equivalent use rights, but **a Fabric capacity is still required for non-Power BI workloads**. ([fabric-trial](https://learn.microsoft.com/fabric/fundamentals/fabric-trial), verified 2026-06-25)
- **At end of trial (60 days):** trial capacity access is revoked, non-Power BI items go inactive, content stays in OneLake for **7 days**, and a paid **F or P** capacity reactivates it. Trial capacity does not support autoscale. ([fabric-trial](https://learn.microsoft.com/fabric/fundamentals/fabric-trial), verified 2026-06-25)

---

## 5. Purchase, reservation, pause, scale

| Topic | Fact | Source (verified 2026-06-25) |
|---|---|---|
| SKU families | **Azure F SKUs** (Azure portal, per-second billing, 1-minute minimum, no commitment, recommended) vs **M365 P SKUs** (monthly/yearly commitment, EA-only, being retired) | [buy-subscription](https://learn.microsoft.com/fabric/enterprise/buy-subscription) |
| Purchase rights | Owner or Contributor on the Azure subscription, or the `Microsoft.Fabric/capacities/*` RBAC actions; plus a Fabric Free or Power BI licence | [buy-subscription](https://learn.microsoft.com/fabric/enterprise/buy-subscription) |
| CSP path | F SKUs can be bought through a Cloud Solution Provider; same product, partner billing | [buy-subscription](https://learn.microsoft.com/fabric/enterprise/buy-subscription) |
| Reservation | 1- or 3-year commitment, bought in 1-CU increments, tied to an Azure region and billing frequency; covers **capacity CU only** (not storage/networking); hourly, **no carryover**; reverts to pay-as-you-go on expiry; refund cap USD 50,000 per rolling 12 months per billing scope | [fabric reservation](https://learn.microsoft.com/azure/cost-management-billing/reservations/fabric-capacity) |
| Saving % (reserved vs PAYG) | **Not published on MS Learn** - the page says it "saves money" and links to Azure pricing. Do not quote a percentage as MS-sourced | [fabric reservation](https://learn.microsoft.com/azure/cost-management-billing/reservations/fabric-capacity) |
| Pause / resume | Pause stops compute billing but **settles outstanding smoothed/overage usage**; resume resumes billing; can be scheduled via Azure Automation or the suspend/resume REST APIs | [pause-resume](https://learn.microsoft.com/fabric/enterprise/pause-resume) |
| Scale | Resize up/down in the Azure portal; charged PAYG for the size you scale to; scaling below a reservation does not change the bill; sub-F64 scale-up is near-immediate (licence update up to a day) | [scale-capacity](https://learn.microsoft.com/fabric/enterprise/scale-capacity) |

---

## 6. Copilot / AI in Fabric metering

- No per-user Copilot-in-Fabric licence; it consumes capacity CUs. Requires paid F2+/P1+ (Pro/PPU alone insufficient); not on trial SKUs. ([copilot overview](https://learn.microsoft.com/fabric/fundamentals/copilot-fabric-overview), verified 2026-06-25)
- Token rates: **100 CU-seconds per 1,000 input tokens, 400 per 1,000 output**; background-smoothed over 24h; **rates can change** (date any quote). Worked example: 2,000 input + 500 output = 400 CU-seconds. ([copilot consumption](https://learn.microsoft.com/fabric/fundamentals/copilot-fabric-consumption), verified 2026-06-25)
- The compute-cost monitoring, baselining, and runaway control for this is owned by `fabric-data-agent-ops` - not restated here.
- Region gate: Azure OpenAI in US + EU data boundary only; outside that, Copilot is disabled until an admin enables cross-geo processing. ([copilot overview](https://learn.microsoft.com/fabric/fundamentals/copilot-fabric-overview), verified 2026-06-25)

---

## 7. What is and is NOT priced on MS Learn

**Not published on MS Learn (do not invent):**

- F-SKU dollar list prices - the buy-subscription and plan-capacity pages link to the Azure pricing calculator; pricing is regional. ([buy-subscription](https://learn.microsoft.com/fabric/enterprise/buy-subscription), verified 2026-06-25)
- Per-user (Pro/PPU) dollar prices - the licensing pages link to the Power BI pricing page, not a number. ([PPU FAQ](https://learn.microsoft.com/power-bi/enterprise/service-premium-per-user-faq), verified 2026-06-25)
- The reserved-vs-PAYG saving percentage.

**Cost-positioning facts that ARE on MS Learn:** PPU is cheaper than a Premium capacity below ~250 users; the Fabric trial is free for 60 days; F SKUs bill per second with no commitment.

---

## 8. Citation list

**Licenses / per-user / F64**
- https://learn.microsoft.com/fabric/enterprise/licenses
- https://learn.microsoft.com/power-bi/enterprise/service-premium-per-user-faq
- https://learn.microsoft.com/power-bi/fundamentals/service-features-license-type
- https://learn.microsoft.com/fabric/fundamentals/fabric-trial

**Capacity purchase / reservation / pause / scale**
- https://learn.microsoft.com/fabric/enterprise/buy-subscription
- https://learn.microsoft.com/fabric/enterprise/plan-capacity
- https://learn.microsoft.com/azure/cost-management-billing/reservations/fabric-capacity
- https://learn.microsoft.com/fabric/enterprise/pause-resume
- https://learn.microsoft.com/fabric/enterprise/scale-capacity

**Copilot in Fabric**
- https://learn.microsoft.com/fabric/fundamentals/copilot-fabric-overview
- https://learn.microsoft.com/fabric/fundamentals/copilot-fabric-consumption

**Live dollar figures:** Azure pricing calculator and the Fabric pricing page (azure.microsoft.com/pricing/details/microsoft-fabric/).
