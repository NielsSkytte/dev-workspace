---
id: stream-matrix-needs-panel
ts: 2026-09-16T09:20:00Z
type: decision
scope: own/MetaAtomic
source: /log
tags: [metaatomic, stream-matrix, self-describing, deployment]
description: The stream matrix page lists every value it cannot show ("What this page still needs") with the pipeline parameter or judgement-file field that supplies it; the hardcoded DEV/TEST scope sentence is gone
status: distilled
---

Owner's requirement (2026-09-16): the matrix must run once environment and workspace ids are given, and
from then on the page itself must say what is still to be input and where. `stream_matrix/render.needs`
derives two kinds of rows and embeds them as `_needs`: measured (ENVIRONMENTS unset -> environment
columns empty; a store whose count was refused -> read right on the item) and authored (a stage's
`missing_actions`, an empty `models_and_activation`, a placeholder `environment_scope`), each naming
`design/stream_matrix_data.json` and the field, or the pipeline parameter. The template renders a
collapsible panel above the legend. The template's hardcoded "Active development ... in DEV and TEST"
note was false for any production customer and is replaced by the document's `environment_scope`,
hidden when empty. Lines in the judgement file that say "fill from the live workspace" are measured by
the run and must not stay as authored gaps (removed from the Element Logic file).
