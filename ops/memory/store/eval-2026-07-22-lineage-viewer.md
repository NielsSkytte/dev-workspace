---
id: eval-2026-07-22-lineage-viewer
ts: 2026-07-23T07:30:00Z
type: evaluative
scope: workspace
source: session:14457941
tags: [evaluative, skill-dataviz, skill-pingala-visual-identity, skill-pingala-fabric-platform]
status: distilled
description: "dataviz + pingala-visual-identity fired and helped (validator caught real brand failures); pingala-fabric-platform GAP: no layer-identification conventions documented, engine had to derive them"
---

Element Logic lineage sessions (07-20 → 07-23):

- **Fired + helped:** `dataviz` — loaded before the HTML viewer; its run-the-validator
  rule caught that the Pingala brand palette genuinely fails CVD/chroma checks
  (would have shipped broken otherwise); the in-browser validator loop drove the
  palette to a passing state. `pingala-visual-identity` — supplied the brand
  parameters; the conflict it surfaced is recorded in [[pingala-palette-dataviz-conflict]].
- **Gap (should have carried more):** `pingala-fabric-platform` — the Phase-0 agent
  found the skill documents medallion/Views-to-Tables but NOT the concrete
  layer-identification conventions (datastore name prefixes `Lakehouse_Raw_*` /
  `Warehouse_Enriched_*`, warehouse schema roles `viewtransform`/`dim`/`fact`,
  item prefixes PL_/NB_/VL_, dynamic-CTAS materialization pattern). The engine
  derived them from the repo and Niels confirmed. **Candidate skill update**, not
  a new skill (freeze rule): fold the confirmed conventions from
  `LineageDocumentation/docs/phase0-architecture-proposal.md` section 5 into the skill.
- **Correctly silent:** offer/email/writing skills (no customer-facing prose).
- **Process note:** all verification this session ran through workflows/agents
  (bake-off, censuses, adversarial edge verification) — the never-fabricate
  audit pattern held up and is worth repeating for correctness-critical builds.
