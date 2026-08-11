---
id: eval-2026-08-11-binding-is-not-code
ts: 2026-08-11T09:20:00Z
type: evaluative
scope: workspace
source: session:7500d6dd
tags: [evaluation, method, fabric, notebook, deployment-pipeline, carl-ras]
status: distilled
description: "Cleared a notebook as safe to run in TEST after verifying its serialized lakehouse binding, without reading the code that ignores it - would have silently written TEST's ingest into DEV"
---

**What happened.** Diagnosing why `Warehouse_Enriched_GTM` failed to deploy into Fabric-ETL-TEST,
I established the fix needed `NB_Raw_GTM` to run in TEST and populate its Raw lakehouse. To check
the notebook would target the right environment, I exported TEST's deployed copy and read its
`.platform`/META block:

```
"default_lakehouse": "26291c66…",                 # TEST's Lakehouse_Raw_GTM
"default_lakehouse_workspace_id": "c2792367…",    # TEST
```

Correctly remapped by the deployment pipeline. I told Niels: "I checked the deployed copy… it will
run", and listed it as a step to execute.

**Why that was wrong.** The notebook does not use its default lakehouse. Line 93 read
`lakehouse.get(name="Lakehouse_Raw_GTM", workspaceId="fe4c7544…")` — the DEV workspace id,
hardcoded. Running it in TEST would have written TEST's ingest into **DEV's** Raw lakehouse and
exited green. I had the file open in context from the repo before I made the claim; I read the
first 80 lines for the parameters cell and did not read line 93 until the next turn, when Niels
said "run them" and I went looking for the job syntax.

**The error of method.** I verified the *declared binding* and treated it as proof of *runtime
behaviour*. Those are different artifacts, and in Fabric they routinely disagree: the META block
is what the deployment pipeline rewrites, the code is what executes. Checking the one that gets
rewritten is checking the thing least likely to be wrong.

**Cost.** None realised — the pre-run check caught it. It was one "okay run them" away from a
silent cross-environment write with a success message on it, which is the hardest kind to notice
later.

**Rule.** Before saying an item is safe to run in an environment, read the code that resolves its
targets, not the serialized binding. Grep the item for GUIDs and account for every one. Config
that a deploy step rewrites is never evidence about code that ignores it.

See [[fabric-env-portability]] for the resulting convention.
