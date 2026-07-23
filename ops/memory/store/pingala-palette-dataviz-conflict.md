---
id: pingala-palette-dataviz-conflict
ts: 2026-07-23T07:30:00Z
type: reference
scope: workspace
source: session:14457941
tags: [pingala-visual-identity, dataviz, palette]
status: distilled
description: "Pingala's muted brand palette FAILS the dataviz validator (teal chroma 0.048-0.056 < 0.10 floor; teal steps dE 12.8 < 15); use the validated chroma-boosted brand-hue sets derived 2026-07-21"
---

Pingala's brand palette cannot produce validator-passing categorical data colors:
the teals (#4D7878, #6BA0A0, #60756E) sit at OKLCH chroma 0.048-0.056 (floor 0.10,
"reads gray") and the two teal steps fail the normal-vision floor (dE 12.8 < 15).
Only the terracotta row passes chroma.

**Resolution precedent (Element Logic lineage viewer, validated in-browser both modes):**
derive chroma-boosted steps ON the brand hues, distinct hue families with a
lightness ladder; neutrals stay structural (never data colors — matches the brand's
own "neutrals for structure" rule).
- Light surface `#EEE4DE`: raw `#CC845A`, enriched `#5A781E`, curated `#24A8A8`, exchange `#BA7242`
- Dark surface `#232B2A`: raw `#CC783C`, enriched `#3C783C`, curated `#1EA29C`, exchange `#AE7836`
Contrast check lands in the "relief" band → visible labels + a table view are mandatory.

Reuse these sets (or the derivation method: same hue, C >= 0.105, lightness ladder,
validate with the dataviz `validate_palette.js`) for any Pingala data visualization.
