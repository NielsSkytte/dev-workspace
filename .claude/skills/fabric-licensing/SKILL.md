---
name: fabric-licensing
bundle: custom
description: >
  Microsoft Fabric licensing and cost - capacity SKUs (F2 to F2048), the per-user tiers
  (Free / Pro / PPU), the F64 viewing threshold, how capacity is bought (pay-as-you-go vs a
  capacity reservation, pause/resume), how Copilot and AI in Fabric are metered, the tenant and
  data-residency gates, and how to state any of it in a customer offer without leaving Pingala
  exposed. Use this skill whenever someone asks what Fabric costs, which licence a user needs,
  how to size an F SKU, Pro vs PPU vs Free, the F64 rule, reserved vs pay-as-you-go capacity,
  pausing a capacity to save money, how Copilot/AI in Fabric is licensed, or how to price or size
  a Fabric or data-agent offer. Trigger on "what does Fabric cost", "which Fabric licence", "do
  they need Pro or PPU", "F64 rule", "F2 vs F4 vs F64", "reserved vs pay-as-you-go capacity",
  "pause the capacity", "Copilot in Fabric licensing", "price the Fabric offer". This skill owns
  the LICENCE and CAPACITY-PURCHASE picture. Data-agent consumption (Teams, M365 Copilot vs
  Copilot Credits, publishing, residency) is in `references/data-agent-consumption.md`. The
  CU / AI-Query compute MONITORING and runaway control live in `fabric-data-agent-ops`. Composes
  with `pingala-offer` (what a fact looks like in an offer). Every fact is cited to MS Learn with a
  verified date; re-verify before any priced commitment. Use even if the user asks about one piece.
---

# Microsoft Fabric licensing

The money-and-access reference for Fabric: which licence a user needs, what capacity to buy and how, and how Copilot/AI is metered. **Every fact is cited to MS Learn with a verified date**, because Fabric licensing is version-volatile (the Power BI Premium P SKUs are being retired; Copilot CU rates can change). Re-verify on the canonical pages (end of this file) before any priced commitment.

## How to use this skill

- **Who needs what, and capacity-purchase mechanics:** this file plus `references/capacity-and-per-user.md`.
- **Consuming a DATA AGENT** (Teams / M365 Copilot vs Copilot Credits, publishing surfaces, residency): `references/data-agent-consumption.md` and `references/data-agent-licensing-tables.md`.
- **CU / AI-Query compute COST monitoring, baselines, runaway alerting:** `fabric-data-agent-ops` (do not restate it here).
- **Putting any of it in a customer offer:** the *Offer translation* section below, plus `pingala-offer`.
- **Need a current, precise answer:** use the Microsoft Learn MCP (`microsoft_docs_search` / `microsoft_docs_fetch`) and update the citations and the verified date.

## The two licence types (they stack)

