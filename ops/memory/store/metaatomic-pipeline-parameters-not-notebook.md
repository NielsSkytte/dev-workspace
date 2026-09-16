---
id: metaatomic-pipeline-parameters-not-notebook
ts: 2026-09-16T11:30:00Z
type: fact
scope: own/MetaAtomic
source: /log
tags: [metaatomic, fabric, pipeline, notebook, parameters, deployment]
description: Every customer value is a pipeline parameter on the NB_MetaAtomic activity in pipeline-content.json; the pipeline overrides the notebook's parameter cell on every run, so the notebook is identical at every customer and is never edited
status: distilled
---

Owner asked (2026-09-16) whether step 2.3 of Lars's checklist edits the notebook's parameter cell in the
service or the pipeline. Answer: the pipeline. Editing the cell would hold for a manual notebook run
only; the scheduled pipeline injects its values and wins. Two equivalent routes: edit
`Fabric/Orchestration/Schedule/PL_UpdateLineage.DataPipeline/pipeline-content.json` in the repo and
push, or after Update open the pipeline in the service, select the activity, Settings > Base parameters,
set the values, commit from Source control - git ends with the same file. Written into the checklist as
the alternative. Related: a `tags: [parameters]` cell is NOT honoured by Fabric; the `# PARAMETERS CELL`
header is (measured 2026-09-15, build.py).
