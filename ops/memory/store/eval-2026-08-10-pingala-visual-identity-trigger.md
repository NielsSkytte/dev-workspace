---
id: eval-2026-08-10-pingala-visual-identity-trigger
ts: 2026-08-10T12:40:00Z
type: evaluative
scope: workspace
source: session:7cf8059d
tags: [skills, pingala-visual-identity, design, evaluation, M]
status: distilled
description: "Evaluative: pingala-visual-identity skill was not automatically loaded prior to creating HTML architecture diagrams. Corrected: invoke pingala-visual-identity for ALL visual, HTML, and presentation deliverables."
---

**The miss:** When asked to generate an architecture diagram / HTML overview for Carl Ras, the assistant generated a generic dark/light theme rather than immediately loading the `pingala-visual-identity` skill. The user corrected: *"look at our pingala design skill for this... agent M this should be a job for you"*.

**Root cause:** While the `.agents/skills` junction was correctly created, `pingala-visual-identity` was not automatically triggered by context during visual output generation.

**Rule earned / Action taken:**
1. **Agent M Mandate:** Whenever creating ANY visual output (HTML pages, architecture diagrams, slides, document formatting, design artifacts), **Agent M must check and invoke `pingala-visual-identity` first**.
2. **Pingala Visual Standards:**
   - Palette: Deep Teal (`#4D7878`), Sage (`#60756E`), Terracotta (`#B5442A`), Warm Cream (`#EEE4DE`), Warm Gray (`#827560`).
   - Fonts: `Aptos Display` for headings, `Aptos` for body, `Ink Free` for callout notes / annotations.
3. Updated [`customers/Carl-Ras/datahub/design/carlras_architecture_overview.html`](file:///C:/Dev/customers/Carl-Ras/datahub/design/carlras_architecture_overview.html) to full Pingala Visual Identity compliance.
