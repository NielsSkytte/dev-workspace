---
id: eval-2026-08-18-answered-a-narrower-question
ts: 2026-08-18T18:40:00Z
type: evaluative
scope: workspace
source: session:metaatomic-fabric-host
tags: [evaluative, research, docs, fabric, workspace-identity, own-output]
status: distilled
description: "evaluative: asked whether a notebook can use the workspace identity, I searched, found the execution-context doc, and answered 'no' - the doc answered a narrower question than the one asked, and the user knew it"
---

**Niels:** "can we use workspace identity?"

I searched MS Learn, found *Security context of running notebook*, and reported a flat **no** —
workspace identity is for trusted access to external resources, a notebook runs as the interactive
user / the pipeline's last-modified user / the schedule's creator.

**Niels:** *"wrong, you can run a notebook as wi, its a setting when you create the connection and
when you run the notebook in a pipeline you can then select that, check up on that now."*

He was right. Workspace identity is reachable from a notebook through a Fabric Connection created
with WI authentication and the *Allow Code-First Artifacts* checkbox, and a Fabric Apache Airflow
Job runs notebooks as the workspace identity outright.

## What actually went wrong

The document I found was accurate and I quoted it correctly. It answers **"what identity executes
the notebook's code?"**. The question asked was **"can we use workspace identity?"** — which is
also about what the notebook *authenticates as*, a different axis. I collapsed the two, and the
citation made the wrong answer look settled.

This is not a search-depth failure. One more query (`connection authentication kind workspace
identity`) would have found it, and I ran exactly that query *after* being corrected. It is a
scope failure: I stopped when a document answered *a* question rather than *the* question.

**Rule earned:** when a doc answers a narrower question than the one asked, say which question it
answered. "The execution context is X; whether WI can be used for *authentication* is a separate
question I haven't checked" would have been correct, useful, and would have invited exactly the
correction that came anyway.

## What the correction was worth

Chasing it down found a latent defect in code already deployed to a customer: the notebook wired
`notebookutils.credentials.getToken` straight into the engine's token hook, but that API takes an
**audience key** (`pbi`, `storage`, `keyvault`, `kusto`), not a resource URL. The first live online
call would have failed. Only offline mode had run, so nothing had surfaced it.

Following the corrected thread further removed the premise entirely: the SQL leg needs no connection
and no token, because `notebookutils.data.connect_to_artifact` queries a lakehouse or warehouse
under the notebook's own identity. The user's push produced a **simpler** design than the one I was
defending — I had been about to ask him to create a connection he did not need.

**Second-order lesson:** a confident wrong answer costs more than a slow one, because it stops the
person who knows better from telling you. He only pushed back because he happened to be certain.

Related: [[fabric-notebook-identity-and-sql]], [[eval-2026-08-07-convenient-sample]],
[[eval-2026-08-06-sample-of-four]]
