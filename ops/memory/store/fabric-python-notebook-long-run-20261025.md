---
id: fabric-python-notebook-long-run-20261025
ts: 2026-10-25T17:30:00Z
type: fact
scope: workspace
source: /log session ebd8d221 (MetaAtomic base runs)
tags: [fabric, python-notebook, configure, vcores, notebookutils, azcopy, metaatomic]
status: distilled
description: "Fabric Python notebooks on long runs: default 2-vCore node segfaulted (exit -11); %%configure first cell fixes it and serializes in git as '# MAGIC' lines; fs.cp (azcopy) failed after 1 h 48 min, fs.put fallback"
---

- Pingala base `PL_UpdateLineage` (MetaAtomic, 1017 Fabric Link tables): on the default Python node
  (2 vCores, 16 GB) the kernel died with exit -11 (Invalid memory reference) at 1 h 22 min. With
  `{"vCores": 8}` the run Completed end to end (13:17-17:31 CET). Memory as the cause is inference.
- `%%configure -f` must be the FIRST code cell for a pipeline run. In the git `.py` format a code cell
  written as `# MAGIC %%configure -f` / `# MAGIC {"vCores": 8}` imports as a real code cell
  (checked with getDefinition format=ipynb). MetaAtomic `build.py` emits this for any `%%` cell (`b2b34ef`).
- `notebookutils.fs.cp("file:...", abfss)` of a large file goes through azcopy and failed after
  1 h 48 min (AzCopyFailedException; full log not retrievable, livy driver logs 404). MetaAtomic now
  falls back to `fs.put` with the text (`c52c741`). Cause (token age vs size) unproven.
- Livy sessions API gives state and cancellationReason only; driver logs for Python notebooks 404.
