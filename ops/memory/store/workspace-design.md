---
id: workspace-design
ts: 2026-05-26T15:23:20Z
type: semantic
scope: workspace
source: session:d4312c2c-133a-40da-9be4-adf97e82ea38
tags: [project]
status: distilled
description: "DEV workspace design decisions — two buckets (own/customers), two types (content/function), focus field, scale, agents, knowledge flow via INBOX.md"
---

DEV workspace uses a two-bucket model based on delivery obligation:
- `own/` — discretionary, no external obligation
- `customers/[client]/[project]/` — someone external is waiting

**Why:** Origin of work is often blurry (customer work spawns tools, personal tools serve customers). Delivery obligation is the one clear axis.

**How to apply:** Never suggest scratch/ or team/ buckets. Scale (spike/project) replaces the old scratch concept. Track origin via `initiated_by:` field, not folder location.

Related: [[agent-framework]], [[knowledge-flow]]