Fabric needs **both** a capacity and **at least one per-user licence**; they are not interchangeable, they stack. ([licenses](https://learn.microsoft.com/fabric/enterprise/licenses), verified 2026-06-25)

- **Capacity** = the compute pool, sized in Capacity Units (CUs) via SKUs (F2 to F2048; legacy P1 to P5). It licenses Fabric features and lets you create and run Fabric items.
- **Per-user** = Free, Pro, or Premium-Per-User (PPU). Governs what an individual can author and view.

## Capacity SKUs (F2 to F2048)

- **The F number equals the CU count** (F2 = 2 CU, F64 = 64 CU = 8 v-cores = the old P1). Full ladder in `references/capacity-and-per-user.md`. ([licenses](https://learn.microsoft.com/fabric/enterprise/licenses), verified 2026-06-25)
- **F2 is the floor to turn features on** (including data agents and Copilot), not a sizing recommendation. Pingala starts at F4 and sizes production from measured CU - that sizing is an ops call (`fabric-data-agent-ops`).
- **P-SKU retirement:** Microsoft is retiring the Power BI Premium per-capacity P SKUs; new and existing customers should move to **F SKUs**. Flag this in any offer or environment that still assumes a P SKU. ([licenses](https://learn.microsoft.com/fabric/enterprise/licenses), verified 2026-06-25)

## Per-user tiers and the F64 rule (the biggest cost lever)

- **Free** is auto-assigned on first Fabric sign-in. It can create and share **non-Power BI Fabric items** (lakehouse, warehouse, notebook, pipeline) in an F or Trial-capacity workspace, but cannot create or share Power BI items outside its own *My workspace*. ([licenses](https://learn.microsoft.com/fabric/enterprise/licenses), verified 2026-06-25)
- **Pro** can create and share Power BI content. **Every org using Power BI in Fabric needs at least one Pro or PPU user.** ([licenses](https://learn.microsoft.com/fabric/enterprise/licenses), verified 2026-06-25)
- **PPU** adds most Premium features per user (the XMLA endpoint, larger models, 48 refreshes/day), but **does not provision a Fabric capacity** - PPU alone cannot run non-Power BI Fabric items. ([licenses](https://learn.microsoft.com/fabric/enterprise/licenses); [PPU FAQ](https://learn.microsoft.com/power-bi/enterprise/service-premium-per-user-faq), verified 2026-06-25)
- **The F64 line (the single biggest per-seat cost lever):** **below F64**, every user *viewing* Power BI content needs **Pro, PPU, or an individual trial**; **at F64 or larger** (or a P capacity), a **Free** viewer can view. ([licenses](https://learn.microsoft.com/fabric/enterprise/licenses), verified 2026-06-25)
- **Creating** non-Power BI Fabric items needs only **Free plus an F/Trial capacity**, at any SKU size. ([licenses](https://learn.microsoft.com/fabric/enterprise/licenses), verified 2026-06-25)

Full capability matrix and trial rules in `references/capacity-and-per-user.md`.

## Buying capacity (the cost mechanics MS Learn states)

- **Two SKU families:** **Azure F SKUs** (bought in the Azure portal, **billed per second with a one-minute minimum, no commitment**, pay-as-you-go, the **recommended** option) and **Microsoft 365 P SKUs** (monthly/yearly commitment, EA-only, being retired). ([buy-subscription](https://learn.microsoft.com/fabric/enterprise/buy-subscription), verified 2026-06-25)
- F SKUs can be **scaled** and **paused/resumed**, and discounted with a **1- or 3-year capacity reservation**. A reservation covers **capacity CU only** (not storage or networking), applies hourly with no carryover, and reverts to pay-as-you-go when it expires. ([buy-subscription](https://learn.microsoft.com/fabric/enterprise/buy-subscription); [fabric reservation](https://learn.microsoft.com/azure/cost-management-billing/reservations/fabric-capacity), verified 2026-06-25)
- **Pausing** an F SKU stops compute billing, but **settles outstanding smoothed/overage usage** at pause; resuming resumes billing. A pause is a real cost lever for non-production capacities. ([pause-resume](https://learn.microsoft.com/fabric/enterprise/pause-resume), verified 2026-06-25)
- F SKUs can also be bought via a **Cloud Solution Provider (CSP)**; same product, partner billing.
- **Dollar prices are NOT on MS Learn.** The pages point to the **Azure pricing calculator** for regional list prices. Quote from the calculator at offer time; do not state a price from memory. ([buy-subscription](https://learn.microsoft.com/fabric/enterprise/buy-subscription), verified 2026-06-25)

## Copilot and AI in Fabric licensing

- **No separate per-user licence for Copilot-in-Fabric** - it **consumes capacity CUs** (metered, not seat-licensed). ([copilot overview](https://learn.microsoft.com/fabric/fundamentals/copilot-fabric-overview), verified 2026-06-25)
- Requires a paid **F2+/P1+** capacity; **Pro or PPU alone is not sufficient**; not available on trial SKUs. ([copilot overview](https://learn.microsoft.com/fabric/fundamentals/copilot-fabric-overview), verified 2026-06-25)
- Metered by tokens (**100 CU-seconds per 1,000 input, 400 per 1,000 output**), background-smoothed over 24h; **these rates can change** so any quote must be dated. The CU monitoring and runaway side is `fabric-data-agent-ops`. ([copilot consumption](https://learn.microsoft.com/fabric/fundamentals/copilot-fabric-consumption), verified 2026-06-25)
- **Region gate:** Copilot runs on Azure OpenAI in the US and the EU data boundary; if the capacity is outside US/EU it is **disabled until an admin enables cross-geo processing**. UK maps to the EU boundary but still counts as cross-geo. ([copilot overview](https://learn.microsoft.com/fabric/fundamentals/copilot-fabric-overview), verified 2026-06-25)
- **M365 Copilot is a different, separately-licensed product.** The data-agent-in-Teams path and Copilot Credits live in `references/data-agent-consumption.md`, not here.

## Offer translation (business altitude)

Stance and structure are governed by `pingala-offer`; voice by `writing-voice`. In a customer offer:

- Commit **one capacity spec** (e.g. "F4"), **never its region or placement**. F2 is a floor, not the plan.
- State the **per-user position as the plan for this customer** (Pro/PPU below F64, Free viewers at F64+), not as a menu or a rule book.
- State **cost exposure in business terms** - what scales with use, what the customer must licence and budget - so nothing surprises later. Keep the CU rates, credit meters, reservation mechanics, and dollar figures OUT (technical-note or live-quote material).
- The only legitimate customer decision is a **named compliance sign-off** (e.g. data residency), never "which do you prefer".

**This skill replaces the licensing facts** once single-sourced in `writing-voice/references/business-offers.md`. That file keeps its before/after passage as a **voice demonstration only** and points here for facts. If they disagree, **this skill is authoritative.**

## Re-verify (these facts decay)

Fabric licensing is mid-transition: the P SKUs are being retired, "license mode" was renamed "workspace type", and Copilot CU rates are explicitly "subject to change". **Re-verify on the canonical pages before any priced commitment and at least quarterly**, then update the inline "(verified YYYY-MM-DD)" stamps.

Canonical pages:

1. Understand Fabric licenses - https://learn.microsoft.com/fabric/enterprise/licenses
2. Buy a Fabric subscription - https://learn.microsoft.com/fabric/enterprise/buy-subscription
3. What is Copilot in Fabric - https://learn.microsoft.com/fabric/fundamentals/copilot-fabric-overview
4. Copilot consumption and billing - https://learn.microsoft.com/fabric/fundamentals/copilot-fabric-consumption

Data-agent consumption pages are listed in `references/data-agent-licensing-tables.md`. Live dollar figures: the Azure pricing calculator / Fabric pricing page.

> Licensing facts verified against MS Learn on 2026-06-25 (capacity, per-user, Copilot in Fabric) and 2026-06-24 (data-agent consumption).
