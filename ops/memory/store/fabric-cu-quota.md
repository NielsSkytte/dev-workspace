---
id: fabric-cu-quota
ts: 2026-07-23T00:00:00Z
type: reference
scope: workspace
source: session:36359848 (/log distill, Carl-Ras fabric CapacityManager session 07-17)
tags: [fabric, capacity, quota, azure, arm, scale, carl-ras]
status: distilled
description: Fabric regional CU quota - a per-subscription/region ceiling separate from licensing; blocks scale/create with ARM 400 BadRequest; portal request can auto-deny -> support ticket; reservations never block scaling
---

Facts established 2026-07-17 debugging the Carl Ras CapacityManager scale-up (ARM rejected
F16 -> F32) plus MS Learn / community verification:

1. **Regional CU quota is its own gate.** Each Azure subscription has a regional Microsoft
   Fabric CU quota (sum of all Fabric capacities' CUs in that region). Exceeding it fails a
   scale PATCH / capacity create with **HTTP 400 `BadRequest`** stating
   `TotalCapacityUnits / RegionalQuota / RequestedSku` - not a 403, so it reads like a malformed
   request until the body is inspected. ([fabric-quotas](https://learn.microsoft.com/fabric/enterprise/fabric-quotas))
2. **Quota depends on subscription type and region; defaults are not published.** Observed:
   Carl Ras sub = 16, Niels's leita test sub = 32. A delta like this is NOT by itself evidence
   Microsoft lowered defaults (sub types differ). No official statement of lowered Fabric
   defaults in NEU/WEU found (checked 2026-07-17), though general EU capacity pressure is
   documented (Aidan Finn, June 2026: WEU severely constrained, NEU emerging pressure - VMs/
   OpenAI, Fabric not named) and firsthand reports say new NEU/WEU Fabric capacities need
   support tickets.
3. **Increase path:** Azure portal -> Quotas -> Microsoft Fabric -> New Quota Request; reviewed
   "within minutes" but can be **auto-denied** (Microsoft caps self-service by sub type +
   region); the fallback is a support ticket (Service and subscription limits -> Microsoft
   Fabric). A Microsoft moderator pointed an identical F8->F64 case straight to the ticket.
4. **Reservations never block scaling** - a reservation is a billing-layer discount only; you
   pay PAYG for CUs above the reserved volume and scaling below the reservation doesn't change
   the bill ([scale-capacity](https://learn.microsoft.com/fabric/enterprise/scale-capacity),
   also in the fabric-licensing skill, verified 2026-06-25). Quota, not reservation, is the
   scale ceiling.
5. **Consulting takeaway:** when sizing a scale-up pattern (CapacityManager), check the
   subscription's Fabric quota headroom up front - `GET .../providers/Microsoft.Fabric/
   locations/.../usages` or portal Quotas - and put the quota request in the customer-setup
   requirements, since the round-trip can take days if it escalates to a ticket.

Candidate skill update: `fabric-licensing` has no quota section (quota is purchase-adjacent,
not licence) - consider adding this as a reference there or to a capacity-ops skill.
